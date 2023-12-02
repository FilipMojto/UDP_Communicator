import crcmod

class BitManager:

    @staticmethod
    def set_bit(byte, position: int, value: bool):
        ExceptionHandler.check_comp(obj=position, name="position", type=int, min=0)
    
        if value:
            return byte | (1 << position)
        else:
            return byte & ~(1 << position)

    # @staticmethod
    # def clear_bit(byte, position):
    #     #Clear the bit at the specified position to 0.
    #     return byte & ~(1 << position)

    @staticmethod
    def toggle_bit(byte, position):
        #Inverse the bit at the specified position.
        return byte ^ (1 << position)
    
    @staticmethod
    def is_bit_set(byte, pos: int):
        return (byte & (1 << pos)) != 0

# @staticmethod
# def calculate_crc16(frame):
#     crc16_func = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, xorOut=0xFFFF)

#     # Calculate the CRC-16 checksum of the frame
#     checksum = crc16_func(frame)

#     # Convert the 16-bit checksum to a bytes object (2 bytes)
#     crc16_bytes = checksum.to_bytes(2, byteorder='little')

#     return crc16_bytes

class ExceptionHandler:

    @staticmethod
    def check_comp(obj, name : str, type = None, min = None, max = None) -> None:
            type_name = type.__name__

            if type and not isinstance(obj, type):
                raise TypeError(f"Invalid type for parameter '{name}'. '{type_name}' is needed.")
            
            if min and obj < min:
                raise ValueError(f"Invalid value for parameter '{name}'. More than {min} needed.")
            
            if max and obj > max:
                raise ValueError(f"Invalid value for parameter '{name}'. Less than {max} needed.")