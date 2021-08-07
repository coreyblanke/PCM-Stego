import argparse
from StegoLogic import stegoread, stegowriter

# select read mode or write mode
parser = argparse.ArgumentParser(description="Does some steganography.")
parser.add_argument('mode', type=str, help="Select read or write mode.", choices=['r', 'w'])

args = parser.parse_args()


if args.mode == 'w':
    stegowriter.run()
else:
    stegoread.run()
