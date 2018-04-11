import pyaudio
import wave
import time
import code
import random
import cv2

# filename = r".\10kHz_44100Hz_16bit_05sec.wav"
filename = r".\concept_test\StarCraft.wav"
# filename = r".\concept_test\440Hz_44100Hz_16bit_05sec.wav"

# # -----------------------------BLOCKING-------------------------------------

# # open a wav format music
# f = wave.open(
#     filename, "rb")

# # instantiate PyAudio
# p = pyaudio.PyAudio()

# # print(f.getsampwidth())
# # print(f.getnchannels())
# # print(f.getframerate())
# # code.interact(local=locals())

# # input()

# # open stream
# stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
#                 channels=f.getnchannels(),
#                 rate=f.getframerate(),
#                 output=True)

# # define stream chunk
# chunk = 1024

# # read data
# data = f.readframes(chunk)

# # play stream
# while data:
#     stream.write(data)
#     # time.sleep(random.random()/10)
#     data = f.readframes(chunk)

# # stop stream
# stream.stop_stream()
# stream.close()

# # close PyAudio
# p.terminate()


# -----------------------------NON BLOCKING-------------------------------------------
import pyaudio
import wave
import time
import sys

# if len(sys.argv) < 2:
#     print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
#     sys.exit(-1)

wf = wave.open(filename, 'rb')

print(dir(wf))
print(wf.getsampwidth())
print(wf.getnchannels())
print(wf.getframerate())

framesize = wf.getsampwidth()
n_channels = wf.getnchannels()

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)

P = 1


def callback(in_data, frame_count, time_info, status):
    # print(in_data)
    global P
    if P:
        data = wf.readframes(frame_count)
    else:
        data = bytes(frame_count*framesize*n_channels)
    print(len(data))
    # print(type(data))
    return (data, pyaudio.paContinue)


# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)


# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    try:
        P = P
        time.sleep(0.1)
    except KeyboardInterrupt:
        P = 1-P
        print('Changed state')
    # key = cv2.waitKey(10)
    # if key == 13 or key == 27:
    #     P = 1-P

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()
