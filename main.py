import argparse
from StegoLogic import stegoread, stegowriter

# select read mode or write mode
parser = argparse.ArgumentParser(description="Does some steganography.")
parser.add_argument('mode', type=str, help="Select read or write mode.", choices=['r', 'w'])

args = parser.parse_args()

# modify these for different results
variables = {"hz": 7000,
             "amplitude": -50,
             "offset": 13,
             "hop_length": 64,
             "n_fft": 2048
             }

if args.mode == 'w':
    #cover = input("Path to cover file: ")
    cover = "ExampleData\\jazz.wav"
    message = "ExampleData\\message.txt"
    #message = input("Path to message file: ")
    stegowriter.run(cover=cover, message=message, **variables)
else:
    stegoread.run(**variables)
