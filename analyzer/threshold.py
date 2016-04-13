import skimage


class Filters():

    @classmethod
    def threshold(cls, image, thresh):
        return image >= thresh

    @classmethod
    def threshold_li(cls, image):
        thresh = skimage.filters.threshold_li(image)
        return cls.threshold(image, thresh)

    @classmethod
    def threshold_otsu(cls, image):
        thresh = skimage.filters.threshold_otsu(image)
        return cls.threshold(image, thresh)

    @classmethod
    def threshold_yen(cls, image):
        thresh = skimage.filters.threshold_yen(image)
        return cls.threshold(image, thresh)

    @classmethod
    def threshold_otsu_local(cls, image, radius=3):
        selem = skimage.morphology.disk(radius)
        local_otsu_thresh = skimage.filters.rank.otsu(image, selem)
        return image >= local_otsu_thresh

    @classmethod
    def gauss_filter(cls, image, radius):
        return skimage.ndimage.filters.gaussian_filter(image, radius,
                                                       mode='nearest')
