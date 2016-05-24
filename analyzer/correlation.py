import numpy
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
        the number of frames specified in the third argument"""

    n_neurons = activities.shape[0]
    n_frames = activities.shape[1]
    n_shifts = round(CORRELATION_MAX_SHIFT / exposure_time)

    correlations = numpy.ndarray((n_neurons, n_neurons, n_shifts),
                                 dtype='float')

    def calc_one_correlation(i, j):
        for k in range(0, n_shifts):
            correlated = numpy.correlate(activities[j], activities[i], 'same')
            correlations[i, j, :] = (
                correlated[n_frames // 2: n_frames // 2 + n_shifts])

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for i in range(0, n_neurons):
            for j in range(0, n_neurons):
                executor.submit(calc_one_correlation, i, j)

    return correlations
