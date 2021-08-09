# PCM-Stego
Hide data inside ANY audio file using steganography. Fundamentally, audio is represented as a PCM (Pulse Code Modulation) binary-stream before compression. This is our attempt at hijacking the audio-stream &amp; discreetly injecting data WITHOUT introducing new audible features. Project for steganography course.

# SETUP
Download the Kaggle Dataset (1000 songs): https://www.kaggle.com/andradaolteanu/gtzan-dataset-music-genre-classification; 

(Or you can use the provided example file, 1.txt is a randomly generated file 1mb in length and it defaults to running that); 

Install pipenv: https://pypi.org/project/pipenv/;

cd into directory containing main.py;

use the command "pipenv install && pipenv run python main.py w";

enjoy the demo;

feel free to play around with the variables dictionary in main.py and see what they do, how they affect capacity, noise levels in the output, etc;
