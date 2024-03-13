import uhd
import argparse
import matplotlib.pyplot as plt
import os


def clear_buffer(usrp, *args, **kwargs) -> None:
    """Clear the buffer in the USRP device."""
    usrp.clear_command_time()


def parse_arguments(*args, **kwargs) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description='USRP Parameters')
    parser.add_argument('--sample-time', type=float, help='Duration of sample')
    parser.add_argument('--frequency', type=float, help='Center frequency in Hz')
    parser.add_argument('--sampling-rate', type=float, help='Sampling rate in Hz')
    parser.add_argument('--channels', type=int, nargs='+', help='Receive channels')
    parser.add_argument('--gain', type=float, help='RX gain in dB')

    args = parser.parse_args()

    if args.sample_time is None:
        args.sample_time = int(input("Enter the sample duration: "))
    if args.frequency is None:
        args.frequency = float(input("Enter the center frequency in Hz: "))
    if args.sampling_rate is None:
        args.sampling_rate = float(input("Enter the sampling rate in Hz: "))
    if args.channels is None:
        channels_str = input("Enter the receive channels separated by commas: ")
        args.channels = [int(ch) for ch in channels_str.split(',')]
    if args.gain is None:
        args.gain = float(input("Enter the RX gain in dB: "))
    print(type(args))
    return args


def recv_to_file(args) -> None:
    """RX samples and write to file"""
    num_samples = int(args.sampling_rate * args.sample_time)

    # Create a USRP device object (B200 in this case)
    usrp = uhd.usrp.MultiUSRP("type=b200")
    clear_buffer(usrp)  # Clear buffer before parsing arguments

    # Receive samples
    samples = usrp.recv_num_samps(num_samples, args.frequency, args.sampling_rate, args.channels, args.gain)

    index = 1
    while True:
        file_name = f'samples_{args.sampling_rate / 1e6}Mhz_{args.frequency / 1e6}Mhz_{args.gain}dB_{index}.dat'
        if not os.path.exists(file_name):
            break
        index += 1
    try:

        with open(file_name, 'wb') as file:
            file.write(samples.tobytes())

    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    index = 1
    while True:
        png_name = f'spectrogram_{args.sampling_rate / 1e6}Mhz_{args.frequency / 1e6}Mhz_{args.gain}dB_{index}.png'
        if not os.path.exists(png_name):
            break
        index += 1

    plt.figure()
    plt.specgram(samples[0], Fc=args.frequency, Fs=args.sampling_rate, NFFT=1024, noverlap=512, scale_by_freq=False)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Spectrogram')
    plt.colorbar(label='Intensity (dB)')
    plt.savefig(png_name, format='png', dpi=900)
    plt.show()
    

def main() -> None:
    """Main function to receiving samples using USRP."""
    parsed_args = parse_arguments()
    recv_to_file(parsed_args)


if __name__ == '__main__':
    main()
