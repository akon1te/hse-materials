import time
import numpy as np
from functools import wraps

import numba 
from numba import jit, int64, float64

NUM_THREADS = numba.get_num_threads()


def timeit(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time.time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time.time() * 1000)) - start
            print(f"{func.__name__}: {end_} ms")
    return _time_it


@timeit
@jit(int64[:](float64[:], float64[:]), nopython=True)
def match_timestamps(timestamps1: np.ndarray, timestamps2: np.ndarray) -> np.ndarray:

    ts2_idx = 0
    timestamps = np.zeros(len(timestamps1), dtype=np.int64)
    
    for ts1_idx in range(len(timestamps1)):
        while ts2_idx + 1 < len(timestamps2) and \
            np.abs(timestamps1[ts1_idx] - timestamps2[ts2_idx]) > np.abs(timestamps1[ts1_idx] - timestamps2[ts2_idx + 1]):
                ts2_idx += 1
        timestamps[ts1_idx] = ts2_idx
        ts1_idx += 1
        
    return timestamps


@timeit
@numba.njit(int64[:](float64[:], float64[:]), parallel=True)
def parallel_match_timestamps(timestamps1: np.ndarray, timestamps2: np.ndarray) -> np.ndarray:
    ts1_size = len(timestamps1)
    print("NUM_THREADS for parallel_match_timestamps:", NUM_THREADS)
    chunk_size = (ts1_size + NUM_THREADS - 1) // NUM_THREADS
    timestamps = np.zeros(ts1_size, dtype=np.int64)

    for chunk_idx in numba.prange(NUM_THREADS):
        left = chunk_idx * chunk_size
        right = min(left + chunk_size, ts1_size) - 1
        
        ts2_idx = 0
        for ts1_idx in range(left, right + 1):
            while ts2_idx + 1 < len(timestamps2) and \
                np.abs(timestamps1[ts1_idx] - timestamps2[ts2_idx]) > np.abs(timestamps1[ts1_idx] - timestamps2[ts2_idx + 1]):
                    ts2_idx += 1
            timestamps[ts1_idx] = ts2_idx
            ts1_idx += 1

    return timestamps


def make_timestamps(fps: int, st_ts: float, fn_ts: float) -> np.ndarray:
    """
    Create array of timestamps. This array is discretized with fps,
    but not evenly.
    Timestamps are assumed sorted nad unique.
    Parameters:
    - fps: int
        Average frame per second
    - st_ts: float
        First timestamp in the sequence
    - fn_ts: float
        Last timestamp in the sequence
    Returns:
        np.ndarray: synthetic timestamps
    """
    # generate uniform timestamps
    timestamps = np.linspace(st_ts, fn_ts, int((fn_ts - st_ts) * fps))
    # add an fps noise
    timestamps += np.random.randn(len(timestamps))
    timestamps = np.unique(np.sort(timestamps))
    return timestamps


def main():
    """
    Setup:
        Say we have two cameras, each filming the same scene. We make
        a prediction based on this scene (e.g. detect a human pose).
        To improve the robustness of the detection algorithm,
        we average the predictions from both cameras at each moment.
        The camera data is a pair (frame, timestamp), where the timestamp
        represents the moment when the frame was captured by the camera.
        The structure of the prediction does not matter here. 

    Problem:
        For each frame of camera1, we need to find the index of the
        corresponding frame received by camera2. The frame i from camera2
        corresponds to the frame j from camera1, if
        abs(timestamps[i] - timestamps[j]) is minimal for all i.

    Estimation criteria:
        - The solution has to be optimal algorithmically. If the
    best solution turns out to have the O(n^3) complexity [just an example],
    the solution with O(n^3 * logn) will have -1 point,
    the solution O(n^4) will have -2 points and so on.
    Make sure your algorithm cannot be optimized!
        - The solution has to be optimal python-wise.
    If it can be optimized ~x5 times by rewriting the algorithm in Python,
    this will be a -1 point. x20 times optimization will give -2 points, and so on.
    You may use any library, even write your own
    one in C++.
        - All corner cases must be handled correctly. A wrong solution
    will have -3 points.
        - Top 3 solutions get 10 points. The measurement will be done in a single thread. 
        - The base score is 9.
        - Parallel implementation adds +1 point, provided it is effective
    (cannot be optimized x5 times)
        - Maximal score is 10 points, minimal score is 5 points.
        - The deadline is November 14 23:59. Failing the deadline will
    result in -2 points, and each additional week will result in -1 point.
        - The solution can be improved/fixed after the deadline provided that the initial
    version is submitted on time.

    Optimize the solution to work with ~2-3 hours of data.
    Good luck!
    """
    # generate timestamps for the first camera
    timestamps1 = make_timestamps(30, time.time() - 100, time.time() + 360 * 2)
    timestamps2 = make_timestamps(60, time.time() + 200, time.time() + 360 * 2.5)

    # Основная функция match_timestamps с декоратором @timeit для замера времени
    matching = match_timestamps(timestamps1, timestamps2)
    parallel_matching = parallel_match_timestamps(timestamps1, timestamps2)
    
    print(f'Shapes equal - {matching.shape == parallel_matching.shape}')
    print(f'Ts values equal - {(matching == parallel_matching).all()}')


if __name__ == '__main__':
    main()