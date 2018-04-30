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

# choice = -1
#     try:
#         choice = int(input('Select folder:'))
#     except:
#         choice = -1


for choice in range(1, len(folders)+1):
    selected_folder = folders[choice-1]

    pkl_path = glob.glob(os.path.join(selected_folder, 'query_scores.pkl'))

    if len(pkl_path) and not FORCE_CREATE:
        tic = time.time()
        print('Loading pre-calculated comparison metrics')
        with open(pkl_path[0], 'rb') as pkl_fp:
            query_scores = pickle.load(pkl_fp)
        print('Loaded in %0.4fs' % (time.time()-tic))
    else:
        pkl_path = [pth for pth in glob.glob(os.path.join(
            selected_folder, '*.pkl')) if not os.path.basename(pth).startswith('query_scores')]

        if len(pkl_path) and not FORCE_CREATE:
            tic = time.time()
            print('Loading pre-calculated features')
            with open(pkl_path[0], 'rb') as pkl_fp:
                query_vid = pickle.load(pkl_fp)
            print('Loaded in %0.4fs' % (time.time()-tic))
        else:
            # Loading query video
            tic = time.time()
            vid_path = selected_folder
            aud_path = glob.glob(os.path.join(selected_folder, '*.wav'))[0]
            print('Loading video %s' % os.path.basename(vid_path))
            query_vid = Video(vid_path, aud_path)
            print('Loaded in %0.4fs' % (time.time()-tic))

            # Computing features
            tic = time.time()
            print('Calculating video features')
            extract_features(query_vid)
            print('Calculated in %0.4fs' % (time.time()-tic))

            print('Caching query')
            with open(os.path.join(selected_folder, '%s.pkl' % query_vid.name), 'wb') as pkl_fp:
                pickle.dump(query_vid, pkl_fp)
        # code.interact(local=locals())

        # Computing featurewise scores
        query_scores = {}
        for i, db_vid in enumerate(db_vids[:]):
            print('Comparing features with %s' % db_vid.name)
            tic = time.time()
            query_scores[db_vid.name] = compare_features(query_vid, db_vid)
            print('Feature comparison completed in %0.4fs' % (time.time()-tic))

        print('Saving results to database')
        with open(os.path.join(selected_folder, 'query_scores.pkl'), 'wb') as pkl_fp:
            pickle.dump(query_scores, pkl_fp)

    # Final ranking and plotting
    final_ranks = rank_features(query_scores)
    generate_plots(final_ranks, title=os.path.basename(selected_folder))
plt.show()

# code.interact(local=locals())

# root = tk.Tk()
# player = VideoPlayer(root, query_vid)

# root.wm_title("Video Player")
# root.wm_protocol("WM_DELETE_WINDOW", player.onClose)
# try:
#     root.mainloop()
# except:
#     pass
# root.destroy()
