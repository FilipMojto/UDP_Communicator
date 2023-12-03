from network_utils import Frame, FragmentSequenceProcessor
import random, math, os
from typing import List


class Test:
    ID_MIN: int = 1
    ID_MAX: int = 16777216
    ID: int = 1

    def __init__(self) -> None:
         pass
    
    def generate_ID(self) -> int:
        cur_ID = self.ID

        # the capacity was reached, need to reset it!
        if self.ID == self.ID_MAX - 1:
            self.ID = 0

        self.ID += 1

        return cur_ID

    def corrupt_data(self, frame: bytearray, corruption: float = 0.10) -> bytearray:

            # Calculate the number of bytes to corrupt
            num_bytes_to_corrupt = int(len(frame) * corruption / 100)

            # Get random indices to corrupt
            indices_to_corrupt = random.sample(range(len(frame)), num_bytes_to_corrupt)

            # Corrupt the data at selected indices
            for index in indices_to_corrupt:
                # Flip a random bit in the byte at the selected index
                frame[index] = frame[index] ^ (1 << random.randint(0, 7))

            return frame

    def send_file(self, f_path: str, name: str = None):
            __max_output_size = 1000
            __frame_corruptness = 0.1
            
            print(f_path)
            print(name)

            if not name:
                name = os.path.basename(f_path)

            fragments: List[Frame] = []
            frag_count = 0
            data_count = 0

            try:
                with open(f_path, 'rb') as file:
                    file_name = bytes(name + ' ', encoding='utf-8')
                    data = file.read(__max_output_size - len(file_name))
                    prev: int = -1
                    
                    while data:
                        data_frame = None

                        if data_count == 0 and frag_count == 0:
                            data_frame = Frame(ID=self.generate_ID(), payload=bytearray(file_name + data), SET=True, MORE_FRAGS=True)
                        else:
                            data_frame = Frame(ID=self.generate_ID(), target=prev, payload=bytearray(data), SET=True, MORE_FRAGS=True)


                        prev = data_frame.get_ID_dec()
                        fragments.append(data_frame)
                        data = file.read(__max_output_size)
                        data_count += len(data_frame.get_payload())
                        frag_count += 1
            except FileNotFoundError:
                print("The input file is non-existent. Creating a new one...")
                with open(f_path, 'w'):
                    pass
                return self.send_file(f_path=f_path, name=name)
            
            
            if frag_count == 0:
                print("Input file is empty!")
                return
            
            fragments[frag_count - 1].set_more_frags(False)
            
            corrupted_frags: List[int] = []
            
            if __frame_corruptness > 0:
                corrupted_frags = random.sample(range(0, frag_count), math.floor(frag_count * __frame_corruptness ))
                corrupted_frags.sort()


            corrupted_list: List[Frame] = []

            for i in range (0, frag_count):
                frag=fragments[i]

                if len(corrupted_frags) > 0 and i == corrupted_frags[0]:
                    #frag.frame()
                    #self.corrupt_send_wait(frame=frag)
                    corrupted = Frame(frame=self.corrupt_data(frame=bytearray(frag.byte_frame)))
                    #fragments.remove(frag)
                    corrupted_list.append({'num': i, 'frag': corrupted})

                    corrupted_frags.remove(corrupted_frags[0])
                # else:
                #     self.send_and_wait(frame=frag)

            #     print(f"Fragment {frag.get_ID_dec()}: {len(frag.get_payload())}")

            #self.__print_file_data(os.path.abspath(f_path), data_count)
            return fragments, corrupted_list

processor = FragmentSequenceProcessor()


tester = Test()

frags, corrupted = tester.send_file(f_path='./test_files/attempt.pdf', name='f.pdf')
replaced: List[Frame] = []

print(f"Orignal len: {len(frags)}")

print(len(frags))

#print(len(frags))
for frag in corrupted:
    print(frag['num'])
    replaced.append(frags[frag['num']])
    frags.remove(frags[frag['num']])


print(len(replaced))

for frag in frags:

    seq = processor.push(frame=frag)
    # if seq:
    #     print("completed!")
    
    #     cur = seq.root

    #     while cur:
    #         cur.frame.frame()
    #         cur = cur.next


for frag in replaced:
    # print("pushing again...")
    # frag.frame()
    seq = processor.push(frame=frag)
    if seq:
        print("completed!")
    
        cur = seq.root

        while cur:
            cur.frame.frame()
            cur = cur.next
    #print(f"Result: {processor.push(frame=frag)}")

# for frag in corrupted:
#     replaced.append(frags[frag['num']])
#     frags.remove(frag)
#     #frags[frag['num']] = frag['frag']





# for frag in frags:
    
#     #print(processor.push(frame=frag))

# for frag in replaced:

#     if frag.get_crc_dec() != frag.calculate_FCS():
#         print("CORRUPTED!")
#         frag.frame()


print("here")
# lists = []

# frame = Frame(ID=1, target=2, FIN=True, QUIT=True, CONTROL=True)

# print(frame.get_crc_dec())
# print(frame.calculate_FCS())

# frame.frame()

# lists.append(frame)

# print(lists[0].get_crc_dec())
# print(lists[0].calculate_FCS())

# new = Frame(frame = corrupt_data(frame=bytearray(frame.byte_frame)))

# new.frame()

# print(new.get_crc_dec())
# print(new.calculate_FCS())

# print(lists[0].get_crc_dec())
# print(lists[0].calculate_FCS())