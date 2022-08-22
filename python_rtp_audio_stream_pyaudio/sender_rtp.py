from struct import pack
import pyaudio
import sys
import socket
import datetime
import pyrtp_2 as rtp
import random

HOST = sys.argv[1]
PORT = sys.argv[2]

data = bytes() # Stream of audio bytes 
seq_num = 0

CHUNK_SIZE = 1024
Header = 24
Payload = 1024
BROADCAST_SIZE = Header + Payload 
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
    global seq_num
    if (len(data) >= Payload):
        seq_num += 1
        packet_vars = {'version' : 2,
                    'padding' : 0,
                    'extension' : 0,
                    'csi_count' : 0,
                    'marker' : 0,
                    'payload_type' : 97,
                    'sequence_number' : seq_num,
                    'timestamp' : random.randint(1, 99999),
                    'ssrc' : 185755418,
                    'payload' : data}
        rtp_packet = rtp.GenerateRTP(packet_vars)

        sock.sendto(rtp_packet[:BROADCAST_SIZE], (HOST, int(PORT)))
        data = data[Payload:]
        print(f'Sent {str(BROADCAST_SIZE)} bytes of audio. {datetime.datetime.now().time()}')
        #print(rtp_packet)
        print(f" Sending Info\n Sequence Number: {packet_vars['sequence_number']}\n Payload Size : {len(packet_vars['payload'])}\n Packet Size : {len(rtp_packet)}")
try:
    while True:
        send_data()
        # if seq_num==1:
        #     break

except KeyboardInterrupt:
    print('\nClosing stream...')
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
