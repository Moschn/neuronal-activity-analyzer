import numpy


def normalize(activities):
    n_neurons = activities.shape[0]
    n_frames = activities.shape[1]

    for i in range(0, n_neurons):
        # correct the bleaching
        # Fit a linear function through the activity data
        x = numpy.arange(0, n_frames)
        coeffs = numpy.polyfit(x, activities[i], 2)
        fn = numpy.poly1d(coeffs)
        activities[i] = activities[i] - fn(x)

        # shift to be around zero
        activities[i] = activities[i] - numpy.mean(activities[i])
        # normalize values to standard deviation
        activities[i] = activities[i] / numpy.std(activities[i])

    return activities
