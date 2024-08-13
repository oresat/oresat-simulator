#!/usr/bin/env python
import socket
import argparse

#TO DO

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Socket to serial TCP client."
    )

    parser.add_argument(
        "-IP", help="127.0.0.1 is loopback address",
        default="127.0.0.1"
    )

    args = parser.parse_args()

    """
    Ask the OS for a socket.
    How do I do UNSPEC??? INET enables IPv4 only. Answer: There is a flag for it that says dual...
    SOCK_STREAM enables TCP only.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        """Create a port integer."""
        port = 16327

        """
        Connect to an IP address on a specific port.
        Connection will fail if there is no server listening on said port.
        """

        sock.connect((args.IP, port))

        try:
            while True:    
                msg = input("Enter text, good sir: ")

                sock.send(msg.encode())

        except KeyboardInterrupt:
            print("\nEnded via ctrl-c.\n")










