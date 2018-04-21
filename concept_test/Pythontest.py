import cv2
import numpy as np

# Python gradient calculation 
 
# Read image
im = cv2.imread('Boat.jpg')
im.astype('float32')
im =  im / 255.0 
# Calculate gradient 
gx = cv2.Sobel(im, cv2.CV_64F, 1, 0, ksize=1)
gy = cv2.Sobel(im, cv2.CV_64F, 0, 1, ksize=1)
mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
im2=np.loadtxt("file.txt")
# f=open("write.text","w+")
# f.write(str(im))
# f.close()

cv2.imshow('Image2',im)
cv2.imshow('Image1',im2)
cv2.waitKey(0)