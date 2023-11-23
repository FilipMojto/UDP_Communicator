import socket, threading, time

from network_utils import IPv4, Port, Header, FrameType, SlidingWindowProtocol
from utils import ExceptionHandler


class Node():
    __PORT_MIN: int = 0
    __PORT_MAX: int = 0
    __ID_MAX: int = 65536
    
    def __get_ID(self) -> int:
        cur_ID = self.__ID

        # the capacity was reached, need to reset it!
        if self.__ID == self.__ID_MAX - 1:
            self.__ID = 0

        self.__ID += 1
        return cur_ID

    def set_port(self, port : int) -> None:
        ExceptionHandler.check_comp(obj=port, name="port", type=int, min=self.__PORT_MIN, max=self.__PORT_MAX)

        if self.__running:
            with self.__lock:
                self.__sock.close()

                #self.__sock.bind((self.__ip_addr.get_str(), port))

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
        ExceptionHandler.check_comp(obj=ip_addr, name="ip_addr", type=IPv4)
        
        if self.__running:
            with self.__lock:
                self.__sock.close()
                self.__configure_socket(ip_addr, self.__port)

        self.__ip_addr = ip_addr
        print(f"New IP: {self.__ip_addr.get_str()}")

    def get_ip(self) -> str:
        return self.__ip_addr.get_str()

    def __listen(self):

        while not self.__stop_event.is_set():
            
            try:
                with self.__lock:
                    #self.__sock.settimeout(1)
                    
                    #self.__configure_socket(self.__ip_addr, port=self.__port, timeout=1.5)

                    data, self.second = self.__sock.recvfrom(1024)

                    if data:
                        print("Got data! Processing...")
                        print(data)
                    data = None

            except socket.timeout:
                pass

            time.sleep(0.5)
        
        self.__listener_signal.set()
        print("Node has stopped listening!")

    def __send_control_messages(self, ip_addr : IPv4, port : int, timeout: float = 1.5, sleep: int = 5):
        header = Header(ID=self.__get_ID(), CONTROL=True)
        self.__ARQ.push(header.get_ID_dec())

        with self.__lock:
            try:
                print("NOW!")
                self.__sock.settimeout(timeout)
                self.__sock.sendto(header.byte_frame, (ip_addr.get_str(), port) )
            except TimeoutError:
                pass

        while not self.__stop_event.is_set():
            time.sleep(sleep)
            header = Header(ID=self.__get_ID(), target=self.__ARQ.top(), CONTROL=True)

            if not self.__ARQ.push(header.get_ID_dec()):
                print("The window buffer is full")

            with self.__lock:
                try:
                    print("NOW!")
                    self.__sock.settimeout(timeout)
                    self.__sock.sendto(header.byte_frame, (ip_addr.get_str(), port))
                except TimeoutError:
                    pass

        self.__checker_signal.set()
        print("Node has stopped checking!")


    def keep_alive(self, ip_addr : IPv4,  port : int):
        print("Launching connectivity check...", end=" ")

        if not self.__running:
            raise ValueError("Server not running! Launch it first.")

        control_check_thread = threading.Thread(target=self.__send_control_messages, args=(ip_addr, port))
        control_check_thread.start()
        
        self.__ip_addr_2 = ip_addr
        self.__port_2 = port
        self.__is_checking = True

        print("Connectivity is being checked!")


    def set_frag_size(self, size : int) -> None:
        ExceptionHandler.check_comp(size, name="size", type=int, min=0)

        self.__fragment_size = size

    def get_frag_size(self) -> int:
        return self.__fragment_size

    def is_running(self) -> bool:
        return self.__running


    def start(self):
        print("Launching node...", end = " ")

        if self.__running:
            print("Node is already listening!")
            return
        print("here")
        self.__configure_socket(self.__ip_addr, self.__port)
        print("here")
        server_thread = threading.Thread(target=self.__listen)
        server_thread.start()

        self.__running = True
        self.__fragment_size = 100

        print("Server launched succesfully!")

    def quit(self):
        print("Closing node...")

        if not self.__running:
            print("Node is not running! Launch it first.")
            return
        
        # Signalling the Reader thread to stop reading
        self.__stop_event.set()

        # Here the server is attempted to be closed
        # Waiting for the Reader to stop reading
        while not self.__listener_signal.is_set() or (self.__is_checking and not self.__checker_signal.is_set()):
            print("Socket or checker yet used!")
            time.sleep(1)

        # Here the server is successfully closed
        self.__sock.close()

        self.__is_checking = False
        self.__running = False
        
        self.__stop_event.clear()
        self.__listener_signal.clear()
        self.__checker_signal.clear()

        print("Node closed successfully!")

    def send_message(self, ip: str, port: int, message : str):
        print("Sending message...", end=" ")

        frame = Header(self.__get_ID(), target=0, type=FrameType.MESSAGE)
        print(frame.byte_frame)
        with self.__lock:
            try:
                self.__sock.settimeout(1.5)
                #self.__sock.sendto(frame.byte_frame, (self.__ip_addr_2.get_str(), self.__port_2))
                self.__sock.sendto(frame.byte_frame, (ip, port))
            except TimeoutError:
                pass

        
        print("Message sent!")
    
    # ------------ CONSTRUCTOR ------------- #

    def __init__(self, port : int = 5000, ip_addr : str = "127.0.0.1", port_2 : int = 5000, ip_addr_2: str = "127.0.0.1",
                 is_sender : bool = True):
        print("Configuring node...", end=" ")

        ExceptionHandler.check_comp(obj=ip_addr, name="ip_addr", type=str)
        ExceptionHandler.check_comp(obj=port, name="port", type=int)
        ExceptionHandler.check_comp(obj=ip_addr_2, name="ip_addr_2", type=str)
        ExceptionHandler.check_comp(obj=port_2, name="port_2", type=int)

        if not Port.is_udp(port) or not Port.is_udp(port_2):
            raise ValueError("Invalid value for udp port!")

        self.__is_sender: bool = is_sender
        self.__running: bool = False
        self.__is_checking: bool = False
        
        self.__port: int = port
        self.__ip_addr: IPv4 = IPv4(ip_addr)
        self.__port_2: int = port_2
        self.__ip_addr_2: IPv4 = IPv4(ip_addr_2)


        self.__lock = threading.Lock()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.__sock.bind((self.__ip_addr, self.__port))

        self.__stop_event = threading.Event()
        self.__listener_signal = threading.Event()
        self.__checker_signal = threading.Event()
        self.__ID: int = 1
        self.__ARQ: SlidingWindowProtocol = SlidingWindowProtocol()
        print("Node successfully configured!")

