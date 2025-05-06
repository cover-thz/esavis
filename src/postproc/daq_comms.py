#############################################################################
# File Name: daq_comms.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   This file contains all the code required to interface properly with 
#   the DAQ subsystem so it can be easily grabbed by the main data_processor
#   code
# 
# NOTE consider putting some sort of logging capability for all messages etc.
# so you can check it later even without a proper terminal
#
# Copyright Cover.ai 2025
#############################################################################

import multiprocessing as mp
import numpy as np
import copy
import uuid
import socket
import time
import os
import daq_acq_core as dac
import ipdb
from collections import OrderedDict

# NOTE TODO NOTE TODO 
# NOTE TODO NOTE TODO 
#
# "en_channels" is a list.  Formatted per the code below.  i.e. if one channel
# is enabled, an integer 0 or 1 is the only element in that list, corerspoding
# to the enabled channel.  If both channels are enabled, the list is [0, 1]
# if neither channel is enabled it's an empty list []
#
#   def get_enabled_channels(self):
#       arr = []
#       if self.channel_0_enabled:
#           arr.append(0)
#       if self.channel_1_enabled:
#           arr.append(1)
#       return arr
#
# NOTE TODO NOTE TODO 
# NOTE TODO NOTE TODO 


# as simplified interface class for the radar when dealing with the DAQ
class SimpRadar:
    addr                = None
    #daq_sock            = None
    en_channels         = None 
    rangeline_buffer    = None
    state               = "RESET"
    daq_connected       = None

    def __init__(s):
        #s.daq_sock = DAQSocket()
        s.tot_rangelines    = 0
        s.en_channels       = []
        s.cdh_msg_id        = 0
        s.acq_timeout       = 10.0

        # buffer of radar data samples
        s.rangeline_buffer = None
        s.az_buffer = None
        s.el_buffer = None
        s.ch_buffer = None
        s.num_buf_samples = 0
        s.buf_ind = 0
        s.dbg_chunk_0 = None
        s.dbg_chunk_1 = None
        s.dbg_chunk_2 = None
        s.az_val_prev = None
        s.acq_dbg_flag = False

        s.constr_acq_proc()
        s.prev_chunk_count = -1
    
    # construct the aquisition process 
    def constr_acq_proc(s):
        data_queue    = mp.Queue(maxsize=100000)
        cdh_queue_tx = mp.Queue(maxsize=1000)
        cdh_queue_rx = mp.Queue(maxsize=1000)

        #(acq_cdh_pipe_in, cdh_pipe_out)  = mp.Pipe(duplex=False)
        #(cdh_pipe_in, acq_cdh_pipe_out)  = mp.Pipe(duplex=False)
        #s.acq_obj = mp.Process(target=dac.main_acq_loop, args=(acq_cdh_pipe_in, 
        #    acq_cdh_pipe_out, data_queue,))
        s.acq_obj = mp.Process(target=dac.main_acq_loop, args=(cdh_queue_tx, 
            cdh_queue_rx, data_queue,))
        #s.cdh_pipe_in       = cdh_pipe_in
        #s.cdh_pipe_out      = cdh_pipe_out
        s.cdh_queue_tx      = cdh_queue_tx
        s.cdh_queue_rx      = cdh_queue_rx
        s.data_queue        = data_queue
        s.acq_obj.start()


    # close down the acquisition process
    def end_acq_proc(s):
        s.acq_obj.terminate()
        s.acq_obj.join() 


    def en_acq_dbg(s, en_val):
        if s.acq_dbg_flag != en_val:
            _ = s.ack_cdh_handshake_trans("ACQ_DBG", en_val)
            s.acq_dbg_flag = en_val


    # sends a value to the acq_obj using the cdh pipe and waits for a response
    # from the acq_obj
    def ack_cdh_handshake_trans(s, key, value_out):
        new_dict_out        = OrderedDict()
        msg_id_out          = s.cdh_msg_id
        #print(f"handshake trans: {key}, {value_out}, {msg_id_out}")
        new_dict_out[key]   = (msg_id_out, value_out)
        s.cdh_msg_id       += 1
        #s.cdh_pipe_out.send(new_dict_out)
        s.cdh_queue_tx.put(new_dict_out)
        start = time.time()
        while True:
            #if s.cdh_pipe_in.poll():
            if not s.cdh_queue_rx.empty():
                #new_dict_in = s.cdh_pipe_in.recv()
                new_dict_in = s.cdh_queue_rx.get()
                if key in new_dict_in.keys():
                    (msg_id_in, value_in) = new_dict_in[key]
                    #print(f"handshake reply: {key}, {msg_id_in}, {value_in}")
                    # verify that the response is directed to the same message
                    # and not just the same message type
                    if msg_id_in == msg_id_out:
                        response = value_in
                        break

            if time.time() - start > s.acq_timeout:
                print("Warning: ack_cdh_handshake_trans() timeout")
                response = None
                break
        return response


    def setup_comms(s, addr, ch0_en, ch1_en):
        s.addr = addr
        s.set_en_channels(ch0_en, ch1_en, send_trace=False)
        status = s.init_connection()
        s.daq_connected = status
        return status


    def set_en_channels(s, ch0_en, ch1_en, send_trace=True):
        if 0 in s.en_channels:
            ch0_en_prev = True
        else:
            ch0_en_prev = False

        if 1 in s.en_channels:
            ch1_en_prev = True
        else:
            ch1_en_prev = False

        if (ch0_en == ch0_en_prev) and (ch1_en == ch1_en_prev):
            pass
        else:
            en_channels = []
            if ch0_en:
                en_channels.append(0)
            if ch1_en:
                en_channels.append(1)
            s.en_channels = copy.copy(en_channels)
            if send_trace:
                s.send_trace_config()


    def init_connection(s):
        status = s.ack_cdh_handshake_trans("INIT_CONN", (s.addr, s.en_channels))
        if status:
            print("Connected")
            return True
        else:
            return False

    # this grabs the connection status from the local daq_connected variable
    # a much "cheaper" operation than querying the daq_acq_core
    def get_conn_status(s):
        return s.daq_connected

    def get_true_conn_status(s):
        status = s.ack_cdh_handshake_trans("CONN_STATUS", None) 
        # update the daq_connected variable
        s.daq_connected = status
        return s.daq_connected



    def disconnect(s):
        ack = s.ack_cdh_handshake_trans("DISCONNECT", None)
    

    # need to call this at the beginning and whenever we change the number of 
    # channels.  I think.
    def send_trace_config(s):
        ack = s.ack_cdh_handshake_trans("SEND_TRACE", s.en_channels)


    def get_sample(s):
        try:
            if s.num_buf_samples == 0:
                if s.data_queue.empty():
                    # here's when we ACTUALLY check for the connection status
                    # since data has stopped flowing
                    _ = s.get_true_conn_status()
                    time.sleep(0.01)
                    return (None, None, None, None, False)
                else:
                    (rangelines_array_in, az_array_in, el_array_in, 
                        ch_array_in, chunk_count) = s.data_queue.get(timeout=5)
                    #print(f"chunk_count {chunk_count} pulled")
                    count_diff = chunk_count - s.prev_chunk_count
                    if count_diff != 1:
                        print(f"chunk_count diff: {count_diff}")
                        print(f"chunk_count = {chunk_count}\n")
                    s.prev_chunk_count = chunk_count

                    s.rangeline_buffer = rangelines_array_in
                    s.az_buffer = az_array_in
                    s.el_buffer = el_array_in
                    s.ch_buffer = ch_array_in
                    s.num_buf_samples = len(s.rangeline_buffer)
                    s.buf_ind = 0
                    #if s.num_buf_samples != 500:
                    #    print(f"num_buf_samples = {s.num_buf_samples}")


            # now we actually return the sample
            rangeline   = s.rangeline_buffer[s.buf_ind]
            az_val      = s.az_buffer[s.buf_ind]
            el_val      = s.el_buffer[s.buf_ind]
            channel_val = s.ch_buffer[s.buf_ind]
            s.num_buf_samples -= 1
            s.buf_ind += 1

        except Exception as e:
            ipdb.set_trace()

        return (rangeline, az_val, el_val, channel_val, True)




    #def __del__(s):
    #    s.acq_obj.join() # might need to close the pipes brutally in order
                         # for this to work



    # main workhorse function
    # NOTE currently a little hacky since I wanted to minimize the number
    # of changes, but the method by which reangelines are iterated through
    # to detect turnaround is inefficient now that we grab many rangelines
    # at once
    def get_daq_data(s, num_rangelines, turnaround_mode, turn_hyst, min_az, 
                     max_az, ch0_offset, ch1_offset, timeout=3, debug=False):
                                              
        start_time = time.time()
        
        if not turnaround_mode:
            s.state = "RESET"
            turn_flag = "DISABLED"


        temp_buffer_setup = False
        status_flag = "OK"
        rangelines_array = None
        az_array = None
        el_array = None
        ch_array = None
        prev_az = None
        reset_in_array = False
        az_val_prev = None

        # index of the rangeline.  Also doubles as number of rangelines 
        # captureed
        i = 0 
        
        # debug time vals
        tot_dur             = 0
        tot_datagrab_dur    = 0
        tot_other_dur       = 0
        tot_misc_dur        = 0
        if debug:
            loop_start          = time.time_ns()
            data_grab_start     = loop_start
            other_time_start    = loop_start
            loop_end            = loop_start
        while True:
            if debug:
                tot_inc             = (loop_end - loop_start)
                tot_datagrab_inc    = (other_time_start - data_grab_start)
                tot_other_inc       = (loop_end - other_time_start)
                tot_misc_inc        = (tot_inc - tot_datagrab_inc - 
                                       tot_other_inc)
                                        

                tot_dur             += tot_inc
                tot_datagrab_dur    += tot_datagrab_inc
                tot_other_dur       += tot_other_inc
                tot_misc_dur        += tot_misc_inc

                loop_start = time.time_ns()
            if not s.get_conn_status():
                turn_flag = "DISABLED"
                status_flag = "DAQ_NOT_CONNECTED"
                break

            # there's a sort of "inner" buffer local only to this loop
            # this is an inefficient way of doing it, but allowed me to make
            # a faster update to the code
            if temp_buffer_setup:
                if i == num_rangelines:
                    print("num_rangelines reached")
                    break


            # this is if there's a timeout
            if time.time() - start_time > timeout:
                turn_flag = "DISABLED" 
                status_flag = "TIMEOUT"
                break

            # check for status from the core
            #if s.cdh_pipe_in.poll():
            if not s.cdh_queue_rx.empty():
                #cdh_dict_in = s.cdh_pipe_in.recv()
                cdh_dict_in = s.cdh_queue_rx.get()
                if "STATUS" in cdh_dict_in:
                    if cdh_dict_in["STATUS"] == "CONN_RESET":
                        status_flag = "CONN_RESET"
                        turn_flag = "DISABLED"
                        break


            ##################################################################
            ########################## CORE SAMPLE GRAB ######################
            ##################################################################
            if debug:
                data_grab_start = time.time_ns()

            (rangeline, az_val, el_val, 
             channel_val, data_valid) = s.get_sample()
            
            if debug:
                other_time_start = time.time_ns()

            # check for returning none
            if data_valid == False:
                if debug:
                    loop_end = time.time_ns()
                    #print("daq_comms: data_valid == False")
                continue

            # DEBUG
            #if az_val_prev == None:
            #    pass
            #else:
            #    az_diff = (az_val - az_val_prev)
            #    abs_diff = np.abs(az_diff)
            #    if abs_diff > 5:
            #        pass
                    #print(f"az_diff = {az_diff}")
            #az_val_prev = az_val



            # setup the buffers now because you don't know the 
            # length of the rangeline until now
            if not temp_buffer_setup:
                len_rangeline = len(rangeline)
                #rangelines_array = np.zeros((num_rangelines, 
                #    len_rangeline), dtype=np.complex128)
                rangelines_array = np.zeros((num_rangelines, 
                    len_rangeline), dtype=np.complex64)
                az_array = np.zeros((num_rangelines))
                el_array = np.zeros((num_rangelines))
                ch_array = np.zeros((num_rangelines))
                temp_buffer_setup = True

            if len(rangeline) != len_rangeline:
                status_flag = "RANGELINE_LEN_CHANGE"
                s.state = "RESET"
                break


            # state machine
            # Note: nonzero turn_hyst will produce "wobble" at frame
            # edges
            if turnaround_mode:
                if channel_val == 0:
                    az_val_adj = az_val + ch0_offset
                else:
                    az_val_adj = az_val + ch1_offset

                if s.state == "RESET":
                    turn_flag = "RESET"
                    if az_val_adj < (min_az - turn_hyst):
                        s.state = "TURNING_MIN"
                    elif az_val_adj > (max_az + turn_hyst):
                        s.state = "TURNING_MAX"
                    else:
                        az_val_adj = "WAITING_FOR_TURN"

                elif s.state == "WAITING_FOR_TURN":
                    turn_flag = "RESET"
                    if az_val_adj < (min_az - turn_hyst):
                        s.state = "TURNING_MIN"
                    elif az_val_adj > (max_az + turn_hyst):
                        s.state = "TURNING_MAX"

                    # else: s.state stays the same

                elif s.state == "TURNING_MIN":
                    turn_flag = "RESET"
                    # start of frame
                    if az_val_adj > (min_az + turn_hyst):
                        s.state = "RUNNING_TO_MAX"
                        turn_flag = "START_FRAME"

                elif s.state == "TURNING_MAX":
                    turn_flag = "RESET"
                    # start of frame
                    if az_val_adj < (max_az - turn_hyst):
                        s.state = "RUNNING_TO_MIN"
                        turn_flag = "START_FRAME"

                elif s.state == "RUNNING_TO_MAX":
                    turn_flag = "RUNNING"
                    if az_val_adj > (max_az + turn_hyst):
                        s.state = "TURNING_MAX"
                        turn_flag = "END_FRAME"

                elif s.state == "RUNNING_TO_MIN":
                    turn_flag = "RUNNING"
                    if az_val_adj < (min_az - turn_hyst):
                        s.state = "TURNING_MIN"
                        turn_flag = "END_FRAME"

                else:
                    raise Exception("Invalid SimpRadar State")
                
                # Now we perform the appropriate updates based on 
                # state


                # this is to ensure the processing reset prior to 
                # grabbing the first data sample 
                if turn_flag in ["RESET", "START_FRAME"]:
                    reset_in_array = True

                # only add values to the array in valid azimuth ranges
                if turn_flag in ["RUNNING", "START_FRAME", "END_FRAME"]:
                    rangelines_array[i] = rangeline
                    az_array[i] = az_val
                    el_array[i] = el_val
                    ch_array[i] = channel_val
                    i += 1

                if turn_flag == "END_FRAME":
                    #status_flag = "TURNAROUND"
                    s.state = "RESET"
                    break

            else: # turnaround mode not enabled
                rangelines_array[i] = rangeline
                az_array[i] = az_val
                el_array[i] = el_val
                ch_array[i] = channel_val
                i += 1

            if debug:
                loop_end = time.time_ns()

        if debug:
            if i != 0:
                print("---------------DURATIONS PER RANGELINE ACQ ------------")
                print(f"Total number of rangelines: {i}")
                print(f"tot_dur: {tot_dur/1e3/i:.4f} us")
                #print(f"tot_daq_sock_dur: {tot_daq_sock_dur/1e3/i:.4f} us")
                print(f"tot_datagrab_dur: {tot_datagrab_dur/1e3/i:.4f} us")
                print(f"tot_other_dur: {tot_other_dur/1e3/i:.4f} us")
                print(f"tot_misc_dur: {tot_misc_dur/1e3/i:.5f} us")
                print("-------------------------------------------------------\n")

        return (rangelines_array, az_array, el_array, ch_array, 
                i, turn_flag, reset_in_array, status_flag)


