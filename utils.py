class BitManager:

    @staticmethod
    def set_bit(byte, position):
    #Set the bit at the specified position to 1.
        return byte | (1 << position)

    @staticmethod
    def clear_bit(byte, position):
        #Clear the bit at the specified position to 0.
        return byte & ~(1 << position)

    @staticmethod
    def toggle_bit(byte, position):
        #Inverse the bit at the specified position.
        return byte ^ (1 << position) 