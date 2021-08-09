# PCM-Stego
Hide data inside ANY audio file using steganography. Fundamentally, audio is represented as a PCM (Pulse Code Modulation) binary-stream before compression. This is our attempt at hijacking the audio-stream &amp; discreetly injecting data WITHOUT introducing new audible features.

# SETUP
Download the Kaggle Dataset (1000 songs): https://www.kaggle.com/andradaolteanu/gtzan-dataset-music-genre-classification
(Or you can use the provided example file, 1.txt is a randomly generated file 1mb in length)
Install pipenv: https://pypi.org/project/pipenv/ 
cd into directory containing main.py
run >>pipenv install && pipenv run python main.py w
enjoy the demo
