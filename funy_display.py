import os
try:
    from sense_hat import SenseHat
    USING_8x8 = True
except ImportError:
    USING_8x8 = False
import random as rnd
import time

COL_DICT = {0: (0, 0, 0), 1: (0, 0, 0), 2: (0, 0, 0), 3: (0, 0, 0), 4: (0, 0, 0),
               5: (125, 0, 0), 6: (0, 125, 0), 7: (0, 0, 125),
               8: (125, 125, 0), 9: (125, 0, 125), 10: (0, 125, 125)}

def funy_display(mode: int = 0, delay: float = 0.1):

    def mode_0():
        return [COL_DICT[rnd.randint(0, 10)] for _ in range(64)]

    def mode_1():
        return [COL_DICT[rnd.randint(5, 10)]] * 64

    pattern_dict = {0: mode_0,
                    1: mode_1,
                    2: None}

    if USING_8x8:
        sense = SenseHat()
        sense.low_light = False

    while True:
        flatmat = pattern_dict[mode]()
        if USING_8x8:
            sense.set_pixels(flatmat)
        else:
            print(flatmat)
        time.sleep(delay)



if __name__ == "__main__":
    matrix_in = [[0, 0, 1, 0, 0, 1, 0, 0],
                 [0, 1, 0, 1, 1, 0, 1, 0],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 1, 0, 0, 0, 0, 1, 0],
                 [0, 0, 1, 0, 0, 1, 0, 0],
                 [0, 0, 0, 1, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0]]

    _delay = 2
    _mode = 1
    funy_display(mode = _mode, delay=_delay)