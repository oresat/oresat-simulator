

import random
import time
from multiprocessing import Process, Pipe, Manager
import parse_tle
import serial
from Rose_Sim import run

from datetime import datetime
from sgp4.api import Satrec, jday


sat_data = parse_tle.Tle("tle.txt")
sat_data._parse_tle()

def all_data(conn, shared_data):
    # initial simulation
    #timeInitString = str(sat_data.epoch)

    now = datetime.now()
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

    with open("tle.txt", "r") as fd:
        lines = fd.readlines()
        tle1 = lines[0]
        tle2 = lines[1]

    satellite = Satrec.twoline2rv(tle1, tle2)
    e, r, v= satellite.sgp4(jd, fr)

    init_position = [element*1000 for element in r]
    init_velocity = [element*1000 for element in v]

    print(r)
    print(v)


    timeInitString = str(sat_data.epoch)

    init_epoch = int(time.time())

    #timeInitString = '2025 MAY 04 07:47:48.965 (UTC)'
    #init_position = [-4963946.392216118, 4601467.815050239, -1311445.5818653065]
    #init_velocity = [1731.502687329283, -238.55435888532116, -7398.92444558897] 
    init_MRP_attitude = [[0.1], [0.2], [-0.3]]  # sigma_BN_B
    init_ang_velocity = [[0.05], [-0.1], [0.05]]
    rI = [16.50e7, 71145.23, 457069.94,
        71145.23, 15.96e7, 310717.76,
        457069.94, 310717.76, 65.18e6]

    sim_output = run(      

        

        True,  # show_plots
        False,  # livestream
        step_time = 1.0,
        stop_time = 60.0,
        rI = rI,
        init_pos = init_position,
        init_vel = init_velocity,
        init_att = init_MRP_attitude,
        init_ang_vel = init_ang_velocity,
        init_timestring = timeInitString,
        init_epoch = init_epoch)
    

    
    
    # add initial simulation to memory
    shared_data.update(sim_output)

    # let the other process know to start
    conn.send("initial simulation ready")

    # start other simulation

    print("Simulation Done")


def solar_data(conn, shared_data):
    output_numbers = conn.recv()
    
    has_serial = False
    try:
        ser = serial.Serial(
                port= '/dev/ttyACM0',
                baudrate = 115200
                )
        has_serial = True
    except:
        print("Failed to connect to serial, will only print numbers to terminal.")


    header = shared_data["header"]
    print(shared_data["header"])

    if has_serial:
        ser.write(3)

    time.sleep(1)


    try:

        while True:
            wait_time = 1 - (time.time() % 1)
            time.sleep(wait_time)

            epoch = time.time()
            my_list = shared_data.get(int(epoch))
            
            if my_list is None:
                print("ran out of data at ", epoch)
                break
            
            print(epoch, my_list)

            print("column index", column_index := header.index("sun_x+"))
            
            value_to_send = int(100*my_list[column_index])

            if has_serial:
                ser.write((str(value_to_send) + "\n").encode("utf-8"))

    except e:
        print("An error occured", e)
    finally:
        if has_serial:
            ser.write("0\n".encode("utf-8"))
            print("Attempted to turn off solar simulator")
            ser.close()
            print("Closed serial")



def magne_data(conn, shared_data):
    output_numbers = conn.recv()
        
    for the_line in shared_data:
        print(the_line)
        time.sleep(1) #seconds to pause (ONLY OUTPUT)

def time_print(conn, shared_data):
    output_numbers = conn.recv()

    for the_line in shared_data:
        print(the_line)
        time.sleep(1) #seconds to pause (ONLY OUTPUT)




if __name__ == "__main__":
    with Manager() as manager:
        send_conn, recv_conn = Pipe()

        shared_data = manager.dict()

        # do it for the list
        sim_process = Process(target=all_data, args=(send_conn, shared_data))
        sim_target = Process(target=solar_data, args=(recv_conn, shared_data))

        sim_process.start()
        sim_target.start()
        
        # wait
        #process_1.join()
        sim_target.join()
        
        
