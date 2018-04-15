import os
import glob

import numpy as np
import matplotlib.pyplot as plt

import config
from Video import Video


def extract_features(vid_obj, feature_list=()):
    # all_ = False
    available_features = [
        'vid_bt_profile'
    ]
    if len(set(feature_list).intersection(set(available_features))) == 0:
        # all_ = True
        feature_list = tuple(available_features)

    if 'vid_bt_profile' in feature_list:
        bt, r, g, b = video_brightness_profile(
            vid_obj.frames)
        plt.figure()
        plt.plot(bt, label='Y', c='k')
        plt.plot(r, label='R', c='r')
        plt.plot(g, label='G', c='g')
        plt.plot(b, label='B', c='b')
        plt.title('Brightness profile - %s' % (vid_obj.name))
        plt.legend()
    # plt.show()


def video_brightness_profile(frames):
    bt_profile = np.zeros(len(frames))
    r_profile = np.zeros(len(frames))
    g_profile = np.zeros(len(frames))
    b_profile = np.zeros(len(frames))
    for i, frame in enumerate(frames):
        bt_profile[i] = compute_frame_brightness(frame)
        r_profile[i] = compute_frame_brightness(frame[:, :, 0])
        g_profile[i] = compute_frame_brightness(frame[:, :, 1])
        b_profile[i] = compute_frame_brightness(frame[:, :, 2])

    # norm_fact = np.max(
    #     [np.max(r_profile), np.max(g_profile), np.max(b_profile)]
    # )
    # bt_profile = bt_profile / norm_fact
    # r_profile = r_profile / norm_fact
    # g_profile = g_profile / norm_fact
    # b_profile = b_profile / norm_fact
    return bt_profile, r_profile, g_profile, b_profile


def compute_frame_brightness(frame):
    if len(frame.shape) > 2:
        R = frame[:, :, 0]
        G = frame[:, :, 1]
        B = frame[:, :, 2]
        Y = 0.299 * R + 0.587 * G + 0.114 * B

        return np.mean(Y)
    else:
        return np.mean(frame)


def video_perceptive_hash(frames):
    pass


def frame_perceptive_hash(frames):
    pass


def audio_perceptive_hash(frames):
    pass


if __name__ == '__main__':
    folders = [x[0]
               for x in os.walk('D:\\Scripts\\CS576\\Final_project\\database\\')][1:]
    print('='*80)
    print('Video list')
    print('-'*80)
    print('\n'.join(['%d. %s' % (i+1, f) for (i, f) in enumerate(folders)]))
    print('='*80)

    # choice = 4
    # while choice not in range(1, len(folders)+1):
    #     choice = int(input('Select folder:'))

    # for choice in range(1, len(folders)+1):
    for choice in range(1, 2):
        selected_folder = folders[choice-1]
        print(selected_folder)

        vid_path = selected_folder
        aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
        v = Video(vid_path, aud_path)

        extract_features(v)
    plt.show()
