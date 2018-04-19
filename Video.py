import glob
import os
import code

import wave
import cv2
import numpy as np

import config


class Video(object):
    def __init__(self, video_path, audio_path, fps=config.FRAME_RATE, name=None):
        if name is None:
            name = os.path.basename(video_path)

        self.name = name

        self.read_video(video_path)
        self.read_audio(audio_path)

        self.fps = fps
        self.frame_delay = 1.0/fps

        self.features = {}

        self.check_audio_video_length()

    def read_video(self, video_path):
        framelist = glob.glob(os.path.join(video_path, '*.rgb'))
        self.frames = []

        for frame_path in framelist:
            self.frames.append(self.load_frame(frame_path))

        self.num_video_frames = len(framelist)

        self.curr_frame = 0

        return self.frames

    def load_frame(self, frame_path):
        with open(frame_path, 'rb') as frame_file:
            x = np.fromfile(
                frame_file, dtype='uint8'
            ).reshape(
                config.FRAME_DIM, order='F'
            ).swapaxes(0, 1)

        return x

    def read_audio(self, audio_path):
        audio = wave.open(audio_path, 'rb')

        self.audio_width = audio.getsampwidth()
        self.audio_rate = audio.getframerate()
        self.audio_channels = audio.getnchannels()
        self.num_audio_frames = audio.getnframes()

        self.audio = audio.readframes(
            self.num_audio_frames)

        audio.close()

        return self.audio

    def check_audio_video_length(self):
        self.audioframes_per_videoframe = self.audio_rate // self.fps
        # print(self.audioframes_per_videoframe)
        if not (self.num_audio_frames // self.audioframes_per_videoframe == self.num_video_frames):
            print("Insufficient audio frames. Padding with 0 at end")
            print("Length of audio", self.num_audio_frames/self.audio_rate)
            print("Length of video", self.num_video_frames/self.fps)

    def get_video_frame(self, frame_no):
        f = max(0, min(frame_no, self.num_video_frames-1))
        return self.frames[f]

    def get_audio_frame(self, frame_no):
        f_start = frame_no * self.audioframes_per_videoframe
        f_end = f_start + self.audioframes_per_videoframe

        f_start = max(0, min(f_start, self.num_audio_frames))
        f_end = max(0, min(f_end, self.num_audio_frames))

        f_start = f_start * self.audio_width * self.audio_channels
        f_end = f_end * self.audio_width * self.audio_channels

        buffer_data = bytes(self.num_audio_frames - (f_end - f_start))
        # print(f_start, f_end)
        # print(len(buffer_data))

        return self.audio[f_start: f_end] + buffer_data


if __name__ == '__main__':
    folders = [x[0]
               for x in os.walk(config.DB_VID_ROOT)][1:]
    print('='*80)
    print('Video list')
    print('-'*80)
    print('\n'.join(['%d. %s' % (i+1, f) for (i, f) in enumerate(folders)]))
    print('='*80)

    choice = -1
    while choice not in range(1, len(folders)+1):
        choice = int(input('Select folder:'))

    selected_folder = folders[choice-1]
    print(selected_folder)

    vid_path = selected_folder
    aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
    v = Video(vid_path, aud_path)
    code.interact(local=locals())
