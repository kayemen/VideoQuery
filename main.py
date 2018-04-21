import os
import glob
import pickle
import code
import tkinter as tk
import time

import numpy as np
import matplotlib.pyplot as plt

import config
from Video import Video
from VideoPlayer import VideoPlayer
from feature_extraction import extract_features
from feature_comparison import compare_features, rank_features, generate_plots


# LOAD DATABASE VIDEOS
FORCE_CREATE = False

folders = [x[0]
           for x in os.walk(config.DB_VID_ROOT)][1:]
print('=' * 80)
print('Database video list')
print('-' * 80)
print('\n'.join(['%d. %s' % (i+1, f) for (i, f) in enumerate(folders)]))
print('=' * 80)

db_vids = []
for selected_folder in folders:
    print(selected_folder)
    pkl_path = glob.glob(os.path.join(selected_folder, '*.pkl'))
    if len(pkl_path) and not FORCE_CREATE:
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
    db_vids.append(v)


# SELECT QUERY VIDEO
folders = [x[0]
           for x in os.walk(config.QUERY_VID_ROOT)][1:]
print('='*80)
print('Query video list')
print('-'*80)
print('\n'.join(['%d. %s' % (i+1, f) for (i, f) in enumerate(folders)]))
print('='*80)

choice = -1
while choice not in range(1, len(folders)+1):
    choice = int(input('Select folder:'))

selected_folder = folders[choice-1]
vid_path = selected_folder
aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]

# Loading query video
tic = time.time()
print('Loading video')
query_vid = Video(vid_path, aud_path)
print('Loaded in %0.4fs' % (time.time()-tic))

# Computing features
tic = time.time()
print('Calculating video features')
extract_features(query_vid)
print('Calculated in %0.4fs' % (time.time()-tic))

code.interact(local=locals())

query_scores = {}
for i, db_vid in enumerate(db_vids[:]):
    query_scores[db_vid.name] = compare_features(query_vid, db_vid)
final_ranks = rank_features(query_scores)
generate_plots(final_ranks)

code.interact(local=locals())

# root = tk.Tk()
# player = VideoPlayer(root, query_vid)

# root.wm_title("Video Player")
# root.wm_protocol("WM_DELETE_WINDOW", player.onClose)
# try:
#     root.mainloop()
# except:
#     pass
# root.destroy()
