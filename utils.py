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