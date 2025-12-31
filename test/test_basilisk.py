#!/usr/bin/env python3
from simulation.basilisk_setup import BasiliskSimulation
import time

print("Testing Complete Basilisk Simulation...")
print("="*60)

try:
    # Create simulation
    sim = BasiliskSimulation(time_step_sec=1.0)
    print("Simulation created")
    
    # Add spacecraft
    sim.add_spacecraft(mass_kg=50.0)
    print("Spacecraft added")
    
    # Add gravity
    sim.add_gravity_model(use_j2=True)
    print("Gravity model added")
    
    # Set orbit (ISS-like)
    sim.set_orbit(altitude_km=418, inclination_deg=51.6)
    print("Orbit set (418 km, 51.6° inclination)")
    
    # Add ground station (Boulder, CO)
    sim.add_ground_station(
        name="Boulder",
        latitude_deg=40.009971,
        longitude_deg=-105.243895,
        altitude_m=1624,
        min_elevation_deg=10.0
    )
    print("Ground station added (Boulder, CO)")
    
    # Initialize
    sim.initialize()
    print("Simulation initialized")
    
    print("\n" + "="*60)
    print("Running simulation for 60 seconds...")
    print("="*60)
    
    # Run for 60 seconds
    for i in range(60):
        sim_time_ns = (i + 1) * int(1e9)  # Convert to nanoseconds
        sim.step(sim_time_ns)
        
        # Get access info
        access = sim.get_ground_station_access()
        
        # Print every 10 seconds
        if (i + 1) % 10 == 0:
            if access['has_access']:
                print(f"[t={i+1:3d}s]  ACCESS | "
                      f"Range: {access['slant_range_km']:7.1f} km | "
                      f"El: {access['elevation_deg']:5.1f}° | "
                      f"Az: {access['azimuth_deg']:6.1f}°")
            else:
                print(f"[t={i+1:3d}s] NO ACCESS")
    
    print("\n" + "="*60)
    print("Simulation complete!")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()