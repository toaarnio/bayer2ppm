#!/usr/bin/python -B

"""
A collection of utility functions for processing Bayer raw and demosaiced
RGB image data using NumPy.
"""

from __future__ import print_function as __print  # hide from help(isptools)

import numpy as np        # pip install numpy

###############################################################################
#
#  P U B L I C   A P I
#
###############################################################################

def blacklevel(frame, max_outliers=100):
    """
    Returns the practical lower bound of pixel values in the given frame.
    A straight minimum would always yield zero if there is even a single
    dead pixel in the sensor, so instead a given number of outliers are
    allowed (i.e., disregarded).
    """
    pct = (float(max_outliers) / frame.size) * 100.0
    return np.percentile(frame, pct)

def whitelevel(frame, max_outliers=100):
    """
    Returns the practical upper bound of pixel values in the given frame.
    A straight maximum would always yield maxval (e.g. 1023) if there is
    even a single stuck pixel in the sensor, so instead a given number of
    outliers are allowed (i.e., disregarded).
    """
    pct = (1.0 - float(max_outliers) / frame.size) * 100.0
    return np.percentile(frame, pct)

def quantize(frame, maxval=65535, newmaxval=1023):
    """
    Quantizes the given image (raw or demosaiced) to the given bit depth.
    Returns the image in float64 format, except when maxval == newmaxval,
    in which case this function does nothing.
    """
    if maxval != newmaxval:
        scale = float(newmaxval) / maxval
        frame = frame * scale  # frame.dtype is now np.float64
    return frame

def gamma(frame, mode):  # mode = rec709 | sRGB | None
    """
    Applies rec709 or sRGB gamma on the given frame, boosting especially the
    near-zero pixel values. If mode is None, the frame is returned untouched.
    """
    if mode is not None:
        if mode == "sRGB":
            srgb_lo = 12.92 * frame
            srgb_hi = 1.055 * np.power(frame, 1.0/2.4) - 0.055
            threshold_mask = (frame > 0.0031308)
        if mode == "rec709":
            srgb_lo = 4.5 * frame
            srgb_hi = 1.099 * np.power(frame, 0.45) - 0.099
            threshold_mask = (frame > 0.018)
        frame = srgb_hi * threshold_mask + srgb_lo * (~threshold_mask)
    return frame

def degamma(frame, mode):  # mode = rec709 | sRGB | None
    """
    Applies rec709 or sRGB inverse gamma on the given frame. If mode is None,
    the frame is returned untouched.
    """
    if mode is not None:
        if mode == "sRGB":
            srgb_lo = frame / 12.92
            srgb_hi = np.power((frame + 0.055) / 1.055, 2.4)
            threshold_mask = (frame > 0.04045)
        if mode == "rec709":
            srgb_lo = frame / 4.5
            srgb_hi = np.power((frame + 0.099) / 1.099, 1/0.45)
            threshold_mask = (frame > 0.081)
        frame = srgb_hi * threshold_mask + srgb_lo * (~threshold_mask)
    return frame
