# Running looped tests on an ATCA Switch

import sys
import os
from subprocess import Popen, PIPE
import json
import time

from version import VERSION
from arg_parser import ArgParser

from switch_test_logging import logging
logger = logging.getLogger(__name__)

from switchTest.scripts.switchTest import write_values


def main():
    logger.info("\n\n############ TEST STARTS #############\n")

    # Parsing command arguments
    args = _parse_arguments()

    config_file = vars(args)["config-file"]
    test_configs = _parse_config_file(config_file)

    verbose_logging = vars(args)["verbose_logging"]
    if not verbose_logging:
        logger.setLevel(logging.INFO)

    # Get the Shelf Manager address
    shelf_manager = test_configs["hardware"]["shelf_manager"]

    # Get the FPGA Board's slot number, and translate it to the the IPMI address
    slot_number = test_configs["hardware"]["slot"]
    target = str(hex(int(0x80) + 2 * slot_number))

    # IPMP command prefix. We'll be using the Ethernet (LAN) interface, with no authentication
    cmd_prefix = 'ipmitool -I lan -H ' + shelf_manager + ' -t ' + str(target) + ' -b 0 -A NONE '

    # Get the customized status, board activation, and board deactivation commands from the user's configurations
    status_cmd = cmd_prefix + test_configs["test"]["commands"]["status"]
    activation_cmd = cmd_prefix + test_configs["test"]["commands"]["activation"]
    deactivation_cmd = cmd_prefix + test_configs["test"]["commands"]["deactivation"]

    # If the user indicates the test duration to be -1, the test will keep running until it encounters an unrecoverable
    # failure. Otherwise, the test will stop after reaching the user's run limits (in seconds)
    test_duration_seconds = int(test_configs["test"]["test_duration_minutes"])
    if test_duration_seconds == -1:
        logger.info("Looping test indefinitely. Press <Ctrl-C> to terminate.\n")
    else:
        logger.info("Looping test for {0} minutes. Press <Ctrl-C> to terminate.\n".format(test_duration_seconds))

    # The board IP address to ping to confirm its activation/deactivation
    board_ip_address = test_configs["hardware"]["fpga_board_ip_address"]

    # Run the test
    run_test(activation_cmd, deactivation_cmd, status_cmd, board_ip_address,
             test_duration_seconds=test_duration_seconds)

    logger.info("\n############ TEST ENDS #############\n\n")
    logger.info(''.join(['-' * 30, '\n']))


def run_test(activation_cmd, deactivation_cmd, status_cmd, board_ip_address, test_duration_seconds=60*60*24,
             retries=10):
    """
    Run the test after verifying that the board is active. If the board is not, the test will terminate immediately.

    Parameters
    ----------
    activation_cmd : str
        The command to activate the board
    deactivation_cmd : str
        The command to deactivate the board
    status_cmd : str
        The status of the board, used for diagnostics if the activation/deactivation fails
    board_ip_address : str
        The IP address of the board, used for pinging to confirm its activation/deactivation. The ping is expected
        to fail for deactivation of the board; and to be successful for the activation of the board
    test_duration_seconds : int
        The total number of seconds to run the test
    retries: int
        The number of retries the same command if it fails the first time.

    Raises SystemError, RuntimeError
    """
    # Make sure the board is active before starting the test
    is_board_active = _detect_board_active(board_ip_address, expected_board_is_active=True)
    if not is_board_active:
        logger.error("Cannot start the test. The board has to be activated first.")
        raise SystemError

    timeout = time.time() + test_duration_seconds * 60
    while True:
        if time.time() > timeout:
            break

        retry_count = 0

        # Running board deactivation test
        while retry_count <= retries:
            logger.debug("\n*** BOARD DEACTIVATION ***")
            _run_cmd(deactivation_cmd)
            if not _detect_board_active(board_ip_address, expected_board_is_active=False):
                if retry_count < retries:
                    retry_count += 1
                    logger.debug("Retrying board deactivation. Attempt {0} out of {1}".format(retry_count, retries))
                else:
                    # Run the status command to get diagnostic data
                    _run_cmd(status_cmd)

                    logger.error("The board CANNOT be DEACTIVATED. Ending the test.")
                    raise RuntimeError
            else:
                retry_count = 0
                break

        # Running board activation test
        while retry_count < retries:
            logger.debug("\n*** BOARD ACTIVATION ***")
            _run_cmd(activation_cmd)
            if not _detect_board_active(board_ip_address, expected_board_is_active=True):
                if retry_count < retries:
                    retry_count += 1
                    logger.debug("Retrying board activation. Attempt {0} out of {1}".format(retry_count, retries))
                else:
                    # Run the status command to get diagnostic data
                    _run_cmd(status_cmd)

                    logger.error("The board CANNOT be ACTIVATED. Ending the test.")
                    raise RuntimeError
            else:
                # Writing values to board
                logger.debug("\n*** WRITING VALUE TO BOARD ***")
                _write_values_to_board()
                break


