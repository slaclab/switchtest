import sys
import os
from subprocess import Popen, PIPE
import json
import time

from arg_parser import ArgParser

from switch_test_logging import logging
logger = logging.getLogger(__name__)

from version import VERSION

INTERFACE = "ipmi_tool"
INTERFACE_TYPE = "lan"

SLOT_NUMBER = 0x2
target = 0x80 + 2 * SLOT_NUMBER

SHELF_MANAGER = "shm-b084-sp02"


def main():
    logger.info("############ TEST STARTS #############\n")

    # Parsing command arguments
    args = _parse_arguments()

    config_file = vars(args)["config-file"]
    test_configs = _parse_config_file(config_file)

    verbose_logging = vars(args)["verbose_logging"]
    if not verbose_logging:
        logger.setLevel(logging.INFO)

    shelf_manager = test_configs["hardware"]["shelf_manager"]

    slot_number = test_configs["hardware"]["slot"]
    target = str(hex(int(0x80) + 2 * slot_number))

    ipmi_cmd = test_configs["test"]["ipmi_command"]
    cmd = 'ipmitool -I lan -H ' + shelf_manager + ' -t ' + str(target) + ' -b 0 -A NONE ' + ipmi_cmd

    test_duration_minutes = int(test_configs["test"]["test_duration_minutes"])
    if test_duration_minutes == -1:
        logger.info("Looping test indefinitely. Press <Ctrl-C> to terminate.\n")
    else:
        logger.info("Looping test for {0} minutes. Press <Ctrl-C> to terminate.\n".format(test_duration_minutes))

    _run_cmd([cmd], test_duration_minutes)

    logger.info("\n\n############ TEST ENDS #############\n \n")
    logger.info(''.join(['-' * 30, '\n']))


def _run_cmd(cmds, test_duration_minutes):
    timeout = time.time() + test_duration_minutes * 60
    while True:
        if time.time() > timeout:
            break

        for cmd in cmds:
            logger.debug("\n\n----- Running IPMI comand: -----")
            logger.debug(cmd + "\n")

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

            for i in range(5, 0, -1):
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
    config_file = os.path.expandvars(os.path.expanduser(config_file))
    with open(config_file, encoding="utf-8") as f:
        test_configs = json.loads(f.read())
    return test_configs


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.error("Unexpected exception while sending the IPMI command. Exception type: {0}. Exception: {1}"
                     .format(type(error), error))



