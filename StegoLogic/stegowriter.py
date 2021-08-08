import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
from bitstring import Bits
import soundfile


def run(cover="", message="", output="output.wav", **kwargs):
    """
    :param output: name of output file
    :param cover: path to cover audio
    :param message: path to payload
    :param kwargs: kwargs dict, look at main
    :return:
    """
    cover_audio, cover_sr = librosa.load(cover, sr=None)
    cover_stft = librosa.stft(cover_audio, hop_length=kwargs["hop_length"])
    cover_idxes = _get_valid_bins(stft=cover_stft, sr=cover_sr, **kwargs)
    _write_to_stft(stft=cover_stft, cover_indices=cover_idxes, message=message, **kwargs)
    return


def _get_valid_bins(stft, sr, **kwargs):
    """
    grabs the starting index of the desired hz threshold
    :param stft: stft to grab from
    :param sr: sample rate of audio
    :param kwargs: n_fft, hz
    :return: list of all valid indexes for each bin in the stft
    """
    bins = librosa.fft_frequencies(sr=sr, n_fft=kwargs["n_fft"])
    start_idx = 0
    for freq in bins:
        if freq < kwargs["hz"]:
            start_idx += 1
        else:
            break
    else:
        raise ValueError("hz parameter must be lower than the maximum frequency bin of stft")
    valid = []
    for freq_bins in stft.T:  # go thru each frequency bin and find the idxs of all the ones that are < amplitude
        valid_in_bin = []
        for i in range(start_idx, stft.shape[0]):
            if (20 * np.log10(freq_bins[i])) >= kwargs["amplitude"]:
                valid_in_bin.append(i)
        valid.append(sorted(valid_in_bin, reverse=True))  # append reverse sorted so that most inaudible freqs are first
    return valid


def _plot_power(stft):
    """
    :param stft: stft matrix to plot
    :return:
    """
    fig, ax = plt.subplots()
    img = librosa.display.specshow(librosa.amplitude_to_db(stft,
                                                           ref=np.max),
                                   y_axis='log', x_axis='time', ax=ax)
    ax.set_title('Power spectrogram')
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    plt.show()


def _write_to_stft(stft, cover_indices, message, **kwargs):
    """
    :param stft: stft to modify
    :param message: message filename to read it into
    :return: modified stft
    """
    capacity = (sum([len(val) for val in cover_indices]))
    message_size = os.stat(message).st_size * 8

    # convert payload to bitstring
    message_file = open(message, mode="rb")
    message_bits = Bits(message_file)
    size_bits = Bits(int=message_size, length=kwargs["offset"])
    if capacity < (message_size + kwargs["offset"]):
        raise ValueError("Message exceeds capacity for current settings, try messing with them " +
                         "or changing cover file")

    return
