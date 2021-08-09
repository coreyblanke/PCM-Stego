import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
from bitstring import Bits
import soundfile
from tqdm import tqdm


def run(cover="", message="", output="output.wav", **kwargs):
    """
    :param output: name of output file
    :param cover: path to cover audio
    :param message: path to payload
    :param kwargs: kwargs dict, look at main
    :return:
    """
    print(f"Attempting to write {message} into {cover}...")
    my_args = {"hop_length": kwargs["hop_length"],
               "win_length": kwargs["win_length"],
               "center": kwargs["center"]
               }
    cover_audio, cover_sr = librosa.load(cover, sr=None)
    cover_stft = librosa.stft(cover_audio, n_fft=kwargs["n_fft"], **my_args)
    m, p = librosa.magphase(cover_stft)
    cover_idxes = _get_valid_bins(stft=m, sr=cover_sr, **kwargs)
    newstft = _write_to_stft(stft=m, cover_indices=cover_idxes, message=message, **kwargs)
    newstft = newstft * p
    stegaudio = librosa.istft(newstft, **my_args)
    soundfile.write(output, stegaudio, cover_sr)
    print(f"{output} successfully generated.")
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
    for freq_bins in tqdm(stft.T[: int(stft.shape[1] * kwargs['x_ratio'])], "Calculating capacity"):  # go thru each
        # frequency bin and find the
        # idxs of all the ones that are < amplitude
        valid_in_bin = []
        for i in range(start_idx, stft.shape[0]):
            if 20*np.log10(freq_bins[i]) >= kwargs["amplitude"]:
                valid_in_bin.append(i)
        valid.append(valid_in_bin)

    return valid


def _plot_power(stft):
    """
    :param stft: stft matrix to plot
    :return:
    """
    fig, ax = plt.subplots()
    img = librosa.display.specshow(librosa.amplitude_to_db(abs(stft),
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
    flipped = 0
    if capacity < (message_size + kwargs["offset"]):
        raise ValueError(f"Message of size {message_size + kwargs['offset']} bits exceeds capacity {capacity} bits"
                         f" for current settings, "
                         f"try messing with them " +
                         "or changing cover file")
    # for each bit in size_bits, write to next valid bit
    i = 0
    j = 0
    # mag, phase = librosa.magphase(stft)
    mag = stft
    for b in tqdm(size_bits.bin, "Writing size"):
        row = cover_indices[i][j]
        col = i
        db = librosa.amplitude_to_db([mag[row][col]])[0]
        op = np.floor(db) % 2
        if b == "1" and int(op) == 0:
            flipped += 1
            mag[row][col] = librosa.db_to_amplitude(db + 10)
        elif b == "0" and int(op) == 1:
            flipped += 1
            mag[row][col] = librosa.db_to_amplitude(db + 10)
        i, j = _find_next_idx(i, j, cover_indices)

    for b in tqdm(message_bits.bin, "Writing message"):
        row = cover_indices[i][j]
        col = i
        db = librosa.amplitude_to_db([mag[row][col]])[0]
        op = np.floor(db) % 2
        if b == "1" and int(op) == 0:
            flipped += 1
            mag[row][col] = librosa.db_to_amplitude(db + 10)
        elif b == "0" and int(op) == 1:
            flipped += 1
            mag[row][col] = librosa.db_to_amplitude(db + 10)
        i, j = _find_next_idx(i, j, cover_indices)
    # stft = mag * phase
    print(f"{flipped} amplitude modifications to encode {(message_size+kwargs['offset']) // 8} bytes of information.")
    print(f"Capacity with current settings is {capacity}")
    return stft


def _find_next_idx(i, j, cover_indices):
    # iterate, skipping over invalid values
    i += 1
    if i >= len(cover_indices):
        i = 0
        j += 1
    while j >= len(cover_indices[i]):
        i += 1
        if i >= len(cover_indices):
            i = 0
            j += 1
    return i, j
