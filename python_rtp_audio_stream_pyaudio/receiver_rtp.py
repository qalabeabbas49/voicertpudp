import pyaudio
import sys
import socket
import pyrtp_2 as rtp

HOST = sys.argv[1]
PORT = sys.argv[2]

data = bytes() # Stream of audio bytes
is_receiving = False


CHUNK_SIZE = 1024     # Size of frame window to write audio (frames_per_buffer)
Header = 24
Payload = 1024
BROADCAST_SIZE = Header + Payload   # Socket receives audio with this size
BUFFER_SIZE = BROADCAST_SIZE * 10       # Receive this amount of data before playback
CHANNELS = 1
FORMAT = pyaudio.paInt16 # 2 bytes size
RATE = 16000

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def pyaudio_callback(in_data, frame_count, time_info, status):
    if not is_receiving:
        return (bytes([0] * frame_count * CHANNELS * 2), pyaudio.paContinue)

    global data
    try:
        # Cut the data, if it started to bufferize 
        if len(data) >= BUFFER_SIZE * 2:
            print('Cutting Audio Buffer..')
            data = data[-BUFFER_SIZE:]
        avail_data_count = min(frame_count * CHANNELS * 2, len(data))
        return_data =  data[:avail_data_count]
        data = data[avail_data_count:]
        
        # Inflate end of the array with zeros, if there is not enough audio.
        return_data += bytes([0] * (frame_count * CHANNELS * 2 - avail_data_count))
        
        return (return_data, pyaudio.paContinue)
    except:
        print('Exception in pyaudio_callback...')


# open stream (3)
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=pyaudio_callback)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, int(PORT)))
#sock.listen(1)
#connection, client_address = sock.accept()
print('Socket bind succeed.')

try:
    while True:
        new_data = sock.recv(BROADCAST_SIZE)
        #print(f"Incomming raw data : {len(new_data)}")
    
        rtp_packet = rtp.DecodeRTP(new_data)
        #print(rtp_packet)
        print(f" Receiving Info\n Sequence Number: {rtp_packet['sequence_number']}\n Payload Size : {len(rtp_packet['payload'])}\n Packet Size : {len(new_data)}")
        #payload = rtp_packet['payload']
        ##break
        data += rtp_packet['payload']
        print(len(data))
        if len(data) >= BUFFER_SIZE and not is_receiving:
            is_receiving = True

            # start stream (4)
            stream.start_stream()
            print(f'Stream started, when {len(data)} bytes of data were received.\nThis causes {str(len(data) / RATE)} seconds of latency')
except KeyboardInterrupt:
    print('\nClosing socket and stream...')
    sock.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
