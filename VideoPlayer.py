import os
import glob
import time
import datetime
import threading
import multiprocessing
import tkinter as tk
from queue import Queue, Empty, Full
import code
import traceback

import numpy as np
import pyaudio
from PIL import Image, ImageTk

import config
from Video import Video


class VideoPlayer(tk.Frame):
    PLAY = 0
    PAUSE = 1

    def __init__(self, master, video_obj=None):
        super().__init__(master)
        self.master = master
        # self.pack()

        # self.root = tk.Tk()
        # self.root.wm_title("Video Query")
        # self.root.overrideredirect(1)

        self.state = self.PAUSE
        self.init_frame = np.zeros(
            (
                config.FRAME_DIM[1],
                config.FRAME_DIM[0],
                config.FRAME_DIM[2]
            ),
            dtype='uint8'
        )

        init_frame = ImageTk.PhotoImage(
            Image.fromarray(
                self.init_frame
            )
        )

        # quit_btn = tk.Button(
        #     self, text='QUIT',
        #     command=self.onClose
        # )

        self.panel = tk.Label(self, image=init_frame)
        self.panel.image = init_frame
        self.panel.pack(side='top')

        self.play_pause_btn = tk.Button(
            self, text=u'\u23f8', command=self.play_pause
        )

        stop_btn = tk.Button(
            self, text='\u23f9', command=self.stop
        )

        self.seek_bar = tk.Scale(
            self, from_=0, to=1,
            orient=tk.HORIZONTAL, command=self.seek, length=200,
            showvalue=0
        )

        self.time_label = tk.Label(self, text="--:--")

        # quit_btn.pack(side='top')
        self.play_pause_btn.pack(side='left')
        stop_btn.pack(side='left')
        self.seek_bar.pack(side='left')
        self.time_label.pack(side='left')

        self.video_obj = None
        self.frame_ptr = 0

        # if config.USE_MULTIPROCESSING:
        if False:
            self.videoBuffer = multiprocessing.Queue(maxsize=2)
            self.audioBuffer = multiprocessing.Queue(maxsize=2)

            self.stop_buffering = multiprocessing.Event()
            self.stop_rendering = multiprocessing.Event()

            self.bufferingThread = multiprocessing.Process(
                target=self.buffer_frame_data)
            self.bufferingThread.start()

            self.renderingThread = multiprocessing.Process(
                target=self.play_video_frame)
            self.renderingThread.start()
        else:
            self.videoBuffer = Queue(maxsize=10)
            self.audioBuffer = Queue(maxsize=10)

            self.stop_buffering = threading.Event()
            self.stop_rendering = threading.Event()

            self.bufferingThread = threading.Thread(
                target=self.buffer_frame_data)
            self.bufferingThread.start()

            self.renderingThread = threading.Thread(
                target=self.play_video_frame)
            self.renderingThread.start()

            self.audio_stream = None
        self.stop()
        self.load_video(video_obj)
        # if video_obj is not None:

    def load_video(self, video_obj=None):
        if video_obj is None:
            return
        self.stop()
        self.video_obj = video_obj
        self.seek_bar.config(to=self.video_obj.num_video_frames)

        self.delay = self.video_obj.frame_delay

        self.pyaudio_inst = pyaudio.PyAudio()
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        self.audio_stream = self.pyaudio_inst.open(
            format=self.pyaudio_inst.get_format_from_width(
                self.video_obj.audio_width),
            channels=self.video_obj.audio_channels,
            rate=self.video_obj.audio_rate,
            frames_per_buffer=video_obj.audioframes_per_videoframe,
            output=True,
            stream_callback=self.play_audio_frame
        )
        self.audio_stream.start_stream()

    def buffer_frame_data(self):
        tic = time.time()
        while not self.stop_buffering.is_set():
            # This line is magic. DO NOT REMOVE. SYNC BREAKS
            print('')
            if self.state == self.PLAY:
                vid_frame = self.video_obj.get_video_frame(self.frame_ptr)
                aud_frame = self.video_obj.get_audio_frame(self.frame_ptr)
                try:
                    # print(self.video_obj.name, 'buffering')
                    self.videoBuffer.put(
                        vid_frame, block=False)
                    self.audioBuffer.put(
                        aud_frame, block=False)
                    # print(self.video_obj.name, 'buffered')
                    # Change to mod to loop video
                    self.frame_ptr = (
                        self.frame_ptr + 1) % self.video_obj.num_video_frames
                    # self.frame_ptr = self.frame_ptr + 1
                except Full:
                    pass
                    # print('Buffer full')

                if not self.stop_buffering.is_set():
                    self.seek_bar.set(self.frame_ptr)
                    # time_str = str(datetime.timedelta(
                    #     seconds=self.delay * self.frame_ptr))
                    time_str = time.strftime(
                        "%M:%S", time.gmtime(self.delay * self.frame_ptr))
                    self.time_label.config(text=time_str)
                if self.frame_ptr == self.video_obj.num_video_frames:
                    self.state = self.PAUSE

                toc = time.time()
                delay = max(0, self.delay - (toc - tic))
                time.sleep(delay)
                tic = time.time()

            else:
                if self.stop_buffering.is_set():
                    break
        print('Stopping buffering thread')

    def play_video_frame(self):
        while not self.stop_rendering.is_set():
            # This line is magic. DO NOT REMOVE. SYNC BREAKS
            print('')
            # tic = time.time()
            if self.state == self.PAUSE:
                try:
                    self.videoBuffer.get(block=False)
                except Empty:
                    pass
                if self.stop_rendering.is_set():
                    break
            else:
                # Read queue and render
                try:
                    frame = self.videoBuffer.get(block=False)
                    # print('buffer emptied')
                    # print('rendering to screen')
                    self.draw_video_frame(frame)
                    # print('rendered')
                except Empty:
                    pass
                # stop_flag = self.stop_rendering.wait(delay)
                # print(delay)
            # print(time.time() - tic)
        print('stopping rendering')

    def draw_video_frame(self, frame):
        if not self.stop_rendering.is_set():
            panel_frame = ImageTk.PhotoImage(
                Image.fromarray(frame)
            )
            self.panel.configure(image=panel_frame)
            self.panel.image = panel_frame

    def play_audio_frame(self, in_data, frame_count, time_info, status):
        try:
            if self.state == self.PAUSE:
                try:
                    self.audioBuffer.get(block=False)
                except Empty:
                    pass
                data = bytes(
                    frame_count * self.video_obj.audio_channels * self.video_obj.audio_width
                )
                return (data, pyaudio.paContinue)
            else:
                try:
                    data = self.audioBuffer.get(block=False)
                except Empty:
                    data = bytes(
                        frame_count * self.video_obj.audio_channels * self.video_obj.audio_width
                    )
                return (data, pyaudio.paContinue)
        except:
            traceback.print_exc()
            data = bytes(1)
            print('PyAudio buffer underflow. Stream aborted')
            return (data, pyaudio.paAbort)

    def play_pause(self):
        if self.state == self.PLAY:
            self.play_pause_btn.config(text='\u25b6')
            self.state = self.PAUSE
            return
        if self.frame_ptr < self.video_obj.num_video_frames:
            self.play_pause_btn.config(text='\u23f8')
            self.state = self.PLAY

    def stop(self):
        if self.state == self.PLAY:
            self.state = self.PAUSE
        self.frame_ptr = 0
        self.seek_bar.set(0)
        self.time_label.config(text="--:--")
        self.play_pause_btn.config(text='\u25b6')

        self.draw_video_frame(self.init_frame)

    def seek(self, value):
        self.frame_ptr = int(value)

    def onClose(self):
        self.state = self.PAUSE
        self.stop_buffering.set()
        self.stop_rendering.set()
        # while not self.videoBuffer.empty():
        #     self.videoBuffer.get()
        # while not self.audioBuffer.empty():
        #     self.audioBuffer.get()
        print('Joining buffering thread')
        self.bufferingThread.join()
        print('Buffer thread complete')

        print('Joining rendering thread')
        self.renderingThread.join()
        print('Render thread complete')
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()


if __name__ == '__main__':
    folders = [x[0]
               for x in os.walk(config.QUERY_VID_ROOT)][1:]
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
    v1 = Video(vid_path, aud_path)

    selected_folder = folders[choice]
    print(selected_folder)

    vid_path = selected_folder
    aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
    v2 = Video(vid_path, aud_path)

    root = tk.Tk()
    f = tk.Frame()
    player1 = VideoPlayer(f, v1)
    player1.pack()
    player2 = VideoPlayer(f, v2)
    player2.pack()
    f.pack()

    def close():
        player1.onClose()
        player2.onClose()
        root.quit()

    k = threading.Event()

    def timer():
        ptime = time.time()
        while not k.is_set():
            print(time.time()-ptime)
            ptime = time.time()

    root.wm_title("Video Player")
    root.wm_protocol("WM_DELETE_WINDOW", close)

    # t = threading.Thread(target=timer)
    # t.start()
    try:
        root.mainloop()
    except:
        pass
    # k.set()
    # t.join()
    root.destroy()
    # onClose()
    # code.interact()
