
import random
import time
from datetime import datetime, timedelta
from multiprocessing import Process, Pipe, Manager

import serial
from sgp4.api import Satrec, jday

import parse_tle
from Rose_Sim import run



#sat_data = parse_tle.Tle("tle.txt")
#sat_data._parse_tle()

def get_init_parameters(tle_filename, shift_seconds=0):
    """
    Gets some simulation parameters
    """
    
    # Read the tle
    with open(tle_filename, "r") as fd:
        lines = fd.readlines()
        tle1 = lines[0]
        tle2 = lines[1]

    # get the simulation start time
    start_time = datetime.now() + timedelta(seconds=shift_seconds)
    init_epoch = int(time.time() + shift_seconds)
    init_timestring = str(start_time.isoformat())

    # get initial position and velocity
    satellite = Satrec.twoline2rv(tle1, tle2)
    jd, fr = jday(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second)
    e, r, v= satellite.sgp4(jd, fr)
    # earth's radius is nearly 6360 km, position and velocity are in meters
    init_position = [element*1000 for element in r]
    init_velocity = [element*1000 for element in v]

    return {"init_pos": init_position,
            "init_vel": init_velocity,
            "init_epoch": init_epoch,
            "init_timestring": init_timestring}



def all_data(conn, shared_data, shift_seconds=0):
    """
    Parameters:
        conn: object for communicating with another node
        shared_data: mulithreaded server dictionary object
        shift_seconds: number of seconds to shift the simulation
    """
    with open("tle.txt", "r") as fd:
        lines = fd.readlines()
        tle1 = lines[0]
        tle2 = lines[1]

    start_time = datetime.now() + timedelta(seconds=shift_seconds)
    jd, fr = jday(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second)
    timeInitString = str(start_time.isoformat())
    init_epoch = int(time.time() + shift_seconds)

    # get initial position and velocity
    satellite = Satrec.twoline2rv(tle1, tle2)
    e, r, v= satellite.sgp4(jd, fr)
    # earth's radius is nearly 6360 km, position and velocity are in meters
    init_position = [element*1000 for element in r]
    init_velocity = [element*1000 for element in v]


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

    # start other simulations
    print("Simulation Done")


def solar_data(conn, shared_data, shift_seconds=0):
    output_numbers = conn.recv()
    
    has_serial = False
    try:
        ser = serial.Serial(port= '/dev/ttyACM0',baudrate = 115200)
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
            # delay until the next second
            wait_time = 1 - (time.time() % 1)
            time.sleep(wait_time)

            # find the data at the timestamp
            epoch = time.time()
            my_list = shared_data.get(int(epoch + shift_seconds))
            
            if my_list is None:
                print("ran out of data at ", epoch)
                break
            
            print(epoch, my_list)
            column_index = header.index("sun_x+")
            print("column index", column_index)
            value_to_send = int(100*my_list[column_index])
            print("value to send", value_to_send)
            
            if has_serial:
                ser.write((str(value_to_send) + "\n").encode("utf-8"))


    except:
        print("\n\nAn error occured")
    finally:
        print("\n\nClosing the simulator")
        if has_serial:
            ser.write("0\n".encode("utf-8"))
            print("\n\nAttempted to turn off solar simulator")
            ser.close()
            print("\n\nClosed serial")
        print("\n\nSimulator finished\n\n")



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

        init_MRP_attitude = [[0.1], [0.2], [-0.3]]  # sigma_BN_B
        init_ang_velocity = [[0.05], [-0.1], [0.05]]
        rI = [16.50e7, 71145.23, 457069.94,
            71145.23, 15.96e7, 310717.76,
            457069.94, 310717.76, 65.18e6]

        # if you want to be in the sun, figure how much to shift the data
        sun_fastforward = True
        sim_shift_seconds = 0
        if sun_fastforward:
            sun_ff_init_params = get_init_parameters(tle_filename="tle.txt", shift_seconds=0)

            sun_ff_params = {"show_plots": False,
                    "livestream": False,
                    "step_time": 1,
                    "stop_time": 60*90,
                    "rI": rI,
                    "init_pos": sun_ff_init_params["init_pos"],
                    "init_vel": sun_ff_init_params["init_vel"],
                    "init_att": init_MRP_attitude,
                    "init_ang_vel": init_ang_velocity,
                    "init_timestring": sun_ff_init_params["init_timestring"],
                    "init_epoch": sun_ff_init_params["init_epoch"]}

            sun_ff_output = run(**sun_ff_params)

            sim_shift_seconds = 0
            for check_epoch in sun_ff_output.keys():
                sun_column = 0
                if check_epoch == "header":
                    continue

                num_consecutive_secs = 600
                total = 0
                for shift_seconds in range(num_consecutive_secs):
                    lookup = int(check_epoch) + shift_seconds
                    total += sun_ff_output.get(lookup)[sun_column]

                if (total / num_consecutive_secs) >= 1.0:
                    sim_shift_seconds = int(check_epoch - time.time() + 1)
                    break


        print("\nShifting simulation by", sim_shift_seconds, "seconds.\n")
        # do it for the list
        sim_process = Process(target=all_data, args=(send_conn, shared_data, sim_shift_seconds))
        sim_target = Process(target=solar_data, args=(recv_conn, shared_data, sim_shift_seconds))

        sim_process.start()
        sim_target.start()
        
        # wait
        sim_process.join()
        sim_target.join()
        
        
