#!/usr/bin/env python3
from simulation.basilisk_setup import BasiliskSimulation
from hardware.usb_attenuator import USBAttenuator
from utils.range_mapper import RangeToAttenuationMapper
import time

print("Integrated Satellite Link Simulator with Attenuator")
print("="*70)

# Initialize Attenuator
use_attenuator = True
attenuator = None
channel = 1

if use_attenuator:
    try:
        print("\nConnecting to USB Attenuator...")
        attenuator = USBAttenuator()
        print(f"  Model: {attenuator.get_model_name()}")
        print(f"  Serial: {attenuator.get_serial_number()}")
        print(f"  Channel: {channel}")
        attenuator.set_attenuation(channel, 95.0)  # Start at max
        print(f"  Initial: 95.0 dB")
    except Exception as e:
        print(f"  Attenuator error: {e}")
        print(f"  Continuing without hardware")
        use_attenuator = False

# Initialize Range Mapper
print("\n Initializing Range Mapper...")
mapper = RangeToAttenuationMapper(
    frequency_mhz=2400,
    min_range_km=200,
    max_range_km=3000,
    min_attenuation_db=10,
    max_attenuation_db=90
)
print(f"  Frequency: 2400 MHz")
print(f"  Range: 200-3000 km")
print(f"  Attenuation: 10-90 dB")

# Initialize Basilisk Simulation
print("\n Initializing Basilisk Simulation...")
sim = BasiliskSimulation(time_step_sec=1.0)
sim.add_spacecraft(mass_kg=50.0)
sim.add_gravity_model(use_j2=True, time_init_utc="2020 MAY 21 12:00:00 (UTC)")

sim.set_orbit(
    altitude_km=550,
    eccentricity=0.001,
    inclination_deg=90.0,
    raan_deg=0.0,
    arg_periapsis_deg=0.0,
    true_anomaly_deg=0.0
)

sim.add_ground_station(
    name="Boulder",
    latitude_deg=40.009971,
    longitude_deg=-105.243895,
    min_elevation_deg=5.0
)

sim.enable_realtime(acceleration_factor=1.0)
sim.initialize()

print(f"  Orbit: 550 km polar (90°)")
print(f"  Ground Station: Boulder, CO")
print(f"  Real-time: Enabled")

print("\n" + "="*70)
print("Starting Real-Time Simulation (Ctrl+C to stop)")
print("="*70 + "\n")

duration_sec = 6000
sim_t_ns = 0
end_ns = int(duration_sec * 1e9)
step_ns = sim.dtN

try:
    wall_start = time.time()
    while sim_t_ns < end_ns:
        sim_t_ns += step_ns
        sim.step(sim_t_ns)

        # Get access information
        access = sim.get_ground_station_access()
        has_access = access['has_access']
        range_km = access['slant_range_km']
        elev_deg = access['elevation_deg']
        az_deg = access['azimuth_deg']
        
        # Calculate attenuation from range
        atten_db = mapper.range_to_attenuation(range_km, has_access)
        
        # Update hardware attenuator
        if use_attenuator and attenuator:
            try:
                attenuator.set_attenuation(channel, atten_db)
            except Exception as e:
                print(f"  Attenuator error: {e}")
        
        # Print status
        sim_sec = sim_t_ns * 1e-9
        status = "OK" if has_access else "NO"
        print(f"[t={sim_sec:6.0f}s] {status} access={int(has_access)}  "
              f"range={range_km:8.2f} km  "
              f"az={az_deg:7.2f}°  el={elev_deg:6.2f}°  "
              f"atten={atten_db:4.1f}dB")

except KeyboardInterrupt:
    print("\n\nStopped by user")

finally:
    # Reset attenuator to safe state
    if use_attenuator and attenuator:
        print("\nResetting attenuator...")
        try:
            attenuator.set_attenuation(channel, 95.0)
            print(" Attenuator reset to 95 dB (safe state)")
        except:
            pass

print("\n Done!")