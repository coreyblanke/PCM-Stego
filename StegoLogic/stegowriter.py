import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
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
    message_binary = open(message, mode="rb")
    cover_stft = librosa.stft(cover_audio, hop_length=kwargs["hop_length"])
    cover_modded = librosa.istft(cover_stft, hop_length=kwargs["hop_length"])
    # _plot_power(cover_stft)
    # print(cover_stft[:][0])
    soundfile.write(output, cover_modded, cover_sr)
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
    for freq_bins in stft.T:
        valid_in_bin = []
        for i in range(start_idx, stft.shape[0]):
            if librosa.amplitude_to_db(freq_bins[i]) >= kwargs["amplitude"]:
                valid_in_bin.append(i)
        valid.append(valid_in_bin)
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
