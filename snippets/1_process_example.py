

import random
import time
from multiprocessing import Process



def double(my_num):
    print(my_num*2)

def triple(my_num):
    print(my_num*3)


if __name__ == "__main__":
    process_1 = Process(target=double, args=(5,))
    process_2 = Process(target=triple, args=(7,))

    process_1.start()
    process_2.start()
    
    # don't wait
    #process_1.join()
    #process_2.join()
