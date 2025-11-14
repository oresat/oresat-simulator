"""
USB Attenuator Hardware Interface
"""
import platform
import usb.core
import usb.util


class USBAttenuator:
    """Interface for Mini-Circuits USB attenuators."""
    
    # Class constants - these identify the specific device
    VENDOR_ID = 0x20ce
    PRODUCT_ID = 0x0023
    CMD_BUFFER_SIZE = 64  # Mini-Circuits uses 64-byte buffers
    
    def __init__(self, vendor_id=None, product_id=None):
        """Initialize and connect to the device."""
        # Use provided IDs or fall back to defaults
        self.vendor_id = vendor_id or self.VENDOR_ID
        self.product_id = product_id or self.PRODUCT_ID
        
        # Initialize variables
        self.cmd_buffer = [0] * self.CMD_BUFFER_SIZE
        self.dev = None
        self.serial_number = None
        self.model_name = None
        
        # Connect to device
        self._connect()
        self._initialize()

    def _connect(self):
        """Establish USB connection to the device."""
        # Find the device using vendor and product IDs
        self.dev = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        
        if self.dev is None:
            raise ConnectionError(
                f"USB Attenuator not found (VID: 0x{self.vendor_id:04x}, PID: 0x{self.product_id:04x})"
            )
        
        # Linux needs special handling for kernel drivers
        if platform.system() == "Linux":
            self._detach_kernel_drivers()
        
        # Set USB configuration
        try:
            self.dev.set_configuration()
        except usb.core.USBError as e:
            raise ConnectionError(f"Failed to configure USB device: {e}")
        
    def _detach_kernel_drivers(self):
        """Detach kernel drivers on Linux systems."""
        for configuration in self.dev:
            for interface in configuration:
                ifnum = interface.bInterfaceNumber
                if self.dev.is_kernel_driver_active(ifnum):
                    try:
                        self.dev.detach_kernel_driver(ifnum)
                    except usb.core.USBError:
                        pass  # Already detached or can't detach

    def _initialize(self):
        """Read device information after connection."""
        self.serial_number = self._read_device_info(cmd_code=41)
        self.model_name = self._read_device_info(cmd_code=40)


    def _read_device_info(self, cmd_code):
            """
            Read device information using specific command code.
            
            Args:
                cmd_code: Command code (40=model name, 41=serial number)
                
            Returns:
                Device information string
            """
            # Prepare command buffer
            self.cmd_buffer[0] = cmd_code
            
            # Send command to device (endpoint 0x01)
            self.dev.write(0x01, self.cmd_buffer)
            
            # Read response from device (endpoint 0x81)
            response = self.dev.read(0x81, self.CMD_BUFFER_SIZE)
            
            # Convert response bytes to string (skip first byte, stop at null)
            return "".join(chr(response[i]) for i in range(1, len(response)) if response[i] > 0)

    def get_serial_number(self):
            """Get device serial number."""
            return self.serial_number
        
    def get_model_name(self):
        """Get device model name."""
        return self.model_name
    
    def send_scpi_command(self, command):
        """
        Send SCPI command to the device.
        
        Args:
            command: SCPI command string (e.g., ":CHAN:1:SETATT:30")
            
        Returns:
            Device response string
        """
        # Clear buffer
        self.cmd_buffer = [0] * self.CMD_BUFFER_SIZE
        
        # Set command code for SCPI
        self.cmd_buffer[0] = 42  # 42 = SCPI command code
        
        # Copy command string to buffer (starting at position 1)
        for idx, char in enumerate(command, start=1):
            if idx >= self.CMD_BUFFER_SIZE:
                break
            self.cmd_buffer[idx] = ord(char)
        
        # Add null terminator
        if len(command) + 1 < self.CMD_BUFFER_SIZE:
            self.cmd_buffer[len(command) + 1] = 0
        
        # Send command and read response
        try:
            self.dev.write(0x01, self.cmd_buffer)
            response = self.dev.read(0x81, self.CMD_BUFFER_SIZE)
            return "".join(chr(response[i]) for i in range(1, len(response)) if response[i] > 0)
        except usb.core.USBError as e:
            raise IOError(f"USB communication error: {e}")
        
    def set_attenuation(self, channel, value_db):
            """
            Set attenuation for a specific channel.
            
            Args:
                channel: Channel number (1-4)
                value_db: Attenuation value in dB (0-95)
                
            Returns:
                Device response string
            """
            if not 1 <= channel <= 4:
                raise ValueError(f"Invalid channel {channel}. Must be 1-4.")
            
            # Clamp value to valid range
            value_db = max(0, min(95, float(value_db)))
            
            command = f":CHAN:{channel}:SETATT:{value_db}"
            return self.send_scpi_command(command)
        
    def get_attenuation(self, channel):
        """
        Query current attenuation for a specific channel.
        
        Args:
            channel: Channel number (1-4)
            
        Returns:
            Current attenuation value in dB
        """
        if not 1 <= channel <= 4:
            raise ValueError(f"Invalid channel {channel}. Must be 1-4.")
        
        command = f":CHAN:{channel}:ATT?"
        response = self.send_scpi_command(command)
        
        try:
            # Extract just the numeric part (handle cases like "25.00-6G-95")
            # Split on non-numeric characters and take the first valid float
            numeric_part = response.split()[0] if ' ' in response else response.split('-')[0]
            return float(numeric_part)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid response: {response}")