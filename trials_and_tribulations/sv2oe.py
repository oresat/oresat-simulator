import numpy as np
from scipy.constants import G, pi
from datetime import datetime

# Constants
mu = 398600.4418  # Standard gravitational parameter for Earth in km^3/s^2
mass_of_earth = 5.972 * np.power(10,24) #kg

def state_vectors_to_orbital_elements(position, velocity):
    r = np.linalg.norm(position)
    v = np.linalg.norm(velocity)

    r_dot_v = np.dot(position, velocity)
    
    # Specific orbital energy
    epsilon = (v**2 / 2) - (mu / r)
    
    # Semi-major axis
    a = -mu / (2 * epsilon)
    
    # Angular momentum
    h_vector = np.cross(position, velocity)
    h = np.linalg.norm(h_vector)

    # Eccentricity vector
    e_vector = ((np.cross(velocity, h_vector) / mu) - (position / r))
    e = np.linalg.norm(e_vector)
    
    # Inclination
    i = np.arccos(h_vector[2] / h)
    
    # Longitude of the ascending node
    K = np.array([0, 0, 1])
    N = np.cross(K, h_vector)
    N_mag = np.linalg.norm(N)
    if N_mag != 0:
        Omega = np.arccos(N[0] / N_mag)
        if N[1] < 0:
            Omega = 2 * pi - Omega
    else:
        Omega = 0
    
    # Argument of periapsis
    if N_mag != 0:
        argument_of_periapsis = np.arccos(np.dot(N, e_vector) / (N_mag * e))
        if e_vector[2] < 0:
            argument_of_periapsis = 2 * pi - argument_of_periapsis
    else:
        argument_of_periapsis = 0
    
    # True anomaly
    true_anomaly = np.arccos(np.dot(e_vector, position) / (e * r))
    if np.dot(position, velocity) < 0:
        true_anomaly = 2 * pi - true_anomaly

    # Eccentric Anomaly
    ecc_anomaly = 2 * np.arctan((np.tan((true_anomaly / 2)) / np.sqrt((1+e)/(1-e))))

    # Mean Anomaly
    M = ecc_anomaly - (e * np.sin (ecc_anomaly))

    # Mean Motion in rad/sec
    n = np.sqrt( mu / (a ** 3) )
    
    # We want Mean Motion with revolutions per day
    n_rev_day = n * (86400 / (2 * pi))

    #First Der Of Mean Motion (close basic estimate)
    num = n * (1.08263 * (10 ** (-3))) * (6378.1 ** 2) #last number in km
    den = 2 * (a ** 2) * ((1 - (e ** 2)) ** 2)
    n_dot = (-3 / 2) * (num/den) * (np.cos(i) / a)


    return {
        'semi_major_axis': a,
        'eccentricity': e,
        'inclination': i,
        'longitude_of_ascending_node': Omega,
        'argument_of_periapsis': argument_of_periapsis,
        'true_anomaly': true_anomaly,
        'mean_anomaly': M,
        'mean_motion': n_rev_day,
        'first_der_mean_motion': n_dot
    }

def input_vector(name):
    while True:
        try:
            vector_name = input(f"Enter the {name} vector components (x, y, z) separated by spaces in km: ").split()
            vector = list(map(float, vector_name))
            if len(vector) != 3: raise ValueError
            return np.array(vector)
        except ValueError:
            print("Invalid input. Please enter three numerical values separated by spaces.")

# User input for position and velocity vectors
position = input_vector("position")
velocity = input_vector("velocity")

#Epoch 

from_date = str(input('Enter date(yyyy-mm-dd hh:mm:ss): '))

dt = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
epoch = dt.timestamp() 

# Convert to orbital elements
orbital_elements = state_vectors_to_orbital_elements(position, velocity)

# Print the result
print("\nOrbital Elements:")
print(f"Semi-major axis (a): {orbital_elements['semi_major_axis']:.4f} km")
print(f"Eccentricity (e): {orbital_elements['eccentricity']:.4f}")
print(f"Inclination (i): {np.degrees(orbital_elements['inclination']):.4f} degrees")
print(f"Longitude of Ascending Node (Ω): {np.degrees(orbital_elements['longitude_of_ascending_node']):.4f} degrees")
print(f"Argument of Periapsis (ω): {np.degrees(orbital_elements['argument_of_periapsis']):.4f} degrees")
print(f"True Anomaly (ν): {np.degrees(orbital_elements['true_anomaly']):.4f} degrees")

print("\nTLE format:")
print("OreSAT0.5")
print(f"1 98876 (International Designator) ", epoch, f"{orbital_elements ['first_der_mean_motion']:f}" ,
      " 00000-0 00000+0 0")
print(f"2 (Sat Number w/out classification)", 
      f"{np.degrees(orbital_elements['inclination']):.4f}",
      f"{np.degrees(orbital_elements['longitude_of_ascending_node']):.4f}", 
      f"{orbital_elements['eccentricity']:.4f}" ,
      f"{np.degrees(orbital_elements['argument_of_periapsis']):.4f}",
      f"{np.degrees(orbital_elements['mean_anomaly']):.4f}", 
      f"{orbital_elements['mean_motion']:.4f}", 
      "1")
