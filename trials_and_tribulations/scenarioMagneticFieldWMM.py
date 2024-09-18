#!/usr/bin/env python3
#
#  ISC License
#
#  Copyright (c) 2016, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

r"""
Overview
--------

This script sets up a 3-DOF spacecraft which is orbiting the with a
magnetic field model.  This scenario is similar to the centered dipole model
:ref:`scenarioMagneticFieldCenteredDipole`, but here
the World Magnetic Model (WMM) is employed.  This model is specific
to Earth and not suitable for other planets. The purpose
is to illustrate how to create and setup the WMM magnetic field,
as well as determine the
magnetic field at a spacecraft location.  The orbit setup is similar to that used in
:ref:`scenarioBasicOrbit`.

The script is found in the folder ``basilisk/examples`` and executed by using::

    python3 scenarioMagneticFieldWMM.py

Simulation Scenario Setup Details
---------------------------------

The simulation layout is shown in the following illustration.  A single simulation process is created
which contains the spacecraft object.  The spacecraft state message is connected to the magnetic field
module which outputs the local magnetic field in inertial frame components.

.. image:: /_images/static/test_scenario_MagneticFieldWMM.svg
   :align: center

When the simulation completes 2 plots are shown for each case.  One plot always shows
the inertial position vector components, while the second plot
shows the local magnetic field
vector components with respect to the inertial frame.

As this :ref:`MagneticFieldWMM` model is specific to Earth, there are
no parameters to set of tune.  Rather, the ``WMM.COF`` WMM coefficient
file is loaded from the ``dataPath`` variable.

The default planet's position vector is assumed to be the inertial
frame origin and an identity orientation matrix.
If a different planet state message is required this can be
specified through the optional input message ``planetPosInMsg``.

As with :ref:`scenarioMagneticFieldCenteredDipole`, the magnetic
field module can produce the magnetic field for a vector of spacecraft
locations, not just for a single spacecraft.

The WMM module requires an epoch time to determine the magnetic field.
If this is not set, then the BSK
default epoch time is used.  To set a general epoch time, the module
can read in an epoch message with a
gregorian UTC date.  This is set using the support method
``timeStringToGregorianUTCMsg``.

The WMM model is driven of a time variable that is a decimal year value.
The module can set this as well by specifying the module parameter
``epochDateFractionalYear``.  However, note that if the epoch message is
specified, the message information is used instead of the
``epochDateFractionalYear`` variable.

Every time a spacecraft is added to the magnetic field module, an
extra output message is autmatically created. For `magModule` is "WMM_0_data"
as the ModelTag string is ``WMM`` and the spacecraft number is 0.
This output name is created in the  ``addSpacecraftToModel()``
function.  However, if the default output name is used for the second
planetary magnetic field model, then both module share  the same
output name and one will overwrite the others output.

The reach of the magnetic field model is specified through the
module variables ``envMinReach`` and ``envMaxReach``. Their
default values are -1 which turns off this feature, giving
the magnetic field evaluation infinite reach.

Illustration of Simulation Results
----------------------------------

The following images illustrate the expected simulation run returns for a range of script configurations.

::

    show_plots = True, orbitCase='circular'

.. image:: /_images/Scenarios/scenarioMagneticFieldWMM1circular.svg
   :align: center

.. image:: /_images/Scenarios/scenarioMagneticFieldWMM2circular.svg
   :align: center

::

   show_plots = True, orbitCase='elliptical'

.. image:: /_images/Scenarios/scenarioMagneticFieldWMM1elliptical.svg
   :align: center

.. image:: /_images/Scenarios/scenarioMagneticFieldWMM2elliptical.svg
   :align: center

"""

#
# Basilisk Scenario Script and Integrated Test
#
# Purpose:  Integrated test illustrating how to use a world magnetic model (WMM) for spacecraft about Earth.
# Author:   Hanspeter Schaub
# Creation Date:  March 16, 2019
#

import os

import matplotlib.pyplot as plt
import numpy as np
# The path to the location of Basilisk
# Used to get the location of supporting data.
from Basilisk import __path__

bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])


