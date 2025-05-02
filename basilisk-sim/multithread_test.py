
import random
import time
from datetime import datetime, timedelta
from multiprocessing import Process, Pipe, Manager, Barrier
import subprocess

import serial
from sgp4.api import Satrec, jday

# import parse_tle
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




def all_data(init_barrier, shared_data, sim_params, shift_seconds=0):
    """
    Parameters:
        conn: object for communicating with another node
        shared_data: mulithreaded server dictionary object
        sim_params: a keyword dictionary to pass to the simulator 
        shift_seconds: number of seconds to shift the simulation
    """
    sim_output = run(**sim_params)
    
    # add initial simulation to memory
    shared_data.update(sim_output)

    # let the other process know to start
    # conn.send("initial simulation ready")
    init_barrier.wait()
    
    # start other simulations
    print("Simulation Done")




def run_vizard(init_barrier, shared_data, shift_seconds):


    init_barrier.wait()
    
    vizard_app_path = "/home/monitor/Vizard_Linux/Vizard.x86_64"
    vizard_bin_path = "/home/monitor/oresat-simulator/basilisk-sim/_VizFiles/Rose_Sim_UnityViz.bin"
    vizard_cmd = [vizard_app_path, "-loadFile", vizard_bin_path]

    subprocess.Popen(vizard_cmd)    


    while True:
        # delay until the next second
        wait_time = 1 -  ((time.time()) % 1)
        time.sleep(wait_time + 0.1)

        # find the data at the timestamp
        epoch = time.time()
        sim_time = int(epoch) + int(shift_seconds) - int(shared_data.keys()[1])
        print("VIZARD: sim time (s):", sim_time)
        print("VIZARD: epoch:", epoch)
        print("VIZARD: epoch + shift:", str(epoch + shift_seconds))

        time.sleep(0.2)
        print("\n")







def solar_data(init_barrier, shared_data, shift_seconds=0, intensity_cap=50):
    
    has_serial = False
    try:
        ser = serial.Serial(port= '/dev/ttyACM0',baudrate = 115200)
        has_serial = True
        
        # send control c
        ser.write(b'\x03')
        time.sleep(1)
        
        # send control d 
        ser.write(b'\x04')
        time.sleep(1)

        # Accept default settings
        ser.write('\r\n'.encode())
        time.sleep(1)
        
        # Put into basilisk mode, uses \r for some reason
        ser.write('3\r'.encode())
        
    except:
        print("Failed to connect to serial, will only print numbers to terminal.")

    init_barrier.wait()

    header = shared_data["header"]
    print(shared_data["header"])
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
                print("SOLAR_SIMULATOR: ran out of data at ", epoch)
                break
            
            # print(epoch, my_list)
            column_index = header.index("sun_z+")
            # print("SUN: column index", column_index)
            value_to_send = int(100*my_list[column_index])
            value_to_send = value_to_send if value_to_send < intensity_cap else intensity_cap
            print("SOLAR_SIMULATOR: value to send (intensity):", value_to_send)
            
            if has_serial:
                ser.write((str(value_to_send) + "\r").encode("utf-8"))


    except:
        print("\n\nSUN: An error occured")
    finally:
        print("\n\nClosing the simulator")
        if has_serial:
            ser.write("0\r".encode("utf-8"))
            ser.write("0\n".encode("utf-8"))
            ser.write("0\r".encode("utf-8"))
            ser.write("0\n".encode("utf-8"))
            print("\n\nAttempted to turn off solar simulator")
            ser.write("0\r".encode("utf-8"))
            ser.write("0\n".encode("utf-8"))
            ser.write("0\r".encode("utf-8"))
            ser.write("0\n".encode("utf-8"))
            
            ser.close()
            print("\n\nClosed serial")
        print("\n\nSimulator finished\n\n")



def magne_data(conn, shared_data):
    output_numbers = conn.recv()
        
    for the_line in shared_data:
        print(the_line)
        time.sleep(1) #seconds to pause (ONLY OUTPUT)



def groundstation_data(init_barrier, shared_data, shift_seconds):
    init_barrier.wait()

    header = shared_data["header"]
    print(shared_data["header"])
    time.sleep(1)

    pos_indicies = [header.index(column_name) for column_name in ["pos_x", "pos_y", "pos_z"]]


    while True:
        # delay until the next second
        wait_time = 1 - (time.time() % 1)
        time.sleep(wait_time)

        # find the data at the timestamp
        epoch = time.time()
        my_list = shared_data.get(int(epoch + shift_seconds))
        
        if my_list is None:
            print("GROUND_STATION: ran out of data at ", epoch)
            break
        
        # print(epoch, my_list)

        # calculate the distance
        column_index = header.index("sun_x+")
        # print("GS: column index", column_index)
        value_to_send = int(100*my_list[column_index])

        # get the satellite position
        sat_position = [my_list[index] for index in pos_indicies]
        gs_position = [-2417635.58, -3768603.60, 4527222.18]

        distance = (sum([(sat_position[ii] - gs_position[ii])**2 for ii in range(3)]))**0.5

        print("GROUND_STATION: value to send (distance): ", distance)
        






