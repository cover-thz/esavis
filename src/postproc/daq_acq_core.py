#############################################################################
# File Name: daq_acq_core.py
# Date Created: 4/30/2025
# Original Author: Max Bryk
# Description
#   This is the DAQ acquisition core, which is a seperate process that 
#   retrieves data from the DAQ, and properly organizes it to be sent 
#   over a multiprocessing pipe when requested 
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
import ipdb
from collections import OrderedDict
from tlv import (
    TLV,
    TLVMessage,
    TLVPlotCmd,
    TLVPlotTag,
    TLVTracePCIeHTGZRF80002Tag,
    TLVType,
)

delimiter = bytes([0xAA, 0x99, 0x55, 0x66])

def from_14_bit(data: bytes, signed: bool):
    new_data = bytearray(data)
    if data[2] & 0x20 != 0 and signed:
        new_data[2] = data[2] | 0xC0
        new_data[0] = 0xFF
        new_data[1] = 0xFF
    return int.from_bytes(new_data, "big", signed=signed)


#############################################################################
#############################################################################
# this is modified to incorporate the various functions from daq_comms that 
# were previously in SimpRadar
class DAQSocket:
    def __init__(self):
        self.sock = None

    def connect(self, addr):
        self.sock = socket.socket()
        self.sock.connect((addr, 10001))
        self.sock.settimeout(0.25)
        self.data_buffer = bytearray()

        # buffer variables
        #self.MAX_BUF_SIZE = 65536
        self.MAX_BUF_SIZE = 1048576 
        self.sock_accesses = 0
        self.buf_init = False
        self.curr_buf = None
        self.next_buf = None
        self.curr_buf_bytes = 0
        self.buf_ind = 0

    def close(self):
        self.buf_init = False
        self.sock.close()


    def read_from_buf(self, length):
        # initialize the buffer
        if not self.buf_init:
            #self.curr_buf = self.sock.recv(self.MAX_BUF_SIZE)
            vals = self.recv_alias(self.MAX_BUF_SIZE)
            if vals == None:
                return None
            else:
                self.curr_buf = vals
            self.curr_buf_bytes = len(self.curr_buf)
            self.buf_init = True

        # the straighforward grab
        if length <= self.curr_buf_bytes:
            data_out = self.curr_buf[self.buf_ind:self.buf_ind+length]
            self.buf_ind = self.buf_ind + length
            self.curr_buf_bytes = self.curr_buf_bytes - length
            return data_out

        # need to read more bytes from the socket 
        if length > self.curr_buf_bytes:
            #self.next_buf = self.sock.recv(self.MAX_BUF_SIZE)
            vals = self.recv_alias(self.MAX_BUF_SIZE)
            if vals == None:
                return None
            else:
                self.next_buf = vals
            #self.next_buf = self.recv_alias(self.MAX_BUF_SIZE)
            self.next_buf_bytes = len(self.next_buf)

            # not enough bytes, hopefully a rare occurrence
            if length > (self.curr_buf_bytes + self.next_buf_bytes):
                print("Warning: LOW DATA RATE OR BUFFER PROBLEM")
                #self.next_buf += self.sock.recv(self.MAX_BUF_SIZE)
                #self.next_buf += self.recv_alias(self.MAX_BUF_SIZE)
                vals = self.recv_alias(self.MAX_BUF_SIZE)
                if vals == None:
                    return None
                else:
                    self.next_buf = vals
                self.next_buf_bytes = len(self.next_buf)

            # if it happens again we abort
            if length > (self.curr_buf_bytes + self.next_buf_bytes):
                print("Warning: TOO FEW BYTES")
                return None
            
            # grab everything left in the current buffer
            data_out = self.curr_buf[self.buf_ind:]
            excess_bytes = length - self.curr_buf_bytes

            # grab the remaining necessary from the next buffer
            data_out += self.next_buf[:excess_bytes]
            self.curr_buf_bytes = self.next_buf_bytes - excess_bytes
            self.buf_ind = excess_bytes
            self.curr_buf = self.next_buf
            return data_out

    # if we get something that derails the acquisition process we want to 
    # return the bytes we grabbed from the buffer back to the buffer
    # this is designed to happen infrequently as it requires messing with
    # the size of teh buffer in order to be done cleanly which theoretically
    # is a very slow thing and this file is a speed bottleneck for the code
    def return_to_buf(self, vals):
        self.curr_buf = self.curr_buf[self.buf_ind:]
        self.curr_buf = vals + self.curr_buf
        self.buf_ind  = 0
        self.curr_buf_bytes += len(vals)
                   
                
    def recv_full(self, length):
        data = bytearray()
        while len(data) < length:
            try:
                if len(self.data_buffer) > 0:
                    data = self.data_buffer[:length]
                    self.data_buffer = self.data_buffer[length:]
                if len(data) == length:
                    break
                data += self.read_from_buf(length-len(data))
                #data += self.sock.recv(length-len(data))
            except socket.timeout:
                self.data_buffer += data
                return None
        return bytes(data)


    #def recv_full(self, length):
    #    data = bytearray()
    #    while len(data) < length:
    #        try:
    #            if len(self.data_buffer) > 0:
    #                data = self.data_buffer[:length]
    #                self.data_buffer = self.data_buffer[length:]
    #            if len(data) == length:
    #                break
    #            data += self.read_from_buf(length-len(data))
    #            #data += self.sock.recv(length-len(data))
    #        except socket.timeout:
    #            self.data_buffer += data
    #            return None
    #    return bytes(data)


    def receive_message(self):
        #length = self.recv_full(4)
        length = self.read_from_buf(4)

        # if a timeout occurred getting the data, we just wait til the next
        # loop iteration
        if length == None:
            return (None, False)

        packet_size = int.from_bytes(length, "big", signed=False)
        #data = self.recv_full(packet_size)
        data = self.read_from_buf(packet_size)

        # for a timeout, we return the valid length value back to the buffer 
        # so on the next iteration we pull that from the buffer 
        if data == None:
            #self.data_buffer += length
            self.return_to_buf(length)
            return (None, False)

        #recv_delimiter = self.recv_full(4)
        recv_delimiter = self.read_from_buf(4)
        # for a timeout here we have to return both "data" and "length" values
        # to the buffer
        if recv_delimiter == None:
            #self.data_buffer += data 
            #self.data_buffer += length
            self.return_to_buf(data)
            self.return_to_buf(length)
            return (None, False)

        if recv_delimiter != delimiter:
            file_name = uuid.uuid4().hex + ".bin"
            with open(file_name, "wb") as dump_file:
                dump_file.write(length)
                dump_file.write(data)
                dump_file.write(recv_delimiter)
            except_str  = f"Packet end delimiter ({str(recv_delimiter)}) "
            except_str += f"was not equal to {str(delimiter)}. Full packet "
            except_str += f"dumped to {file_name}"
            raise RuntimeError(except_str)

        return (TLVMessage.decode(data), True)
    
    @staticmethod
    def pack_message(message: TLVMessage):
        encoded = message.encode()
        length = len(encoded)
        full_message = (length.to_bytes(4, "big", signed=False) + 
                        message.encode() + delimiter)
        
        return full_message

    def send_message(self, message: TLVMessage):
        self.sock.send(DAQSocket.pack_message(message))

    # so I can track accesses to the socket better
    def recv_alias(self, length):
        try:
            vals = self.sock.recv(length)
        except socket.timeout:
            return None

        #self.sock_accesses += 1
        #if vals != self.MAX_BUF_SIZE:
        #    print(f"sock accessed only grabbed {len(vals)} vals")
        #if self.sock_accesses % 1000 == 0:
        #    print(f"numb sock_accesses = {self.sock_accesses}")
        return vals


    ##########################################################################
    ############# Functions formerly from SimpRadar ##########################
    ##########################################################################
    def send_trace_config(s, en_channels):
        # need to have trace_config.xml in the same directory as the 
        # postprocessing code
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.name == "nt":
            #REPO_TOP_DIR = os.path.dirname(os.getcwd())
            trace_cfg_fpath = current_dir + "\\trace_config.xml"
        else:
            trace_cfg_fpath = current_dir + "/trace_config.xml"

        trace_template = ""
        with open(trace_cfg_fpath, "r", encoding="utf-8") as tc:
            trace_template = tc.read()
        traces = []
        for channel in en_channels:
            traces.append(trace_template.replace("{{channel}}", str(channel)))
        full_config = "<configs>\n{{traces}}\n</configs>\x00"
        full_config = full_config.replace("{{traces}}", "\n".join(traces))
        trace_tlv = TLV(
            TLVPlotTag.CONFIGSXML_STRING,
            TLVType.CHAR_ARRAY,
            bytes(full_config, "utf-8"),
        )

        trace_message = TLVMessage(TLVPlotCmd.SEND_TRACE_CONFIG, [trace_tlv])
        s.send_message(trace_message)

    def init_connection(s, addr, en_channels):
        try:
            s.connect(addr)
        
        except IOError as e:
            #s.daq_connected = False
            s.close()
            return False

        except Exception as e:
            #s.daq_connected = False
            s.close()
            print(e)
            return False
   
        # receive configs (and do nothing with them)
        s.receive_message()
        s.send_trace_config(en_channels)
        return True





