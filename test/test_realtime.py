#!/usr/bin/env python3
from simulation.basilisk_setup import BasiliskSimulation
import time

print("Testing with POLAR orbit (guaranteed to pass over Boulder)")
print("="*70)

# Create simulation
sim = BasiliskSimulation(time_step_sec=1.0)
sim.add_spacecraft(mass_kg=50.0)
sim.add_gravity_model(use_j2=True, time_init_utc="2020 MAY 21 12:00:00 (UTC)")

# Use POLAR orbit (90° inclination) - passes over ALL latitudes
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
    min_elevation_deg=5.0  # Lower threshold
)
                
sim.enable_realtime(acceleration_factor=1.0)
sim.initialize()

print("Using 550 km polar orbit (90° inclination)")
print("This orbit WILL pass over Boulder")
print("Searching...\n")


duration_sec = 6000

# 6) Incremental execution loop
print("Starting realtime ground range printout (Ctrl+C to stop)...")
sim_t_ns = 0
end_ns = int(duration_sec * 1e9)
step_ns = sim.dtN

try:
    while sim_t_ns < end_ns:
        sim_t_ns += step_ns
        sim.step(sim_t_ns)

        # Read current ground access message
        access = sim.get_ground_station_access()
        sim_sec = sim_t_ns * 1e-9
        print(f" [t={sim_sec:6.0f}s] Range: {access['slant_range_km']:.1f} km")
        # Print out data every sec



except KeyboardInterrupt:
    print("\nStopped by user.")


print("\n Done!")