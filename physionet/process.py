"""
Basic routines to process and show data
"""

import numpy


def build_spatial_correlations(channels) -> numpy.ndarray:
    """
    Build the spatial correlation matrix
    """
    x = numpy.array([c - numpy.mean(c) for i, c in enumerate(channels)])
    return x.dot(x.T)
