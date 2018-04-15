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

# Loading local settings
#   To create a local configuration and add local overrides to these settings, make a local_config.py and override any setting values.
#   Do not add any additional settings in local_config.py. All settings in local_config must also appear in config.py
if os.path.exists(os.path.join(BASE_DIR, 'local_config.py')):
    print("Loading local configuration and overriding base settings")
    exec(open(os.path.join(BASE_DIR, 'local_config.py'), 'r').read())
else:
    print("No local configuration files found")
