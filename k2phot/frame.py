import numpy as np
from numpy import ma
from skimage import measure
from photutils import CircularAperture
import pandas as pd
from matplotlib import pylab as plt

import circular_photometry
from io_utils.pixel import get_stars_pix

class Frame(np.ndarray):
    """
    Frame 

    Lightweight extension to ndarray object. Can compute momments of
    the image and plot itself
    """

    def __new__(cls, input_array,locx=None,locy=None,r=None,pixels=None,
                ap_weights=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        obj.locx = locx
        obj.locy = locy
        obj.r = r
        obj.pixels = pixels
        obj.ap_weights = ap_weights
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return

    def get_moments(self):
        """
        Return moments from frame

        Returns
        -------
        moments : pandas Series object with the following keys
                  - m10 : row position of centroid
                  - m01 : col position of centroid
                  - mupr20 : higher moments
                  - mupr02 : higher moments
                  - mupr11 : higher moments
        """
        frame = ma.masked_invalid(self)
        frame.fill_value = 0
        frame = frame.filled()
        frame *= self.ap_weights # Multiply frame by aperture weights

        # Compute the centroid
        m = measure.moments(frame)
        m10=m[1,0]
        m01=m[0,1]
        moments = np.array([m10,m01])
        moments /= m[0,0]

        # Compute central moments (second order)
        mu = measure.moments_central(frame,moments[0],moments[1])
        
        mupr20 = mu[2,0]
        mupr02 = mu[0,2]
        mupr11 = mu[1,1]

        c_moments = np.array([mupr20,mupr02,mupr11])
        c_moments/=mu[0,0]

        moments = np.hstack([moments,c_moments])
        return moments

    def plot(self,scale='log'):
        apertures = CircularAperture([self.locx,self.locy], r=self.r)

        z = self.copy()
        z -= np.nanmedian(z)
        if scale=='log':
            z = np.log10(self)
            z = ma.masked_invalid(z)
            z.mask = z.mask | (z < 0)
            z.fill_value = 0
            z = z.filled()

        imshow2(z)

        if self.pixels is not None:
            for i,pos in enumerate(self.pixels):
                r,c = pos
                plt.text(c,r,i,va='center',ha='center',color='Orange')

        apertures.plot(color='Lime',lw=1.5,alpha=0.5)
        plt.xlabel('Column (pixels)')
        plt.ylabel('Row (pixels)')

    def plot_label(self,fn,epic):
        """
        Query the catalog for nearby stars. Pull the WCS from the fits file
        """
        catcut, shift = get_stars_pix(fn,self, dkepmag=5)
        xcen,ycen = catcut.ix[epic]['pix0 pix1'.split()]
        plot_label(self,catcut,epic,colorbar=True )


def test_frame_moments():
    flux = np.ones((20,20))
    locx,locy = 10.5,7.5
    positions = np.array([locx,locy]).reshape(-1,2)
    radius = 3
    ap_weights = circular_photometry.circular_photometry_weights(
        flux,positions,radius)
    frame = Frame(flux,locx=locx,locy=locy,r=radius,ap_weights=ap_weights)
    moments = frame.get_moments()

    firstmoments = moments[[0,1]]
    assert np.allclose(firstmoments,positions),\
        'Centroid must match center of aperture'


def plot_label(image,catcut,epic,colorbar=True, shift=None, retim=False, 
               cmap=None):
    """
    """

    # 2014-09-30 18:33 IJMC: Added shift option.
    # 2014-10-07 20:58 IJMC: Added 'retim' flag and 'cmap' option.

    targstar = catcut.ix[epic]
    if shift is None:
        x0,x1 = 0,0
    else:
        x0,x1 = shift[0:2]

    def label_stars(x,**kwargs):
        plt.text(x['pix0'] + x0,x['pix1'] + x1,'%(epic)09d, %(kepmag).1f' % x,**kwargs)

    plt.plot(catcut['pix0']+x0,catcut['pix1']+x1,'oc')
    catcut.apply(lambda x : label_stars(x,color='c',size='x-small'),axis=1)

    plt.plot(targstar['pix0']+x0,targstar['pix1']+x1,'o',color='Tomato')
    label_stars(targstar,color='Tomato',size='x-small')

    if retim:
        ret = im
    else:
        ret = None

    return ret


def imshow2(im,**kwargs):
    extent = None#(0,im.shape[0],0,im.shape[1])

    if kwargs.has_key('cmap')==False or kwargs['cmap'] is None:
        kwargs['cmap'] = plt.cm.gray 

    im = plt.imshow(im,interpolation='nearest',origin='lower',
                    extent=extent,**kwargs)

    return im
