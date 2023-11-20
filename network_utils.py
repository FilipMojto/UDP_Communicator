from utils import BitManager
from enum import Enum

class IPv4:
    OCTET_COUNT = 4

    def get_str(self):
        string = ""
        for octet in self.octets:
            string += str(octet)
            string += '.'
            #string.append(str(octet))
            #string.append(".")
        
        return string[:-1]

    def __init__(self, ip_str=None):
        self.octets = self.OCTET_COUNT * [0]

        octets = ip_str.split('.')
        oct_len = len(octets)

        for i in range(0, oct_len):
            self.set(int(octets[i]), i)
        
    def set(self, val, i):
        if not (0 <= val <= 255):
            raise ValueError("Invalid value for ip address octet!")
        elif 0 > i > 3:
            raise IndexError("Index parameter out of range!")
        
        self.octets[i] = val
    
    def bytes(self):
        byte_list = []

        for octet in self.octets:
            byte_list.append(octet.to_bytes(1, byteorder='big'))

        return byte_list

class Port:
    MAX_UDP_PORT = 65536

    def is_udp(port : int):
        if 0 <= port <= Port.MAX_UDP_PORT:
            return True
        
        return False

class CommState(Enum):
    UNITIATED = 1
    INITIATED = 2
    COMPLETE = 3



class Header:
    #ip_src : IPv4
    #ip_dst : IPv4
    HEADER_LENGTH = 12
    SYN_BIT_POS = 8
    ACK_BIT_POS = 7
    FIN_BIT_POS = 6

    def get_src_ip(self):
        return self.byte_frame[0:4]
    
    def get_dst_ip(self):
        return self.byte_frame[4:8]
    
    def get_src_port(self):
        return self.byte_frame[8:10]
    
    def get_dst_port(self):
        return self.byte_frame[10:12]
    
    def get_flags(self):
        return self.byte_frame[12]

    def __init__(self, src_ip : IPv4 = IPv4('0.0.0.0'), dst_ip : IPv4 = IPv4('0.0.0.0'),
                 src_port = 50000, dst_port = 50000, syn : bool = False, ack : bool = False, fin: bool = False):
       
        if not Port.is_udp(src_port) or not Port.is_udp(dst_port):
            raise ValueError('Invalid value for UDP port!')
        
        self.byte_frame = src_ip.bytes() + dst_ip.bytes()
        data = src_port.to_bytes(2, byteorder='big')
        
        self.byte_frame.append(data[0].to_bytes(1, byteorder='big'))
        self.byte_frame.append(data[1].to_bytes(1, byteorder='big'))

        data = dst_port.to_bytes(2, byteorder='big')

        self.byte_frame.append(data[0].to_bytes(1, byteorder='big'))
        self.byte_frame.append(data[1].to_bytes(1, byteorder='big'))

        flags = 0b00000000

        if syn:
            flags = BitManager.set_bit(flags, Header.SYN_BIT_POS - 1)
        if ack:
            flags = BitManager.set_bit(flags, Header.ACK_BIT_POS - 1)
        if fin:
            flags = BitManager.set_bit(flags, Header.FIN_BIT_POS - 1)

        self.byte_frame.append(flags.to_bytes(1, byteorder='big'))



        #+ list(dst_port.to_bytes(2, byteorder='big'))

        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port

class Communication:
    
    def accept(self, header : Header):
        if(self.state == CommState.COMPLETE):
            raise TypeError("Communication already complete!")
        
        if (header.get_src_ip() != self.src_ip or header.get_dst_ip() != self.dst_ip) and (
            header.get_src_ip() != self.dst_ip or header.get_dst_ip() != self.src_ip):
            raise ValueError("Invalid IP for this communication!")
        
        frame_len = len(self.frames)
        #Handling SYN
        if bin(header.get_flags)[2] and self.state == CommState.UNITIATED and frame_len == 0:
            self.frames.append(header)
        #Handling SYN+ACK
        elif bin(header.get_flags)[2] and bin(header.get_flags())[3] and self.state == CommState.UNITIATED and frame_len == 1:
            self.frames.append(header)
        #Handling ACK
        elif bin(header.get_flags)[2] and bin(header.get_flags())[3] == 0 and self.state == CommState.UNITIATED and frame_len == 2:
            self.frames.append(header)
            self.state == CommState.INITIATED
        #Handling FIN
        #Not yet implemented
        elif bin(header.get_flags())[4]:
            pass
    
        
        #if bin(header[12])

    def __init__(self, src_ip : IPv4, dst_ip : IPv4) -> None:
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.state = CommState.UNITIATED
        self.frames = []