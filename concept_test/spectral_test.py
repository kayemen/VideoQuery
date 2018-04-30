import os
import code
import traceback

import numpy as np
from fastdtw import fastdtw
from scipy.signal import welch
from scipy.spatial.distance import euclidean
import wave
import matplotlib.pyplot as plt


def audio_spectral_profile(audio_frames, num_audio_frames):
    # num_audio_frames=len(audio_frames)/4
    # audio_concat = [None]*num_audio_frames*2
    # audio_mono = [None]*num_audio_frames
    # for i in range (0,len(audio_frames)-1,2):
    #     audio_concat[int(i/2)]=(audio_frames[i]*256)+(audio_frames[i+1])
    audio_concat = np.frombuffer(audio_frames, dtype=np.dtype('>u2'))
    # audio_concat = np.asarray(audio_concat)
    audio = (audio_concat[0::2] + audio_concat[1::2])/2
    Pxx = []

    q_audio = audio[200000:200000+44100*4]

    print('start')
    dist, pth = fastdtw(audio, q_audio, dist=euclidean)
    print('end')

    code.interact(local=locals())

    # for x in range(0, len(audio_mono)-44100, 1470):
    #     v1, v2 = welch(audio_mono[x:(44100+x)], fs=44100, nperseg=44100)

    #     v2[np.where(v1 < 20)] = 0
    #     v2[np.where(v1 > 20000)] = 0

    #     # fz.append(v1)
    #     Pxx.append(v2)
    return Pxx


if __name__ == '__main__':
    audio_path = os.path.join(os.path.dirname(__file__), 'StarCraft.wav')
    audiofp = wave.open(audio_path, 'rb')

    num_audio_frames = audiofp.getnframes()

    audio = audiofp.readframes(num_audio_frames)

    audiofp.close()

    audio_spectral_profile(audio, num_audio_frames)
