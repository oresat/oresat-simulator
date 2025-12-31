import serial
import time


class SolarSimulator:
    """
    Interface for solar simulator hardware via UART/Serial.
    Controls light intensity to simulate sun at different distances.
    """
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1.0):
        """
        Initialize solar simulator connection.
        
        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM3' on Windows)
            baudrate: Baud rate (common: 9600, 19200, 38400, 115200)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.current_intensity = 0.0
        
        self._connect()
        self._initialize()
    
    def _connect(self):
        """Establish serial connection."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(0.1)  # Wait for connection to stabilize
            
            # Flush buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to solar simulator on {self.port}: {e}")
    
    def _initialize(self):
        """Initialize simulator and read current state."""
        # Query current intensity
        try:
            self.current_intensity = self.get_intensity()
        except:
            self.current_intensity = 0.0
    
    def _send_command(self, command):
        """
        Send command to solar simulator.
        
        Args:
            command: Command string to send
            
        Returns:
            Response string from simulator
        """
        if not self.serial or not self.serial.is_open:
            raise IOError("Serial port not open")
        
        # Add newline if not present
        if not command.endswith('\n'):
            command += '\n'
        
        # Send command
        self.serial.write(command.encode('ascii'))
        self.serial.flush()
        
        # Read response
        time.sleep(0.05)  # Short delay for device to respond
        response = self.serial.readline().decode('ascii').strip()
        
        return response
    
    def set_intensity(self, intensity_percent):
        """
        Set light intensity.
        
        Args:
            intensity_percent: Light intensity 0-100%
        """
        # Clamp to valid range
        intensity_percent = max(0.0, min(100.0, float(intensity_percent)))
        
        # Format command (adjust based on your simulator's protocol)
        command = f"INTENSITY:{intensity_percent:.1f}"
        
        response = self._send_command(command)
        
        # Verify command accepted
        if "OK" in response or "ACK" in response:
            self.current_intensity = intensity_percent
        else:
            raise IOError(f"Failed to set intensity. Response: {response}")
        
        return response
    
    def get_intensity(self):
        """
        Query current light intensity.
        
        Returns:
            Current intensity in percent (0-100)
        """
        command = "INTENSITY?"
        response = self._send_command(command)
        
        try:
            # Parse response (adjust based on your simulator's format)
            intensity = float(response.split(':')[-1].strip())
            self.current_intensity = intensity
            return intensity
        except ValueError:
            raise ValueError(f"Invalid intensity response: {response}")
    
    def set_on(self):
        """Turn light on."""
        command = "LIGHT:ON"
        response = self._send_command(command)
        return response
    
    def set_off(self):
        """Turn light off."""
        command = "LIGHT:OFF"
        response = self._send_command(command)
        return response
    
    def get_status(self):
        """
        Get simulator status.
        
        Returns:
            dict with status information
        """
        return {
            'port': self.port,
            'baudrate': self.baudrate,
            'connected': self.serial.is_open if self.serial else False,
            'intensity': self.current_intensity
        }
    
    def close(self):
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.set_off()  # Turn off before closing
            self.serial.close()
    
    def __repr__(self):
        return f"SolarSimulator(port={self.port}, intensity={self.current_intensity}%)"
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.close()
