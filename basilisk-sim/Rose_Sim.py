
import inspect
import os
import json

import numpy as np
from matplotlib import pyplot as plt
import parse_tle
import argparse

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
bskName = 'Basilisk'
splitPath = path.split(bskName)

# Import all of the modules that we are going to be called in this simulation
from Basilisk.utilities import SimulationBaseClass
from Basilisk.simulation import simplePowerSink
from Basilisk.simulation import simpleBattery
from Basilisk.simulation import simpleSolarPanel
from Basilisk.simulation import eclipse
from Basilisk.simulation import spacecraft
from Basilisk.simulation import coarseSunSensor

from Basilisk.utilities import macros
from Basilisk.utilities import orbitalMotion
from Basilisk.utilities import simIncludeGravBody
from Basilisk.utilities import astroFunctions
from Basilisk.utilities import unitTestSupport
from Basilisk.utilities import vizSupport
from Basilisk.simulation import simSynch


from Basilisk import __path__
bskPath = __path__[0]

path = os.path.dirname(os.path.abspath(__file__))

fileName = os.path.basename(os.path.splitext(__file__)[0])


import basilisk_wrapper

# Importing our TLE textfile
sat_data = parse_tle.Tle("tle.txt")
sat_data._parse_tle()



def run(show_plots, livestream, step_time, stop_time, rI, init_pos, init_vel, init_att, init_ang_vel, init_timestring):
    """
    The scenarios can be run with the followings setups parameters:

    Args:
        show_plots (bool): Determines if the script should display plots
        step_time: duration of a simulation step [seconds]
        stop_time: approximate duration of a simulation [seconds]
        rI = Rotational Inertia 

    """
    taskName = "simulation-task"               # arbitrary name (don't change)
    processName = "simulation-process"         # arbitrary name (don't change)

    # Importing our TLE textfile
    #sat_data = parse_tle.Tle("tle.txt")
    #sat_data._parse_tle()

    # Create a sim module as an empty container
    scenarioSim = SimulationBaseClass.SimBaseClass()
    simProc = scenarioSim.CreateNewProcess(processName)
    simProc.addTask(scenarioSim.CreateNewTask(taskName, macros.sec2nano(step_time)))

    # Create a spacecraft around Earth
    # initialize spacecraft object and set properties
    scObject, scObjectMsg, satLog = basilisk_wrapper.get_satellite('oresat',rI, init_pos, init_vel, init_att, init_ang_vel)
    scenarioSim.AddModelToTask(taskName, scObject)
    scenarioSim.AddModelToTask(taskName, satLog)

    # Setup spice interface iwth earth and sun
    # store planet and sun msgs (which will be used later) and logs
    spiceObject, plMsg, plLog, sunMsg, sunLog= basilisk_wrapper.get_spice_earth_sun(scObject, init_timestring)
    scenarioSim.AddModelToTask(taskName, spiceObject, -1)
    scenarioSim.AddModelToTask(taskName, plLog)
    scenarioSim.AddModelToTask(taskName, sunLog)

    # Create magnetic field
    # Initialize magnetic field and mag logger
    magModule, magMsg, magLog = basilisk_wrapper.get_mag_model("magModel", scObject)
    scenarioSim.AddModelToTask(taskName, magModule)
    scenarioSim.AddModelToTask(taskName, magLog)


    # Create an eclipse object so the panels don't always work
    eclipseObject, eclipseMsg, eclipseLog = basilisk_wrapper.get_eclipse_model("eclipseModel", scObjectMsg, sunMsg, plMsg)
    scenarioSim.AddModelToTask(taskName, eclipseObject)
    scenarioSim.AddModelToTask(taskName, eclipseLog)

    # define directions
    directions = {"x+": [1, 0, 0],
                  "x-": [-1, 0, 0],
                  "y+": [0, 1, 0],
                  "y-": [0, -1, 0],
                  "z+": [0, 0, 1],
                  "z-": [0, 0, -1]}


    # coarse solar sensor
    sun_sensors = dict()
    sun_logs = dict()
    for direction,vector in directions.items():
        # later, see if we can do a constallation
        sun_sensors[direction] = coarseSunSensor.CoarseSunSensor()
        sun_sensors[direction].ModelTag = "sunSensor_"+direction
        # field of view from normal is 90 degrees
        sun_sensors[direction].fov = 90. * macros.D2R
        sun_sensors[direction].nHat_B = np.array(vector)
        sun_sensors[direction].sunInMsg.subscribeTo(sunMsg)
        sun_sensors[direction].stateInMsg.subscribeTo(scObjectMsg)
        sun_sensors[direction].sunEclipseInMsg.subscribeTo(eclipseMsg)
        sun_logs[direction] = sun_sensors[direction].cssDataOutMsg.recorder()
        scenarioSim.AddModelToTask(taskName, sun_sensors[direction])
        scenarioSim.AddModelToTask(taskName, sun_logs[direction])



    # Create a solar panel
    # Set the panel normal vector in the body frame, the area,
    #solarPanel = basilisk_wrapper.get_solar_panel("solarPanel", scObjectMsg, eclipseMsg, sunMsg, [[1,0,0], 0.2*0.3, 0.20]) 
    #spLog = solarPanel.nodePowerOutMsg.recorder()
    #scenarioSim.AddModelToTask(taskName, solarPanel)
    #scenarioSim.AddModelToTask(taskName, spLog)


    #   Create a simple power sink
    #powerSink = basilisk_wrapper.get_power_sink("powerSink2", -3)
    #psLog = powerSink.nodePowerOutMsg.recorder()
    #scenarioSim.AddModelToTask(taskName, powerSink)
    #scenarioSim.AddModelToTask(taskName, psLog)


    # Create a simpleBattery and attach the sources/sinks to it
    #powerMonitor = basilisk_wrapper.get_power_monitor("powerMonitor", capacity=(10.0*3600.0), init_charge=(10.0*3600.0))
    #powerMonitor.addPowerNodeToModel(solarPanel.nodePowerOutMsg)
    #powerMonitor.addPowerNodeToModel(powerSink.nodePowerOutMsg)
    #pmLog = powerMonitor.batPowerOutMsg.recorder()
    #scenarioSim.AddModelToTask(taskName, powerMonitor)
    #scenarioSim.AddModelToTask(taskName, pmLog)


    #   Try and get Vizard to work
    if livestream:
        clockSync = simSynch.ClockSynch()
        clockSync.accelFactor = (stop_time / 20)
        scenarioSim.AddModelToTask(taskName, clockSync)

    vizSupport.enableUnityVisualization(scenarioSim, taskName, scObject,
                                               saveFile=__file__,
                                               liveStream=livestream
                                              )

    # SIMULATION
    # Need to call the self-init and cross-init methods
    # Start the simulation
    scenarioSim.InitializeSimulation()
    scenarioSim.ConfigureStopTime(macros.sec2nano(stop_time))        # seconds to stop simulation
    scenarioSim.ExecuteSimulation()



    # This pulls the actual data log from the simulation run.
    # Note that range(3) will provide [0, 1, 2]  Those are the elements you get from the vector (all of them)

    # Position and Time
    posData = satLog.r_BN_N
    timeAxis = satLog.times() * macros.NANO2HOUR

    # Magnetic Field
    magData = magLog.magField_N

    # Solar
    eclipseData = eclipseLog.shadowFactor
    #supplyData = spLog.netPower
    #sinkData = psLog.netPower
    #storageData = pmLog.storageLevel
    #netData = pmLog.currentNetPower

    sunData = { direction:[float(reading) for reading in sunLog.OutputData] for direction,sunLog in sun_logs.items() }

    sun_data = [["sun_exposure", "x+", "x-", "y+", "y-", "z+", "z-"]]
    for ii in range(len(timeAxis)):
        sun_data.append([float(eclipseData[ii])] + [direction[ii] for direction in sunData.values()])
    with open('sun.csv', 'w') as fd:
        for line in sun_data:
            fd.write(",".join([str(thing) for thing in line]) + "\n")



    temp_data = [["time", "mag_x", "mag_y", "mag_z", "is_eclipsed"]]
    for ii in range(len(timeAxis)):
        temp_data.append([float(timeAxis[ii])] + [float(magd) for magd in magData[ii]] + [float(eclipseData[ii])])
    with open('output.txt','w') as fd:
        for line in temp_data:
            fd.write(str(line) + "\n")


    time_ns = satLog.times()

    time_ns = satLog.times()
    time_ns_m = time_ns * macros.NANO2HOUR

    tvec = satLog.times()
    tvec = tvec * macros.NANO2HOUR

    #   Plot the power states
    figureList = {}
    
    # sol_modular graph data
    #plt.figure(1)
    #plt.plot(time_ns_m, storageData/3600., label='Stored Power (W-Hr)')
    #plt.plot(time_ns_m, netData, label='Net Power (W)')
    #plt.plot(time_ns_m, supplyData, label='Panel Power (W)')
    #plt.plot(time_ns_m, sinkData, label='Power Draw (W)')
    #plt.xlabel('Time (Hr)')
    #plt.ylabel('Power (W)')
    #plt.grid(True)
    #plt.legend()

    #pltName = "scenario_powerDemo"
    #figureList[pltName] = plt.figure(1)


    plt.figure(2)
    fig = plt.gcf()
    ax = fig.gca()
    for idx in range(3):
        plt.plot(posData[: ,idx])

    pltName = "position"
    figureList[pltName] = plt.figure(2)


    # mag_modular graph data

    plt.figure(3)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='sci')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    for idx in range(3):
        plt.plot(timeAxis, magData[:, idx] *1e9,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$B\_N_{' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [hours]')
    plt.ylabel('Magnetic Field [nT]')
    pltName = filename + "3"
    figureList[pltName] = plt.figure(3)

    if show_plots:
        plt.show()
    plt.close("all")

    return figureList




#
# This statement below ensures that the unitTestScript can be run as a
# stand-alone python script
#
if __name__ == "__main__":
    
    timeInitString = str(sat_data.epoch)
    #timeInitString = '2025 MAY 04 07:47:48.965 (UTC)'
    init_position = [-4963946.392216118, 4601467.815050239, -1311445.5818653065]
    init_velocity = [1731.502687329283, -238.55435888532116, -7398.92444558897] 
    init_MRP_attitude = [[0.1], [0.2], [-0.3]]  # sigma_BN_B
    init_ang_velocity = [[0.05], [-0.1], [0.05]]
    rI = [16.50e7, 71145.23, 457069.94,
        71145.23, 15.96e7, 310717.76,
        457069.94, 310717.76, 65.18e6]

    run(
        True,  # show_plots
        False,  # livestream
        step_time = 1.0,
        stop_time = 259200.0,
        rI = rI,
        init_pos = init_position,
        init_vel = init_velocity,
        init_att = init_MRP_attitude,
        init_ang_vel = init_ang_velocity,
        init_timestring = timeInitString
    )
