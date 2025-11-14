#!/usr/bin/env python3
from hardware.usb_attenuator import USBAttenuator

print("Testing USB Attenuator...")
try:
    attenuator = USBAttenuator()
    print(f" Connected: {attenuator.get_model_name()}")
    print(f"  Serial: {attenuator.get_serial_number()}")
    print()
    
    # Test setting attenuation
    print("Setting channel 1 to 25 dB...")
    attenuator.set_attenuation(1, 25.0)
    
    # Read it back
    current = attenuator.get_attenuation(1)
    print(f"Current attenuation: {current} dB")
    
    # Test a few values
    print("\nTesting different values:")
    for value in [10, 30, 50, 70]:
        attenuator.set_attenuation(1, value)
        actual = attenuator.get_attenuation(1)
        print(f"  Set {value} dB → Read {actual} dB")
    
    print("\n All tests passed!")
    
except Exception as e:
    print(f" Error: {e}")
    import traceback
    traceback.print_exc()