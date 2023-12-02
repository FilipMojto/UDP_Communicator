import crcmod, threading, socket, time
from typing import List, Dict

from utils import BitManager, ExceptionHandler

    
class IPv4:
    OCTET_COUNT = 4

    def get_str(self):
        string = ""
        for octet in self.octets:
            string += str(octet)
            string += '.'
        
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

     #header structure:
    #   a) ID
    #   b) Target
    #   c) Flags
    #   d) FCS

    # Flags:
    #   a) SYN
    #   b) ACK
    #   c) NACK
    #   d) FIN
    #   e) CONTROL
    #   f) SET
    #   g) QUIT
    #   h) MORE FRAGS

class Frame:
    ID_MIN = 1
    ID_MAX = 65536

    ID_START: int = 0
    ID_END: int = ID_START + 2
    TARGET_START: int = ID_END + 1
    TARGET_END: int = TARGET_START + 2
    FLAG_INDEX = TARGET_END + 1
    PAYLOAD_INDEX = FLAG_INDEX + 1

    __CRC_LENGTH = 2
    __HEADER_LENGTH = PAYLOAD_INDEX + __CRC_LENGTH

    SYN_BIT_POS = 7
    ACK_BIT_POS = SYN_BIT_POS - 1
    NACK_BIT_POS = ACK_BIT_POS - 1
    FIN_BIT_POS = NACK_BIT_POS - 1
    CONTROL_BIT_POS = FIN_BIT_POS - 1
    SET_BIT_POS = CONTROL_BIT_POS - 1
    QUIT_BIT_POS = SET_BIT_POS - 1
    MORE_FRAGS_POS = QUIT_BIT_POS - 1

    def frame(self):
        
        print("")

        print(f"ID: {self.get_ID_dec()}")
        print(f"Target: {self.get_target_dec()}")

        print(f"SYN flag: {self.is_syn()}")
        print(f"ACK flag: {self.is_ack()}")
        print(f"NACK flag: {self.is_nack()}")
        print(f"FIN flag: {self.is_fin()}")
        print(f"CNTRL flag: {self.is_control()}")
        print(f"SET flag: {self.is_set()}")
        print(f"QUIT flag: {self.is_quit()}")
        print(f"MRFRGS flag: {self.is_more_frags()}")
        
        print(f"FCS: {self.calculate_FCS()}")


    @staticmethod
    def get_header_len() -> int:
        return Frame.__HEADER_LENGTH
    
    @staticmethod
    def verify_frame_struct(frame : bytearray) -> bool:
        ExceptionHandler.check_comp(obj=frame, name="frame", type=bytearray)

        if len(frame) < Frame.__HEADER_LENGTH:
            raise ValueError(f"Invalid minimum frame size for parameter frame! The required size: {Frame.__HEADER_LENGTH}")
        
   
    def get_ID(self) -> bytearray:
        return self.byte_frame[Frame.ID_START:Frame.ID_END + 1]
    
    def get_ID_dec(self) -> int:
        return int.from_bytes(self.get_ID(), byteorder='big')
    
    def get_target(self) -> bytearray:
        return self.byte_frame[Frame.TARGET_START:Frame.TARGET_END + 1]

    def get_target_dec(self) -> int:
        return int.from_bytes(self.get_target(), byteorder='big')

    def set_target(self, target: int) -> None:
        ExceptionHandler.check_comp(obj=target, name="target", type=int, min=0)
        target_b = target.to_bytes(2, byteorder="big")
        self.byte_frame[Frame.TARGET_START] = target_b[0]
        self.byte_frame[Frame.TARGET_END] = target_b[1]

        self.__recalculate_csc()
    
    def is_syn(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[Frame.FLAG_INDEX], Frame.SYN_BIT_POS)

    def set_syn(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.SYN_BIT_POS, value=flag)
        self.__recalculate_csc()

    def is_ack(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[Frame.FLAG_INDEX], Frame.ACK_BIT_POS)
    
    def set_ack(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.ACK_BIT_POS, value=flag)
        self.__recalculate_csc()

    def is_nack(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[self.FLAG_INDEX], Frame.NACK_BIT_POS)

    def set_nack(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.NACK_BIT_POS, value=flag)
        self.__recalculate_csc()

    def is_fin(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[self.FLAG_INDEX], Frame.FIN_BIT_POS)

    def set_fin(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.FIN_BIT_POS, value=flag)
        self.__recalculate_csc()

    def is_control(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[self.FLAG_INDEX], Frame.CONTROL_BIT_POS)
    
    def set_control(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.CONTROL_BIT_POS, value=flag)
        self.__recalculate_csc()

    def is_set(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[self.FLAG_INDEX], Frame.SET_BIT_POS)
    
    def set_set(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.SET_BIT_POS, value=flag)
        self.__recalculate_csc()

    def is_quit(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[self.FLAG_INDEX], Frame.QUIT_BIT_POS)
    
    def set_quit(self, flag: bool) -> None:
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.QUIT_BIT_POS, value=flag)
        self.__recalculate_csc()


    def is_more_frags(self) -> bool:
        return BitManager.is_bit_set(self.byte_frame[self.FLAG_INDEX], Frame.MORE_FRAGS_POS)
    
    
    def set_more_frags(self, flag : bool):
        self.byte_frame[self.FLAG_INDEX] = BitManager.set_bit(byte=self.byte_frame[self.FLAG_INDEX], position=Frame.MORE_FRAGS_POS, value=flag)
        self.__recalculate_csc()

    def contains_payload(self) -> bool:
        if len(self.byte_frame) > self.__HEADER_LENGTH:
            return True
        
        return False
    
    def get_payload(self, start: int = 0, end: int = 0) -> bytearray:
        if not self.contains_payload():
            return None

        if end == 0:
            end = len(self.byte_frame) - self.__CRC_LENGTH - self.PAYLOAD_INDEX

        if start > end:
            raise ValueError("Invalid values for parameters start and end!")
        
        return self.byte_frame[self.PAYLOAD_INDEX + start : self.PAYLOAD_INDEX + end]

    def get_payload_str(self) -> str:
        if not self.contains_payload():
            return None

        return self.byte_frame[self.PAYLOAD_INDEX : len(self.byte_frame) - self.__CRC_LENGTH].decode(encoding="utf-8")
    
    def get_crc(self) -> bytearray:
        return self.byte_frame[len(self.byte_frame) - self.__CRC_LENGTH: len(self.byte_frame)]

    def get_crc_dec(self) -> int:
        return int.from_bytes(self.get_crc(), byteorder='big')

    def calculate_FCS(self) -> int:
        return self.__crc16(self.byte_frame[0: len(self.byte_frame) - self.__CRC_LENGTH])

    def __recalculate_csc(self):
        length = len(self.byte_frame)
        crc = self.__crc16(self.byte_frame[0 : length - self.__CRC_LENGTH]).to_bytes(self.__CRC_LENGTH, byteorder='big')

        for i in range(0, self.__CRC_LENGTH):
            self.byte_frame[length - self.__CRC_LENGTH + i] = crc[i]

        #self.byte_frame[length - 1] = crc[1]

    def __init__(self, ID : int = 0, target : int = 0, #type : FrameType = FrameType.NO_DATA,
                 SYN: bool=False, ACK: bool=False, NACK: bool=False, FIN: bool=False, CONTROL: bool=False, SET: bool=False, QUIT: bool=False,
                 MORE_FRAGS: bool=False, frame: bytearray = None, payload = None) -> None:

        if not frame:
            ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=self.ID_MIN, max=Frame.ID_MAX)
            ExceptionHandler.check_comp(obj=target, name="target", type=int, min=0, max=Frame.ID_MAX)

        self.__crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, xorOut=0xFFFF)

        if frame:
            Frame.verify_frame_struct(frame=frame)
            
            self.byte_frame = frame
            return
        
        self.byte_frame = bytearray()
        
        ID_b = ID.to_bytes(self.ID_END - self.ID_START + 1, byteorder="big")

        for i in range(0, len(ID_b)):
            self.byte_frame.append(ID_b[i])

        target_b = target.to_bytes(self.TARGET_END - self.TARGET_START + 1, byteorder="big")

        for i in range(0, len(target_b)):
            self.byte_frame.append(target_b[i])

        #self.byte_frame.append(target_b[0])
        #self.byte_frame.append(target_b[1])
        
        flags = 0b00000000

        if SYN:
            flags |= (1 << self.SYN_BIT_POS)
        if ACK:
            flags |= (1 << self.ACK_BIT_POS)
        if NACK:
            flags |= (1 << self.NACK_BIT_POS)
        if FIN:
            flags |= (1 << self.FIN_BIT_POS)
        if CONTROL:
            flags |= (1 << self.CONTROL_BIT_POS)
        if SET:
            flags |= (1 << self.SET_BIT_POS)
        if QUIT:
            flags |= (1 << self.QUIT_BIT_POS)
        if MORE_FRAGS:
            flags |= (1 << self.MORE_FRAGS_POS)

        self.byte_frame.append(flags)

        if payload:
            if isinstance(payload, str):
                self.byte_frame.extend(payload.encode('utf-8'))
            elif isinstance(payload, bytearray):
                self.byte_frame.extend(payload)

        
        self.byte_frame += self.__crc16(self.byte_frame).to_bytes(self.__CRC_LENGTH, byteorder='big')

