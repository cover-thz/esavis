#############################################################################
# File Name: external_loader.py
# Description
#   Loads an externally-processed radar data cube from an HDF5 file and
#   returns a PowerCube (see power_cube.py).
#
#   Expected HDF5 layout
#   --------------------
#   Datasets:
#     /power_cube    (xlen, ylen, range_bins)  float64  linear power or dB
#     /valid_mask    (xlen, ylen)              bool     (optional)
#     /range_axis    (range_bins,)             float64  meters
#     /x_axis        (xlen,)                   float64  meters
#     /y_axis        (ylen,)                   float64  meters
#
#   Root attributes (optional, used when present):
#     data_units       "linear_power" | "dB"     default: "linear_power"
#     range_units      "m" | "cm"                default: "m"
#     spatial_units    "m" | "cm"                default: "m"
#
#   Root attributes (required):
#     type             must be "power_cube"
#     format_version   integer (currently 1)
#############################################################################

import numpy as np
import h5py
from power_cube import make_power_cube


def load_h5_cube(fpath):
    """
    Read an HDF5 file and return a PowerCube OrderedDict.

    Parameters
    ----------
    fpath : str
        Absolute path to the HDF5 file.

    Returns
    -------
    power_cube : OrderedDict   (see power_cube.make_power_cube)
    metadata   : dict          additional info extracted from the file
    """
    with h5py.File(fpath, "r") as f:
        # --- required type check ---
        file_type = f.attrs.get("type", None)
        if isinstance(file_type, bytes):
            file_type = file_type.decode()
        if file_type != "power_cube":
            raise ValueError(
                f"HDF5 file type mismatch: expected 'power_cube', "
                f"got '{file_type}' — {fpath}"
            )

        # --- required datasets ---
        power_grid = np.array(f["power_cube"], dtype=np.float64)
        range_axis = np.array(f["range_axis"], dtype=np.float64)
        x_axis     = np.array(f["x_axis"], dtype=np.float64)
        y_axis     = np.array(f["y_axis"], dtype=np.float64)

        # --- optional valid mask (default: all True) ---
        if "valid_mask" in f:
            valid_mask = np.array(f["valid_mask"], dtype=bool)
        else:
            valid_mask = np.ones(power_grid.shape[:2], dtype=bool)

        # --- optional attributes ---
        data_units    = f.attrs.get("data_units",    "linear_power")
        range_units   = f.attrs.get("range_units",   "m")
        spatial_units = f.attrs.get("spatial_units",  "m")

        # convert string types from bytes if needed (h5py quirk)
        if isinstance(data_units, bytes):
            data_units = data_units.decode()
        if isinstance(range_units, bytes):
            range_units = range_units.decode()
        if isinstance(spatial_units, bytes):
            spatial_units = spatial_units.decode()

    # --- unit conversions ---

    # dB → linear power
    if data_units == "dB":
        power_grid = np.power(10.0, power_grid / 10.0)

    # range to cm (thzvis internal unit)
    if range_units == "m":
        range_lut_cm = range_axis * 100.0
    elif range_units == "cm":
        range_lut_cm = range_axis.copy()
    else:
        raise ValueError(f"Unsupported range_units: {range_units}")

    # spatial axes stay in meters for the PowerCube
    if spatial_units == "cm":
        x_axis = x_axis / 100.0
        y_axis = y_axis / 100.0

    cube = make_power_cube(power_grid, valid_mask, range_lut_cm,
                           x_axis, y_axis)

    metadata = {
        "xlen":       power_grid.shape[0],
        "ylen":       power_grid.shape[1],
        "range_bins": power_grid.shape[2],
        "fpath":      fpath,
    }

    return cube, metadata
