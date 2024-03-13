import paramiko

import argparse

import subprocess


def run_tx_USRP_script(file_path_tx: str, channels: list) -> None:
    channels_str = ' '.join(str(channel) for channel in channels)
    command = ["python3", "tx_USRP.py", file_path_tx, "--channels", channels_str]
    try:
        subprocess.run(command[0], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


def parse_args() -> argparse.Namespace:
    # Tx Arguments
    parser = argparse.ArgumentParser(description='Options for running the program')
    parser.add_argument('--file_path_tx', type=str, nargs=1, help='Name of the .dat file containing samples')
    parser.add_argument('--channels', type=int, nargs='+', help='Receive channels')

    # CPP Arguments
    parser.add_argument('-file', action='store', dest='file', type=str, nargs=1,
                        help='Read the samples from the file S')
    parser.add_argument('-fscanfile', action='store', dest='fscanfile', type=str, nargs=1,
                        help='Configure CaribouLite to scan frequencies as defined in a specified text file [KHz]')
    parser.add_argument('-nslots', action='store', dest='nslots', type=int, nargs='?',
                        help='Read nslots slots when processing')
    parser.add_argument('-syscode', action='store', dest='syscode', type=str, nargs='?',
                        help='SYSCODES TO BE REVISED')
    parser.add_argument('-basesmp', action='store', dest='basesmp', type=int, nargs='?',
                        help='Base sample to read from (in file mode)')
    parser.add_argument('-v', action='store', dest='verbose', type=str, choices=['none', 'trace', 'debug', 'deep'],
                        nargs='?',
                        help='Verbose level, can be none, trace, debug, deep (lowercase please)')
    parser.add_argument('-rxgain', action='store', dest='rxgain', type=float, nargs='?',
                        help='Set radio gain')
    parser.add_argument('-radioiters', action='store', dest='radioiters', type=int, nargs='?',
                        help='Set number of radio iterations')
    parser.add_argument('-occdetthresh', action='store', dest='occdetthresh', type=float, nargs='?',
                        help='Threshold for correlation detection snr')
    parser.add_argument('-lgtdetthresh', action='store', dest='lgtdetthresh', type=float, nargs='?',
                        help='Threshold for correlation detection snr')
    parser.add_argument('-pwrmeter', action='store_true', dest='pwrmeter',
                        help='Calculate the average sample power')
    parser.add_argument('-interpmode', action='store', dest='interpmode', type=int, choices=[5, 7, 17], nargs='?',
                        help='5 or 7 or 17 (different complexities), default 7')
    parser.add_argument('-corrplotena', action='store_true', dest='corrplotena',
                        help='Enable correlation plot')
    parser.add_argument('-saveflags', action='store', dest='saveflags', type=int, nargs='?',
                        help='Bitfield for saving flags')
    parser.add_argument('-detmode', action='store', dest='detmode', type=str, nargs='?',
                        help='Detector mode string')
    parser.add_argument('-clipth', action='store', dest='clipth', type=float, nargs='?',
                        help='Clipping threshold, 0 for no clipping')
    parser.add_argument('-smpdumpsize', action='store', dest='smpdumpsize', type=int, nargs='?',
                        help='How many samples to dump after flushing the buffer')
    parser.add_argument('-gryfforcerec', action='store_true', dest='gryfforcerec',
                        help='Force recording of gryfon data (all the data), used for checking the signal')
    parser.add_argument('-gryfpacketusec', action='store', dest='gryfpacketusec', type=int, nargs='?',
                        help='Assumed gryfon packet size, used to terminate the recording beyond some duration')
    parser.add_argument('-gryfdwellusec', action='store', dest='gryfdwellusec', type=int, nargs='?',
                        help='Gryfon dwell on frequency time')
    parser.add_argument('-gryfdeletefiles', action='store', dest='gryfdeletefiles', type=int, choices=[0, 1], nargs='?',
                        help='Gryfon delete files after each radio iteration, 0/1')
    parser.add_argument('-smpdumptofile', action='store', dest='smpdumptofile', type=int, nargs='?',
                        help='Dump samples to file, specify number of samples')
    parser.add_argument('-detdumptofile', action='store', dest='detdumptofile', type=str, nargs='?',
                        help='Dump detection scores to file')

    args = parser.parse_args()
    return args


def run_cpp_file_via_ssh(hostname: str, username: str, password: str, arguments: argparse.Namespace) -> None:
    # Create an SSH client instance
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the server
        ssh.connect(hostname=hostname, username=username, password=password)

        parts = arguments.file_path_tx[0].split("_")

        frequency = float(parts[2].rstrip("Mhz")) * 1e3

        if hasattr(arguments, 'file_path_tx'):
            delattr(arguments, 'file_path_tx')

        command = f"echo '{frequency} 15 56000' > /home/pi/cariboulite/applications/scanner1/myscan.txt "
        print(command)
        args_dict = vars(arguments)
        filtered_args = {k: v for k, v in args_dict.items() if v is not None}

        # Define the command string
        # Iterate through the filtered arguments and add them to the command string
        for key, value in filtered_args.items():
            command += f' -{key}'
            if value is not True:  # For boolean flags, only add the flag itself without a value
                command += f' {value}'
        print(command)

        _stdin, _stdout, _stderr = ssh.exec_command(command)

        # command = "/home/pi/cariboulite/applications/scanner1/build/scanner1 -nslots 10 -fscanfile /home/pi/cariboulite/applications/scanner1/myscan.txt -v trace"

        print(_stdout.read().decode())
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials")
    except paramiko.SSHException as ssh_ex:
        print(f"SSH connection failed: {ssh_ex}")
    finally:
        # Close the SSH connection
        ssh.close()
        print("session closed")


def main():
    # Example usage
    hostname = 'raspberrypi02.local'
    username = 'pi'
    password = '1234'

    parsed_args = parse_args()

    # Arguments to pass to the Python file
    # run_tx_USRP_script(parsed_args.file_path_tx, parsed_args.channels)
    # Arguments to pass to the C++ file
    if hasattr(parsed_args, 'channels'):
        delattr(parsed_args, 'channels')

    run_cpp_file_via_ssh(hostname=hostname, username=username, password=password, arguments=parsed_args)


if __name__ == '__main__':
    main()



################## ask Nadav about false params and we can i get 15 and 56000