class KeepRespondedSlidingWindow:
    
    def __init__(self, socket: socket.socket, node_2: tuple, lock: threading.Lock, window_limit: int = 7) -> None:
        ExceptionHandler.check_comp(obj=window_limit, name="window_limit", type=int, min=0)
        
        self.__window_limit: int = window_limit
        self.__frames: List[Dict[Frame, int]] = []
        self.__sock = socket
        self.__node_2 = node_2
    
        self.__lock: threading.Lock = lock
        self.__access_lock: threading.Lock = threading.Lock()
        self.__keeping_responded = False
        self.__stop_signal: threading.Event = threading.Event()

    def __resend_frames(self, sleep: int = 3):

        while not self.__stop_signal.is_set():
            
            with self.__access_lock:

                for frame in self.__frames:
                    if frame['count'] == 0:
                        print("Unresponded frame detected! Resending... ")
                        
                        with self.__lock:
                            self.__sock.sendto(frame['frame'].byte_frame, self.__node_2)
                    else:
                        frame['count'] -= 1

            
            time.sleep(sleep)

    def keep_responded(self, sleep: int = 3):
        print("Starting the keep-responded process...", end=" ")

        if self.__keeping_responded:
            raise ValueError("Already keeping responded! Stop the process first.")

        self.__thread = threading.Thread(target=self.__resend_frames, args=(sleep,))
        self.__thread.start()
        
        self.__keeping_responded = True
        print("Process started successfully!")

    def stop(self):
        print("Stopping the keep-responded process...", end=" ")

        if not self.__keeping_responded:
            raise ValueError("Not keeping responded! Start the process first!")

        self.__stop_signal.set()
        time.sleep(1)

        self.__thread.join()

        self.__keeping_responded = False
        self.__stop_signal.clear()

        print("Process stopped successfully!")

    def clear(self) -> None:
        with self.__access_lock:
            self.__frames.clear()
   
    def push(self, frame: Frame) -> bool:
        ExceptionHandler.check_comp(obj=frame, name="frame", type=Frame)

        #We have reached the limit!

        with self.__access_lock:
            if len(self.__frames) == self.__window_limit:
                return False
            
            self.__frames.append({'frame': frame,
                                  'count': 3})

        return True

    def get(self, ID: int) -> Frame:
        ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=1)

        with self.__access_lock:
            for frame in self.__frames:
                if frame['frame'].get_ID_dec() == ID:
                    return frame['frame']

        return None

    def respond(self, ID: int) -> Frame:
        ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=1)

        with self.__access_lock:
            for i in range(0, len(self.__frames)):
                if self.__frames[i]['frame'].get_ID_dec() == ID:
                    return self.__frames.pop(i)['frame']
    
        return None