if __name__ == "__main__":
    role = "0"
    node = None

    while(1):
        role = input("Specify your role (0 for receiver, 1 for sender): ")

        match role:
            case "0":
                node = Node()
                break
            case "1":
                node = Node(is_sender=True)
                break

        print("Invalid role specification!")

    #node.start()

    while(1):
        print("")
        command = input("Enter command: ")
        print("")

        args = command.split(' ')

        try:
            match(args[0]):
                    case "--set_ip":
                        if len(args) != 2:
                            print("Invalid command structure. See help for more information.")
                            continue

                        node.set_ip(IPv4(ip_str=args[1]))
                        continue
                    case "--get_ip":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                            continue

                        print(node.get_ip())
                        continue
                    case "--set_port":
                        if len(args) != 2:
                            print("Invalid command structure. See help for more information.")
                            continue

                        node.set_port(port=int(args[1]))
                        continue
                    case "--get_port":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                            continue

                        print(node.get_port())
                        continue
                    
                    case "-s":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                            continue

                        node.start()
                        continue
                    case "-k":
                        if len(args) != 3:
                            print("Invalid command structure. See help for more information.")
                            continue

                        node.keep_alive(IPv4(args[1]), int(args[2]))
                        continue
                    case "-m":
                        if len(args) != 4:
                            print("Invalid command structure. See help for more information.")
                            continue
                        
                        node.send_message(ip=args[1], port=int(args[2]), message=args[3])
                        continue
                    case "-q":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                            continue

                        node.quit()
                        continue
                    case "-t":
                        if len(args) != 1:
                            print("Invalid command structure. See help for more information.")
                            continue

                        if node.is_running():
                            print("Server still running! Quit it first in order to terminate the program.")
                            continue
                        
                        break
                    case "-h":
                        print ("""List of supported commands:
    
    --set_ip <value>
    --get_ip
    --set_port <value>
    --get_port
    -s: starts a server
    -m: sends a message
    -q: quits a server""")
                        continue
            
            print("Unknown command. Use -h for more information.")
        except Exception as e:
            raise e
            


    print("Program terminated successfully!")



    



