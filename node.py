import socket, threading, time, math, os

from exceptions import InvalidCommStateError, IllegalServerState
from network_utils import *
from utils import ExceptionHandler
from typing import List

class Node():
    __PORT_MIN: int = 0
    __PORT_MAX: int = 0
    __ID_MIN: int = 1
    __ID_MAX: int = 16777216
    
    def __get_ID(self) -> int:
        cur_ID = self.__ID

        # the capacity was reached, need to reset it!
        if self.__ID == self.__ID_MAX - 1:
            self.__ID = 0

        self.__ID += 1
        return cur_ID

    def __restart_ID(self) -> int:
        self.__ID = 1

    def set_port(self, port : int) -> None:
        if self.__comm_initated:
            raise InvalidCommStateError("You must close the communication before changing the port!")

        ExceptionHandler.check_comp(obj=port, name="port", type=int, min=self.__PORT_MIN, max=self.__PORT_MAX)

        if self.__running:
            with self.__lock:
                self.__sock.close()
                self.__configure_socket(self.__ip_addr, port=port)

        self.__port = port
        print(f"New port: {port}")

    def get_port(self) -> int:
        return self.__port

    def __configure_socket(self, ip : IPv4, port : int, timeout: float = 1):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((ip.get_str(), port))
        self.__sock.settimeout(timeout)

    def set_ip(self, ip_addr: IPv4) -> None:
        if self.__comm_initated:
            raise InvalidCommStateError("You must close the communication before changing the IP!")
        
        ExceptionHandler.check_comp(obj=ip_addr, name="ip_addr", type=IPv4)
        
        if self.__running:
            with self.__lock:
                self.__sock.close()
                self.__configure_socket(ip_addr, self.__port)

        self.__ip_addr = ip_addr
        print(f"New IP: {self.__ip_addr.get_str()}")

    def get_ip(self) -> str:
        return self.__ip_addr.get_str()
    
    def set_input_size(self, size: int) -> None:
        if not self.__comm_initated:
            raise InvalidCommStateError("Communication not initiated!")
        
        ExceptionHandler.check_comp(obj=size, name="size", type=int, min=1)

        request = Frame(ID=self.__get_ID(), target=size, SET=True)
        self.send_and_wait(frame=request)

        self.__max_input_size = size

        print(f"New input size: {self.__max_input_size}")

    def __set_output_size(self, size: int) -> None:
        ExceptionHandler.check_comp(obj=size, name="size", type=int, min=1)
        self.__max_output_size = size

        print(f"New output size: {self.__max_input_size}")


    def get_input_size(self) -> int:
        return self.__max_input_size

    def get_output_size(self) -> int:
        if self.__max_output_size is None:
            return "Not set"

        return self.__max_output_size

    def print_role(self):
        if self.__is_sender:
            print("Assigned role: Sender")
        else:
            print("Assigned role: Receiver")

    def __swap_roles(self):
        if self.__is_sender:
            self.__is_sender = False
        else:
            self.__is_sender = True

    def __print_msg(self, msg: str, size: int):
        print(f"Content: \"{msg}\"")
        print(f"Complete size: {size}")

    def __print_file_data(self, path: str, size: int):
        print(f"File path: {path}")
        print(f"Complete size: {size}")


    def swap_roles(self):
        print("Swapping the roles... ", end=" ")

        if self.__is_sender == None:
            raise InvalidCommStateError("No role assigned! Initiate a communication for this.")

        swapper = Frame(ID=self.__get_ID(), SET=True)

        with self.__lock:
            self.__sock.settimeout(0.5)
            self.__sock.sendto(swapper.byte_frame, self.__node_2)

        self.__unresponded_ARQ.push(swapper)

    def start_comm(self, ip: str, port: int, requested: bool = False, interval=1.5) -> bool:
        print("Initiating communication...", end=" ")

        if not self.__running:
            print("Server not running! Launch it first.")
            return

        if self.__comm_initated:
            print("Communication already initiated!")
            return False

        if not Port.is_udp(port):
            raise ValueError("Invalid value for UDP port!")
        
        self.__node_2 = (ip, port)
        self.__unresponded_ARQ = KeepRespondedSlidingWindow(socket=self.__sock, node_2=self.__node_2, lock=self.__lock)
        
        if requested:
            initializer = Frame(ID=self.__get_ID(), target=self.__max_input_size, SYN=True)

            with self.__lock:
                self.__sock.sendto(initializer.byte_frame, self.__node_2)
   
            self.__comm_requested = True
            self.__unresponded_ARQ.push(initializer)

        time.sleep(interval)

        if not self.__comm_initated:
            self.__comm_requested = False
            raise TimeoutError("Communication inititation was unsuccessful! There was no response!")

        self.__unresponded_ARQ.keep_responded()
        
        if not self.__is_keeping_alive:
            print("Starting the keep-alive process...", end= " ")

            self.__keep_alive_thread = threading.Thread(target=self.__send_control_messages)
            self.__keep_alive_thread.start()
            self.__is_keeping_alive = True

            print("Success!")


        print("Communication initiated successfully!")
        return True

    def __configure_comm(self, is_sender: bool) -> None:
        self.__comm_requested = False
        self.__comm_initated = True
        self.__is_sender = is_sender

        print("Connection configured!")
        self.print_role()

    def __terminate_comm(self) -> None:
        self.__comm_requested = False
        self.__comm_initated = False
        self.__is_sender = None

    def __extract_file_name(self, payload: bytearray) -> str:
        name = ""
        suffix = False

        for char_i in payload:
            char = chr(char_i)

            if char == ".":
                suffix = True
            
            if char == ' ' and suffix:
                break

            name += char
        
        return name


    def __listen(self, wait_when_data: int = 0.1, wait_when_no_data: int = 0.5):

        while not self.__listen_stop_signal.is_set():
        
            try:
                data = None
                with self.__lock:
                    data, self.__node_2 = self.__sock.recvfrom(Frame.get_header_len() + self.__max_input_size)

                if not data:
                    time.sleep(wait_when_no_data)
                    continue

                #print("")

                frame = Frame(frame=bytearray(data))

                #let's first check the FCS
                if frame.get_crc_dec() != frame.calculate_FCS():
                    print("Corrupted frame detected! Sending NACK response...")
    
                    NACK_response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), NACK=True)
                    with self.__lock:
                        self.__sock.sendto(NACK_response.byte_frame, self.__node_2)

                elif frame.is_control():
                    #print("Checking a control message...")
                    response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)

                    with self.__lock:
                        self.__sock.sendto(response.byte_frame, self.__node_2)  

                elif frame.is_syn():
                    print("Checking a SYN request...", end=" ")
                    response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)
                    self.__max_output_size = frame.get_target_dec()

                    with self.__lock:
                        self.__sock.sendto(response.byte_frame, self.__node_2)

                    if not self.__comm_requested:
                        response = Frame(ID=self.__get_ID(), target=self.get_input_size(), SYN=True)
                        
                        thread = threading.Thread(target=self.start_comm, args=(self.__node_2[0], self.__node_2[1]))
                        thread.start()

                        self.send_and_wait(response)

                    else:
                        self.__configure_comm(is_sender=True)

                elif frame.is_ack():
                    #print("Checking an acknowledgment...", end=" ")
                    # let's first check all the control messages
                    if self.__KEEP_ALIVE_ARQ.respond(frame.get_target_dec()):
                        with self.__comm_force_lock:
                            self.__can_force_to_stop = False

                        #print("A control message was responded!")
                        continue
                    
                    responded_f = self.__unresponded_ARQ.respond(frame.get_target_dec())

                    if not responded_f:
                        print("Unable to find the frame!")
                        continue

                    if responded_f.is_syn() and not self.__comm_requested:
                        self.__configure_comm(is_sender=False)

                    elif responded_f.is_fin() and not self.__comm_requested:
                        self.__terminate_comm()

                    elif responded_f.is_set() and responded_f.get_target_dec() == 0:
                        self.__swap_roles()
                        print("Role swapped.")
                        self.print_role()
                    elif responded_f.is_set() and responded_f.get_target_dec() > 0:
                        print("Fragment size modified successfully!.")
                    
                    print(f"Unresponded frame {responded_f.get_ID_dec()} responded!")
                
                elif frame.is_fin():
                    print("Checking a FIN request...", end=" ")
        

                    if not self.__comm_requested:
                        response = Frame(ID=self.__get_ID(), FIN=True)
                        self.send_and_wait(response)

                        thread = threading.Thread(target=self.finish_comm)
                        thread.start()

                    else:
                        response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)
                        self.send_and_wait(response)

                        self.__comm_initated = False
                        self.__is_sender = None

                elif frame.is_set() and frame.get_target_dec() == 0 and not frame.contains_payload():
                    print("Processing a SWAP request...", end=" ")
                    response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)
                    
                    with self.__lock:
                        self.__sock.sendto(response.byte_frame, self.__node_2)
                    
                    self.__swap_roles()
                    print("Role swapped.")
                    self.print_role()

                elif frame.is_set() and frame.get_target_dec() > 0 and not frame.contains_payload():
                    print("Getting a request to change the maximum output size for the second site. Processing...")

                    self.__set_output_size(frame.get_target_dec())

                    print("Success. Sending response...")
                    response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)

                    with self.__lock:
                        self.__sock.sendto(response.byte_frame, self.__node_2)

                elif frame.is_quit():
                    print("Getting a quit notification. The other site quit the communication forcefully!")

                elif FragmentSequence.is_fragment(frame): 
                    
                    print("Fragment detected. Processing...")
                    completed_seq = self.__incomplete_frags.push( frame )

                    if completed_seq:
                        print("Sequence has been completed! Processing...")
                        if not completed_seq.root.frame.is_set():
                            msg: str = ""
                            payload_len: int = 0

                            cur = completed_seq.root

                            while cur:
                                msg += cur.frame.get_payload_str()
                                payload_len += len(cur.frame.get_payload())
                                cur = cur.next


                            self.__print_msg(msg=msg, size=payload_len)
                        elif completed_seq.root.frame.is_set():
                        
                            #root_payload = completed_seq.root.frame.get_payload()
                            file_name = self.__extract_file_name(payload=completed_seq.root.frame.get_payload())
                            # suffix = False

                            # for char_i in root_payload:
                            #     char = chr(char_i)

                            #     if char == ".":
                            #         suffix = True
                                
                            #     if char == ' ' and suffix:
                            #         break

                            #     file_name += char

                            with open(file_name, 'wb') as file:
                                payload_len: int = 0
                                frag_count: int = 0

                                cur = completed_seq.root

                                while cur:
                                    print(f"Fragment {cur.frame.get_ID_dec()}: {len(cur.frame.get_payload())}")
                                    
                                    if frag_count == 0 and payload_len == 0:
                                        file.write(cur.frame.get_payload()[len(file_name) :])
                                    else:
                                        file.write(cur.frame.get_payload())

                                    payload_len += len(cur.frame.get_payload())
                                    frag_count += 1
                                    cur = cur.next

                                self.__print_file_data(path=os.path.abspath(file.name),
                                                    size= payload_len)
                                
                                print(f"Fragments: {frag_count}")
                        
                    print("Sending an ACK message...")
                    response = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)
                    
                    with self.__lock:
                        self.__sock.sendto(response.byte_frame, self.__node_2)

                #Handling NACK messages here
                elif frame.is_nack() and frame.get_target_dec() > 0:
                    print("Received a NACK message. Resending the message...", end=" ")

                    #Resending the frame
                    unresponded_f = self.__unresponded_ARQ.get(frame.get_target_dec())

                    with self.__lock:
                            self.__sock.sendto(unresponded_f.byte_frame, self.__node_2)

                    print("The message sent successfully!")

                elif not frame.is_set():
                    print("A message received! Processing...")
                    
                    respons: Frame = Frame(ID=self.__get_ID(), target=frame.get_ID_dec(), ACK=True)

                    with self.__lock:
                        self.__sock.sendto(respons.byte_frame, self.__node_2)

                    self.__print_msg(msg=frame.get_payload_str(), size=len(frame.get_payload()))


                elif frame.is_set():
                    print("File data received! Processing...")

                    
                    with open(self.__extract_file_name(payload=frame.get_payload()), 'w') as file:                            
                        file.write(frame.get_payload_str())
                        self.__print_file_data(os.path.abspath(file.name), len(frame.get_payload()))
                else:
                    print("Unknown header structure! Sending error...")

                #print("")

                time.sleep(wait_when_data)
                data = None
            # else:
            #     time.sleep(wait_when_no_data)
            except ConnectionResetError:
                print("There is no other node in the network!")
                pass
            except socket.timeout:
                pass

        print("Node has stopped listening!")

    def __send_control_messages(self, timeout: float = 1.5, sleep: int = 1):
        header = Frame(ID=self.__get_ID(), CONTROL=True)
        self.__KEEP_ALIVE_ARQ.push(header.get_ID_dec())

        with self.__lock:
            try:
                self.__sock.settimeout(timeout)
                self.__sock.sendto(header.byte_frame, self.__node_2)
            except TimeoutError:
                pass

        while not self.__keep_alive_stop_signal.is_set():
            time.sleep(sleep)
            ARQ_top = self.__KEEP_ALIVE_ARQ.top()

            header = None

            if ARQ_top == -1:
                header = Frame(ID=self.__get_ID(), CONTROL=True)
            else:    
                header = Frame(ID=self.__get_ID(), target=self.__KEEP_ALIVE_ARQ.top(), CONTROL=True)

            if not self.__KEEP_ALIVE_ARQ.push(header.get_ID_dec()):
                print("The window buffer is full. You can now force communication to terminate!")
                with self.__comm_force_lock:
                    self.__can_force_to_stop = True   

            with self.__lock:
                try:
                    self.__sock.settimeout(timeout)
                    self.__sock.sendto(header.byte_frame, self.__node_2)
                except TimeoutError:
                    pass

        print("Node has stopped checking!")


    # def keep_alive(self):
    #     print("Launching connectivity check...", end=" ")

    #     if not self.__running:
    #         raise IllegalServerState("Server not running! Launch it first.")

    #     if not self.__comm_initated:
    #         raise InvalidCommStateError("Communication not initiated!")

    #     self.__keep_alive_thread = threading.Thread(target=self.__send_control_messages)
    #     self.__keep_alive_thread.start()
    #     self.__is_keeping_alive = True

    #     print("Connectivity is being checked!")

    def stop_keep_alive(self):
        print("Stopping the keep-alive process...", end=" ")

        if not self.__is_keeping_alive:
            raise IllegalServerState("The server is not sending controlling messages!")
        
        self.__keep_alive_stop_signal.set()
        self.__keep_alive_thread.join()

        self.__is_keeping_alive = False
        self.__keep_alive_stop_signal.clear()
        self.__KEEP_ALIVE_ARQ.clear()

        print("Terminated successfully!")
    

    def is_running(self) -> bool:
        return self.__running

    def start(self):
        print("Launching node...", end = " ")

        if self.__running:
            print("Node is already listening!")
            return
        
        try:
            self.__configure_socket(self.__ip_addr, self.__port)
        except OSError as e:
            print(e)
            print("Changing the port to next possible one...")
            self.set_port(self.get_port() + 1)
            print("Retrying...")
            return self.start()
        

        print("\nStarting the listening process...", end=" ")
        
        self.__listen_thread = threading.Thread(target=self.__listen)
        self.__listen_thread.start()

        print("Success!")

        self.__running = True

        print("Node configured succesfully!")

    def quit(self):
        print("Closing node...")

        if not self.__running:
            print("Node is not running! Launch it first.")
            return
        
        if self.__comm_initated:
            print("Initiated communication! Finish it before shutting the server down.")
            return

        # Signalling the Reader thread to stop reading
        #self.__keep_alive_stop_signal.set()
        self.__listen_stop_signal.set()

        # Here the server is attempted to be closed
        # Waiting for the Reader to stop reading
        self.__listen_thread.join()

        # Here the server is successfully closed
    
        self.__sock.close()
        self.__running = False
        self.__listen_stop_signal.clear()

        print("Node closed successfully!")

    def finish_comm(self, requested: bool=False):
        print("Finishing the communication... ", end=" ")

        if not self.__comm_initated:
            raise InvalidCommStateError("There is no active communication to close!")

        if requested:
            self.__comm_requested = True
            terminator = Frame(ID=self.__get_ID(), FIN=True)
            self.send_and_wait(frame=terminator)

        time.sleep(1)
        while self.__comm_initated:
            print("Communication is still open...")
            time.sleep(1)

        print("")
        if self.__is_keeping_alive:
            self.stop_keep_alive()
            self.__is_keeping_alive = False

        self.__unresponded_ARQ.stop()
        self.__unresponded_ARQ.clear()
        self.__restart_ID()

        print("Communication closed successfully!")
    
    def force_finish_comm(self):
        print("Forcing the communication to terminate...", end=" ")

        if not self.__comm_initated:
            raise InvalidCommStateError("There is no active communication to close!")

        with self.__comm_force_lock:
            if not self.__can_force_to_stop:
                raise InvalidCommStateError("Communication can't be now closed forcefully!")
            

        terminator = Frame(ID=self.__get_ID(), QUIT=True)

        with self.__lock:
            self.__sock.sendto(terminator.byte_frame, self.__node_2)

        # while self.__comm_initated:
        #     time.sleep(1)

        if self.__is_keeping_alive:
            print("\nStopping keep-alive process...", end=" ")
            self.stop_keep_alive()
            self.__is_keeping_alive = False
        
        self.__comm_initated = False
        self.__unresponded_ARQ.stop()
        self.__unresponded_ARQ.clear()
        self.__restart_ID()

        print("Communication closed successfully!")    

    def send_and_wait(self, frame: Frame):
        while not self.__unresponded_ARQ.push(frame):
            print("The buffer with unresponded frames is full. Waiting...")
            time.sleep(0.1)

        with self.__lock:
            self.__sock.sendto(frame.byte_frame, self.__node_2)

    def send_message(self, message : str):
        if not self.__is_sender:
            raise IllegalServerState("The node is not a sender! Send SWAP request to the other node.")
        
        print(f"Sending message: {message}...", end=" ")

        if not self.__running:
            raise IllegalServerState("Server not running! Launch it first.")
        
        if not self.__comm_initated:
            raise InvalidCommStateError("Communication not initiated!")

        payload_size = len(message.encode(encoding='utf-8'))
        print(f"\nComplete size: {payload_size}")

        if payload_size <= self.__max_output_size:
            print("Message size not beyond the limit. No fragmentation needed!")

            frame = Frame(self.__get_ID(), target=0, payload=message)
            self.send_and_wait(frame = frame)
            
        else:
            print("Message size beyond the limit. Fragmentation needed!")

            cur = 0
            frag_count = math.ceil(payload_size/self.__max_output_size)
            prev_frame_ID = 0
            msg_len = len(message)

            print(f"Sending {frag_count} packets!")
            for frag_i in range(0, frag_count):
                end = cur + self.__max_output_size

                if end > msg_len:
                    end = msg_len

                frame = Frame(self.__get_ID(), target=prev_frame_ID, MORE_FRAGS=True, payload=message[cur:end])
            
                if frag_i == frag_count - 1:
                    frame.set_more_frags(False)

                prev_frame_ID = frame.get_ID_dec()
                cur += self.__max_output_size
                self.send_and_wait(frame=frame)
        
        print("Message sent!")

    def send_file(self, f_path: str, name: str = None):
        if not self.__is_sender:
            raise IllegalServerState("The node is not a sender! Send SWAP request to the other node.")
        
        print("Sending file data...", end=" ")

        if not self.is_running:
            raise IllegalServerState("Server not running! Launch it first.")
        
        if not self.__comm_initated:
            raise InvalidCommStateError("Communication not initiated!")

        print(f_path)
        print(name)

        if not name:
            name = os.path.basename(f_path)

        fragments: List[Frame] = []
        frag_count = 0
        data_count = 0

        try:
            with open(f_path, 'rb') as file:
                file_name = bytes(name + ' ', encoding='utf-8')
                data = file.read(self.__max_output_size - len(file_name))
                prev: int = -1
                
                while data:
                    data_frame = None

                    if data_count == 0 and frag_count == 0:
                        data_frame = Frame(ID=self.__get_ID(), payload=bytearray(file_name + data), SET=True, MORE_FRAGS=True)
                    else:
                        data_frame = Frame(ID=self.__get_ID(), target=prev, payload=bytearray(data), SET=True, MORE_FRAGS=True)

                    #data_frame.print_rep()

                    # if prev:
                    #     data_frame.set_target(prev.get_ID_dec())
                    
                    prev = data_frame.get_ID_dec()
                    fragments.append(data_frame)
                    data = file.read(self.__max_output_size)
                    data_count += len(data_frame.get_payload())
                    frag_count += 1
        except FileNotFoundError:
            print("The input file is non-existent. Creating a new one...")
            with open(f_path, 'w'):
                pass
            return self.send_file(f_path=f_path, name=name)
        

        if len(fragments) == 0:
            print("Input file is empty!")
            return
        
        fragments[len(fragments) - 1].set_more_frags(False)
        

        for frag in fragments:
            self.send_and_wait(frame=frag)
            print(f"Fragment {frag.get_ID_dec()}: {len(frag.get_payload())}")

        self.__print_file_data(os.path.abspath(f_path), data_count)

        print(f"Fragments: {frag_count}")
        print("File data sent successfully!")

    # ------------ CONSTRUCTOR ------------- #

    def __init__(self, port: int = 5000, ip_addr : str = "127.0.0.1", port_2 : int = None, ip_addr_2: str = "127.0.0.1",
                 max_input_size: int = 1000, input_file_path: str = './input_file.txt', output_file_path: str = './output_file.txt'):
                 #is_sender : bool = True):
        print("Configuring node...", end=" ")

        ExceptionHandler.check_comp(obj=ip_addr, name="ip_addr", type=str)
        ExceptionHandler.check_comp(obj=port, name="port", type=int)
        ExceptionHandler.check_comp(obj=ip_addr_2, name="ip_addr_2", type=str)
        if port_2:
            ExceptionHandler.check_comp(obj=port_2, name="port_2", type=int)

        if not Port.is_udp(port) or (port_2 and not Port.is_udp(port_2)):
            raise ValueError("Invalid value for udp port!")

        # ------------ SERVER CONFIGURATON -------------
        self.__is_sender: bool = None
        self.__running: bool = False
        self.__is_keeping_alive: bool = False
        self.__comm_requested: bool = False
        self.__comm_initated: bool = False
        self.__can_force_to_stop: bool = False

        self.__port: int = port
        self.__ip_addr: IPv4 = IPv4(ip_addr)
        self.__node_2: tuple = None
        self.__max_input_size: int = max_input_size
        self.__max_output_size: int = None
        # self.__input_file: str = input_file_path
        # self.__output_file: str = output_file_path
     
        # ---------- CONFIGURATION OF THREADS -----------
        self.__lock = threading.Lock()
        self.__comm_force_lock = threading.Lock()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.__listen_stop_signal = threading.Event()
        self.__listen_thread: threading.Thread = threading.Thread(target=self.__listen)
        
        self.__keep_alive_stop_signal = threading.Event()
        self.__keep_alive_thread: threading.Thread = threading.Thread(target=self.__send_control_messages)

        self.__ID: int = self.__ID_MIN

        # ---------- ARQ & FRAGMENT MANAGEMENT -----------
        self.__KEEP_ALIVE_ARQ: KeepAliveSlidingWindow = KeepAliveSlidingWindow()
        self.__unresponded_ARQ: KeepRespondedSlidingWindow = None
        self.__incomplete_frags: FragmentSequenceProcessor = FragmentSequenceProcessor()

        print("Node successfully configured!")