class SequenceNode:
    
    def __init__(self, frame: Frame, prev = None, next = None) -> None:
        self.prev: SequenceNode = prev
        self.next: SequenceNode = next
        self.frame: Frame = frame
        pass

class FragmentSequence:
        
    @staticmethod
    def is_fragment(frame: Frame):
        

        if (frame.is_more_frags() or frame.get_target_dec() > 0) and not (frame.is_syn() or
                                                                            frame.is_fin() or
                                                                            frame.is_control() or
                                                                            frame.is_quit() or
                                                                            frame.is_ack() or
                                                                            frame.is_nack()):
            
            return True
        
        return False

    def __analyze_frag(self, fragment: Frame) -> int:

        if fragment.is_more_frags() and fragment.get_target_dec() == 0:
            self.contains_start = True
        elif not fragment.is_more_frags() and fragment.get_target_dec() > 0:
            self.contains_end = True

        if self.contains_start and self.contains_end:
            self.complete = True

        
    def clear(self):
        self.root = None
        self.last = None
        self.contains_start = False
        self.contains_end = False
        self.complete = False
    
    def is_complete(self) -> bool:
        return self.complete

    def push(self, frame: Frame) -> int:
        frame.frame()

        if not FragmentSequence.is_fragment(frame):
            raise TypeError("Passed frame is not a fragment!")
        
        if not self.root:
            self.root = SequenceNode(frame=frame)
            self.last = self.root
            self.__analyze_frag(frame)
            return 1    

        if self.root.frame.get_target_dec() > 0 and frame.get_ID_dec() == self.root.frame.get_target_dec():
            self.root.prev = SequenceNode(frame=frame, next=self.root)
            self.root = self.root.prev
            self.__analyze_frag(frame)
            return 1

        if frame.get_target_dec() == self.last.frame.get_ID_dec() and self.last.frame.is_more_frags():
            self.last.next = SequenceNode(frame=frame, prev=self.last)
            self.last = self.last.next
            self.__analyze_frag(frame)
            return 1

        return 0
    
    def __init__(self, root: Frame = None) -> None:

        self.contains_start: bool = False
        self.contains_end: bool = False
        self.complete: bool = False

        if root:
            self.root: SequenceNode = SequenceNode(frame=root)
            self.__analyze_frag(root)
        else:    
            self.root: SequenceNode = None

        self.last: SequenceNode = self.root

        

