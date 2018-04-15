import cv2
import os
import sys
import numpy as np
import time


base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print('base_dir')
print(base_dir)
database_dir = os.path.join(base_dir, 'database')

im_h = 288
im_w = 352


def rgb_read(img_path):
    with open(img_path, 'rb') as fp:
        y = np.fromfile(fp, dtype='uint8').reshape(
            (im_w, im_h, 3), order='F').swapaxes(0, 1)

    return y


# video_dir = 'flowers'
# video_dir = 'interview'
# video_dir = 'movie'
# video_dir = 'musicvideo'
# video_dir = 'sports'
video_dir = 'starcraft'
# video_dir = 'traffic'

print(os.path.join(database_dir, video_dir))

for i in range(1, 601):
    img_path = os.path.join(
        database_dir,
        video_dir,
        '%s%03d.rgb' % (video_dir, i)
    )
    # print(img_path)
    # print(os.path.exists(img_path))

    y = rgb_read(img_path)

    cv2.imshow('test', y)
    key = cv2.waitKey(1000//30) & 0xFF
    # time.sleep(1)

    # while cv2.getWindowProperty('test', 0) >= 0:
    #     key = cv2.waitKey(1) & 0xFF
    #     print(key)
    if key == 13 or key == 27:
        break
cv2.destroyAllWindows()
