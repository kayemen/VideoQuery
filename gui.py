import glob
import os
import time
import pickle
import code
import threading
import tkinter as tk
# from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt

import config
from Video import Video
from VideoPlayer import VideoPlayer
from feature_extraction import extract_features
from feature_comparison import compare_features, rank_features, generate_plots


class VideoQueryGUI(tk.Frame):
    FORCE_CREATE = False

    def __init__(self, master):
        self.master = master
        master.title("CSCI 576 Project - Video Query System")
        master.wm_title("Video Player")
        master.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        self.folders = [x[0]
                        for x in os.walk(config.DB_VID_ROOT)][1:]
        self.load_database()
        self.create_frames()
        print('%s%s%s' % ('*'*20, 'Loaded GUI', '*'*20))
        self.query_player.load_video(self.db_vids[0])
        self.db_player.load_video(self.db_vids[1])

        # self.load_db_thread = threading.Thread(target=self.load_database)
        # self.load_db_thread.start()

        # self.load_database()
    # def load_database(self):
    #     print('Thread start')
    #     time.sleep(3)
    #     print('Thread end')

    def load_database(self):
        print('Started')
        print('=' * 80)
        print('Database video list')
        print('-' * 80)
        print('\n'.join(['%d. %s' % (i+1, f)
                         for (i, f) in enumerate(self.folders)]))
        print('=' * 80)

        self.db_vids = []
        for selected_folder in self.folders:
            print(selected_folder)
            pkl_path = glob.glob(os.path.join(selected_folder, '*.pkl'))
            if len(pkl_path) and not self.FORCE_CREATE:
                tic = time.time()
                print('Loading pre-calculated features')
                with open(pkl_path[0], 'rb') as pkl_fp:
                    v = pickle.load(pkl_fp)
                print('Loaded in %0.4fs' % (time.time()-tic))
            else:
                tic = time.time()
                print('Loading video')
                vid_path = selected_folder
                aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
                v = Video(vid_path, aud_path)
                print('Loaded in %0.4fs' % (time.time()-tic))

                # Computing features
                tic = time.time()
                print('Calculating video features')
                extract_features(v)
                print('Calculated in %0.4fs' % (time.time()-tic))

                print('Saving results to database')
                with open(os.path.join(selected_folder, '%s.pkl' % v.name), 'wb') as pkl_fp:
                    pickle.dump(v, pkl_fp)
            self.db_vids.append(v)

    def create_frames(self):
        # Top frame - Buttons and list
        self.frame1 = tk.LabelFrame(
            self.master, text='', relief=tk.RAISED
        )

        self.frame1.pack(side='top', expand=True, fill='both')

        self.load_q_button = tk.Button(
            self.frame1, text='Load Query', command=self.load_query_video)
        self.load_q_button.grid(row=0, column=0)

        self.run_button = tk.Button(
            self.frame1, text='Find matches', command=self.run_match)
        self.run_button.grid(row=1, column=0)

        self.match_list = tk.Listbox(self.frame1, height=4)
        self.yscroll = tk.Scrollbar(
            self.frame1, orient=tk.VERTICAL, command=self.match_list.yview)
        self.match_list['yscrollcommand'] = self.yscroll.set

        self.match_list.grid(row=0, column=1, rowspan=2, stick='wens')
        self.yscroll.grid(row=0, column=1, rowspan=2, sticky='nse')

        self.curr_selection = -1
        self.poll_match_list()

        self.frame1.grid_columnconfigure(0, weight=1)
        self.frame1.grid_columnconfigure(1, weight=2)

        # Middle frame - Status box and correlation plots
        self.frame2 = tk.LabelFrame(
            self.master, text='', relief=tk.RAISED,
            height=200
        )
        self.frame2.pack(side='top', expand=True, fill='both')

        self.info_label = tk.Label(self.frame2, text='STATUS')
        self.info_label.grid(row=0, column=0)

        self.corr_curve_label = tk.Label(self.frame2, text='')
        self.corr_curve_label.config(background='yellow')
        self.corr_curve_label.bind("<Button-1>", self.show_corr_plots)
        self.corr_curve_label.grid(row=0, column=1, stick='nsew')

        self.frame2.grid_columnconfigure(0, weight=1)
        self.frame2.grid_columnconfigure(1, weight=1)

        # End frame - Video players
        self.frame3 = tk.LabelFrame(
            self.master, text='', relief=tk.RAISED,
            height=200
        )
        self.frame3.pack(side='top', expand=True, fill='both')

        self.query_player = VideoPlayer(self.frame3)
        self.query_player.grid(row=0, column=0, stick='nsw')
        self.db_player = VideoPlayer(self.frame3)
        self.db_player.grid(row=0, column=1, stick='nse')

    def load_query_video(self, filepath=None):
        print('Loading query video')

    def run_match(self):
        print('Running query in database')
        print(self.query_player.videoBuffer is self.db_player.videoBuffer)

        # self.match_list.delete(0, tk.END)
        # matchlist = [
        #     'vid1',
        #     'vid2',
        #     'vid3',
        #     'vid4',
        #     'vid5',
        #     'vid6',
        #     'vid7',
        # ]
        # for match in matchlist:
        #     self.match_list.insert(tk.END, match)

    def poll_match_list(self):
        current = self.match_list.curselection()
        if current != self.curr_selection:
            print('Selection updated to ')
            print(current)
            self.curr_selection = current
        self.master.after(250, self.poll_match_list)

    def show_corr_plots(self, event):
        print('Show plots')

    def onClose(self):
        self.query_player.onClose()
        self.db_player.onClose()
        self.master.quit()


if __name__ == '__main__':
    root = tk.Tk()
    app = VideoQueryGUI(root)
    root.mainloop()
    root.destroy()
