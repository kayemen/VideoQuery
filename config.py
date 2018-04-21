import os
import json
import time
import re
import shutil
import traceback

# Directories
BASE_DIR = os.path.dirname(__file__)

FRAME_DIM = (352, 288, 3)

FRAME_RATE = 30

AUDIO_RATE = 44100

AUDIO_DEPTH = 2

DB_VID_ROOT = os.path.join(BASE_DIR, 'database')
QUERY_VID_ROOT = os.path.join(BASE_DIR, 'query')

BM_MACROBLOCK_SIZE = 16
BM_DISTANCE = 5

FEATURE_WEIGHTS = {
    # 'brightness_profile_y': 0.1,
    # 'brightness_profile_r': 0.1,
    # 'brightness_profile_g': 0.1,
    # 'brightness_profile_b': 0.1,
    # 'perceptual_hash_ahash': 1,
    # 'perceptual_hash_phash': 1,
    # 'perceptual_hash_whash': 1,
    # 'perceptual_hash_dhhash': 1,
    # 'perceptual_hash_dvhash': 1,
    'blockmotion_vecs_x': 1,
    'blockmotion_vecs_y': 1,
}

DEFAULT_WEIGHT = 0

# Loading local settings
#   To create a local configuration and add local overrides to these settings, make a local_config.py and override any setting values.
#   Do not add any additional settings in local_config.py. All settings in local_config must also appear in config.py
if os.path.exists(os.path.join(BASE_DIR, 'local_config.py')):
    print("Loading local configuration and overriding base settings")
    exec(open(os.path.join(BASE_DIR, 'local_config.py'), 'r').read())
else:
    print("No local configuration files found")
