import glob
import os
import threading
import code
import time
import traceback

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

    def __init__(self, video_path, audio_path, fps=config.FRAME_RATE):
        self.read_video(video_path)
        self.read_audio(audio_path)

        # self.num_video_frames = len(self.frames)
        # self.num_audio_frames = len(self.frames)

        self.frame_delay = 1/fps

        self.features = {
            'video': {},
            'frame': [{} for _ in range(self.num_video_frames)],
            'audio': {}
        }

        self.state = self.PAUSE

        self.sync_flag = threading.Event()
        self.sync_flag.clear()

        self.sync_counter = 0

        print(self.num_video_frames, self.num_audio_frames)

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
            x = cv2.cvtColor(np.fromfile(frame_file, dtype='uint8').reshape(
                config.FRAME_DIM, order='F').swapaxes(0, 1),
                cv2.COLOR_RGB2BGR
            )

        return x

    def read_audio(self, audio_path):
        self.audio = wave.open(audio_path, 'rb')

        self.audio_width = self.audio.getsampwidth()
        self.audio_rate = self.audio.getframerate()
        self.audio_channels = self.audio.getnchannels()
        self.num_audio_frames = self.audio.getnframes()

        # print(self.audio_width, self.audio_rate, self.audio_channels)

        self.raw_audio = self.audio.readframes(
            self.num_audio_frames)

        self.audio.setpos(0)

        return self.audio

    def play_audio_callback(self, in_data, frame_count, time_info, status):
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
            self.curr_frame = min(self.curr_frame + 1, self.num_video_frames-1)

        continue_flag = self.curr_frame >= self.num_video_frames-1

        if self.sync_counter % 30 == 0 or continue_flag:
            self.sync_flag.set()
        self.sync_counter += 1
        return (data, continue_flag)

    def update_pos(self, seekpos):
        # seekpos is a float in [0,1) as a percentage of total video

        print(int(seekpos * self.num_audio_frames))
        print(int(seekpos * self.num_video_frames))

        self.audio.setpos(int(seekpos * self.num_audio_frames))
        self.curr_frame = int(seekpos * self.num_video_frames)


class FrameStream(object):
    def __init__(self, framename, rate, stream_callback, panel):
        self.fname = framename
        self.delay = 1/rate
        self.callback = stream_callback
        self.stop_flag = threading.Event()
        self.stop_flag.clear()
        self.panel = panel
        self.thread = threading.Thread(
            target=self.stream, args=(), name='frame')

    def draw_frame(self):
        frame, state = self.callback()
        print(frame.shape)
        frame_lab = ImageTk.PhotoImage(
            Image.fromarray(frame))
        # cv2.imshow(self.fname, frame)
        # cv2.waitKey(1)
        try:
            # print(1)
            self.panel.configure(image=frame_lab)
            self.panel.image = frame_lab
            # print(2)
        except:
            traceback.print_exc()
        return state

    def stream(self):
        try:
            state = 0
            # cv2.startWindowThread()
            # cv2.namedWindow(self.fname)

            tic = time.time()
            while not self.stop_flag.is_set():
                print('get frame')
                state = self.draw_frame()
                print('got frame')
                toc = time.time()
                # print(toc-tic)
                if toc-tic < self.delay:
                    time.sleep(self.delay - (toc - tic))

                # print('a' if self.stop_flag.is_set() else '')
                # if self.stop_flag.wait(0.001):
                #     print('stopping stream')
                #     # cv2.destroyAllWindows()
                #     break
                tic = time.time()
                print('end')
            else:
                print(state, self.stop_flag.is_set())
            print('Stopping frame thread')
        except:
            traceback.print_exc()
        print('closing frame thread')

    def start_stream(self):
        self.stop_flag.clear()
        self.thread.start()

    def stop_stream(self):
        self.stop_flag.set()
        self.thread.join()

    def is_active(self):
        return self.thread.is_alive()


class VideoPlayer(object):
    def __init__(self, video_obj):
        self.root = tk.Tk()
        self.root.wm_title("Video Query")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        self.video_obj = video_obj

        frame_lab = ImageTk.PhotoImage(
            Image.fromarray(self.video_obj.frames[0]))

        self.panel = tk.Label(image=frame_lab)
        play_btn = tk.Button(self.root, text='PLAY',
                             command=self.play)
        pause_btn = tk.Button(self.root, text='PAUSE',
                              command=self.pause)
        seek_btn = tk.Button(self.root, text='RESET',
                             command=self.seek)

        self.panel.image = frame_lab

        self.panel.pack(side='top')
        play_btn.pack(side='left')
        pause_btn.pack(side='left')
        seek_btn.pack(side='left')
        self.thread = threading.Thread(
            target=self.run_player, args=(), name='player')
        self.stopEvent = threading.Event()

        self.pyaudio_inst = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_inst.open(
            format=self.pyaudio_inst.get_format_from_width(
                self.video_obj.audio_width),
            channels=self.video_obj.audio_channels,
            rate=self.video_obj.audio_rate,
            frames_per_buffer=1470,
            output=True,
            stream_callback=self.video_obj.play_audio_callback
        )
        self.frame_stream = FrameStream(
            'test', config.FRAME_RATE, self.video_obj.draw_frame_callback, self.panel
        )
        self.thread.start()

    def run_player(self):
        try:
            self.audio_stream.start_stream()
            self.frame_stream.start_stream()

            self.video_obj.state = Video.PLAY

            counter = 0
            # while self.audio_stream.is_active() and self.frame_stream.is_active():
            #     if self.stopEvent.is_set():

            while (self.audio_stream.is_active() or self.frame_stream.is_active()) and not self.stopEvent.is_set():
                pass
                counter += 1
                # print(counter)
                # if self.stopEvent.is_set():
                #     self.audio_stream.stop_stream()
                #     self.pyaudio_inst.terminate()
                #     self.frame_stream.stop_stream()
                #     break
        except KeyboardInterrupt:
            traceback.print_exc()
            self.onClose()

        if self.stopEvent.is_set():
            print('closing playback thread')
            # self.onClose()
            self.audio_stream.stop_stream()
            self.frame_stream.stop_stream()

        print('closed playback thread')

    def play(self):
        self.video_obj.state = Video.PLAY

    def pause(self):
        self.video_obj.state = Video.PAUSE

    def seek(self):
        self.frame_stream.stop_stream()
        self.video_obj.update_pos(0.2)
        self.frame_stream.start_stream()

    def onClose(self):

        self.stopEvent.set()
        self.thread.join()
        # self.audio_stream.stop_stream()
        self.pyaudio_inst.terminate()
        # self.frame_stream.stop_stream()
        self.root.destroy()
        print('Closing')


if __name__ == '__main__':
    folders = [x[0]
               for x in os.walk(config.DB_VID_ROOT)][1:]
    print('='*80)
    print('Video list')
    print('-'*80)
    print('\n'.join(['%d. %s' % (i+1, f) for (i, f) in enumerate(folders)]))
    print('='*80)

    choice = 1
    while choice not in range(1, len(folders)+1):
        choice = int(input('Select folder:'))

    selected_folder = folders[choice-1]
    print(selected_folder)

    vid_path = selected_folder
    aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
    v = Video(vid_path, aud_path)
    player = VideoPlayer(v)
    # player.start()
    # player.run_player()
    player.root.mainloop()
    # print('Closed')
    code.interact(local=locals())
    # threading.enumerate()
