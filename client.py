import socket, threading
from network_utils import IPv4, Header, Port

CLIENT_IP = " 192.168.1.225"
CLIENT_PORT = 50602
SERVER_IP = " 192.168.1.225"
SERVER_PORT = 50601

class Client:
    def __init__(self, ip : IPv4, port, server_ip : IPv4, server_port) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if not Port.is_udp(port=port) or not Port.is_udp(server_port):
            raise ValueError("Invalid value for UDP port!")
        
        self.ip = ip
        self.port = port
        self.server_ip = server_ip
        self.server_port = server_port
        self.established = False

    def receive(self):
        data = None
        data, self.server = self.sock.recvfrom(1024)    

        print("Received message: %s" % data)

        return str(data, encoding='utf-8')
    
    def send_message(self, message):
        self.sock.sendto(bytes(message, encoding="utf-8"),
                         (self.server_ip, self.server_port))
        
    def send_file(self):
        pass
    def init_com(self):
        header = Header(src_ip=self.ip, dst_ip=self.server_ip, src_port=self.port, dst_port=self.server_port, syn=True)
        
        print(header.byte_frame)
        self.sock.sendto(b''.join(header.byte_frame), (self.server_ip.get_str(), self.server_port))
    
    def ter_comm(self):
        pass        

    def quit(self):
        self.sock.close()
        print("Client closed...")


if __name__=="__main__":
    # client_ip = IPv4(CLIENT_IP)
    # server_ip = IPv4(SERVER_IP)

    client = Client(IPv4(CLIENT_IP), CLIENT_PORT, IPv4(SERVER_IP), SERVER_PORT)
    
    while 1:
        com = input("Enter command: ")

        match com:
            case "-h":
                print("""
Supported commands:
                    -h for printing help
                    -i for initiating a communication
                    -m for sending a message
                    -f for sending a file
                    -t for terminating a communication
                    -q for quitting the socket and program
""")
                continue
            case "-i":
                client.init_com()
                continue
            case "-m":
                client.send_message()
                continue
            case "-f":
                client.send_file()
                continue    
            case "-t":
                client.ter_comm()
                continue
            case "-q":
                client.quit()
                break

        print("Unknown parameter! Use -h for help.")

    print("Program succesfully terminated!")