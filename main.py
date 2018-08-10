# Running looped tests on an ATCA Switch

import sys
import os
import socket
from subprocess import Popen, PIPE
import json
import time
from logging.handlers import RotatingFileHandler

from switchtest_logging import logging, log_formatter
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from version import VERSION
from arg_parser import ArgParser

try:
    import pyrogue as pr
    from FpgaTopLevel import *
except ImportError as error:
    logger.info("ImportError exception: {0}. Make sure you've sourced the pyrogue env script.".format(error))
try:
    from pycpsw import *
except ImportError as error:
    logger.info("ImportError exception: {0}. Make sure you've sourced the CPSW env script.".format(error))

global status_cmd


def main():
    # Parsing command arguments and configurations from the configs file
    args = _parse_arguments()
    config_file = vars(args)["config-file"]
    test_configs = _parse_config_file(config_file)

    # If the user provides a logdir path, use it. Otherwise, use the default, ./logs_{hostname}/
    log_dir_path = test_configs["test"].get("custom_log_directory_path", None)
    logger.info("Log Directory: {0}".format(log_dir_path))
    if not log_dir_path:
        hostname = socket.gethostname()
        log_dir_path = "./logs_" + hostname
    try:
        os.makedirs(log_dir_path)
    except os.error as err:
        # It's OK if the log directory exists. This is to be compatible with Python 2.7
        if err.errno != os.errno.EEXIST:
            raise err

    rotating_log_handler = RotatingFileHandler(os.path.join(log_dir_path, "switch-test.log"), maxBytes=2000000,
                                               backupCount=60)
    rotating_log_handler.setFormatter(log_formatter)

    global_logger = logging.getLogger()
    global_logger.addHandler(rotating_log_handler)

    verbose_logging = vars(args)["verbose_logging"]
    if verbose_logging:
        # This affects the global logger, which affects the pyrogue logger
        global_logger.setLevel(logging.DEBUG)

    logger.info("\n\n############ TEST STARTS #############\n")

    # Get the Shelf Manager address
    shelf_manager = test_configs["hardware"]["shelf_manager"]

    # Get the FPGA Board's slot number, and translate it to the the IPMI address
    slot_number = test_configs["hardware"]["slot"]
    target = str(hex(int(0x80) + 2 * slot_number))

    # IPMI command prefix. We'll be using the Ethernet (LAN) interface, with no authentication
    cmd_prefix = 'ipmitool -I lan -H ' + shelf_manager + ' -t ' + str(target) + ' -b 0 -A NONE '

    # Get the customized status, board activation, and board deactivation commands from the user's configurations
    global status_cmd
    status_cmd = cmd_prefix + test_configs["test"]["commands"]["status"]

    activation_cmd = cmd_prefix + test_configs["test"]["commands"]["activation"]
    deactivation_cmd = cmd_prefix + test_configs["test"]["commands"]["deactivation"]

    # Run the test
    run_test(activation_cmd, deactivation_cmd, status_cmd, test_configs)

    logger.info("\n############ TEST ENDS #############\n\n")
    logger.info(''.join(['-' * 30, '\n']))


