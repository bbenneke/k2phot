import circular_photometry
from pixel_decorrelation import loadPixelFile
import pandas as pd
import numpy as np
from frame import Frame

class ImageStack(object):
    def __init__(self,fn,tlimits=None):
        cube,headers = loadPixelFile(fn,tlimits=tlimits)
        self.fn = fn
        self.headers = headers
        self.flux = cube['FLUX'].astype(float)
        self.t = cube['TIME'].astype(float)
        self.cad = cube['CADENCENO'].astype(int)
        self.ts = pd.DataFrame(dict(t=self.t , cad=self.cad))
        self.tlimits = tlimits

        # Number of frames, rows, and columns
        self.nframe,self.nrow,self.ncol = self.flux.shape 
        self.npix = self.nrow*self.ncol

    def set_apertures(self,locx,locy,radius):
        """
        Set the apertures used to compute photometry
        """
        if hasattr(locx,'__iter__'):
            assert ((len(locx)==self.nframe) &
                    (len(locy)==self.nframe) ), "Must have same length as array"
        self.ts['locx'] = locx
        self.ts['locy'] = locy

        def get_ap_weights(locx,locy):
            positions = np.array([[locx,locy]])
            return circular_photometry.circular_photometry_weights(
                self.flux[0],positions,radius)
            
        ap_weights = map(get_ap_weights,self.ts.locx,self.ts.locy)
        ap_weights = np.array(ap_weights)
        self.ap_weights = ap_weights

    def get_sap_flux(self):
        ap_flux = self.flux * self.ap_weights # flux falling in aperture
        ap_flux = ap_flux.reshape(self.nframe,-1)
        ap_flux = np.nansum(ap_flux,axis=1)
        return ap_flux

    def get_flux(self):
        """Get flux cube
        
        For Imstack object we don't modify the flux cube, so this is a
        no-op. For derived classes, we do and get_flux protechts
        self.flux
        """
        return self.flux

    def get_frame(self,i):
        locx,locy = self.ts.iloc[i]['locx locy'.split()]
        flux = self.get_flux()
        ap_weights = self.ap_weights[i]
        frame = Frame(
            flux[i],locx=locx,locy=locy,r=self.radius,ap_weights=ap_weights)
        return frame

    def get_frames(self):
        flux = self.get_flux()
        def get_frame(i):
            ap_weights = self.ap_weights[i]
            tsi = self.ts.iloc[i]

            frame = Frame(
                flux[i], locx=tsi['locx'], locy=tsi['locy'], r=self.radius,
                ap_weights=ap_weights)
            return frame

        frames = map(get_frame,range(self.nframe))
        return frames

