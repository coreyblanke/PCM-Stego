import time
import librosa
import librosa.display
import numpy as np
from bitstring import BitArray, BitStream
from tqdm import tqdm


def run(stegaudio, **kwargs):
    my_args = {"hop_length": kwargs["hop_length"],
               "win_length": kwargs["win_length"],
               "center": kwargs["center"]
               }
    s_audio, s_sr = librosa.load(stegaudio, sr=None)
    s_stft = librosa.stft(s_audio, n_fft=kwargs["n_fft"], **my_args)
    s_mag, s_phase = librosa.magphase(s_stft)
    data_chunk = _get_valid_bins(s_mag, s_sr, **kwargs)
    _get_payload(s_mag, data_chunk, **kwargs)
    cover_audio, cover_sr = librosa.load("ExampleData\\jazz.wav", sr=None)
    cover_stft = librosa.stft(cover_audio, n_fft=kwargs["n_fft"], **my_args)
    m, p = librosa.magphase(cover_stft)
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
    for freq_bins in tqdm(stft.T[: int(stft.shape[1] * kwargs['x_ratio'])], "Finding data chunk"):  # go thru each
        # frequency bin and find the
        # idxs of all the ones that are < amplitude
        valid_in_bin = []
        for i in range(start_idx, stft.shape[0]):
            if (20 * np.log10(freq_bins[i])) >= kwargs["amplitude"]:
                valid_in_bin.append(i)
        valid.append(valid_in_bin)

    return valid


def _get_payload(mag, data_chunk, **kwargs):
    """
    :param mag: magnitude of stft
    :param data_chunk: list of indices to scan for data
    :param kwargs: contains setting info
    :return: bitstring of payload
    """
    payload_size = "0b"
    i = 0
    j = 0
    for _ in range(kwargs["offset"]):
        row = data_chunk[i][j]
        col = i
        db = librosa.amplitude_to_db([mag[row][col]])[0]
        if db > kwargs["reader_thresh"]:
            payload_size += str(int(np.floor(db) % 2))
        else:
            payload_size += "0"
        i, j = _find_next_idx(i, j, data_chunk)
    payload = "0b"
    payload_size = BitArray(payload_size).int
    time.sleep(10e-3)
    for _ in tqdm(range(payload_size), "Extracting payload"):
        row = data_chunk[i][j]
        col = i
        db = librosa.amplitude_to_db([mag[row][col]])[0]
        if db > kwargs["reader_thresh"]:
            payload += str(int(np.floor(db) % 2))
        else:
            payload += "0"
        i, j = _find_next_idx(i, j, data_chunk)
    return BitStream(payload)


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


def _write_payload(b_stream: BitStream, name="payload.txt"):
    buff = bytearray()
    v = int(b_stream.bin, 2)
    while v:
        buff.append(v & 0xff)
        v >>= 8
    with open(name, "wb+") as f:
        f.write(bytes(buff[::-1]))
        f.close()
    print(f"Payload \"{name}\" written successfully.")
    return
