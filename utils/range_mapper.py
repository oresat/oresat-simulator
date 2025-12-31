"""
Range to Attenuation Mapper
Converts satellite range to RF attenuation
"""
import numpy as np


class RangeToAttenuationMapper:
    """
    Maps satellite slant range to RF attenuation values.
    Uses Free Space Path Loss (FSPL) model.
    """
    
    def __init__(self, frequency_mhz=2400.0, 
                 min_range_km=200.0, 
                 max_range_km=3000.0,
                 min_attenuation_db=10.0, 
                 max_attenuation_db=90.0):
        """
        Args:
            frequency_mhz: RF frequency in MHz (e.g., 2400 for S-band)
            min_range_km: Minimum range (close - strong signal)
            max_range_km: Maximum range (far - weak signal)
            min_attenuation_db: Attenuation when close (strong signal)
            max_attenuation_db: Attenuation when far (weak signal)
        """
        self.frequency_mhz = frequency_mhz
        self.min_range_km = min_range_km
        self.max_range_km = max_range_km
        self.min_attenuation_db = min_attenuation_db
        self.max_attenuation_db = max_attenuation_db
        
        # Pre-calculate FSPL at min and max range
        self.fspl_at_min = self._calculate_fspl(min_range_km)
        self.fspl_at_max = self._calculate_fspl(max_range_km)
    
    def _calculate_fspl(self, range_km):
        """
        Calculate Free Space Path Loss.
        FSPL (dB) = 20*log10(d_km) + 20*log10(f_MHz) + 32.45
        """
        if range_km <= 0:
            return 0.0
        
        fspl = 20.0 * np.log10(range_km) + 20.0 * np.log10(self.frequency_mhz) + 32.45
        return fspl
    
    def range_to_attenuation(self, range_km, has_access=True):
        """
        Convert range to attenuation.
        
        Args:
            range_km: Slant range in kilometers
            has_access: Whether satellite is visible
            
        Returns:
            Attenuation in dB
        """
        # No access = max attenuation (no signal)
        if not has_access or range_km <= 0:
            return self.max_attenuation_db
        
        # Clamp range
        range_km = np.clip(range_km, self.min_range_km, self.max_range_km)
        
        # Calculate FSPL
        fspl = self._calculate_fspl(range_km)
        
        # Map to attenuation range
        fspl_range = self.fspl_at_max - self.fspl_at_min
        if fspl_range > 0:
            normalized = (fspl - self.fspl_at_min) / fspl_range
        else:
            normalized = 0.0
        
        attenuation = self.min_attenuation_db + normalized * (self.max_attenuation_db - self.min_attenuation_db)
        
        return round(attenuation, 1)