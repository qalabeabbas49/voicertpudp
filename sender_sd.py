import pyaudio
import sys
import socket
import datetime
import pyrtp
import random
import sounddevice as sd
HOST = sys.argv[1]
PORT = sys.argv[2]

data = bytes() # Stream of audio bytes

BROADCAST_SIZE = 640
CHUNK_SIZE = 320
CHANNELS = 1
FORMAT = pyaudio.paInt16 # 2 bytes size
RATE = 16000

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def sd_callback(indata, frame, time, status):
    global data
    indata= bytes(indata)
    print(indata, len(indata), type(indata))
    data += indata

    return None
# open stream (3)
stream = sd.InputStream(device= "default"  ,channels=CHANNELS, samplerate=RATE, callback=sd_callback)

# start the stream (4)
stream.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((HOST, int(PORT)))data

def send_data():
    global data
    if (len(data) > BROADCAST_SIZE):
        packet_vars = {'version' : 2,
                    'padding' : 0,
                    'extension' : 0,
                    'csi_count' : 0,
                    'marker' : 0,
                    'payload_type' : 97,
                    'sequence_number' : random.randint(1,9999),
                    'timestamp' : random.randint(1,9999),
                    'ssrc' : 185755418,
                    'payload' : data}
        rtp_packet = pyrtp.GenerateRTP(packet_vars)
        #print(data, type(data))
        sock.sendto(data[:BROADCAST_SIZE], (HOST, int(PORT)))
        data = data[BROADCAST_SIZE:]
        print(f'Sent {str(BROADCAST_SIZE)} bytes of audio. {datetime.datetime.now().time()}')

try:
    while True:
        send_data()
except KeyboardInterrupt:
    print('\nClosing stream...')
    stream.stop()
    stream.close()
    #p.terminate()
    sock.close()
