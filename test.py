
from network_utils import Header
from utils import BitManager

frame = Header(ID=93, target=59, MORE_FRAGS=1, FIN=1, ACK = 1, SYN=1)

print(bin(frame.byte_frame[6]))
print(frame.byte_frame[6])
print("end")


