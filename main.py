import argparse
from StegoLogic import stegoread, stegowriter

# select read mode or write mode
parser = argparse.ArgumentParser(description="Does some steganography.")
parser.add_argument('mode', type=str, help="Select read or write mode.", choices=['r', 'w'])
# NOTE: WRITE MODE IS THE ONLY ONE WITH A SEMI FUNCTIONAL RESULT
# WRITE MODE DEMOS BOTH READ AND WRITE (see final report for details)
# TODO: mention the thing with write mode in final report
args = parser.parse_args()

# modify these for different results
# hop_length and n_fft should be powers of 2 for speed's sake
# hop_length massively increases overhead as you lower it
#   and really shouldn't be lower than 32 but you get more capacity
#   something something nyquist sampling theorem
# amplitude in db from -inf to 0, although realistically something like -80 will capture all usage
# hz in hz, threshold to start looking for valid frequency bins to modify, lower values may affect cover audio more
# offset, num bits to dedicate to telling size of message
# x_ratio, write only in the first x_ratio % of the image
# reader_thresh, tell the reader what counts as a written bit (ideally a little lower than writer)
variables = {"hz": 900,
             "amplitude": -12,
             "offset": 64,
             "hop_length": 64,
             "n_fft": 2048,
             "win_length": 2048,
             "center": True,
             "x_ratio": .95,
             "reader_thresh": -12
             }

if args.mode == 'w':
    #cover = input("Path to cover file: ")
    cover = "ExampleData\\jazz.wav"
    message = "ExampleData\\1.txt"
    #message = input("Path to message file: ")
    stegowriter.run(cover=cover, message=message, **variables)
else:
    stegaudio = "output.wav"
    stegoread.run(stegaudio, **variables)
