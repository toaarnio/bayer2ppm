#!/usr/bin/python -B

"""
A collection of utility functions for processing Bayer raw and demosaiced
RGB image data using NumPy.
"""

from __future__ import print_function as __print  # hide from help(isptools)

import numpy as np

######################################################################################
#
#  P U B L I C   A P I
#
######################################################################################

def blackLevel(frame, maxOutliers=100):
    """
    Returns the practical lower bound of pixel values in the given frame.
    A straight minimum would always yield zero if there is even a single
    dead pixel in the sensor, so instead a given number of outliers are
    allowed (i.e., disregarded).
    """
    pct = (float(maxOutliers) / frame.size) * 100.0
    return np.percentile(frame, pct)

def whiteLevel(frame, maxOutliers=100):
    """
    Returns the practical upper bound of pixel values in the given frame.
    A straight maximum would always yield maxval (e.g. 1023) if there is
    even a single stuck pixel in the sensor, so instead a given number of
    outliers are allowed (i.e., disregarded).
    """
    pct = (1.0 - float(maxOutliers) / frame.size) * 100.0
    return np.percentile(frame, pct)

def quantize(frame, maxval=65535, newmaxval=1023):
    """
    Quantizes the given image (raw or demosaiced) to the given bit depth.
    The image is returned as uint16, whether or not it was originally in
    that format.
    """
    if maxval != newmaxval:
        scale = float(newmaxval) / maxval
        frame = frame * scale  # frame.dtype is now np.float64
    frame = (frame + 0.5).astype(np.uint16)
    return frame

def gamma(frame, maxval, mode):  # mode = rec709 | sRGB | None
    """
    Applies rec709 or sRGB gamma on the given frame, boosting especially the
    near-zero pixel values. If mode is None, the frame is returned untouched.
    """
    if mode != None:
        frame = frame / float(maxval)
        if mode == "sRGB":
            srgb_lo = 12.92 * frame
            srgb_hi = 1.055 * np.power(frame, 1.0/2.4) - 0.055
            thresholdMask = (frame > 0.0031308)
        if mode == "rec709":
            srgb_lo = 4.5 * frame
            srgb_hi = 1.099 * np.power(frame, 0.45) - 0.099
            thresholdMask = (frame > 0.018)
        frame = srgb_hi * thresholdMask + srgb_lo * (~thresholdMask)
        frame *= maxval
    return frame

def degamma(frame, maxval, mode):  # mode = rec709 | sRGB | None
    """
    Applies rec709 or sRGB inverse gamma on the given frame. If mode is None,
    the frame is returned untouched.
    """
    if mode != None:
        frame = frame / float(maxval)
        if mode == "sRGB":
            srgb_lo = frame / 12.92
            srgb_hi = np.power((frame + 0.055) / 1.055, 2.4)
            thresholdMask = (frame > 0.04045)
        if mode == "rec709":
            srgb_lo = frame / 4.5
            srgb_hi = np.power((frame + 0.099) / 1.099, 1/0.45)
            thresholdMask = (frame > 0.081)
        frame = srgb_hi * thresholdMask + srgb_lo * (~thresholdMask)
        frame *= maxval
    return frame
