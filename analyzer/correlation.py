import numpy

from .settings import THREAD_COUNT


def correlate_activities(activities):
    """ Given activities of neurons, this function calculates the corellation of
    their activities with each other

    Args:
        activities(numpy array[num_neurons, n_frames]): activity data

    Returns:
        numpy array[num_neurons, num_neurons, n_frames]
        corellation of the activity of the first neuron with that of the second
        neuron, if the activity of the first neuron is shifted backwards by
        the number of frames specified in the third argument"""

    n_neurons = activities.shape[0]
    n_frames = activities.shape[1]
    correlations = numpy.ndarray((n_neurons, n_neurons, n_frames),
                                 dtype='float')

    def calc_one_correlation(i, j):
        correlations[i, j, :] = numpy.correlate(activities[j],
                                                activities[i], 'same')

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for i in range(0, n_neurons):
            for j in range(0, n_neurons):
                executor.submit(i, j)

    return correlations
