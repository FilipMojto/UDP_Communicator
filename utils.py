class BitManager:

    @staticmethod
    def set_bit(byte, position: int, value: bool):
        ExceptionHandler.check_comp(obj=position, name="position", type=int, min=0)
    
        if value:
            return byte | (1 << position)
        else:
            return byte & ~(1 << position)


    @staticmethod
    def toggle_bit(byte, position):
        return byte ^ (1 << position)
    
    @staticmethod
    def is_bit_set(byte, pos: int):
        return (byte & (1 << pos)) != 0


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
            