# import simulation related support
from Basilisk.simulation import spacecraft
from Basilisk.simulation import magneticFieldWMM
# general support file with common unit test functions
# import general simulation support files
from Basilisk.utilities import (SimulationBaseClass, macros, orbitalMotion,
                                simIncludeGravBody, unitTestSupport)

#attempt to import vizard
from Basilisk.utilities import vizSupport

import parse_tle

def run(show_plots, orbitCase):
    """
    At the end of the python script you can specify the following example parameters.

    Args:
        show_plots (bool): Determines if the script should display plots
        orbitCase (str): {'circular', 'elliptical'}

    """

    sat_oe = parse_tle.Tle("tle.txt")
    sat_oe._parse_tle()

    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()

    #
    #  create the simulation process
    #
    dynProcess = scSim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(60.) #TODO check
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    #
    #   setup the simulation tasks/objects
    #

    # initialize spacecraft object and set properties
    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = "bsk-Sat"

    # add spacecraft object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject)

    # setup Gravity Body
    gravFactory = simIncludeGravBody.gravBodyFactory()
    planet = gravFactory.createEarth()
    planet.isCentralBody = True          # ensure this is the central gravitational body
    mu = planet.mu #sat_oe.mu #
    #print("mu from sim file:", mu)
    earth_rad = planet.radEquator #radius of the earth in meters

    # attach gravity model to spacecraft
    gravFactory.addBodiesTo(scObject)

    # create the magnetic field
    magModule = magneticFieldWMM.MagneticFieldWMM()
    magModule.ModelTag = "WMM"
    magModule.dataPath = bskPath + '/supportData/MagneticField/'

    # set the minReach and maxReach values if on an elliptic orbit
    # if orbitCase == 'elliptical':
    #     magModule.envMinReach = 10000*1000.
    #     magModule.envMaxReach = 20000*1000.

    # set epoch date/time message
    # epochMsg = unitTestSupport.timeStringToGregorianUTCMsg('2019 June 27, 10:23:0.0 (UTC)') #sat_oe.epoch
    #TODO
    #FIXME
    epochMsg = unitTestSupport.timeStringToGregorianUTCMsg('2024 August 13, 12:35:35.0 (UTC)') #sat_oe.epoch

    # add spacecraft to the magnetic field module so it can read the sc position messages
    magModule.addSpacecraftToModel(scObject.scStateOutMsg)  # this command can be repeated if multiple

    # add the magnetic field module to the simulation task stack
    scSim.AddModelToTask(simTaskName, magModule)

    #
    #   setup orbit and simulation time
    #
    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    rPeriapses = sat_oe.perigee * 1000 #6741e3 [m]
    if orbitCase == 'circular':
        oe.a = rPeriapses
        oe.e = 0.0000
    elif orbitCase == 'elliptical':
        rApoapses =  sat_oe.apogee * 1000 # 6749e3 [m]
        oe.a = sat_oe.semimajor_axis * 1000 # 6745e3 [m]
        oe.e = sat_oe.excentricity # 0.0006004
    else:
        print("Unsupported orbit type " + orbitCase + " selected")
        exit(1)
    oe.i = sat_oe.inclination * macros.D2R #97.48
    oe.Omega = sat_oe.right_ascension * macros.D2R #243.87
    oe.omega = sat_oe.arg_perigee * macros.D2R #35.98
    oe.f = sat_oe.true_anomaly * macros.D2R #324.18

    # print(f"Semi-major ax = {oe.a}")

    rN, vN = orbitalMotion.elem2rv(mu, oe)
    # next lines stores consistent initial orbit elements
    # with circular or equatorial orbit, some angles are arbitrary
    # oe = orbitalMotion.rv2elem(mu, rN, vN)

    #
    #   initialize Spacecraft States with the initialization variables
    #
    scObject.hub.r_CN_NInit = rN  # m   - r_BN_N
    scObject.hub.v_CN_NInit = vN  # m/s - v_BN_N

    # set the simulation time
    n = np.sqrt(mu / oe.a**3)
    P = 2. * np.pi / n
    simulationTime = macros.sec2nano(1. * P)
    # print("period:", P)
    # print("simulation time:", simulationTime)

    # connect messages
    magModule.epochInMsg.subscribeTo(epochMsg)

    #
    #   Setup data logging before the simulation is initialized
    #
    numDataPoints = 100
    samplingTime = unitTestSupport.samplingTime(simulationTime, simulationTimeStep, numDataPoints)
    dataLog = scObject.scStateOutMsg.recorder(samplingTime)
    magLog = magModule.envOutMsgs[0].recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, dataLog)
    scSim.AddModelToTask(simTaskName, magLog)

    # if this scenario is to interface with the BSK Viz, uncomment the following line
    if vizSupport.vizFound:
        viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObject,
                                                  # saveFile=fileName,
                                                  )
        viz.epochInMsg.subscribeTo(epochMsg)

        viz.settings.show24hrClock = 1
        viz.settings.showDataRateDisplay = 1

    scSim.InitializeSimulation()

    #
    #   configure a simulation stop time and execute the simulation run
    #
    scSim.ConfigureStopTime(simulationTime)
    scSim.ExecuteSimulation()

    #
    #   retrieve the logged data
    #
    magData = magLog.magField_N
    posData = dataLog.r_BN_N

    np.set_printoptions(precision=16)

    #
    #   plot the results
    #
    # draw the inertial position vector components
    plt.close("all")  # clears out plots from earlier test runs

    timeAxis = dataLog.times() * macros.NANO2SEC
    plt.figure(1)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='sci')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    rData = []
    for idx in range(0, len(posData)):
        rMag = np.linalg.norm(posData[idx])
        rData.append(rMag / 1000.)
    plt.plot(timeAxis / P, rData, color='#aa0000')
    if orbitCase == 'elliptical':
        plt.plot(timeAxis / P, [magModule.envMinReach/1000.]*len(rData), color='#007700', dashes=[5, 5, 5, 5])
        plt.plot(timeAxis / P, [magModule.envMaxReach / 1000.] * len(rData),
                 color='#007700', dashes=[5, 5, 5, 5])

    plt.xlabel('Time [orbits]')
    plt.ylabel('Radius [km]')
    plt.ylim(min(rData)*0.9, max(rData)*1.1)
    figureList = {}
    pltName = fileName + "1" + orbitCase
    figureList[pltName] = plt.figure(1)

    plt.figure(2)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='sci')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    for idx in range(3):
        plt.plot(timeAxis / P, magData[:, idx] *1e9,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$B\_N_{' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [orbits]')
    plt.ylabel('Magnetic Field [nT]')
    pltName = fileName + "2" + orbitCase
    figureList[pltName] = plt.figure(2)


    if show_plots:
        plt.show()

    # close the plots being saved off to avoid over-writing old and new figures
    plt.close("all")

    #search for output files and documentation
    return magData #figureList

def T_to_mG(data): # need to modify to take data rather than a file - currently need to deal with numpy.ndarray
    #convert each value to mG. 1Tesla = 10^7 mG
    mG_vals = []

    for line in data:
        mG_line = []
        for val in line:
            val = float(val)
            format(val, '.12f')
            val = val * (10000000)
            val = round(val, 4)
            mG_line.append(val)

        mG_vals.append(mG_line)
    print(mG_vals)
    return mG_vals

#Send mG_vals to server
import struct
import socket
import time

#Transform data in mG_vals to bytes
def pack_array_data(array):
    to_send = bytes()
    for item in array:
        for i in range(3):
            to_send += struct.pack('f', item[i])
    return to_send 

#
# This statement below ensures that the unit test script can be run as a
# stand-along python script
#
if __name__ == "__main__":
    loopback = "127.0.0.1" #Allows local data send
    
    port = 40000
    yesno = input("Do you want a graphical display or not? Y/n: ")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        try: 
            sock.connect((loopback, port)) 
                
            while True:
                
                if yesno.upper() == 'Y':
                    data = run(
                        True,          # show_plots
                        'elliptical',  # orbit Case (circular, elliptical)
                    )
                else:
                    data = run(
                        False,          # show_plots
                        'elliptical',  # orbit Case (circular, elliptical)
                    )

                cargo = pack_array_data(T_to_mG(data)) #send mG_vals into function
                                                               #and then return it in byte
                                                               #format
                sock.send(cargo) 
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nClient ended via ctrl-c.\n")
