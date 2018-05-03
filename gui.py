import glob
import os
import time
import pickle
import code
import threading
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
# from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from skimage.transform import resize
import matplotlib

# matplotlib.use('agg')

import config
from Video import Video
from VideoPlayer import VideoPlayer
from feature_extraction import extract_features
from feature_comparison import compare_features, rank_features, generate_plots, generate_plot


class VideoQueryGUI(tk.Frame):
    FORCE_CREATE = False

    def __init__(self, master):
        super(VideoQueryGUI, self).__init__()
        self.master = master
        master.title("CSCI 576 Project - Video Query System")
        # master.wm_title("Video Player")
        master.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        self.folders = [x[0]
                        for x in os.walk(config.DB_VID_ROOT)][1:]
        self.query_scores = None

        self.corr_plot = np.ones((100, 356, 3), dtype='uint8')*255

        self.create_frames()
        # self.load_database()
        print('%s%s%s' % ('*'*20, 'Loaded GUI', '*'*20))

        self.load_db_thread = threading.Thread(
            target=self.load_database, name='database loader')
        self.load_db_thread.start()

        # self.load_database()
    # def load_database(self):
    #     print('Thread start')
    #     time.sleep(3)
    #     print('Thread end')

    def load_database(self):
        self.update_status('Loading database', clear=True)
        print('Started')
        print('=' * 80)
        print('Database video list')
        print('-' * 80)
        print('\n'.join(['%d. %s' % (i+1, f)
                         for (i, f) in enumerate(self.folders)]))
        print('=' * 80)

        self.db_vids = []
        for selected_folder in self.folders:
            self.update_status(selected_folder)
            pkl_path = glob.glob(os.path.join(selected_folder, '*.pkl'))
            if len(pkl_path) and not self.FORCE_CREATE:
                tic = time.time()
                self.update_status('Loading pre-calculated features')
                with open(pkl_path[0], 'rb') as pkl_fp:
                    v = pickle.load(pkl_fp)
                self.update_status('Loaded in %0.4fs' % (time.time()-tic))
            else:
                tic = time.time()
                self.update_status('Loading video')
                vid_path = selected_folder
                aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
                v = Video(vid_path, aud_path)
                self.update_status('Loaded in %0.4fs' % (time.time()-tic))

                # Computing features
                tic = time.time()
                self.update_status('Calculating video features')
                extract_features(v)
                self.update_status('Calculated in %0.4fs' % (time.time()-tic))

                self.update_status('Saving results to database')
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

        # self.dummy_btn = tk.Button(
        #     self.frame1, text='Debug', command=self.dummy_fn)
        # self.dummy_btn.grid(row=2, column=0)

        self.match_list = tk.Listbox(self.frame1, height=4)
        self.yscroll = tk.Scrollbar(
            self.frame1, orient=tk.VERTICAL, command=self.match_list.yview)
        self.match_list['yscrollcommand'] = self.yscroll.set

        self.match_list.grid(row=0, column=1, rowspan=2, stick='wens')
        self.yscroll.grid(row=0, column=1, rowspan=2, sticky='nse')

        self.match_list.bind('<Double-Button-1>', self.poll_match_list)

        self.curr_selection = -1

        self.frame1.grid_columnconfigure(0, weight=1)
        self.frame1.grid_columnconfigure(1, weight=2)

        # Middle frame - Status box and correlation plots
        self.frame2 = tk.LabelFrame(
            self.master, text='', relief=tk.RAISED,
            height=200
        )
        self.frame2.pack(side='top', expand=True, fill='both')

        self.info_text = tk.StringVar()
        self.info_text.set('STATUS')
        self.info_label = tk.Label(
            self.frame2, textvar=self.info_text, justify=tk.LEFT, anchor='w')
        # self.info_label = tk.Label(self.frame2, text='')
        self.info_label.grid(row=0, column=0, stick='nswe')

        self.corr_curve_label = tk.Label(self.frame2)
        # self.corr_curve_label.config(background='yellow')
        self.corr_curve_label.bind("<Button-1>", self.show_corr_plots)
        self.corr_curve_label.grid(row=0, column=1, stick='nse')

        self.frame2.grid_columnconfigure(0, weight=1)
        self.frame2.grid_columnconfigure(1, weight=1)

        self.query_player = VideoPlayer(self.frame2)
        self.query_player.grid(row=1, column=0, stick='nsw')
        self.db_player = VideoPlayer(self.frame2)
        self.db_player.grid(row=1, column=1, stick='nse')

        self.draw_corr_label()

    def load_query_video(self):
        self.update_status('Select query', clear=True)
        selected_folder = None
        self.master.update()
        selected_folder = askdirectory(
            initialdir=config.QUERY_VID_ROOT, title='Select query folder')
        # selected_folder = askopenfilename(
        #     initialdir=config.QUERY_VID_ROOT, title='Select query folder')
        self.update_status('Selected ' + selected_folder)

        if selected_folder == '':
            return

        self.query_loader = threading.Thread(
            target=self.load_query, args=(selected_folder, ), name='query_loader')
        self.query_loader.start()

        # while self.query_loader.is_alive():
        #     self.update_idletasks()

    def load_query(self, selected_folder=None):
        self.update_status('Loading query video', clear=True)
        if selected_folder == None:
            selected_folder = os.path.join(
                config.QUERY_VID_ROOT, 'subclip_traffic')
            # selected_folder = askdirectory(
            #     initialdir=config.QUERY_VID_ROOT, title='Select query folder')
            # print(selected_folder)
        self.update_status('Selected '+selected_folder)
        # print('Selected '+selected_folder)

        pkl_path = glob.glob(os.path.join(selected_folder, 'query_scores.pkl'))

        # print(pkl_path)

        if len(pkl_path) and not self.FORCE_CREATE:
            vid_pkl_path = [pth for pth in glob.glob(os.path.join(
                selected_folder, '*.pkl')) if not os.path.basename(pth).startswith('query_scores')]
            tic = time.time()
            self.update_status('Loading pre-calculated comparison metrics')
            # print('Loading pre-calculated comparison metrics')
            with open(pkl_path[0], 'rb') as pkl_fp:
                self.query_scores = pickle.load(pkl_fp)
            with open(vid_pkl_path[0], 'rb') as pkl_fp:
                self.query_vid = pickle.load(pkl_fp)
            self.update_status('Loaded in %0.4fs' % (time.time()-tic))
        else:
            pkl_path = [pth for pth in glob.glob(os.path.join(
                selected_folder, '*.pkl')) if not os.path.basename(pth).startswith('query_scores')]

            if len(pkl_path) and not self.FORCE_CREATE:
                tic = time.time()
                self.update_status('Loading pre-calculated features')
                with open(pkl_path[0], 'rb') as pkl_fp:
                    self.query_vid = pickle.load(pkl_fp)
                self.update_status('Loaded in %0.4fs' % (time.time()-tic))
            else:
                # Loading query video
                tic = time.time()
                vid_path = selected_folder
                aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
                self.update_status('Loading video %s' %
                                   os.path.basename(vid_path))
                self.query_vid = Video(vid_path, aud_path)

                # Computing features
                tic = time.time()
                self.update_status('Calculating video features')
                # print('Calculating video features')
                extract_features(self.query_vid)
                self.update_status('Calculated in %0.4fs' % (time.time()-tic))
                # print('Calculated in %0.4fs' % (time.time()-tic))

                self.update_status('Caching query')
                with open(os.path.join(selected_folder, '%s.pkl' % self.query_vid.name), 'wb') as pkl_fp:
                    pickle.dump(self.query_vid, pkl_fp)

            self.query_scores = {}
            for i, db_vid in enumerate(self.db_vids):
                self.update_status('Comparing features with %s' % db_vid.name)
                tic = time.time()
                self.query_scores[db_vid.name] = compare_features(
                    self.query_vid, db_vid)
                self.update_status('Feature comparison completed in %0.4fs' %
                                   (time.time()-tic))

            self.update_status('Saving results to database')
            with open(os.path.join(selected_folder, 'query_scores.pkl'), 'wb') as pkl_fp:
                pickle.dump(self.query_scores, pkl_fp)
            self.update_status('Saved results to database')

        self.query_player.load_video(self.query_vid)

    def run_match(self):
        if self.query_scores is None:
            self.update_status('No query video selected', clear=True)
            return
        self.update_status('Running query in database', clear=True)
        self.final_ranks = rank_features(self.query_scores)
        self.update_status('Generated ranked list of matches')

        self.match_list.delete(0, tk.END)
        matchlist = [x[0] for x in self.final_ranks]
        for match in matchlist:
            self.match_list.insert(tk.END, match)

        self.poll_match_list()

    def update_status(self, text, clear=False):
        if clear:
            status_text = 'STATUS:\n%s' % text
        else:
            status_text = '%s\n%s' % (self.info_text.get(), text)
        lines = status_text.split('\n')
        if len(lines) < 6:
            status_text = '\n'.join(lines + ['']*(6-len(lines)))
        elif len(lines) > 6:
            status_text = '\n'.join([lines[0]]+lines[-5:])
        self.info_text.set(status_text)

    def poll_match_list(self, event=None):
        current = self.match_list.curselection()[0]
        # print(current)
        if current != self.curr_selection:
            # self.update_status('Selection updated to ' +
            #                    self.final_ranks[current][0])
            curr_video = self.find_matching_db_vid(
                self.final_ranks[current][0])
            self.db_player.load_video(curr_video)
            plot = generate_plot(self.final_ranks[current])
            self.corr_plot = resize(
                plot, (100, 356, 3), preserve_range=True).astype('uint8')
            self.curr_selection = current
        self.master.after(250, self.poll_match_list)

    def show_corr_plots(self, event):
        generate_plots(self.final_ranks, 'Compiled')
        plt.pause(1)

    def draw_corr_label(self):
        im = ImageTk.PhotoImage(
            Image.fromarray(
                self.corr_plot
            )
        )
        self.corr_curve_label.configure(image=im)
        self.corr_curve_label.image = im

        # self.update_status('Drew_plot')
        # self.update_status(repr(self.corr_plot.shape))
        self.master.after(250, self.draw_corr_label)

    def dummy_fn(self):
        self.corr_plot = np.ones(
            (100, 356, 3), dtype='uint8') * np.random.randint(0, 255)
        # self.update_status(str(self.db_player.winfo_width()))

    def find_matching_db_vid(self, vidname):
        for vid in self.db_vids:
            if vid.name == vidname:
                return vid
        else:
            return None

    def onClose(self):
        self.query_player.onClose()
        self.db_player.onClose()
        self.master.quit()


if __name__ == '__main__':
    root = tk.Tk()
    app = VideoQueryGUI(root)
    root.mainloop()
    root.destroy()
