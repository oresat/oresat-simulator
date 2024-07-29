import sys
import tty

tty.setcbreak(sys.stdin)

while True:
    print(sys.stdin.read(1), end="\r\n")