def get_fastforward_epoch(tle_filename, sat_rotational_state, sim_duration, 
                          overlap, iterations, test_functions):
    """Function for calculating how much to fast forward

    Parameters:
        tle_filename: filename where tle is stored
        sat_rotational_state: dictionary with init_att, init_ang_vel, and rI for simulations.
        sim_duration: number of seconds to simulate into the future at a time, maybe 1 hour or 3600 seconds.
        overlap: number of seconds to overlap each iteration, maybe 10 minutes or 600 seconds. Should be sufficient for all test functions
        iterations: number of iterations, skipping seconds_into_future - seconds_to_overlap at a time.
        functions: list of functions which accept:
            sim_data: simulation data
            check_epoch: starting epoch to check from
    """
    for iteration in range(iterations):

        # slightly inaccurate if there are a lot of simulations to do
        big_shift_seconds = (sim_duration - overlap)*iteration
        print("iteration", iteration, "shifted_seconds", big_shift_seconds)

        ff_init_params = get_init_parameters(tle_filename="tle.txt", shift_seconds=big_shift_seconds)
        ff_params = {"show_plots": False,
                    "livestream": False,
                    "step_time": 1,
                    "stop_time": sim_duration}
        ff_params.update(sat_rotational_state)
        ff_params.update(ff_init_params)
                
        ff_output = run(**ff_params)

        sim_shift_seconds = 0
        for check_epoch in ff_output.keys():
            if check_epoch == "header":
                continue


            passed_checks_so_far = True
            # check if the current epoch passes all tests
            for test_func in test_functions:
                passed_checks_so_far = test_func(ff_output, check_epoch)
                # if it does not pass one, just skip checking the rest
                if not passed_checks_so_far:
                    continue
            
            if passed_checks_so_far:
                sim_shift_seconds = int(check_epoch - time.time() + 1)
                return sim_shift_seconds
                break

    return int(-1)




def check_if_soon_eclipsed(sim_data, check_epoch):
    """Checks if it is in the sun for 5 minutes"""
    sun_index = (sim_data["header"]).index("sun_exposure")

    num_consecutive_secs = 600 # 10 min
    total = 0

    for shift_seconds in range(num_consecutive_secs):
        lookup = int(check_epoch) + shift_seconds
        instance_data = sim_data.get(lookup)
        if instance_data is not None:
            total += instance_data[sun_index]

    quality = total / num_consecutive_secs  
    return (quality > 0.3 and quality < 0.7)



def check_in_sun(sim_data, check_epoch):
    """Checks if it is in the sun for 5 minutes"""
    sun_index = (sim_data["header"]).index("sun_exposure")

    num_consecutive_secs = 300 # 5 min
    total = 0

    for shift_seconds in range(num_consecutive_secs):
        lookup = int(check_epoch) + shift_seconds
        instance_data = sim_data.get(lookup)
        if instance_data is not None:
            total += instance_data[sun_index]

    return total / num_consecutive_secs >= 1.0


def check_in_range(sim_data, check_epoch):
    """Checks if it is within range for 5 minutes"""
    pos_indicies = [sim_data["header"].index(column_name) for column_name in ["pos_x", "pos_y", "pos_z"]]

    num_consecutive_secs = 10 # 10 s
    gs_position = [-2417635.58, -3768603.60, 4527222.18]
    req_distance = 5000000 # must be within 1000 km

    for shift_seconds in range(num_consecutive_secs):
        lookup = int(check_epoch) + shift_seconds
        instance_data = sim_data.get(lookup)
        if instance_data is not None:
            sat_position = [instance_data[index] for index in pos_indicies]
            distance = (sum([(sat_position[ii] - gs_position[ii])**2 for ii in range(3)]))**0.5

            if distance > req_distance:
                return False

    return True


if __name__ == "__main__":
    with Manager() as manager:
        send_conn, recv_conn = Pipe()
        init_barrier = Barrier(4)

        shared_data = manager.dict()

        sat_rotational_state = {"init_att": [[0.1], [0.2], [-0.3]],
                                "init_ang_vel": [[0.05], [-0.1], [0.05]],
                                "rI": [16.50e7, 71145.23, 457069.94,
                                       71145.23, 15.96e7, 310717.76,
                                       457069.94, 310717.76, 65.18e6]
                                }
        

        # if you want to be in the sun, figure how much to shift the data
        sun_fastforward = True
        sim_shift_seconds = 0
        if sun_fastforward:

            blah = get_fastforward_epoch(tle_filename="tle.txt", 
                                         sat_rotational_state=sat_rotational_state, 
                                         sim_duration=60*60*6,
                                         overlap=60*5,
                                         iterations=1000, #
                                         test_functions = [check_in_sun])

            print("\n\nshift seconds into the future: ", blah, "\n\n")
            if blah < 0:
                print("Failed to find instance, the situation may be happening NOW, otherwise please increase the number of iterations\n")
                print("Setting default shift to zero\n")
                blah = 0
            sim_shift_seconds = blah



        # build the sim params dictionary
        sim_init_params = get_init_parameters(tle_filename="tle.txt", shift_seconds=sim_shift_seconds)
        sim_params = {"show_plots": False,
                      "livestream": False,
                      "step_time": 1,
                      "stop_time": 600}
        sim_params.update(sim_init_params)
        sim_params.update(sat_rotational_state)
        
        # do it for the list
        sim_process = Process(target=all_data, args=(init_barrier, shared_data, sim_params, sim_shift_seconds))
        viz_process = Process(target=run_vizard, args=(init_barrier, shared_data, sim_shift_seconds))
        sun_process = Process(target=solar_data, args=(init_barrier, shared_data, sim_shift_seconds))
        gs_process = Process(target=groundstation_data, args=(init_barrier, shared_data, sim_shift_seconds))
        # status_process = Process()

        sim_process.start()
        viz_process.start()
        sun_process.start()
        gs_process.start()
        
        # wait
        #sim_process.join()
        # viz_process.join()
        sun_process.join()
        gs_process.join()
        
        
