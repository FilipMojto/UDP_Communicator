import socket
import time
import threading

#This is the configuration for the default server
SERVER_IP = "192.168.1.225"
SERVER_PORT = 50601

class Server:
    def __init__(self, ip, port) -> None:
        self.__running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.stop_event = threading.Event()
        self.stop_event_2 = threading.Event()
        self.sock.settimeout(1)

    def receive(self):
        try:
            data, self.client = self.sock.recvfrom(1024)

            #Here we process the data from the socket
            if data:
                print("\nDetected data in the socket! Processing...")
                print(data)
                bits = bin(data[12])

                data = None        
        except socket.timeout:
            pass

    def start(self):
        print("Launching server...")
        
        if self.__running:
            print("Server is already running! Shut it first.")
            return
        
        self.__running = True
        print("Server launched successfully!")
        
        #data = None
        while not self.stop_event.is_set(): #not self.stop_event.is_set():

            try:
                data, self.client = self.sock.recvfrom(1024)

                #Here we process the data from the socket
                if data:
                    print("\nDetected data in the socket! Processing...")
                    print(data)
                    bits = bin(data[12])

                    data = None        
            except socket.timeout:
                pass
            
            time.sleep(1)
            
        
        self.stop_event_2.set()
        print("Server has stopped listening!")

    def send_response(self):
        self.sock.sendto(b"Message received...", self.client)

    def quit(self):
        print("Closing server...")

        if not self.__running:
            print("Server is not running! Launch it first.")
            return
        
        # Signalling the Reader thread to stop reading
        self.stop_event.set()

        # Here the server is attempted to be closed
        # Waiting for the Reader to stop reading
        while not self.stop_event_2.is_set():
            print("Socket yet used!")
            time.sleep(1)

        # Here the server is successfully closed
        self.sock.close()
        self.__running = False

        print("Server closed successfully!")

if __name__ == "__main__":
    #by default, a new server is launched with the predefined configuration
    server = Server(SERVER_IP, SERVER_PORT)

    #here we create a separate thread to listen for incoming data
    #server_thread = threading.Thread(target=server.start)
    #server_thread.start()

    #here we listen to the user input from the console
    while 1:
        inp = input("Enter command: ")

        match inp:
            case "-s":
                print("sleeping...")
                time.sleep(3)
                continue
            case "-q":
                server.quit()
                #server_thread.join()
                break
            case "-r":
                server.receive()
                continue
            case "-h":
                print("""
Supported commands:
                    -h for printing help
                    -s for making console sleep
                    -q for quitting the server and program
""")
                continue
        print("Unknown parameter! Use -h for help.")
    
    print("Program terminated succesfully!")