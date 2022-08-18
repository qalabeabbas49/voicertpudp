from struct import pack
import pyaudio
import sys
import socket
import datetime
import random
import sounddevice as sd

HOST = sys.argv[1]
PORT = sys.argv[2]

data = bytes() # Stream of audio bytes 

CHUNK_SIZE = 1024 * 2
BROADCAST_SIZE = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16 # 2 bytes size
RATE = 16000

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def pyaudio_callback(in_data, frame_count, time_info, status):
    global data
    data += in_data
    return (None, pyaudio.paContinue)

# open stream (3)
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=pyaudio_callback)

# start the stream (4)
stream.start_stream()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((HOST, int(PORT)))

def send_data():
    global data
    if (len(data) > BROADCAST_SIZE):
  
        sock.sendto(data[:BROADCAST_SIZE], (HOST, int(PORT)))
        print(data[:BROADCAST_SIZE])

        data = data[BROADCAST_SIZE:]
        print(f'Sent {str(BROADCAST_SIZE)} bytes of audio. {datetime.datetime.now().time()}')

try:
    while True:
        send_data()
except KeyboardInterrupt:
    print('\nClosing stream...')
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
