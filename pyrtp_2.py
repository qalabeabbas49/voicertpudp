def GenerateRTP(packet_vars):

    #The first twelve octates are present in every RTP packet.
    #The first octet is the version number of the RTP packet.
    #The second octet is the padding bit.
    #The third octet is the extension bit.
    #The fourth octet is the CSRC count.
    #The fifth octet is the marker bit.
    #The sixth octet is the payload type.
    #The seventh to twelve octets are the sequence number.
    #The thirteen to eighteen octets are the timestamp.
    #The nineteen to twenty-four octets are the synchronization source (SSRC).
    #The remaining octets are the payload data.

    #Generate fist byte of the header a binary string:
    version = format(packet_vars['version'], 'b').zfill(2)
    padding = format(packet_vars['padding'], 'b')
    extension = format(packet_vars['extension'], 'b')
    csrc_count = format(packet_vars['csi_count'], 'b').zfill(4)
    
    byte1 = format(int((version + padding + extension + csrc_count), 2), 'x').zfill(2)


    #Generate second byte of the header as binary string:
    marker = format(packet_vars['marker'], 'b')
    payload_type = format(packet_vars['payload_type'], 'b').zfill(7)

    byte2 = format(int((marker + payload_type), 2), 'x').zfill(2)

    sequence_number = format(packet_vars['sequence_number'], 'x').zfill(4)
    timestamp = format(packet_vars['timestamp'], 'x').zfill(8)
    ssrc = format(packet_vars['ssrc'], 'x').zfill(8)

    payload = packet_vars['payload'].hex()

    packet = byte1 + byte2 + sequence_number + timestamp + ssrc + payload

    return packet.encode('utf-8')


def DecodeRTP(packet_bytes):

    #return dict of cariables from the packet
    packet_vars = {}

    byte1 = packet_bytes[0:2]
    byte1 = int(byte1, 16)
    byte1 = format(byte1, 'b').zfill(8)
    packet_vars['version'] = int(byte1[0:2],2)
    packet_vars['padding'] = int(byte1[2:3],2)
    packet_vars['extension'] = int(byte1[3:4])
    packet_vars['csi_count'] = int(byte1[4:8], 2)

    byte2 = packet_bytes[2:4]
    byte2 = int(byte2, 16)
    byte2 = format(byte2, 'b').zfill(8) 
    packet_vars['marker'] = int(byte2[0:1])
    packet_vars['payload_type'] = int(byte2[1:8], 2)


    packet_vars['sequence_number'] = int(packet_bytes[4:8], 16)
    packet_vars['timestamp'] = int(packet_bytes[8:16], 16)
    packet_vars['ssrc']  = int(packet_bytes[16:24], 16)

    payload = packet_bytes[24:]
    payload = int(payload, 16)
    payload = format(payload, 'b')
    packet_vars['payload'] = payload
    return packet_vars