def run_test(activation_cmd, deactivation_cmd, status_cmd, test_configs, retries_on_test_phase_failure=10):
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
    test_configs : dict
        The user settings to be applied to the test
    retries_on_test_phase_failure: int
        The number of retries the same command if it fails the first time.

    Raises SystemError, RuntimeError
    """
    # If the user indicates the test duration to be -1, the test will keep running until it encounters an unrecoverable
    # failure. Otherwise, the test will stop after reaching the user's limit (number of test cycles to run)
    test_duration = int(test_configs["test"]["cycles_to_run"])
    if test_duration == -1:
        logger.info("Looping the test indefinitely. Press <Ctrl-C> to terminate.")
    else:
        logger.info("Looping the test {0} times. Press <Ctrl-C> to terminate.".format(test_duration))

    # Make sure the board is active before starting the test
    board_ip_address = test_configs["hardware"]["fpga_board_ip_address"]
    is_board_active = _detect_board_active(board_ip_address, expected_board_is_active=True)
    if not is_board_active:
        logger.error("Cannot start the test. The board has to be activated first.")
        raise SystemError

    run_count = 0
    board_activation_toggle_sleep_secs = int(test_configs["test"]["board_activation_toggle_sleep_secs"])
    sleep_after_stress_cmds_secs = int(test_configs["test"]["sleep_after_stress_cmds_secs"])

    while True:
        run_count += 1
        if test_duration != -1 and run_count > test_duration:
            break
        logger.info("\n=== Starting Test Iteration: {0} ===\n".format(run_count))
        retry_count = 0
        # Running board deactivation test
        while retry_count <= retries_on_test_phase_failure:
            logger.info("\n--- BOARD DEACTIVATION ---")
            _run_cmd(deactivation_cmd, board_activation_toggle_sleep_secs)
            if not _detect_board_active(board_ip_address, expected_board_is_active=False):
                if retry_count < retries_on_test_phase_failure:
                    retry_count += 1
                    logger.info("Retrying board deactivation. Attempt {0} out of {1}"
                                .format(retry_count, retries_on_test_phase_failure))
                else:
                    logger.error("The board CANNOT be DEACTIVATED. Ending the test.")
                    raise RuntimeError
            else:
                retry_count = 0
                break

        # Running board activation test
        while retry_count < retries_on_test_phase_failure:
            logger.info("\n--- BOARD ACTIVATION ---")
            _run_cmd(activation_cmd, board_activation_toggle_sleep_secs)
            if not _detect_board_active(board_ip_address, expected_board_is_active=True):
                if retry_count < retries_on_test_phase_failure:
                    retry_count += 1
                    logger.info("Retrying board activation. Attempt {0} out of {1}"
                                .format(retry_count, retries_on_test_phase_failure))
                else:
                    logger.error("The board CANNOT be ACTIVATED. Ending the test.")
                    raise RuntimeError
            else:
                run_pyrogue_stress_cmds = test_configs["test"]["mode"]["run_pyrogue_stress_cmds"]
                run_cpsw_stress_cmds = test_configs["test"]["mode"]["run_cpsw_stress_cmds"]

                if run_pyrogue_stress_cmds:
                    value_quantity_to_write_to_fpga = int(
                        test_configs["test"]["pyrogue"]["value_quantity_to_write_to_fpga"])
                    ddr_read_cycles = int(test_configs["test"]["pyrogue"]["ddr_read_cycles"])

                    run_pyrogue_stress_activities(board_ip_address, write_value_count=value_quantity_to_write_to_fpga,
                                                  ddr_read_cycles=ddr_read_cycles,
                                                  sleep_secs=sleep_after_stress_cmds_secs)
                if run_cpsw_stress_cmds:
                    yaml_filename = test_configs["test"]["cpsw"]["yaml_filename"]
                    value_quantity_to_write_to_fpga = int(
                        test_configs["test"]["cpsw"]["value_quantity_to_write_to_fpga"])

                    run_cpsw_stress_activities(yaml_filename, value_quantity_to_write_to_fpga,
                                               sleep_secs=sleep_after_stress_cmds_secs)

                logger.info("\n\n=== Ending Test Iteration: {0} ===".format(run_count))
                break


def _run_cmd(cmd, sleep_secs=30, log_level_debug=False):
    """
    Run a test command, and then sleep for a few seconds.

    Parameters
    ----------
    cmd : str
        The test command to run
    sleep_secs : int
        The number of seconds to sleep after the command run is finished.
    log_level_debug : bool
        True if to force the log level to DEBUG; False if to keep the current log level
    """
    logger.info("## Running IPMI comand: ##")
    logger.info(cmd)

    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    return_code = proc.returncode

    logger.info("Return Code: {0}\n".format(return_code))

    if log_level_debug:
        logger.setLevel(logging.DEBUG)

    stdout_data = stdout.decode()
    if len(stdout_data):
        logger.debug("### stdout ###")
        logger.debug("{0}".format(stdout_data))

    stderr_data = stderr.decode()
    if len(stderr_data):
        logger.debug("### stderr ###")
        logger.debug("{0}".format(stderr.decode()))

    _count_down_sleep_status(sleep_secs)


def _detect_board_active(board_ip_address, expected_board_is_active, ping_count=5):
    """
    Detect if the board is active or not, and compare the board's activeness with the expectation. The detection is
    accomplished by pinging the board's IP address. If the ping command's return code is 0, the board is determined
    to be active. Otherwise, the board is determined to be inactive.

    Parameters
    ----------
    board_ip_address : str
        The IP address of the board
    expected_board_is_active : bool
        True if the board is expected to be active; False if not
    ping_count : int
        The number of pings to send
    """
    if expected_board_is_active:
        logger.info("\n\n--- Detecting if the board is active ---")
    else:
        logger.info("\n\n--- Detecting if the board is inactive ---")

    proc = Popen("ping " + board_ip_address + " -c " + str(ping_count), shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    return_code = proc.returncode

    status_data = stdout.decode()
    error_data = stderr.decode()

    if expected_board_is_active:
        if return_code != 0:
            logger.debug("The board is expected to be ACTIVE, but it does not respond to {0} pings.\n"
                         "stdout: {1}\n\nstderr: {2}\n".format(ping_count, status_data, error_data))
            return False
        else:
            logger.info("The board is ACTIVE, as expected.")
    elif not expected_board_is_active:
        if return_code == 0:
            logger.debug("The board is expected to be INACTIVE, but it still responds after {0} pings.\n"
                         "stdout: {1}\n\nstderr: {2}\n".format(ping_count, status_data, error_data))
            return False
        else:
            logger.info("The board is INACTIVE, as expected.")

    logger.debug("Board activeness detection is finished.\n")
    return True


class StreamToLogger:
    """
    Source: http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def run_pyrogue_stress_activities(board_ip_address, write_value_count=20000, ddr_read_cycles=100, sleep_secs=600):
    """
    Use pyrogue to stress the board by writing values to the FPGA and reading from DDR.

    Parameters
    ----------
    board_ip_address : str
        The IP address used to connect to the FPGA board
    write_value_count : int
        The number of values to write, default at 20,000
    ddr_read_cycles : int
        The number of times to perform a DDR read
    sleep_secs : int
        The amount of time to sleep after the value writes.
    """
    # Set base
    with pr.Root(name='AMCc', description='') as base:
        # Add Base Device
        base.add(FpgaTopLevel(
            commType='eth-rssi-interleaved',
            ipAddr=board_ip_address,
            pcieRssiLink=4
        ))

        # Start the system
        logger.info("Start base")
        base.start(
            pollEn=1,
        )

        logger.info("\n## BOARD SUMMARY ##\n")

        # Capture the AxiVersion Summary to log
        stdout_handler = sys.stdout
        stderr_handler = sys.stderr

        global_logger = logging.getLogger()
        org_global_logging_level = global_logger.level

        # Temporary bump up the global logging level to get the Summary printout
        global_logger.setLevel(logging.INFO)
        sys.stdout = StreamToLogger(global_logger, logging.INFO)
        sys.stderr = StreamToLogger(global_logger, logging.ERROR)

        base.FpgaTopLevel.AmcCarrierCore.AxiVersion.printStatus()

        # Revert to the current log level and restore stdout and stderr handlers
        global_logger.setLevel(org_global_logging_level)
        sys.stdout = stdout_handler
        sys.stderr = stderr_handler

        logger.info("-- pyrogue: Start writing to and reading values from the board --")

        for i in range(write_value_count):
            logger.debug("-- pyrogue: Writing value: {0} to board".format(i))
            base.FpgaTopLevel.AmcCarrierCore.AxiVersion.ScratchPad.set(i, write=True)

            value = base.FpgaTopLevel.AmcCarrierCore.AxiVersion.ScratchPad.get()
            logger.info("-- pyrogue: Reading value: {0} from board".format(value))

            time.sleep(0.01)

        for i in range(ddr_read_cycles):
            logger.info("-- pyrogue: DDR read cycle {0}".format(i))
            base.FpgaTopLevel.DDR._rawRead(offset=0x0, numWords=0x100000)

            time.sleep(0.01)

        # Close
        logger.debug("Stopping base")
        base.stop()

        logger.debug("Stopping stream")
        base.FpgaTopLevel.stream.stop()
        logger.debug("Stopping finished.")

    logger.info("-- pyrogue: End writing to and reading values from the board --")
    _count_down_sleep_status(sleep_secs)


