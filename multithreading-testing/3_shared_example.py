

import random
import time
from multiprocessing import Process, Pipe, Manager




def random_list(conn, shared_data, lower, upper, num_nums_1, num_nums_2):
    # initial simulation
    my_numbers_1 = random.sample(range(lower, upper), num_nums_1)
    
    # add initial simulation to memory
    shared_data.extend(my_numbers_1)

    # let the other process know to start
    conn.send("initial simulation ready")

    # start other simulation

    my_numbers_2 = random.sample(range(lower, upper), num_nums_2)
    shared_data.extend(my_numbers_2)

    # add other simulation to memory




def time_print(conn, shared_data):
    output_numbers = conn.recv()

    for num in shared_data:
        print(num)
        time.sleep(1)




if __name__ == "__main__":
    with Manager() as manager:
        send_conn, recv_conn = Pipe()

        shared_data = manager.list()

        # do it for the list
        process_1 = Process(target=random_list, args=(send_conn, shared_data, 1, 100, 3, 7))
        process_2 = Process(target=time_print, args=(recv_conn, shared_data))

        process_1.start()
        process_2.start()
        
        # wait
        #process_1.join()
        process_2.join()
        
        
