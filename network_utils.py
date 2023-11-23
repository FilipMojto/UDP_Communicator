from utils import BitManager, ExceptionHandler
from enum import Enum
from typing import List

class ComError(Enum):
    NO_ERROR = 0
    COM_INCOMPLETE = 1
    COM_STARTED = 2,
    COM_COMPLETE = 3

class FrameType(Enum):
    NO_DATA = 0
    MESSAGE = 1
    TXT_FILE = 2
    C_FILE = 3

# class Flag(Enum):
#     SYN = 0,
#     ACK = 1,
#     FIN = 2,
#     CONTROL = 3,
#     QUIT = 4,
#     MORE_FRAGS = 5

# class Flags():

#     def get_bits():


#     def get(self, type: Flag) -> bool:
#         ExceptionHandler.check_comp(type, "type", type=Flag)

#         match type:
#             case Flag.SYN:
#                 return self.__SYN
#             case Flag.FIN:
#                 return self.__FIN
#             case Flag.CONTROL:
#                 return self.__CONTROL
#             case Flag.QUIT:
#                 return self.__QUIT
#             case Flag.MORE_FRAGS:
#                 return self.__MORE_FRAGS
    

#     def set(self, type: Flag, value : bool) -> None:     
#         ExceptionHandler.check_comp(obj=type, name="type", type=Flag)
#         ExceptionHandler.check_comp(obj=value, name="value", type=bool)

#         match type:
#             case Flag.SYN:
#                 self.__SYN = value
#             case Flag.FIN:
#                 self.__FIN = value
#             case Flag.CONTROL:
#                 self.__CONTROL = value
#             case Flag.QUIT:
#                 self.__QUIT = value
#             case Flag.MORE_FRAGS:
#                 self.__MORE_FRAGS = value

        
#     def __init__(self, SYN : bool = False, ACK: bool = False, FIN: bool = False,
#                  CONTROL: bool = False, QUIT: bool = False, MORE_FRAGS: bool = False) -> None:
        
#         ExceptionHandler.check_comp(obj=SYN, name="SYN", type=bool)
#         ExceptionHandler.check_comp(obj=ACK, name="ACK", type=bool)
#         ExceptionHandler.check_comp(obj=FIN, name="FIN", type=bool)
#         ExceptionHandler.check_comp(obj=CONTROL, name="CONTROL", type=bool)
#         ExceptionHandler.check_comp(obj=QUIT, name="QUIT", type=bool)
#         ExceptionHandler.check_comp(obj=MORE_FRAGS, name="MORE_FRAGS", type=bool)

