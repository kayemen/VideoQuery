import glob
import os
import threading
import code
import time

import numpy as np
import cv2
import wave
import pyaudio
import matplotlib.pyplot as plt

import config

from PIL import Image
from PIL import ImageTk
import tkinter as tk


class Video(object):
    PLAY = 0
    PAUSE = 1

    def __init__(self, video_path, audio_path):
        self.read_video(
            video_path,
            audio_path
        )

        self.num_video_frames = len(self.frames)
        # self.num_audio_frames = len(self.frames)

        self.frame_delay = 1/config.FRAME_RATE

        self.features = {
            'Video': {},
            'Frame': [],
            'Audio': []
        }

        self.state = self.PAUSE

        self.sync_flag = threading.Event()
        self.sync_flag.clear()

    def read_video(self, video_path, audio_path):
        framelist = glob.glob(os.path.join(video_path, '*.rgb'))
        self.frames = []

        for frame_path in framelist:
            self.frames.append(self.read_frame(frame_path))

        self.read_audio(audio_path)
        self.curr_frame = 0

        return self.frames, self.audio

    def read_frame(self, frame_path):
        with open(frame_path, 'rb') as frame_file:
            x = cv2.cvtColor(np.fromfile(frame_file, dtype='uint8').reshape(
                config.FRAME_DIM, order='F').swapaxes(0, 1),
                cv2.COLOR_RGB2BGR
            )
            # x[:, :, ]

        return x

    def read_audio(self, audio_path):
        self.audio = wave.open(audio_path, 'rb')

        self.audio_width = self.audio.getsampwidth()
        self.audio_rate = self.audio.getframerate()
        self.audio_channels = self.audio.getnchannels()
        self.audio_length = self.audio.getnframes()

        # print(self.audio_width, self.audio_rate, self.audio_channels)

        # self.audio = self.audio_filepointer.readframes(self.audio_length)

        return self.audio

    def get_frame(self, frame_id):
        return self.frames[frame_id]

    def audio_play_callback(self, in_data, frame_count, time_info, status):
        # print(frame_count)
        self.sync_flag.wait(timeout=self.frame_delay)
        if self.state == self.PLAY:
            audio_data = self.audio.readframes(frame_count)
        elif self.state == self.PAUSE:
            audio_data = bytes(self.audio_channels *
                               self.audio_width * frame_count)

        self.sync_flag.clear()
        return (audio_data, pyaudio.paContinue)

    def draw_frame_callback(self):
        data = self.frames[self.curr_frame]
        if self.state == self.PLAY:
            self.curr_frame += 1

        self.sync_flag.set()
        return (data, self.curr_frame >= self.num_video_frames)

    def seek_update(self, seekpos):
        # seekpos is a float in [0,1] as a percentage of total video
        # self.audio_stream.setpos(seekpos)
        pass

        # for f in self.frames:
        #     key = cv2.waitKey(self.frame_delay)
        #     if key == 13 or key == 27:
        #         self.state = self.PAUSE
        #     while


class FrameStream(object):
    def __init__(self, framename, rate, stream_callback):
        #     super().__init__(*args, **kwargs)
        self.fname = framename
        self.delay = 1/rate
        print(self.delay)
        self.callback = stream_callback
        self.stop_flag = threading.Event()
        self.stop_flag.clear()
        # f = plt.figure()
        # self.ax = f.add_subplot(111)
        # plt.ion()
        # plt.show()

    def draw_frame(self):
        frame, state = self.callback()
        cv2.imshow(self.fname, frame)
        # tic = time.time()
        cv2.waitKey(1)
        # toc = time.time()
        # print(toc-tic)
        return state

    def stream(self):
        state = 0
        print('Starting')
        tot = 0
        cv2.startWindowThread()
        cv2.namedWindow(self.fname)
        # tic = time.time()
        while state == 0:
            tic = time.time()
            state = self.draw_frame()
            toc = time.time()
            # print((toc - tic))
            if toc-tic < self.delay:
                time.sleep(self.delay - (toc - tic))
            # delay = int((self.delay - (toc-tic)) * 1000 * 0.9)
            # tot += self.delay

            # tic = toc
            if self.stop_flag.is_set():
                break
            # time.sleep(delay)
        # print('Video complete', tot)

    def start_stream(self):
        self.thread = threading.Thread(target=self.stream, args=())
        self.thread.start()

    def stop_stream(self):
        self.stop_flag.set()


class VideoPlayer(object):
    def __init__(self, video_obj):
        self.pyaudio_inst = pyaudio.PyAudio()

        # print(video_obj.audio_rate)
        self.video_obj = video_obj

        self.audio_stream = self.pyaudio_inst.open(
            format=self.pyaudio_inst.get_format_from_width(
                video_obj.audio_width),
            channels=video_obj.audio_channels,
            rate=video_obj.audio_rate,
            frames_per_buffer=1470,
            output=True,
            stream_callback=video_obj.audio_play_callback
        )
        self.frame_stream = FrameStream(
            'test', config.FRAME_RATE, video_obj.draw_frame_callback
        )

    def play(self):
        try:
            self.audio_stream.start_stream()
            self.frame_stream.start_stream()
            # self.frame_stream.draw()

            self.video_obj.state = Video.PLAY
            # time.sleep(3)
            # video_obj.state = video_obj.PAUSE
            # time.sleep(3)
            # video_obj.state = video_obj.PLAY

            tic = time.time()
            # while self.frame_stream.thread.is_alive():
            while self.audio_stream.is_active() and self.frame_stream.thread.is_alive():
                pass
            toc1 = time.time()

            while self.audio_stream.is_active() or self.frame_stream.thread.is_alive():
                pass
            toc2 = time.time()
            print("Time 1:", toc1-tic)
            print("Time 2:", toc2-tic)
            # code.interact(local=locals())
        except KeyboardInterrupt:
            self.audio_stream.stop_stream()
            self.frame_stream.stop_stream()


if __name__ == '__main__':
    folders = [x[0]
               for x in os.walk('D:\\Scripts\\CS576\\Final_project\\database\\')][1:]
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
    player = VideoPlayer(v)
    player.play()
