

import random
import time
from multiprocessing import Process, Pipe, Manager
import parse_tle
import serial
from Rose_Sim import run

sat_data = parse_tle.Tle("tle.txt")
sat_data._parse_tle()

def all_data(conn, shared_data):
    # initial simulation
    timeInitString = str(sat_data.epoch)
    #timeInitString = '2025 MAY 04 07:47:48.965 (UTC)'
    init_position = [-4963946.392216118, 4601467.815050239, -1311445.5818653065]
    init_velocity = [1731.502687329283, -238.55435888532116, -7398.92444558897] 
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
        init_timestring = timeInitString)
    
    
    # add initial simulation to memory
    shared_data.extend(sim_output)

    # let the other process know to start
    conn.send("initial simulation ready")

    # start other simulation

    print("Simulation Done")


def solar_data(conn, shared_data):
    output_numbers = conn.recv()
        
    ser = serial.Serial(
        port= '/dev/ttyUSB1',
        baudrate=115200
        )

    for the_line in shared_data:
        print(the_line[3])
        print(the_line[4])
        ser.write()
        time.sleep(1) #seconds to pause (ONLY OUTPUT)

    ser.close()



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

        shared_data = manager.list()

        # do it for the list
        sim_process = Process(target=all_data, args=(send_conn, shared_data))
        sim_target = Process(target=solar_data, args=(recv_conn, shared_data))

        sim_process.start()
        sim_target.start()
        
        # wait
        #process_1.join()
        sim_target.join()
        
        
