## Testing Overview
The test runs a single Python script, which performs the following operations:

    1. Detect if the board is active
    2. Deactivate the board
    3. Pause 30 seconds
    4. Confirm the board is deactivated
    5. Activate the board
    6. Pause 30 seconds
    7. Confirm the board is activated
    8. Run pyrogue or Python CPSW commands to create network traffic over the switch and also stressing the FPGA board
    9. ause 10 seconds
    10. Repeat Steps 1 - 9, depending on the user's test looping setting

## Specific Steps
The test performs the following steps in a loop:

1. Detect if the FPGA board is active, by pinging the board 5 times
   - If the board is not active, terminate the test and require the user to activate the board
2. If the board is active, deactivate the board  by running the IPMI command 

   <code>ipmitool -I lan -H <shelf_manager_hostname> -t <fpga_board_target_number> -b 0 -A NONE picmg deactivate 0</code>
 
   then sleep for 30 seconds. The Shelf Manager hostname, the FPGA IP address, and the sleep time are user-customizable by modifying the configs.json file, which is part of the test structure.

3. Detect if the board is inactive
   - If the board is still active, retry the deactivation command, and then try to detect if the board is inactive, again
   - If after 10 trials and the board is still active, run the IPMI command 

        <code>ipmitool -I lan -H <shelf_manager_hostname> -t <fpga_board_target_number> -b 0 -A NONE sensor get "Hot Swap"</code>
    
     to get a snapshot of the current FPGA status, then terminate the test.

 4. If the board is inactive, activate the board  by running the IPMI command 

        <code>ipmitool -I lan -H <shelf_manager_hostname> -t <fpga_board_target_number> -b 0 -A NONE picmg policy set 0 1 0</code>

    then sleep for 30 seconds (customizable)
   
    - If the board is still inactive, retry the activation command, and then try to detect if the board is active, again
    - If after 10 trials and the board is still inactive, run the IPMI command 

         <code>ipmitool -I lan -H <shelf_manager_hostname> -t <fpga_board_target_number> -b 0 -A NONE sensor get "Hot Swap" </code>
      to get a snapshot of the current FPGA status, then terminate the test.

5. Run a series of pyrogue I/O activities to stress the board
   - Write and read back 20000 values (customizable) to the FPGA board, from 0 to 19999
   - Read 0x100000 bytes from DDR, and repeat the read for 100 times (customizable)
6. Repeat Steps 1 - 5 until one of the followings happens:
   - The user presses <Ctrl-C> on the keyboard to terminate the test
   - The test detects a switch failure, or encounters an execution problem
   - The test has been looped a certain number of times, customizable by the user. If the user sets the loop number to -1, the test will repeat indefinitely, unless either the two previous conditions happens.

The test activities are logged into rotating log files. Each file can contain up to 2 MB of log data, and maximum 30 files are kept. If 2 MB * 30 = 60 MB is exceeded, The test activities are logged into rotating log files. Each file can contain up to 2 MB of log data, and maximum 60 files are kept. If 2 MB * 60 = 120 MB is exceeded, the oldest log file (xxxx.log.1) will be discarded, and will be replaced with the most recent log events. 

## Setting up the Test
1. Clone the switchtest GitHub depot, and source the evironment:
   <code>
   git clone https://github.com/hmbui/switchtest
   </code>
   For pyrogue stress activity commands:
   <code>
   source pyrogue_setup.sh
   </code>
   For CPSW stress activity commands:
   <code>
   source cpsw_setup.sh
   </code>
2. Customize the test by editing the file configs/configs.json:
* shelf_manager: The hostname of the Shelf Manager that can be used for a network connection
* slot: The slot number on the create where the FPGA board resides
* fpga_board_ip_address:	The IP address of the FPGA board	An IP address string, e.g. "10.0.1.102".
* custom_log_directory_path: The directory to save the logs. This is to let the test save logs into a non-network storage, whose access could be unavailable periodically, such as AFS access requires kinit
* run_pyrogue_stress_cmds: Set to true if the test is to run the commands to generate read/write activities to stress the FPGA board, using pyrogue. Set to false to disable this testing portion
* run_cpsw_stress_cmds: Set to true if the test is to run the commands to generate read/write activities to stress the FPGA board, using CPSW. Set to false to disable this testing portion	
* cycles_to_run: How many times to loop the test over (refer to the Specific Steps section). Set to -1 to loop the test indefinitely.	An valid positive integer, or -1 to loop the test indefinitely
* board_activation_toggle_sleep_secs: The number of seconds to sleep after each board activation/deactivation command. This is to allow the board time to transition through its internal stages
* sleep_after_stress_cmds_secs: The number of seconds to sleep after the read/write stress activities.
* value_quantity_to_write_to_fpga: The number of values to write and then read from the FPGA board. The more the value, the more cycles are placed on the board, potentially stressing it. This parameter is required for both stress commands using pyrogue and CPSW.
* ddr_read_cycles: The number of time to read raw bytes (0x100000 bytes) from DDR. The more the value, the stress is to be placed on the board. This parameter is required for just pyrogue stress commands.
* yaml_filename: The filename containing the CPSW YAML definition to connect to the FPGA board. This parameter is required for just CPSW stress commands.
* status: The IPMI command portion to obtain the FPGA board's state transition status. This can be modified if the board model requires a different IPMI sensor get property, e.g. a sensor get property that is different than "Hot Swap"
* activation: The IPMI command portion to activate an FPGA. This can be modified if the board model requires a different IPMI activation command, e.g. "picmg activate 0"
* deactivation	The IPMI command portion to activate an FPGA. This can be modified if the board model requires a different IPMI activation command, e.g. "picmg policyset 0 0 1".

## Running the Test
Testing with pyrogue:

<code>
source pyrogue_setup.sh
python3 main.py <config_file_path> [--verbose-loggging]
</code>

Examples
<code>
source pyrogue_setup.sh
python3 main.py configs/configs.json
</code>
or
<code>
source pyrogue_setup.sh
python3 main.py configs/configs.json --verbose-logging
</code>

Testing with CPSW
<code>
source cpsw_setup.sh
python main.py <config_file_path> [--verbose-loggging]
</code>
   
Examples
<code>
source cpsw_setup.sh
python main.py configs/configs.json
</code>
   
or
<code>
source cpsw_setup.sh
python main.py configs/configs.json --verbose-logging
</code>

### Note
* The env script for running the test with pyrogue is pyrogue_setup.sh, and with CPSW is cpsw_setup.sh
* While pyrogue can be run with Python 3, CPSW can only be run with Python 2.7.

### Command Line Parameters
* Without the --verbose-logging parameter, the test will not log the INFO and DEBUG statements from pyrogue, and will only log any pyrogue WARNING and ERROR statements together with the test's INFO, WARNING, and ERROR statements.
* With the --verbose-logging parameter, the test will log all the INFO and DEBUG statements from pyrogue, and will also log the test's DEBUG, INFO, WARNING, and ERROR statements.

## Command Line Parameters
* Without the <code>--verbose-logging</code> parameter, the test will not log the INFO and DEBUG statements from pyrogue, and will only log any pyrogue WARNING and ERROR statements together with the test's INFO, WARNING, and ERROR statements.
* With the <code>--verbose-logging parameter</code>, the test will not all the INFO and DEBUG statements from pyrogue, and will also log the test's DEBUG, INFO, WARNING, and ERROR statements.