class FragmentSequenceProcessor:

    @staticmethod
    def join(seq_1: FragmentSequence, seq_2: FragmentSequence) -> bool:
        
        if seq_1.root.frame.get_target() == seq_2.last.frame.get_ID_dec():
            seq_1.root.prev = seq_2.last
            seq_1.root = seq_2.root
            return True
        elif seq_2.root.frame.get_target() == seq_1.last.frame.get_ID_dec():
            seq_2.root.prev = seq_1.last
            seq_2.root = seq_1.root
            return True
        
        return False
                
    def push(self, frame: Frame) -> FragmentSequence:
        
        
        #lets check the frame configuration

        for seq in self.__sequences:
            
            if seq.push(frame=frame) == 1:

                if seq.is_complete():
                    completed = seq

                    self.__sequences.remove(seq)

                    return completed
                
                for seq2 in self.__sequences:
                    if seq != seq2 and FragmentSequenceProcessor.join(seq_1=seq, seq_2=seq2):
                        return None

                return None
        else:
            self.__sequences.append( FragmentSequence(root=frame) )    

    def __init__(self) -> None:

        self.__sequences: List[FragmentSequence] = []
        pass





class KeepAliveSlidingWindow:
    
    def __init__(self, window_limit: int = 5) -> None:
        ExceptionHandler.check_comp(obj=window_limit, name="window_limit", type=int, min=0)
        
        self.__window_limit = window_limit
        self.__frames: List[int] = []    

    def clear(self) -> None:
        self.__frames.clear()

    def top(self) -> int:
        if len(self.__frames) == 0:
            return -1
        
        return self.__frames[len(self.__frames) - 1]

    def push(self, ID: int) -> bool:
        ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=1)

        if len(self.__frames) == self.__window_limit:
            return False
        
        self.__frames.append(ID)
        return True

    

    def respond(self, ID: int) -> bool:
        ExceptionHandler.check_comp(obj=ID, name="ID", type=int, min=1)

        try:
            #if the ID was found in the buffer, all ID's are cleared out
            self.__frames.remove(ID)
            self.__frames.clear()
        except ValueError:
            return False
        
        return True