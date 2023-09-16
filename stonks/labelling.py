from numpy_ext import rolling_apply
import numpy as np

def triple_barrier(list1, higher_bound, lower_bound, side = None):

    if side == 'buy':
        list1 = np.array(list1)
        high = np.argwhere(list1 > higher_bound[0])
        if (high.any() == False):
            return 0

        if (high.any() == True):
            return 1

    else:
        list1 = np.array(list1)
        high = np.argwhere(list1 > higher_bound[0])
        low = np.argwhere(list1 < lower_bound[0])

        if (high.any() == False) & (low.any() == False):
            return 0

        if (high.any() == True) & (low.any() == False):
            return 1

        if (high.any() == False) & (low.any() == True):
            return -1

        if np.min(high) > np.min(low):
            return 1
        else:
            return -1

# ATTENTION DO NOT MESS UP SHIFTS
def get_barrier(hist, price, higher_bound, lower_bound, window = 20, side = None):
    hist['barrier'] = rolling_apply(triple_barrier, window, price, higher_bound, lower_bound, side= side)
    shift_window = -window +1
    hist.barrier = hist.barrier.shift(shift_window)

    return hist