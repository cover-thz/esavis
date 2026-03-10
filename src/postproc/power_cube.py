#############################################################################
# File Name: power_cube.py
# Description
#   Defines the PowerCube interface — the shared data structure between
#   radar-specific processing (Stage A) and radar-agnostic peak finding /
#   visualization (Stage B).
#
#   Any data source (THz .dat files, DAQ streaming, external HDF5 cubes)
#   must produce a PowerCube before entering the shared pipeline.
#############################################################################

import numpy as np
from collections import OrderedDict


def make_power_cube(power_grid, valid_mask, range_lut_cm,
                    x_coords_m, y_coords_m):
    """
    Construct a PowerCube OrderedDict.

    Parameters
    ----------
    power_grid : np.ndarray, shape (xlen, ylen, range_bins), dtype float64
        Linear power values at each (x, y, range) voxel.
    valid_mask : np.ndarray, shape (xlen, ylen), dtype bool
        True where pixel contains valid data.
    range_lut_cm : np.ndarray, shape (range_bins,), dtype float64
        Range value in centimeters for each z-index.
    x_coords_m : np.ndarray, shape (xlen,), dtype float64
        Spatial x-axis in meters.
    y_coords_m : np.ndarray, shape (ylen,), dtype float64
        Spatial y-axis in meters.

    Returns
    -------
    OrderedDict
    """
    cube = OrderedDict()
    cube["power_grid"]    = np.asarray(power_grid, dtype=np.float64)
    cube["valid_mask"]    = np.asarray(valid_mask, dtype=bool)
    cube["range_lut_cm"]  = np.asarray(range_lut_cm, dtype=np.float64)
    cube["x_coords_m"]    = np.asarray(x_coords_m, dtype=np.float64)
    cube["y_coords_m"]    = np.asarray(y_coords_m, dtype=np.float64)
    return cube
