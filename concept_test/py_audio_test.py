import pyaudio
import wave
import time
import code
import random


# filename = r".\10kHz_44100Hz_16bit_05sec.wav"
filename = r".\440Hz_44100Hz_16bit_05sec.wav"

# open a wav format music
f = wave.open(
    filename, "rb")

# instantiate PyAudio
p = pyaudio.PyAudio()

print(f.getsampwidth())
print(f.getnchannels())
print(f.getframerate())
code.interact(local=locals())

# input()

# open stream
stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(),
                rate=f.getframerate(),
                output=True)

# define stream chunk
chunk = 1024

# read data
data = f.readframes(chunk)

# play stream
while data:
    stream.write(data)
    # time.sleep(random.random()/10)
    data = f.readframes(chunk)

# stop stream
stream.stop_stream()
stream.close()

# close PyAudio
p.terminate()
