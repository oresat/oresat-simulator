
import inspect
import os
import argparse

import numpy as np
from matplotlib import pyplot as plt

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
bskName = 'Basilisk'
splitPath = path.split(bskName)

# Import all of the modules that we are going to be called in this simulation
from Basilisk.simulation import (simplePowerSink, simpleBattery, simpleSolarPanel,
                                eclipse, spacecraft, magneticFieldWMM, groundLocation, simSynch)
from Basilisk.utilities import (macros, orbitalMotion, simIncludeGravBody,
                               astroFunctions, unitTestSupport, SimulationBaseClass)
from Basilisk.architecture import astroConstants

from Basilisk import __path__
bskPath = __path__[0]

path = os.path.dirname(os.path.abspath(__file__))

# anything attribute that has "OutMsgs" will have a .recorder() function to generate a log
# see message payloads for attributes to get data from


class BasiliskWrapper:
    """
    Basilisk spacecraft simulation Wrapper for creating quick simulations.
    """
    
    def __init__(self, time_step_sec=1.0):
        """
        Initialize simulation.
        
        Args:
            time_step_sec: Simulation time step in seconds
        """
        self.time_step_sec = time_step_sec
        self.scSim = None
        self.task_name = None
        self.dtN = None
        self.spacecraft = None
        self.gravity_factory = None
        self.earth = None
        self.spice = None
        self.ground_station = None
        self.clock_sync = None
        
        self._create_simulation()

    def _create_simulation(self):
        """Create simulation base structure.
    # Simulation
    #   └── Process ("simProcess")
    #        └── Task ("simTask", runs every 1 sec)
    #             └── Models (spacecraft, earth, ground station...)
        
        """
        # Create main simulation object
        self.scSim = SimulationBaseClass.SimBaseClass()
        
        # Create a process (think of it as a "thread" for simulation)
        dynProcess = self.scSim.CreateNewProcess("simProcess")
        
        # Convert time step to nanoseconds (Basilisk uses nanoseconds internally)
        self.dtN = macros.sec2nano(self.time_step_sec)
        
        # Create a task (a scheduled job that runs every dtN nanoseconds)
        self.task_name = "simTask"
        task = self.scSim.CreateNewTask(self.task_name, self.dtN)
        
        # Add task to process
        dynProcess.addTask(task)

    def add_spacecraft(self, mass_kg=50.0, inertia_xx=60.0, inertia_yy=30.0, inertia_zz=40.0):
            """
            Add spacecraft to simulation.
            
            Args:
                mass_kg: Spacecraft mass in kg
                inertia_xx, inertia_yy, inertia_zz: Principal moments of inertia in kg⋅m²
            """
            # Create spacecraft object
            self.spacecraft = spacecraft.Spacecraft()
            self.spacecraft.ModelTag = "bskSat"
            
            # Set mass
            self.spacecraft.hub.mHub = mass_kg
            
            # Set inertia matrix (3x3 diagonal matrix)
            inertia_matrix = unitTestSupport.np2EigenMatrix3d([
                inertia_xx, 0, 0,
                0, inertia_yy, 0,
                0, 0, inertia_zz
            ])
            self.spacecraft.hub.IHubPntBc_B = inertia_matrix
            
            # Add to simulation task
            self.scSim.AddModelToTask(self.task_name, self.spacecraft)

    def add_gravity_model(self, use_j2=True, time_init_utc="2020 MAY 21 18:28:03 (UTC)"):
            """
            Add gravity model and SPICE interface.
            
            Args:
                use_j2: Whether to use J2 gravity perturbation (Earth's bulge effect)
                time_init_utc: Simulation start time in UTC
            """
            # Create gravity factory (manages celestial bodies)
            self.gravity_factory = simIncludeGravBody.gravBodyFactory()
            
            # Create Earth
            self.earth = self.gravity_factory.createEarth()
            self.earth.isCentralBody = True  # Earth is at the center
            
            # Add J2 perturbation if requested
            if use_j2:
                gravity_file = bskPath + '/supportData/LocalGravData/GGM03S-J2-only.txt'
                self.earth.useSphericalHarmonicsGravityModel(gravity_file, 2)
            
            # Create SPICE interface (provides planetary positions over time)
            self.spice = self.gravity_factory.createSpiceInterface(time=time_init_utc)
            
            # Add SPICE to simulation (priority -1 means it runs first)
            self.scSim.AddModelToTask(self.task_name, self.spice, -1)
            
            # Attach gravity to spacecraft
            if self.spacecraft:
                self.gravity_factory.addBodiesTo(self.spacecraft)

    def set_orbit(self, altitude_km=418, eccentricity=0.00061, 
                    inclination_deg=51.6418, raan_deg=119.2314,
                    arg_periapsis_deg=337.8329, true_anomaly_deg=22.2753):
            """
            Set spacecraft orbital elements.
            
            Args:
                altitude_km: Orbit altitude above Earth surface in km
                eccentricity: Orbital eccentricity (0 = circle, <1 = ellipse)
                inclination_deg: Inclination in degrees (0 = equatorial)
                raan_deg: Right ascension of ascending node in degrees
                arg_periapsis_deg: Argument of periapsis in degrees
                true_anomaly_deg: True anomaly in degrees (position in orbit)
            """
            if not self.spacecraft or not self.earth:
                raise RuntimeError("Spacecraft and gravity must be added before setting orbit")
            
            # Calculate semi-major axis from altitude
            radius_earth_m = astroConstants.REQ_EARTH * 1e3  # Earth radius in meters
            semi_major_axis = radius_earth_m + altitude_km * 1e3
            
            # Create orbital elements object
            oe = orbitalMotion.ClassicElements()
            oe.a = semi_major_axis
            oe.e = eccentricity
            oe.i = np.deg2rad(inclination_deg)
            oe.Omega = np.deg2rad(raan_deg)
            oe.omega = np.deg2rad(arg_periapsis_deg)
            oe.f = np.deg2rad(true_anomaly_deg)
            
            # Convert orbital elements to position and velocity
            mu = self.earth.mu  # Earth's gravitational parameter
            rN, vN = orbitalMotion.elem2rv(mu, oe)
            
            # Set initial state
            self.spacecraft.hub.r_CN_NInit = rN  # Position vector
            self.spacecraft.hub.v_CN_NInit = vN  # Velocity vector
            
            return oe
    
    def add_ground_station(self, name="GroundStation",
                          latitude_deg=40.009971, longitude_deg=-105.243895, 
                          altitude_m=1624, min_elevation_deg=10.0, 
                          max_range_m=1e9):
        """
        Add ground station to simulation.
        
        Args:
            name: Ground station name
            latitude_deg: Latitude in degrees (North positive)
            longitude_deg: Longitude in degrees (East positive)
            altitude_m: Altitude above sea level in meters
            min_elevation_deg: Minimum elevation angle for visibility in degrees
            max_range_m: Maximum communication range in meters
        """
        if not self.spice:
            raise RuntimeError("SPICE must be initialized before adding ground station")
        
        # Create ground station object
        self.ground_station = groundLocation.GroundLocation()
        self.ground_station.ModelTag = name
        self.ground_station.planetRadius = astroConstants.REQ_EARTH * 1e3
        
        # Set location on Earth
        self.ground_station.specifyLocation(
            np.radians(latitude_deg),
            np.radians(longitude_deg),
            altitude_m
        )
        
        # Set access constraints
        self.ground_station.minimumElevation = np.radians(min_elevation_deg)
        self.ground_station.maximumRange = max_range_m
        
        # Subscribe to planet state (so ground station knows where Earth is)
        self.ground_station.planetInMsg.subscribeTo(self.spice.planetStateOutMsgs[0])
        
        # Add to simulation
        self.scSim.AddModelToTask(self.task_name, self.ground_station)
        
        # Link spacecraft to ground station
        if self.spacecraft:
            self.ground_station.addSpacecraftToModel(self.spacecraft.scStateOutMsg)

    def initialize(self):
            """Initialize the simulation."""
            self.scSim.InitializeSimulation()

        
    def step(self, sim_time_ns):
        """
        Execute one simulation step.
        
        Args:
            sim_time_ns: Target simulation time in nanoseconds
        """
        self.scSim.ConfigureStopTime(sim_time_ns)
        self.scSim.ExecuteSimulation()

    def get_ground_station_access(self):
            """
            Get current ground station access information.
            
            Returns:
                dict: Access information including:
                    - has_access (bool): Whether satellite is visible
                    - slant_range_m (float): Distance to satellite in meters
                    - slant_range_km (float): Distance to satellite in kilometers
                    - elevation_deg (float): Elevation angle in degrees
                    - azimuth_deg (float): Azimuth angle in degrees
            """
            if not self.ground_station:
                raise RuntimeError("Ground station not configured")
            
            # Read the access message from ground station
            access_msg = self.ground_station.accessOutMsgs[-1].read()
            
            return {
                'has_access': bool(access_msg.hasAccess),
                'slant_range_m': float(access_msg.slantRange),
                'slant_range_km': float(access_msg.slantRange) / 1000.0,
                'elevation_deg': np.degrees(float(access_msg.elevation)),
                'azimuth_deg': np.degrees(float(access_msg.azimuth))
            }
        
    def enable_realtime(self, acceleration_factor=1.0):
            """
            Enable real-time clock synchronization.
            
            Args:
                acceleration_factor: Simulation speed multiplier (1.0 = real-time)
            """
            self.clock_sync = simSynch.ClockSynch()
            self.clock_sync.accelFactor = acceleration_factor
            self.scSim.AddModelToTask(self.task_name, self.clock_sync)


