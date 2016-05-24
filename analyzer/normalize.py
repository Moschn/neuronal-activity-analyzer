import numpy


def normalize(activities):
    n_neurons = activities.shape[0]

    for i in range(0, n_neurons):
        # shift to be around zero
        activities[i] = activities[i] - numpy.mean(activities[i])
        # normalize values to standard deviation
        activities[i] = activities[i] / numpy.std(activities[i])

    return activities
