import os
import glob
import code
import time

import numpy as np
import matplotlib.pyplot as plt
import imagehash as imhash
from PIL import Image

import config
from Video import Video


def extract_features(vid_obj, feature_list=()):
    # all_ = False
    available_features = [
        'brightness_profile',
        # 'audio_spectrogram',
        'frame_perceptive_hash'
    ]
    if len(set(feature_list).intersection(set(available_features))) == 0:
        # all_ = True
        feature_list = tuple(available_features)
    else:
        feature_list = tuple(
            set(feature_list).intersection(set(available_features)))

    if 'brightness_profile' in feature_list:
        y, r, g, b = video_brightness_profile(
            vid_obj.frames)
        # plt.figure()
        # plt.plot(y, label='Y', c='k')
        # plt.plot(r, label='R', c='r')
        # plt.plot(g, label='G', c='g')
        # plt.plot(b, label='B', c='b')
        # plt.title('Brightness profile - %s' % (vid_obj.name))
        # plt.legend()
        vid_obj.features['brightness_profile_y'] = y
        vid_obj.features['brightness_profile_r'] = r
        vid_obj.features['brightness_profile_g'] = g
        vid_obj.features['brightness_profile_b'] = b

    if 'audio_spectrogram' in feature_list:
        pass

    if 'frame_perceptive_hash' in feature_list:
        ah, ph, wh, dh_h, dh_v = video_perceptive_hash(vid_obj.frames)
        vid_obj.features['perceptual_hash_ahash'] = ah
        vid_obj.features['perceptual_hash_phash'] = ph
        vid_obj.features['perceptual_hash_whash'] = wh
        vid_obj.features['perceptual_hash_dhhash'] = dh_h
        vid_obj.features['perceptual_hash_dvhash'] = dh_v

    # plt.show()


def video_brightness_profile(frames):
    def compute_frame_brightness(frame):
        if len(frame.shape) > 2:
            R = frame[:, :, 0]
            G = frame[:, :, 1]
            B = frame[:, :, 2]
            Y = 0.299 * R + 0.587 * G + 0.114 * B

            return np.mean(Y)
        else:
            return np.mean(frame)

    y_profile = np.zeros(len(frames))
    r_profile = np.zeros(len(frames))
    g_profile = np.zeros(len(frames))
    b_profile = np.zeros(len(frames))
    for i, frame in enumerate(frames):
        y_profile[i] = compute_frame_brightness(frame)
        r_profile[i] = compute_frame_brightness(frame[:, :, 0])
        g_profile[i] = compute_frame_brightness(frame[:, :, 1])
        b_profile[i] = compute_frame_brightness(frame[:, :, 2])

    return y_profile, r_profile, g_profile, b_profile


def video_perceptive_hash(frames):
    def frame_perceptive_hash(frame):
        im = Image.fromarray(frame)
        ah = imhash.average_hash(im).hash.astype(float)
        ph = imhash.phash(im).hash.astype(float)
        wh = imhash.whash(im).hash.astype(float)
        dh_h = imhash.dhash(im).hash.astype(float)
        dh_v = imhash.dhash_vertical(im).hash.astype(float)

        return (ah, ph, wh, dh_h, dh_v)

    avg_hash = []
    prcptv_hash = []
    wvlt_hash = []
    diff_horz_hash = []
    diff_vert_hash = []

    for frame in frames:
        ah, ph, wh, dh_h, dh_v = frame_perceptive_hash(frame)
        avg_hash.append(ah)
        prcptv_hash.append(ph)
        wvlt_hash.append(wh)
        diff_horz_hash.append(dh_h)
        diff_vert_hash.append(dh_v)

    avg_hash = np.asarray(avg_hash)
    prcptv_hash = np.asarray(prcptv_hash)
    wvlt_hash = np.asarray(wvlt_hash)
    diff_horz_hash = np.asarray(diff_horz_hash)
    diff_vert_hash = np.asarray(diff_vert_hash)

    # code.interact(local=locals())

    # plt.figure(1)
    # plt.clf()
    # plt.imshow(h.hash.astype(float), cmap='gray')
    # plt.pause(0.1)
    return (avg_hash, prcptv_hash, wvlt_hash, diff_horz_hash, diff_vert_hash)


def audio_perceptive_hash(frames):
    pass


if __name__ == '__main__':
    folders = [x[0]
               for x in os.walk(config.DB_VID_ROOT)][1:]
    print('='*80)
    print('Video list')
    print('-'*80)
    print('\n'.join(['%d. %s' % (i+1, f) for (i, f) in enumerate(folders)]))
    print('='*80)

    # choice = 4
    # while choice not in range(1, len(folders)+1):
    #     choice = int(input('Select folder:'))

    # for choice in range(1, 2):
    for choice in range(1, len(folders)+1):
        tic = time.time()
        selected_folder = folders[choice-1]
        print(selected_folder)

        vid_path = selected_folder
        aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
        v = Video(vid_path, aud_path)

        extract_features(v, ('frame_perceptive_hash', ))
        print('Time taken', time.time()-tic)
    # plt.show()
    # code.interact(local=locals())
