import pixdecor
import plotting
import numpy as np
from config import bjd0

def pipeline(pixfn, lcfn, transfn, tlimits=[-np.inf,np.inf], tex=None, 
             debug=False, ap_select_tlimits=None, singleapsize=None):
    """
    Run the pixel decorrelation on pixel file
    """

    pixdcr = pixdecor.PixDecor(
        pixfn, lcfn,transfn, tlimits=ap_select_tlimits, tex=tex,
        singleapsize=singleapsize 
        )
    pixdcr.set_lc0(3)

    if debug:
        npts = len(pixdcr.lc0)
        idx = [int(0.25*npts),int(0.50*npts)]

        tlimits = [pixdcr.lc0.iloc[i]['t'] - bjd0 for i in idx]
        pixdcr = pixdecor.PixDecor(
            pixfn, lcfn,transfn, tlimits=tlimits, tex=tex
        )
        pixdcr.apertures = [3,4]
        pixdcr.set_lc0(3)
    pixdcr.set_hyperparameters()
    pixdcr.reject_outliers()
    pixdcr.scan_aperture_size()
    dfaper = pixdcr.dfaper
    dmin = dfaper.iloc[0]

    pixdcr = pixdecor.PixDecor(
        pixfn, lcfn,transfn, tlimits=tlimits, tex=tex,
        )
    pixdcr.set_lc0(dmin['r'])
    pixdcr.set_hyperparameters()
    pixdcr.reject_outliers()

    # Sub in best-fitting radius from previous iteration
    pixdcr.dfaper = dfaper
    pixdcr.dmin = dmin 
    detrend_dict = pixdcr.detrend_t_roll_2D(dmin['r'])
    pixdcr.lc = detrend_dict['lc']

    pixdcr.to_fits(lcfn)

    if 0:
        from matplotlib import pylab as plt
        plt.ion()
        plt.figure()
        import pdb;pdb.set_trace()

    with pixdcr.FigureManager('_0-median-frame.png'):
        plotting.medframe(pixdcr)

    with pixdcr.FigureManager('_1-background.png'):
        plotting.background(pixdcr)

    with pixdcr.FigureManager('_2-noise_vs_aperture_size.png'):
        plotting.noise_vs_aperture_size(pixdcr)

    with pixdcr.FigureManager("_3-fdt_t_roll_2D.png"):
        plotting.detrend_t_roll_2D(pixdcr)

    with pixdcr.FigureManager("_4-fdt_t_roll_2D_zoom.png"):
        plotting.detrend_t_roll_2D(pixdcr,zoom=True)

    with pixdcr.FigureManager("_5-fdt_t_rollmed.png"):
        plotting.detrend_t_rollmed(pixdcr)