def get_satellite(modelTag, rI, init_pos=None, init_vel=None, init_att=None, init_ang_vel=None):
    '''
        rI = Rotational Inertia of Sat
        init_pos = initial position in ECI
        init_vel = initial velocity in ECI
        init_att = initial attitude in MRP
        init_ang_vel = initial angular velocities
    returns
        scObject (satellite)
    '''
    satellite = spacecraft.Spacecraft()
    satellite.ModelTag = modelTag
   # I = [16.50e7, 71145.23, 457069.94,
    #     71145.23, 15.96e7, 310717.76,
     #    457069.94, 310717.76, 65.18e6]
    satellite.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(rI)
    if init_pos is not None:
        satellite.hub.r_CN_NInit = init_pos
    if init_vel is not None:
        satellite.hub.v_CN_NInit = init_vel
    if init_att is not None:
        satellite.hub.sigma_BNInit = init_att
    if init_ang_vel is not None:
        satellite.hub.omega_BN_BInit = init_ang_vel

    satMsg = satellite.scStateOutMsg
    satLog = satMsg.recorder() 
    return satellite, satMsg, satLog



def get_gravity_factory_earth(scObject):
    ''' Adds gravity parameters to scenario object

    args:
        scObject: scenario object (satellite)

    returns:
        gravityFactory
    '''
    # setup Gravity Body
    gravFactory = simIncludeGravBody.gravBodyFactory()
    planet = gravFactory.createEarth()
    planet.isCentralBody = True          # ensure this is the central gravitational body
    mu = planet.mu
    # attach gravity model to spacecraft
    gravFactory.addBodiesTo(scObject)
    return gravFactory