def _run_cmd(cmd, sleep_secs=30):
    """
    Run a test command, and then sleep for a few seconds.

    Parameters
    ----------
    cmd : str
        The test command to run
    sleep_secs : int
        The number of seconds to sleep after the command run is finished.
    """
    logger.debug("----- Running IPMI comand: -----")
    logger.debug(cmd)

    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    return_code = proc.returncode

    logger.debug("Return Code: {0}\n".format(return_code))

    stdout_data = stdout.decode()
    if len(stdout_data):
        logger.debug("----- stdout ------")
        logger.debug("{0}".format(stdout_data))

    stderr_data = stderr.decode()
    if len(stderr_data):
        logger.debug("----- stderr ------")
        logger.debug("{0}".format(stderr.decode()))

    _count_down_sleep_status(sleep_secs)


def _detect_board_active(board_ip_address, expected_board_is_active, ping_count=5):
    """
    Detect if the board is active or not, and compare the board's actiness with the expectation. The detection is
    accomplished by pinging the board's IP address. If the ping command's return code is 0, the board is determined
    to be active. Otherwise, the board is determined to be inactive.

    Parameters
    ----------
    board_ip_address : str
        The IP address of the board
    expected_board_is_active : bool
        True if the board is expected to be active; False if not
    timeout : int
        The timeout for the detection command, in seconds
    """
    logger.debug("\n\n----- Detecting if the board is active -----")

    # Send 10 pings (pinging for about 10 seconds)
    proc = Popen("ping " + board_ip_address + " -c " + str(ping_count), shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    return_code = proc.returncode

    status = stdout.decode()
    error = stderr.decode()

    if expected_board_is_active:
        if return_code != 0:
            logger.debug("The board is expected to be ACTIVE, but it does not respond to {0} pings.\n"
                         "stdout: {1}\n\nstderr: {2}\n".format(ping_count, status, error))
            return False
        else:
            logger.debug("The board is ACTIVE, as expected.")
    elif not expected_board_is_active:
        if return_code == 0:
            logger.debug("The board is expected to be INACTIVE, but it still responds after {0} pings.\n"
                         "stdout: {1}\n\nstderr: {2}\n".format(ping_count, status, error))
            return False
        else:
            logger.debug("The board is INACTIVE, as expected.")

    logger.debug("Board activeness detection is finished.\n")
    return True


def _write_values_to_board(sleep_secs=600):
    """
    Write some values to the board to test the board's responsiveness.

    Parameters
    ----------
    sleep_secs : int
        The amount of time to sleep after the value writes.
    """
    write_values()
    _count_down_sleep_status(sleep_secs)


def _count_down_sleep_status(sleep_secs):
    """
    Display a countdown of the remaining sleep seconds.

    Parameters
    ----------
    sleep_secs : int
        The number of seconds for sleep.
    """
    for i in range(sleep_secs, 0, -1):
        sys.stdout.write("\rSleeping for {0} seconds...".format(i))
        sys.stdout.flush()
        time.sleep(1)


def _parse_arguments():
    """
    Parse the command arguments.

    Returns
    -------
    The command arguments as a dictionary : dict
    """
    parser = ArgParser(description="Test hardware responsiveness using IPMI commands.")
    parser.add_argument("config-file", help="The name of test configuration file.")

    parser.add_argument("--verbose-logging", action="store_true")
    parser.add_argument("--version", action="version", version=VERSION)

    args = parser.parse_args()
    return args


def _parse_config_file(config_file):
    """
    Parse the JSON configuration file for the user's testing parameters.

    Parameters
    ----------
    config_file : str
        The path to the config file.

    Returns : dict
        The user's configurations
    -------

    """
    config_file = os.path.expandvars(os.path.expanduser(config_file))
    with open(config_file) as f:
        test_configs = json.loads(f.read())
    return test_configs


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.error("Unexpected exception while running the test. Exception type: {0}. Exception: {1}"
                     .format(type(error), error))



