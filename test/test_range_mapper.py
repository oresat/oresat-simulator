#!/usr/bin/env python3
from utils.range_mapper import RangeToAttenuationMapper

print("Testing Range to Attenuation Mapper")
print("="*60)

# Create mapper for S-band (2400 MHz)
mapper = RangeToAttenuationMapper(
    frequency_mhz=2400,
    min_range_km=200,
    max_range_km=3000,
    min_attenuation_db=10,
    max_attenuation_db=90
)

print(f"Frequency: {mapper.frequency_mhz} MHz")
print(f"Range: {mapper.min_range_km} - {mapper.max_range_km} km")
print(f"Attenuation: {mapper.min_attenuation_db} - {mapper.max_attenuation_db} dB\n")

# Test different ranges
test_ranges = [200, 500, 1000, 1500, 2000, 2500, 3000]

print(f"{'Range (km)':<12} {'FSPL (dB)':<12} {'Attenuation (dB)'}")
print("-" * 45)

for r in test_ranges:
    fspl = mapper._calculate_fspl(r)
    atten = mapper.range_to_attenuation(r, has_access=True)
    print(f"{r:<12} {fspl:<12.2f} {atten}")

print("\n Range mapper working!")