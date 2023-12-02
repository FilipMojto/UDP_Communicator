from network_utils import Frame


frame = Frame(ID=1, MORE_FRAGS=True)


print(frame.get_crc_dec())
#frame.__recalculate_csc()
print(frame.calculate_FCS())

frame.set_more_frags(False)

print(frame.get_crc_dec())
print(frame.calculate_FCS())



if frame.get_crc_dec() != frame.calculate_FCS():
    print("ERROR!")