def main():
    node = Node()

    while(1):
        print("")
        command = input("Enter command: ")
        print("")
        args = command.split(' ', 1)

        try:
            match(args[0]):
            
                    case "--ip":
                        if len(args) == 1:
                            print(node.get_ip())
                        elif len(args) == 2:
                            node.set_ip(IPv4(ip_str=args[1]))
                        else:
                            print("Invalid command structure. See help for more information.")
                        
                        continue
                
                    case "--port":
                        if len(args) == 1:
                            print(node.get_port())
                        elif len(args) == 2:
                            node.set_port(port=int(args[1]))
                        else:
                            print("Invalid command structure. See help for more information.")

                        continue
                    
                    case "--input_size":
                        if len(args) == 1:
                            print(node.get_input_size())
                        elif len(args) == 2:
                            node.set_input_size(int(args[1]))
                        else:
                            print("Invalid command structure. See help for more information.")

                        continue
                    
                    case "--output_size":
                        if len(args) == 1:
                            print(node.get_output_size())
                        else:
                            print("Invalid command structure. See help for more information.")
                        
                        continue
                
                    case "-s":
                        
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                        
                        else:
                            node.start()

                        continue
                    
                    case "-c":
                        if len(args) > 1:
                            args.extend(args[1].split(' '))
                            args.remove(args[1])

                        if len(args) != 3:
                            print("Invalid command structure. See help for more information.")
                        else:
                            node.start_comm(args[1], int(args[2]), requested=True)

                        continue
                    
                    case "-tc":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                        else:
                            node.finish_comm(requested=True)

                        continue
                    
                    case "-ftc":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                        else:
                            node.force_finish_comm()

                        continue
                
                    case "-m":
                        if len(args) < 2:
                            print("Invalid command structure. See help for more information.")
                        else:
                            node.send_message(message=args[1])                        

                        continue
                    
                    case "-f":

                        if len(args) < 2:
                            print("Invalid command structure. See help for more information.")
                            continue

                        args.extend(args[1].split(' '))
                        args.remove(args[1])

                        if len(args) == 2:                    
                            node.send_file(f_path=args[1])
                        elif len(args) == 3:
                            node.send_file(f_path=args[1], name=args[2])
         

                        continue

                    case "--swap":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                        else:
                            node.swap_roles()

                        continue

                    case "--quit_server":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                        else:
                            node.quit()

                        continue
                
                    case "--terminate":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                            continue
                        elif node.is_running():
                            print("Server still running! Quit it first in order to terminate the program.")
                            continue
                        
                        break
                    case "-h":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                        else:
                            print ("""List of supported commands:
    
    --set_ip <value>
    --get_ip
    --set_port <value>
    --get_port
    -s: starts a server
    -m: sends a message
    -q: quits a server""")
                        continue
            
            print("Unknown command. Use \"-h\" for more information.")
        except Exception as e:
            print(e)
            

    print("Program terminated successfully!")

if __name__ == "__main__":
    main()
    