def get_spice_earth_sun(scObject, timeInitString, zeroBase='Earth'):

    '''
        timeInitString:
        zeroBase: Where to place the coordinate system, earth by default
    '''
   # clear prior gravitational body and SPICE setup definitions
    gravFactory = simIncludeGravBody.gravBodyFactory()

    planet = gravFactory.createEarth()
    planet.isCentralBody = True          # ensure this is the central gravitational body
    mu = planet.mu
    sun = gravFactory.createSun()
    # attach gravity model to spacecraft
    gravFactory.addBodiesTo(scObject)

    # setup Spice interface for some solar system bodies
    spiceObject = gravFactory.createSpiceInterface(time=timeInitString)
    spiceObject.zeroBase = zeroBase
    
    plMsg = spiceObject.planetStateOutMsgs[0]
    plLog = plMsg.recorder()
    
    sunMsg = spiceObject.planetStateOutMsgs[1]
    sunLog = sunMsg.recorder()

    return spiceObject, plMsg, plLog, sunMsg, sunLog


def get_mag_model(modelTag, scObject):
    '''
    args:
        scObject: scenario object (satellite)

    returns
        magnetic field model
        magnetic field recorder (log)
    '''
    # create the magnetic field
    magModule = magneticFieldWMM.MagneticFieldWMM()
    magModule.ModelTag = modelTag
    magModule.dataPath = bskPath + '/supportData/MagneticField/'
    magModule.addSpacecraftToModel(scObject.scStateOutMsg)  # this command can be repeated if multiple
    magMsg = magModule.envOutMsgs[0]
    magLog = magMsg.recorder()
    return magModule, magMsg, magLog




