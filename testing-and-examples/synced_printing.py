

import time


if __name__ == "__main__":

    blah = time.time()
    print(blah)

    for i in range(100):
        wait_time = 1 - (time.time() % 1)
        time.sleep(wait_time)

        epoch = time.time()
        print(epoch)
        print(int(epoch))
