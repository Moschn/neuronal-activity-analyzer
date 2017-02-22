""" Thresholding algorithm which implements a dynamic threshold method
developed by Csaba Forro. """

import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
from scipy.spatial.distance import pdist,squareform
import matplotlib.path as mplPath
from .apply_threshold import ApplyThreshold


class DynamicThreshold(ApplyThreshold):

    def apply_threshold(self, image, threshold):
        # Generate contours from image
        contours_list=self.generate_contours(image)

        # Find unique contours in the contour list_implementations
        entries=self.find_unique_loops(contours_list,5)

        # get image shape
        im_width, im_height = image.shape[0], image.shape[1]

        # generate array of image coordinates
        xx,yy=np.meshgrid(np.arange(im_width),np.arange(im_height))
        img_coords=np.asarray((xx.flatten(),yy.flatten())).T

        # empty image
        segmented = np.zeros([im_width, im_height])

        # fill empty image with unique contours
        for i in range(len(entries)):
            bbPath = mplPath.Path(contours_list[entries[i]])
            area = bbPath.contains_points(img_coords).reshape(im_width,im_width)
            segmented +=  area.astype(int)
        # print(loader.pixel_per_um)
        return segmented



    @staticmethod
    def poly_area(xy):
        """
            Calculates polygon area.
            x = xy[:,0], y = xy[:,1]
        """
        l = len(xy)
        s = 0.0
        # Python arrys are zer0-based
        for i in range(l):
            j = (i+1)%l  # keep index in [0,l)
            s += (xy[j,0] - xy[i,0])*(xy[j,1] + xy[i,1])
        return -0.5*s

    @staticmethod
    def poly_perimeter(xy):
        """
            Calculates polygon perimeter.
            x = xy[:,0], y = xy[:,1]
        """
        xy1 = np.roll(xy,-1,axis = 0) # shift by -1
        return np.sum(np.apply_along_axis(np.linalg.norm, 1, xy1-xy))


    def cleaned_contours(self,ct):
        """
        Cleans contours based on area and sphericity
        """

        # Hardcoded parameters optimized for 0.6466px/um
        sphericity_limits = [0.3,2.]
        area_limits = [5.,150.]
        all_paths=ct.collections[0].get_paths()
        num_paths=len(all_paths)
        perimeters=np.zeros(num_paths)
        areas = np.zeros(num_paths)
        sphericities = np.zeros(num_paths)

        for i in range(num_paths):

            xy=all_paths[i].vertices
            perimeters[i]=self.poly_perimeter(xy)
            areas[i]=np.abs(self.poly_area(xy))
            if areas[i]==0:
                sphericities[i]=0
            else:
                sphericities[i]=2*np.sqrt(np.pi*np.abs(areas[i]))/perimeters[i]

        plausible_paths = np.where((sphericities>sphericity_limits[0]) &
                                   (sphericities<sphericity_limits[1]) &
                                   (areas>area_limits[0]) &
                                   (areas<area_limits[1]))[0]
        paths=[all_paths[plausible_paths[i]].vertices for i in range(len(plausible_paths))]
        return paths


    def generate_contours(self,image,absolute_threshold=0):
        """
        Find contors of regions of interests.
        """
        all_cnts=[]

        if absolute_threshold==0:
            t=threshold_otsu(image)
        else:
            t=absolute_threshold
        for m in np.arange(1,15,0.25):
            thresholded=np.zeros(np.shape(image))
            thresholded[image>m*t]=1
            if np.sum(thresholded)!=0:
                cont=plt.contour(thresholded)
                plt.close()
                all_cnts.append(self.cleaned_contours(cont))
            else:
                continue
        return [item for sublist in all_cnts for item in sublist]

    @staticmethod
    def find_unique_loops(list_of_all,threshold_overlap_distance):
        centers=np.asarray([np.mean(list_of_all[i],0) for i in range(len(list_of_all))])
        threshold_distance=threshold_overlap_distance
        indices=np.arange(len(centers))
        ctr=0
        unique_indices=[]
        while len(centers)>0:

            their_dist=np.triu(squareform(pdist(centers)))+1e9*np.diag(np.ones(len(centers)))
            to_remove=np.where(their_dist[0,:]<threshold_distance)[0]
            if len(to_remove)==0:
                unique_indices.append(indices[0])
                indices=np.delete(indices,0)
                centers=np.delete(centers,0,0)
                ctr+=1
            else:
                unique_indices.append(indices[0])
                indices=np.delete(indices,to_remove)
                centers=np.delete(centers,to_remove,0)
                indices=np.delete(indices,0)
                centers=np.delete(centers,0,0)

                ctr+=1
        return unique_indices
