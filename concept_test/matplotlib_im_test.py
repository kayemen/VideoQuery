import code

import matplotlib
import cv2

matplotlib.use('agg')

import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imsave
from skimage.transform import resize

f = plt.figure()
# ax = f.add_subplot(111)
ax = plt.Axes(f, [0., 0., 1., 1.])
ax.set_axis_off()
ax.plot(range(30))
f.add_axes(ax)
# f.patch.set_visible(False)
# ax.axis('off')

f.tight_layout()
f.canvas.draw()

data = np.fromstring(f.canvas.tostring_rgb(), dtype=np.uint8, sep='')
data = data.reshape(f.canvas.get_width_height()[::-1] + (3,))

h, w, _ = data.shape
for i in range(w):
    if np.all(data[:, i, :] == 255):
        continue
    left_lim = i
    break
print(left_lim)
for i in range(1, 1+w):
    if np.all(data[:, -i, :] == 255):
        continue
    right_lim = -i
    break
print(right_lim)

data = data[:, left_lim:right_lim, :]

data = resize(data, (100, 356, 3), preserve_range=True)
cv2.imshow('test', data.astype('uint8'))
cv2.waitKey(0)
# imsave('./test.png', data)
# matplotlib.use('QT4Agg')

# plt.imshow(data)
# plt.show()

code.interact(local=locals())