#         self.__SYN = SYN
#         self.__ACK = ACK
#         self.__FIN = FIN
#         self.__CONTROL = CONTROL
#         self.__QUIT = QUIT
#         self.__MORE_FRAGS = MORE_FRAGS    
    
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

    def __init__(self, ip_str: str):
        ExceptionHandler.check_comp(obj=ip_str, name="ip_str", type=str)

        self.octets = self.OCTET_COUNT * [0]

        octets = ip_str.split('.')
        oct_len = len(octets)

        if oct_len != self.OCTET_COUNT:
            raise ValueError(f"Invalid amount of octets! {self.OCTET_COUNT} needed!")

        for i in range(0, oct_len):
            self.set(int(octets[i]), i)
        
    def set(self, val, i):
        if not (0 <= val <= 255):
            raise ValueError("Invalid value for ip address octet!")
        elif 0 > i > 3:
            raise IndexError("Index parameter out of range!")
        
        self.octets[i] = val
    
    def bytes(self) -> bytearray:
        byte_list = bytearray()

        for octet in self.octets:
            byte_list.append(octet)

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
    __HEADER_LENGTH = 9
    SYN_BIT_POS = 8
    ACK_BIT_POS = 7
    FIN_BIT_POS = 6

    ID_INIT = 0
    ID_END = 1

    ID_START = 0
    ID_BYTE_COUNT = 2
    ID_MAX = 2 ** (ID_BYTE_COUNT * 8)

    TARGET_START = ID_START + ID_BYTE_COUNT
    TARGET_BYTE_COUNT = 2

    TYPE_START = TARGET_START + TARGET_BYTE_COUNT
    TYPE_BYTE_COUNT = 1

    ERROR_START = TYPE_START + TYPE_BYTE_COUNT
    ERROR_BYTE_COUNT = 1

    FLAGS_START = ERROR_START + ERROR_BYTE_COUNT
    FLAGS_BYTE_COUNT = 1

    @staticmethod
    def verify_frame_struct(frame : bytearray) -> bool:
        ExceptionHandler.check_comp(obj=frame, name="frame", type=bytearray)

        if len(bytearray) != Header.__HEADER_LENGTH:
            raise ValueError(f"Invalid array size for parameter frame! The required size: {Header.__HEADER_LENGTH}")
        

    # def get_ID(self):
    #     byte_1 = bin(self.byte_frame[self.ID_INIT])
    #     byte_2 = bin(self.byte_frame[self.ID_END])

    #     return self. 


    


    # def get_src_ip(self):
    #     return self.byte_frame[0:4]
    
    # def get_dst_ip(self):
    #     return self.byte_frame[4:8]
    
    # def get_src_port(self):
    #     return self.byte_frame[8:10]
    
    # def get_dst_port(self):
    #     return self.byte_frame[10:12]
    
    # def get_flags(self):
    #     return self.byte_frame[12]

    #header structure:
    #   a) ID
    #   b) Target
    #   c) Type
    #   d) Error
    #   e) Flags
    #   f) FCS

    
    def get_ID(self) -> bytearray:
        return self.byte_frame[0:2]

    def get_ID_dec(self) -> int:
        return int.from_bytes(self.byte_frame[0:2], byteorder='big')
    
    def get_target(self) -> bytearray:
        return self.byte_frame[2:4]
    
    def get_type(self) -> bytearray:
        return self.byte_frame[4]
    
    def get_error(self) -> bytearray:
        return self.byte_frame[5]
    

    def __init__(self, ID : int = 0, target : int = 0, type : FrameType = FrameType.NO_DATA, error: ComError = ComError.NO_ERROR,
                 SYN: bool=False, ACK: bool=False, FIN: bool=False, CONTROL: bool=False, QUIT: bool=False,
                 MORE_FRAGS: bool=False) -> None:

        ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=0, max=self.ID_MAX)
        ExceptionHandler.check_comp(obj=target, name="target", type=int, min=0, max=self.ID_MAX)
        ExceptionHandler.check_comp(obj=type, name="type", type=FrameType)
        ExceptionHandler.check_comp(obj=error, name="error", type=ComError)

        self.byte_frame = bytearray()

        ID_b = ID.to_bytes(2,byteorder="big")

        self.byte_frame.append(ID_b[0])
        self.byte_frame.append(ID_b[1])

        target_b = target.to_bytes(2,byteorder="big")

        self.byte_frame.append(target_b[0])
        self.byte_frame.append(target_b[1])
        self.byte_frame.append(type.value)
        self.byte_frame.append(error.value)
        
        flags = 0b00000000

        if SYN:
            flags |= (1 << 7)
        if ACK:
            flags |= (1 << 6)
        if FIN:
            flags |= (1 << 5)
        if CONTROL:
            flags |= (1 << 4)
        if QUIT:
            flags |= (1 << 3)
        if MORE_FRAGS:
            flags |= (1 << 2)
        
        self.byte_frame.append(flags)

    # def __init__(self, src_ip : IPv4 = IPv4('0.0.0.0'), dst_ip : IPv4 = IPv4('0.0.0.0'),
    #              src_port = 50000, dst_port = 50000, syn : bool = False, ack : bool = False, fin: bool = False):
       
    #     if not Port.is_udp(src_port) or not Port.is_udp(dst_port):
    #         raise ValueError('Invalid value for UDP port!')
        
    #     self.byte_frame = src_ip.bytes() + dst_ip.bytes()
    #     data = src_port.to_bytes(2, byteorder='big')
        
    #     self.byte_frame.append(data[0].to_bytes(1, byteorder='big'))
    #     self.byte_frame.append(data[1].to_bytes(1, byteorder='big'))

    #     data = dst_port.to_bytes(2, byteorder='big')

    #     self.byte_frame.append(data[0].to_bytes(1, byteorder='big'))
    #     self.byte_frame.append(data[1].to_bytes(1, byteorder='big'))

    #     flags = 0b00000000

    #     if syn:
    #     flags = BitManager.set_bit(flags, Header.SYN_BIT_POS - 1)
    # #     if ack:
    #     flags = BitManager.set_bit(flags, Header.ACK_BIT_POS - 1)
    #     if fin:
    #         flags = BitManager.set_bit(flags, Header.FIN_BIT_POS - 1)

    #     self.byte_frame.append(flags.to_bytes(1, byteorder='big'))



    #     #+ list(dst_port.to_bytes(2, byteorder='big'))

    #     self.src_ip = src_ip
    #     self.dst_ip = dst_ip
    #     self.src_port = src_port
    #     self.dst_port = dst_port

class SlidingWindowProtocol:

    # Method doesnt check the ID maximum or ID uniqueness!    
    def push(self, ID: int) -> bool:
        ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=1)

        #We have reached the limit!
        if len(self.__frames) == self.__window_limit:
            return False
        
        self.__frames.append(ID)
        return True

    def top(self):
        if len(self.__frames) == 0:
            return -1
        
        return self.__frames[len(self.__frames) - 1]

    def __init__(self, __window_limit: int = 5) -> None:
        ExceptionHandler.check_comp(obj=__window_limit, name="__window_limit", type=int, min=0)
        
        self.__window_limit: int = __window_limit
        self.__frames: List[int] = []
        #self.__frames = []

class Communication:
    
    def accept(self, header : Header):
        if(self.state == CommState.COMPLETE):
            raise TypeError("Communication already complete!")

        flags = header.byte_frame[6]

        #Handling SYN
        if (flags >> 7) & 1:
                if self.__state != CommState.UNITIATED:
                    raise ValueError("Communication is not in unitiated state!")
                


        # if (header.get_src_ip() != self.src_ip or header.get_dst_ip() != self.dst_ip) and (
        #     header.get_src_ip() != self.dst_ip or header.get_dst_ip() != self.src_ip):
        #     raise ValueError("Invalid IP for this communication!")
        
        # frame_len = len(self.frames)
        # #Handling SYN
        # if bin(header.get_flags)[2] and self.state == CommState.UNITIATED and frame_len == 0:
        #     self.frames.append(header)
        # #Handling SYN+ACK
        # elif bin(header.get_flags)[2] and bin(header.get_flags())[3] and self.state == CommState.UNITIATED and frame_len == 1:
        #     self.frames.append(header)
        # #Handling ACK
        # elif bin(header.get_flags)[2] and bin(header.get_flags())[3] == 0 and self.state == CommState.UNITIATED and frame_len == 2:
        #     self.frames.append(header)
        #     self.state == CommState.INITIATED
        # #Handling FIN
        # #Not yet implemented
        # elif bin(header.get_flags())[4]:
        #     pass
    
        
        #if bin(header[12])

    def __init__(self) -> None:
        # self.src_ip = src_ip
        # self.dst_ip = dst_ip
        self.__state = CommState.UNITIATED
        self.__frames = []