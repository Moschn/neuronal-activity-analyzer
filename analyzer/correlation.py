import numpy
import time
from concurrent.futures import ThreadPoolExecutor

from .settings import THREAD_COUNT, CORRELATION_MAX_SHIFT


def correlate_activities(activities, exposure_time):
    """ Given activities of neurons, this function calculates the corellation of
    their activities with each other

    Args:
        activities(numpy array[num_neurons, n_frames]): activity data
                                                        (must be normalized)

    Returns:
        numpy array[num_neurons, num_neurons, n_frames]
        corellation of the activity of the first neuron with that of the second
        neuron, if the activity of the first neuron is shifted backwards by
        the number of frames specified in the third argument.
        Normalized to 0 to 1"""

    n_neurons = activities.shape[0]
    n_frames = activities.shape[1]
    n_shifts = round(CORRELATION_MAX_SHIFT / exposure_time)

    correlations = numpy.ndarray((n_neurons, n_neurons, 2 * n_shifts + 1),
                                 dtype='float')

    def calc_one_correlation(i, j):
        # To only retrive correlations with time shifts smaller than
        # n_shifts we pad one of the arrays with zeros on both sides
        # and used numpys 'valid' mode, which only calculates correlations
        # where the arrays overlap completely
        # see https://docs.scipy.org/doc/numpy-1.10.0/reference/generated/
        # numpy.convolve.html#numpy.convolve
        act1 = activities[j]
        # zeropads the array to both sides with n_shifts zeros
        act2 = numpy.pad(activities[i], (n_shifts, n_shifts), 'constant')
        correlated = numpy.correlate(act1, act2, 'valid')
        correlations[i, j, :] = correlated / n_frames  # normalize

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for i in range(0, n_neurons):
            for j in range(0, n_neurons):
                executor.submit(calc_one_correlation, i, j)

    return correlations
