import argparse
import numpy as np
import uhd
from typing import Tuple
from rx_USRP import clear_buffer


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Extract specifications from file name and read samples.')
    parser.add_argument('file_name', type=str, help='Name of the .dat file containing samples')
    parser.add_argument('--channels', type=int, nargs='+', help='Receive channels')

    args = parser.parse_args()

    if args.channels is None:
        channels_str = input("Enter the receive channels separated by commas: ")
        args.channels = [int(ch) for ch in channels_str.split(',')]
    if args.file_name is None:
        args.file_name = int(input("Enter the file name: "))

    return args


def extract_specs_from_filename(file_name: str) -> Tuple[float, float, float]:
    try:
        parts = file_name.split("_")
        frequency = float(parts[2].rstrip("Mhz")) * 1e6
        sample_rate = float(parts[1].rstrip("Mhz")) * 1e6
        gain = float(parts[3].rstrip("dB"))
        return frequency, sample_rate, gain
    except (IndexError, ValueError):
        raise ValueError("Invalid file name format")


def main() -> None:
    """Main function to transmitting samples using USRP."""

    try:
        parsed_args = parse_arguments()
        frequency, sample_rate, gain = extract_specs_from_filename(parsed_args.file_name)

        with open(parsed_args.file_name, 'rb') as file:
            samples_bytes = file.read()

        # Convert the bytes back to numpy array
        samples = np.frombuffer(samples_bytes, dtype=np.complex64)

        # Initialize the USRP
        usrp = uhd.usrp.MultiUSRP("type=b200")
        clear_buffer(usrp)

        # Transmit the waveform
        duration = len(samples) / sample_rate  # Duration based on the number of samples and sample rate
        usrp.send_waveform(samples, duration, frequency, sample_rate, parsed_args.channels, gain)

    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