def get_eclipse_model(modelTag, scObjectMsg, sunMsg, planetMsg):
    '''
        scObjectMsg: satellite messages
        sourceObjectMsg: sun messages
        sinkObjectMsg: earth (or planet) messages
    ''' 
    eclipseObject = eclipse.Eclipse()
    eclipseObject.ModelTag = modelTag
    eclipseObject.addSpacecraftToModel(scObjectMsg)
    eclipseObject.addPlanetToModel(planetMsg)
    eclipseObject.sunInMsg.subscribeTo(sunMsg)

    eclipseMsg = eclipseObject.eclipseOutMsgs[0]
    eclipseLog = eclipseMsg.recorder()
    return eclipseObject, eclipseMsg, eclipseLog






def get_power_sink(modelTag, nodePowerOut):
    '''
        modelTag: name for model
        nodePowerOut: power output in watts. Negative means it consumes power
    '''
    powerSink = simplePowerSink.SimplePowerSink()
    powerSink.ModelTag = modelTag
    powerSink.nodePowerOut = -3.  # Watts

    return powerSink




def get_solar_panel(modelTag, scObjectMsg, eclipseMsg, sunMsg, parameters):
    '''
        modelTag: name for model
        scObjectMsg: satellite messages
        eclipseMsg: eclipse messages
        sunMsg: sun messages
        parameters: additional parameters [normal vector body ref frame, area, something]

    returns
        solarPanel: simpleSolarPanel()
        solarPanelMsg: nodePowerOutMsg
        solarPanelLog: nodePowerOutMsg.recorder()
    '''
    solarPanel = simpleSolarPanel.SimpleSolarPanel()
    solarPanel.ModelTag = modelTag
    solarPanel.stateInMsg.subscribeTo(scObjectMsg)
    solarPanel.sunEclipseInMsg.subscribeTo(eclipseMsg)
    solarPanel.sunInMsg.subscribeTo(sunMsg)
    solarPanel.setPanelParameters(*parameters)
    
    return solarPanel


def get_power_monitor(modelTag, capacity, init_charge):
    '''
        capacity: storage capacity in joules
        init_charge: initial charge in joules
        power_nodes: list of power nodes to add. must have the nodePowerOutMsg attribute
    '''
    powerMonitor = simpleBattery.SimpleBattery()
    powerMonitor.ModelTag = modelTag
    powerMonitor.storageCapacity = capacity
    powerMonitor.storedCharge_Init = init_charge
    return powerMonitor



