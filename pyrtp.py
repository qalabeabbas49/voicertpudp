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
    version = bytes(packet_vars['version']).zfill(2)
    padding = bytes(packet_vars['padding'])
    extension = bytes(packet_vars['extension'])
    csi_count = bytes(packet_vars['csi_count']).zfill(4)
    byte1 = (version + padding + extension +csi_count).zfill(2)


    #Generate second byte of the header as binary string:
    marker = bytes(packet_vars['marker'])
    payload_type = bytes(packet_vars['payload_type']).zfill(7)

    byte2 = (marker + payload_type).zfill(2)

    sequence_number = bytes(packet_vars['sequence_number']).zfill(4)
    timestamp = bytes(packet_vars['timestamp']).zfill(8)
    ssrc = bytes(packet_vars['ssrc']).zfill(8)

    payload = packet_vars['payload']

    packet = byte1 + byte2 + sequence_number + timestamp + ssrc + payload

    return packet


def DecodeRTP(packet_bytes):

    #return dict of cariables from the packet
    packet_vars = {}

    #bytes t0 hex
    packet_bytes = packet_bytes.hex()
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


    packet_vars['sequence_number'] = packet_bytes[4:8]
    packet_vars['timestamp'] = int(packet_bytes[8:16])
    packet_vars['ssrc']  = packet_bytes[16:24]
    packet_vars['payload'] = packet_bytes[24:]

    return packet_vars