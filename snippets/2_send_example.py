

import random
import time
from multiprocessing import Process, Pipe



def double(conn, my_num):
    print(my_num*2)
    conn.send(my_num*2)

def my_print(conn):
    my_output = conn.recv()
    print("the output from process 1 was", my_output)




def random_list(conn, lower, upper, num_nums):
    my_numbers = random.sample(range(lower, upper), num_nums)
    conn.send(my_numbers)


def time_print(conn):
    output_numbers = conn.recv()

    for num in output_numbers:
        print(num)
        time.sleep(1)


if __name__ == "__main__":
    send_conn, recv_conn = Pipe()
    
    process_1 = Process(target=double, args=(send_conn, 5,))
    process_2 = Process(target=my_print, args=(recv_conn,))

    process_1.start()
    process_2.start()
    
    # wait
    process_1.join()
    process_2.join()

    print("First part done")



    # do it for the list
    process_1 = Process(target=random_list, args=(send_conn, 1, 100, 7))
    process_2 = Process(target=time_print, args=(recv_conn,))

    process_1.start()
    process_2.start()
    
    # wait
    process_1.join()
    process_2.join()
    
    print("Second part done")

    
