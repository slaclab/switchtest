## Testing Overview
The test performs the following operations:

1. Detect if the board is active
2. Deactivate the board
3. Pause 30 seconds
4. Activate the board
5. Pause 30 seconds
6. Run pyrogue or Python CPSW commands to create network traffic over the switch and also stressing the FPGA board
7. Pause 10 minutes
8. Repeat Steps 1 - 7, depending on the user's test looping setting

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

The test activities are logged into rotating log files. Each file can contain up to 2 MB of log data, and maximum 30 files are kept. If 2 MB * 30 = 60 MB is exceeded, the latest log events will overwrite the oldest log file.

## Setting up the Test
1. Clone the switchtest GitHub depot, and source the evironment:
   <code>
   git clone https://github.com/hmbui/switchtest
   source setup.sh
   </code>
2. Customize the test by editing the file configs/configs.json:
* "shelf_manager": "xxxxxxxxxx" => The Shelf Manager network name or IP address
* "slot": 6 => The slot number of the FQDN board
* "fpga_board_ip_address": "10.0.2.106" => The IP address of the FPGA board
* "cycles_to_run": 1 => How many times to loop the test. Enter -1 for looping the test indefinitely
* "sleep_between_commands_secs": 30, => The sleep time, in seconds, after each board deactivation and activation command
* "sleep_after_fpga_writes_secs": 600, => The sleep time, in seconds, after the FPGA board writes before running the next command
* "value_quantity_to_write_to_fpga": 20000, => The number of values to write to the FPGA
* "ddr_read_cycles": 100, => The number of times to run a DDR read
* "status": "sensor get \"Hot Swap\"", => The IPMI command to get the current status of the FPGA board
* "activation": "picmg policy set 0 1 0", => The IPMI command portion to activate the FPGA board
* "deactivation": "picmg deactivate 0" => The IPMI command portion to deactivate the FPGA board 

## Running the Test
Syntax:
<code>
python3 main.py <config_file_path> [--verbose-loggging]
</code>

Examples:
<code>
python3 main.py configs/configs.json
</code>
or
<code>
python3 main.py configs/configs.json --verbose-logging
</code>

## Command Line Parameters
* Without the <code>--verbose-logging</code> parameter, the test will not log the INFO and DEBUG statements from pyrogue, and will only log any pyrogue WARNING and ERROR statements together with the test's INFO, WARNING, and ERROR statements.
* With the <code>--verbose-logging parameter</code>, the test will not all the INFO and DEBUG statements from pyrogue, and will also log the test's DEBUG, INFO, WARNING, and ERROR statements.
