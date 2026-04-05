# RC4DAT-6G-95
# https://www.minicircuits.com/softwaredownload/Prog_Manual-6-Programmable_Attenuator.pdf
from re import ASCII
from typing import Literal
from collections.abc import Mapping
import usb.core
import usb.util
import usb.backend.libusb1

# psas programmable attenuator
# Bus 003 Device 069: ID 20ce:0023 Minicircuits Programable Attenuator

# FIXME: Fix libusb library work around
backend = usb.backend.libusb1.get_backend(
    find_library=lambda x: (
        ".venv/lib/python3.14/site-packages/libusb/_platform/linux/x86_64/libusb-1.0.so"
    )
)


class Attenuator:
    write_endpoint = 1
    read_endpoint = 0x81
    msg_length = 64  # see section 5.1 (a) in the programming manual
    Channels = Literal[0, 1, 2, 3]

    def __init__(self, serial_num: str) -> None:
        self.dev = usb.core.find(idVendor=0x20CE, idProduct=0x0023, find_all=True)
        def find_attn(dev):
            return (
                dev.idVendor == 0x20CE
                and dev.idProduct == 0x0023
                and dev.serial_number == serial_num
            )

        # TODO: Fix attenuator detection and see if the solution below works
        self.dev = usb.core.find(idVendor=0x20CE, idProduct=0x0023, custom_match = lambda d: d.iSerialNumber == serial_num)
        if self.dev is None:
            raise RuntimeError("attenuator not found")

        for configuration in self.dev:
            for interface in configuration:
                # Interface class value for HID
                if interface.bInterfaceClass == 0x3:
                    for endpoint in interface:
                        # Highest bit set indicates in endpoitn
                        if endpoint.bEndpointAddress & 0x80:
                            self.read_endpoint = endpoint.bEndpointAddress
                        else:
                            self.write_endpoint = endpoint.bEndpointAddress

                    ifnum = interface.bInterfaceNumber
                    if not self.dev.is_kernel_driver_active(ifnum):
                        continue
                    try:
                        self.dev.detach_kernel_driver(ifnum)
                    except usb.core.USBError:
                        pass

        self.dev.set_configuration()
    # Add RuntimeError for values outside of the acceptable channel
    def scpi_cmd(self, cmd: str):
        self.dev.write(self.write_endpoint, b"\x01" + cmd.encode())
        return self.dev.read(self.read_endpoint, self.msg_length).tobytes().decode()

    def set_attn(self, values: Mapping[Channels, float]) -> None:
        arg = ":".join((f"{ch}:{val}" for ch, val in values.items()))
        return self.scpi_cmd(f":SetAttPerChan:{arg}")

    def get_attn(self):
        return self.scpi_cmd(":ATT?")

    def get_start_attn(self, chan: int):
        return self.scpi_cmd(f":CHAN:{chan}:STARTUPATT:VALUE?")

    def set_start_attn(self, chan: int, value: float):
        return self.scpi_cmd(f":CHAN:{chan}:STARTUPATT:{value}")

    def firmware(self):
        return self.scpi_cmd(":FIRMWARE?")

    def get_usb_addr(self):
        return self.scpi_cmd(":ADD?")

    def set_usb_addr(self, address):
        return self.scpi_cmd(f":SETADD:{address}")

    def serial_num(self):
        return self.scpi_cmd(":SN?")

    def model_num(self):
        return self.scpi_cmd(":MN?")


attenuator1 = Attenuator(serial_num="12601270105")


