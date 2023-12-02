import socket
import time
import threading
from client import Client
from server import Server
from network_utils import IPv4, Frame
from utils import BitManager
from node import Node

#CLIENT_IP = "147.175.163.197"
#CLIENT_IP = '192.168.1.225'
#CLIENT_IP = '192.168.1.191'
CLIENT_IP =  '147.175.160.184'
CLIENT_PORT = 50602
#SERVER_IP = "192.168.1.225"
#SERVER_IP = '192.168.1.191'
#SERVER_IP = "147.175.163.197"
SERVER_PORT = 50601

def main():

    #client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)
    #server = Server(SERVER_IP, SERVER_PORT)
    
    # server_thread = threading.Thread(target=server.start)
    # server_thread.start()
  

    # user_input = "start"

    # while(user_input != "quit"):
    #   user_input = input("enter command: ")

    #   match user_input:
    #       case "sleep":
    #         time.sleep(3)
    #       case "quit":
    #         server.quit()
    #         server_thread.join()
          
          
        
      
        

    #data = server.receive()


  #   client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)

  #   client.init_com(header=Header(syn=True))

  #   #client.send_message("HAHAHHA")
    
  #   #print(data)
    

  #   for el in data:
  #     print(el)
  #     print(f"prev: {format(el, '08b')}")

  #     #print(f"after incrementing: {format(BitManager.set_bit(el, 1), '08b')}")


  # #server.send_response()
  # #client.receive()

  # #client.send_message("SENDING ANOTHER MESSAGE!")
  # #server.receive()

  # client.quit()
  # server.quit()

  # print("done")

if __name__ == '__main__':
    receiver = Node(SERVER_PORT)
    sender = None(CLIENT_IP, CLIENT_PORT)

    main()