#############################################################################
#############################################################################


"""
cdh transactions to code:
    ack = s.ack_cdh_handshake_trans("SEND_TRACE", s.en_channels)
    ack = s.ack_cdh_handshake_trans("DISCONNECT", None)
    status = s.ack_cdh_handshake_trans("INIT_CONN", (s.addr, s.en_channels))


chunksize is the number of rangelines that appear in each "chunk" put into
the queue
chunksize will be hard-coded for now, it's not the kind of thing that should 
be changed often

"""

#def main_acq_loop(cdh_pipe_in, cdh_pipe_out, data_queue):
def main_acq_loop(cdh_queue_in, cdh_queue_out, data_queue):
    CHUNK_SIZE = 10000 
    chunk_count = 0
    daq_sock = DAQSocket()
    daq_connected = False
    tot_rangelines = 0
    acq_msg_id = 0
    buffer_setup = False
    az_val_prev = None
    i = 0

    # debug switch that enables various messages
    # and other debug variables
    acq_debug = False
    loop_start_ns = time.perf_counter_ns()
    time_div_0_ns = loop_start_ns
    time_div_1_ns = loop_start_ns
    time_div_2_ns = loop_start_ns
    time_div_3_ns = loop_start_ns
    time_div_4_ns = loop_start_ns
    time_div_5_ns = loop_start_ns
    time_div_6_ns = loop_start_ns
    time_div_7_ns = loop_start_ns
    time_div_chunk_0 = loop_start_ns
    time_div_chunk_1 = loop_start_ns
    loop_end_ns   = loop_start_ns


    slice_0_ns_dur = 0
    slice_1_ns_dur = 0
    slice_2_ns_dur = 0
    slice_3_ns_dur = 0
    slice_4_ns_dur = 0
    slice_5_ns_dur = 0
    slice_6_ns_dur = 0
    slice_7_ns_dur = 0
    slice_8_ns_dur = 0


    slice_0_tot_us_dur = 0
    slice_1_tot_us_dur = 0
    slice_2_tot_us_dur = 0
    slice_3_tot_us_dur = 0
    slice_4_tot_us_dur = 0
    slice_5_tot_us_dur = 0
    slice_6_tot_us_dur = 0
    slice_7_tot_us_dur = 0
    slice_8_tot_us_dur = 0


    chunk_dur_ns = 0
    chunk_dur_tot_us = 0

    cdh_loop_cntr = 0
    dbg_loop_cntr = 0
    dbg_prev_chunk_time = None
    dbg_prev_chunk_count = 0
    while True:
        cdh_loop_cntr += 1
        #print(f"cdh_loop_cntr: {cdh_loop_cntr}")
        #####################################################################
        #                DEBUG TIME DURATION HANDLING STEPS                 #
        #####################################################################

        if acq_debug:
            slice_0_ns_dur = time_div_0_ns - loop_start_ns
            slice_1_ns_dur = time_div_1_ns - time_div_0_ns
            slice_2_ns_dur = time_div_2_ns - time_div_1_ns
            slice_3_ns_dur = time_div_3_ns - time_div_2_ns
            slice_4_ns_dur = time_div_4_ns - time_div_3_ns
            slice_5_ns_dur = time_div_5_ns - time_div_4_ns
            slice_6_ns_dur = time_div_6_ns - time_div_5_ns
            slice_7_ns_dur = time_div_7_ns - time_div_6_ns
            slice_8_ns_dur = loop_end_ns   - time_div_7_ns

            slice_0_tot_us_dur += slice_0_ns_dur/1e3
            slice_1_tot_us_dur += slice_1_ns_dur/1e3
            slice_2_tot_us_dur += slice_2_ns_dur/1e3
            slice_3_tot_us_dur += slice_3_ns_dur/1e3
            slice_4_tot_us_dur += slice_4_ns_dur/1e3
            slice_5_tot_us_dur += slice_5_ns_dur/1e3
            slice_6_tot_us_dur += slice_6_ns_dur/1e3
            slice_7_tot_us_dur += slice_7_ns_dur/1e3
            slice_8_tot_us_dur += slice_8_ns_dur/1e3

            dbg_loop_cntr += 1

            if dbg_loop_cntr % 20000 == 0:
                print(f"dbg_loop_cntr: {dbg_loop_cntr} loops")
                print(f"slice_0 avg dur: {slice_0_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_1 avg dur: {slice_1_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_2 avg dur: {slice_2_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_3 avg dur: {slice_3_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_4 avg dur: {slice_4_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_5 avg dur: {slice_5_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_6 avg dur: {slice_6_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_7 avg dur: {slice_7_tot_us_dur/dbg_loop_cntr:.4f} us")
                print(f"slice_8 avg dur: {slice_8_tot_us_dur/dbg_loop_cntr:.4f} us\n")


        loop_start_ns = time.perf_counter_ns()
        time_div_0_ns = loop_start_ns
        time_div_1_ns = loop_start_ns
        time_div_2_ns = loop_start_ns
        time_div_3_ns = loop_start_ns
        time_div_4_ns = loop_start_ns
        time_div_5_ns = loop_start_ns
        time_div_6_ns = loop_start_ns
        time_div_7_ns = loop_start_ns
        time_div_chunk_0 = loop_start_ns
        time_div_chunk_1 = loop_start_ns
        loop_end_ns   = loop_start_ns

        #####################################################################
        #                       CDH HANDLING STEPS                          #
        #####################################################################
        loop_start_ns = time.perf_counter_ns()

        # only check once every chunk, see if that speeds things up
        if ((i == CHUNK_SIZE-1) or ((not daq_connected) and 
                (cdh_loop_cntr >= 50)) or (daq_connected and 
                cdh_loop_cntr >= 100000)):
            cdh_loop_cntr = 0
            #while cdh_pipe_in.poll():
            while not cdh_queue_in.empty():
                print("CDH VALUE")
                #command_in = cdh_pipe_in.recv()
                command_in = cdh_queue_in.get()
                command_keys = command_in.keys()

                if "INIT_CONN" in command_keys:
                    (msg_id, (addr, en_channels)) = command_in["INIT_CONN"] 
                    status = daq_sock.init_connection(addr, en_channels)
                    new_dict_out = OrderedDict()
                    new_dict_out["INIT_CONN"] = (msg_id, status)
                    #cdh_pipe_out.send(new_dict_out)
                    cdh_queue_out.put(new_dict_out)

                    if status:
                        daq_connected = True
                    else:
                        daq_connected = False

                elif "DISCONNECT" in command_keys:
                    (msg_id, _) = command_in["DISCONNECT"] 
                    daq_sock.close()
                    new_dict_out = OrderedDict()
                    new_dict_out["DISCONNECT"] = (msg_id, None)
                    #cdh_pipe_out.send(new_dict_out)
                    cdh_queue_out.put(new_dict_out)
                    daq_connected = False

                elif "SEND_TRACE" in command_keys:
                    (msg_id, en_channels) = command_in["SEND_TRACE"] 
                    status = daq_sock.send_trace_config(en_channels)
                    new_dict_out = OrderedDict()
                    new_dict_out["SEND_TRACE"] = (msg_id, status)
                    #cdh_pipe_out.send(new_dict_out)
                    cdh_queue_out.put(new_dict_out)

                elif "CLOSE_PROCESS" in command_keys:
                    (msg_id, _) = command_in["CLOSE_PROCESS"] 
                    daq_sock.close()
                    new_dict_out = OrderedDict()
                    new_dict_out["CLOSE_PROCESS"] = (msg_id, None)
                    #cdh_pipe_out.send(new_dict_out)
                    cdh_queue_out.put(new_dict_out)
                    daq_connected = False

                # activates or deactivates the debug switch for this process
                elif "ACQ_DBG" in command_keys:
                    (msg_id, val) = command_in["ACQ_DBG"] 
                    new_dict_out = OrderedDict()
                    new_dict_out["ACQ_DBG"] = (msg_id, None)
                    #cdh_pipe_out.send(new_dict_out)
                    cdh_queue_out.put(new_dict_out)
                    if val == True:
                        acq_debug = True
                    else:
                        acq_debug = False
                else:
                    print("INVALID CDH Object")


        #####################################################################
        #                  MAIN RANGELINE ACQUISITION                       #
        #####################################################################

        if acq_debug:
            time_div_0_ns = time.perf_counter_ns()
        if daq_connected:
            try:
                (radar_data, data_valid) = daq_sock.receive_message()
            except ConnectionResetError:
                new_dict_out = OrderedDict()
                new_dict_out["STATUS"] = (acq_msg_id, "CONN_RESET")
                #cdh_pipe_out.send(new_dict_out)
                cdh_queue_out.put(new_dict_out)
                acq_msg_id += 1
                daq_connected = False
                buffer_setup = False
                i = 0

            # check for returning none
            if data_valid == False:
                if acq_debug:
                    print(f"data_valid = False")
                    time_div_1_ns = time.perf_counter_ns()
                continue

            else:
                if acq_debug: # NOTE DEBUG
                    time_div_1_ns = time.perf_counter_ns() # NOTE DEBUG
                if radar_data.message_type == TLVPlotCmd.SEND_TRACE_DATA:
                    tot_rangelines += 1

                    if acq_debug: # NOTE DEBUG
                        time_div_2_ns = time.perf_counter_ns() # NOTE DEBUG

                    az_val = float(
                        from_14_bit(
                            radar_data.get_by_tag(
                                TLVTracePCIeHTGZRF80002Tag.AZIMUTH_MOTOR_UINT
                            ).data,
                            True,))
                    
                    if acq_debug: # NOTE DEBUG
                        time_div_3_ns = time.perf_counter_ns() # NOTE DEBUG

                    el_val = float(
                        from_14_bit(
                            radar_data.get_by_tag(
                                TLVTracePCIeHTGZRF80002Tag.ELEVATION_MOTOR_UINT
                            ).data,
                            False,))

                    if acq_debug: # NOTE DEBUG
                        time_div_4_ns = time.perf_counter_ns() # NOTE DEBUG

                    rangeline = np.frombuffer(
                        radar_data.get_by_tag(TLVPlotTag.DATA_DOUBLE).data, 
                            dtype=np.complex64)

                    if acq_debug: # NOTE DEBUG
                        time_div_5_ns = time.perf_counter_ns() # NOTE DEBUG

                    channel_val = int.from_bytes(
                        radar_data.get_by_tag(
                            TLVTracePCIeHTGZRF80002Tag.CHANNEL_UINT).data,
                        "big",
                        signed=False,)

                    if acq_debug: # NOTE DEBUG
                        time_div_6_ns = time.perf_counter_ns() # NOTE DEBUG


                    # setup the buffers now because you don't know the 
                    # length of the rangeline until now
                    if not buffer_setup:
                        print("BUFFER SETUP CHANGED!")
                        len_rangeline = len(rangeline)
                        rangelines_array = np.empty((CHUNK_SIZE, 
                            len_rangeline), dtype=np.complex64)
                        az_array = np.empty((CHUNK_SIZE))
                        el_array = np.empty((CHUNK_SIZE))
                        ch_array = np.empty((CHUNK_SIZE))
                        buffer_setup = True

                    # if the length of the rangeline changes, immediately 
                    # trash whatever's in the current buffers 
                    if len(rangeline) != len_rangeline:
                        status_flag = "RANGELINE_LEN_CHANGE"
                        buffer_setup = False
                        i = 0
                        continue

                    # store grabbed values to the buffer
                    rangelines_array[i] = rangeline
                    az_array[i] = az_val
                    el_array[i] = el_val
                    ch_array[i] = channel_val
                    i += 1

                    # DEBUG
                    #if az_val_prev == None:
                    #    pass

                    #else:
                    #    az_diff = (az_val - az_val_prev)
                    #    abs_diff = np.abs(az_diff)
                    #    if abs_diff > 5:
                    #        print(f"ACQ->az_diff = {az_diff}")
                    #az_val_prev = az_val

                else:
                    print("Warning: Received non-plot command data")

            if acq_debug: # NOTE DEBUG
                time_div_7_ns = time.perf_counter_ns() # NOTE DEBUG

            # condition to transfer a chunk to the queue
            if acq_debug: # NOTE DEBUG
                chunk_dur_ns = 0
            if i == CHUNK_SIZE:
                if acq_debug: # NOTE DEBUG
                    time_div_chunk_0 = time.perf_counter_ns() # NOTE DEBUG
                while True:
                    if data_queue.full():
                        print("data_queue Full!")
                        time.sleep(0.01)
                    else:
                        break
                # I am having some weird stuff happen and copying these arrays
                # fixed it.
                # I suspect that the queue.put() function isn't completed 
                # before those arrays start getting modified by the next 
                # set of data coming in
                # Might make more sense to have a ping-pong buffer system
                # going on here
                rng_arr_cpy = None
                az_arr_cpy  = None
                el_arr_cpy  = None
                ch_arr_cpy  = None

                #rng_arr_cpy = copy.deepcopy(rangelines_array)
                #az_arr_cpy  = copy.deepcopy(az_array)
                #el_arr_cpy  = copy.deepcopy(el_array)
                #ch_arr_cpy  = copy.deepcopy(ch_array)

                rng_arr_cpy = rangelines_array
                az_arr_cpy  = az_array
                el_arr_cpy  = el_array
                ch_arr_cpy  = ch_array

                rangelines_array = None
                az_array = None
                el_array = None
                ch_array = None

                #data_queue.put((rangelines_array, az_array, el_array, 
                #    ch_array, chunk_count))
                data_queue.put((rng_arr_cpy, az_arr_cpy, el_arr_cpy, 
                    ch_arr_cpy, chunk_count))

                rangelines_array = np.empty((CHUNK_SIZE, 
                    len_rangeline), dtype=np.complex64)
                az_array = np.empty((CHUNK_SIZE))
                el_array = np.empty((CHUNK_SIZE))
                ch_array = np.empty((CHUNK_SIZE))

                chunk_count += 1
                i = 0
                if (chunk_count % 10) == 0:
                    dbg_curr_chunk_time = time.time()
                    if dbg_prev_chunk_time == None:
                        pass
                    else:
                        chunk_rangelines = ((chunk_count - 
                            dbg_prev_chunk_count) * CHUNK_SIZE)
                        chunk_time_diff  = dbg_curr_chunk_time - dbg_prev_chunk_time
                        rng_per_sec      = chunk_rangelines / chunk_time_diff
                        print(f"rangelines per second: {rng_per_sec}")
                    dbg_prev_chunk_time  = dbg_curr_chunk_time
                    dbg_prev_chunk_count = chunk_count

                if acq_debug: # NOTE DEBUG
                    time_div_chunk_1 = time.perf_counter_ns() # NOTE DEBUG
                    chunk_dur_ns = time_div_chunk_1 - time_div_chunk_0
                    chunk_dur_tot_us += chunk_dur_ns/1e3

        else: # daq not connected
            time.sleep(0.01)

        if acq_debug: # NOTE DEBUG
            loop_end_ns = time.perf_counter_ns() # NOTE DEBUG