def run_cpsw_stress_activities(yaml_filename, write_value_count=20000, sleep_secs=600):
    """
    Use CPSW to stress the board by writing values to and then reading these from the FPGA

    Parameters
    ----------
    yaml_filename : str
        The CPSW YAML file containing the read/write specifications
    write_value_count : int
        The number of values to write, default at 20,000
    sleep_secs : int
        The amount of time to sleep after the value writes.
    """
    top_dev = "NetIODev"
    root = Path.loadYamlFile("cpsw_yaml/" + str(yaml_filename), top_dev)

    scratch_pad = ScalVal.create(root.findByName("mmio/AmcCarrierCore/AxiVersion/ScratchPad"))

    logger.info("-- CPSW: Start writing to and reading values from the board... --")
    for i in range(write_value_count):
        logger.debug("-- CPSW: Writing value: {0} to board".format(i))
        scratch_pad.setVal(i)

        value = scratch_pad.getVal()
        logger.info("-- CPSW: Reading value: {0} from board".format(value))

        time.sleep(0.01)

    logger.info("-- CPSW: End writing to and reading values from the board --")
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
        logger.error("\nUnexpected exception while running the test. Exception type: {0}. Exception: {1}"
                     .format(type(error), error))
        for h in logger.handlers:
            h.flush()

        # Run the status command to get diagnostic data
        _run_cmd(status_cmd, 10, log_level_debug=True)
        logger.info("Ending the test...")

