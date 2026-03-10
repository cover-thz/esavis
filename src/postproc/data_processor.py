#############################################################################
# File Name: data_processor.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   This file contains the main processing loop that loads HDF5 power cubes
#   and processes them into frames for the GUI via multiprocessing pipes.
#
# Copyright Cover.ai 2025
#############################################################################

import multiprocessing as mp
from collections import OrderedDict
import main_proc_fcns as mpf
import external_loader as extl
import time
import traceback


def main_proc_loop(cfg_obj_pipe, error_pipe, data_out_pipe, query_in_pipe, 
                   query_out_pipe, cfg_dict):

    dbg_prof    = False
    proc_obj    = mpf.CoverProc()

    update_id = 0

    try:
        while True:
            new_frame_flag = False

            ###################################################################
            #                      QUERY HANDLING STEPS                       #
            ###################################################################
            while query_in_pipe.poll():
                query_in_pipe.recv()

            ###################################################################
            #                       SETUP CHANGES STEPS                       #
            ###################################################################
            cfg_update = False
            if (cfg_obj_pipe.poll()):
                new_cfg_vals = cfg_obj_pipe.recv()
                query_out_dict = OrderedDict()
                query_out_dict["CFG_ACK"] = None
                query_out_pipe.send(query_out_dict)

                # update the configuration
                for keyval in new_cfg_vals.keys():
                    cfg_dict[keyval] = new_cfg_vals[keyval]
                    cfg_update = True

                cfg_flags = new_cfg_vals["flags"]
                if "close_process" in cfg_flags:
                    print("data_processor shutting down....")
                    break

                # profiling toggle
                if "enable_profiler" in cfg_flags:
                    dbg_prof = True
                if "disable_profiler" in cfg_flags:
                    dbg_prof = False

            else:
                cfg_flags = []

            ###################################################################
            #                      DATA PROCESSING STEPS                      #
            ###################################################################

            if cfg_dict["data_src"] == "external_h5":
                h5_fpath = cfg_dict.get("external_h5_fpath")
                if h5_fpath is None:
                    time.sleep(0.01)
                    continue

                # only (re)load / reprocess when triggered
                if (("fname_changed" in cfg_flags) or
                    ("reproc_buf" in cfg_flags)):

                    query_out_dict = OrderedDict()
                    query_out_dict["FILE_PROCESSING"] = True
                    query_out_pipe.send(query_out_dict)

                    try:
                        power_cube, h5_meta = extl.load_h5_cube(h5_fpath)

                        # send spatial metadata to GUI so it can
                        # set up axis grids correctly
                        x_m = power_cube["x_coords_m"]
                        y_m = power_cube["y_coords_m"]
                        meta_dict = OrderedDict()
                        meta_dict["EXTERNAL_H5_META"] = {
                            "min_az": float(x_m[0])  * 100.0,
                            "max_az": float(x_m[-1]) * 100.0,
                            "min_el": float(y_m[0])  * 100.0,
                            "max_el": float(y_m[-1]) * 100.0,
                        }
                        query_out_pipe.send(meta_dict)

                        (frame_out, aux_data_out,
                         frame_id_out) = proc_obj.process_power_cube(
                                             power_cube, cfg_dict,
                                             update_id, dbg_prof)
                        new_frame_flag = True

                    except Exception as err_h5:
                        print(f"external_h5 load error: {err_h5}")
                        traceback.print_exc()
                        new_frame_flag = False

                else:
                    time.sleep(0.005)
                    continue

            else: # "disabled" or unknown
                time.sleep(0.01)
                continue

            # send frame
            if new_frame_flag:
                data_src_out = cfg_dict["data_src"]
                data_out_pipe.send([frame_out, frame_id_out, data_src_out, 
                                    aux_data_out])

    except Exception as e2:
        print("\n\ndata_processor exception:")
        print(e2)
        traceback.print_exc()

##############################################################################
##############################################################################
##############################################################################
