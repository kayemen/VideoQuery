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
    'brightness_profile_y': 0.1,
    'brightness_profile_r': 0.05,
    'brightness_profile_g': 0.05,
    'brightness_profile_b': 0.05,
    'perceptual_hash_ahash': 0,
    'perceptual_hash_phash': 1,
    'perceptual_hash_whash': 0,
    'perceptual_hash_dhhash': 0,
    'perceptual_hash_dvhash': 0,
    'blockmotion_vecs_x': 1,
    'blockmotion_vecs_y': 1,
    'audio_spectral_profile': 0.1,
}

FEATURE_COLORS = {
    'brightness_profile_y': '#0000ff',
    'brightness_profile_r': '#00007f',
    'brightness_profile_g': '#00003f',
    'brightness_profile_b': '#00001f',
    'perceptual_hash_ahash': '#00ff00',
    'perceptual_hash_phash': '#007f00',
    'perceptual_hash_whash': '#003f00',
    'perceptual_hash_dhhash': '#001f00',
    'perceptual_hash_dvhash': '#000f00',
    'blockmotion_vecs_x': '#ff0000',
    'blockmotion_vecs_y': '#7f0000',
    'audio_spectral_profile': '#ff00ff',
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
