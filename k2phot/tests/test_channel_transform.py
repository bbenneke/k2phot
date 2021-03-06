import os
from ..channel_transform import channel_transform
from ..config import K2_ARCHIVE, K2PHOTFILES, K2_DIR

fitsfiles = """ktwo201222515-c01_lpd-targ.fits ktwo201223635-c01_lpd-targ.fits
ktwo201226808-c01_lpd-targ.fits ktwo201227422-c01_lpd-targ.fits
ktwo201228585-c01_lpd-targ.fits ktwo201230523-c01_lpd-targ.fits
ktwo201233437-c01_lpd-targ.fits ktwo201233864-c01_lpd-targ.fits
ktwo201234630-c01_lpd-targ.fits ktwo201234711-c01_lpd-targ.fits
ktwo201235266-c01_lpd-targ.fits""".split()

fitsfiles = map(lambda x : os.path.join(K2_ARCHIVE, 'pixel/C1/',x) , fitsfiles)
h5file = os.path.join(K2_DIR,"test_channel_trans_C1_ch04.h5")

def test_channel_transform():
    channel_transform(fitsfiles, h5file, iref= None)
