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
        self.MAX_BUF_SIZE = 8192
        self.buf_init = False
        self.curr_buf = None
        self.next_buf = None
        self.curr_buf_bytes = 0
        self.buf_ind = 0

    def close(self):
        self.sock.close()


    def read_from_buf(self, length):
        # initialize the ping buffer
        if not self.buf_init:
            self.curr_buf = self.sock.recv(self.MAX_BUF_SIZE)
            self.curr_buf_ping = True
            self.curr_buf_bytes = len(self.curr_buf)

        else:
            # the straighforward grab
            if length <= self.curr_buf_bytes:
                data_out = self.curr_buf[self.buf_ind:self.buf_ind+length]
                self.buf_ind = self.buf_ind + length
                self.curr_buf_bytes = self.curr_buf_bytes - length
                return data_out

            # need to read more bytes from the socket 
            if length > self.curr_buf_bytes:
                self.next_buf = self.sock.recv(self.MAX_BUF_SIZE)
                self.next_buf_bytes = len(self.next_buf)

                # not enough bytes, hopefully a rare occurrence
                if length > (self.curr_buf_bytes + self.next_buf_bytes):
                    print("Warning: LOW DATA RATE OR BUFFER PROBLEM")
                    self.next_buf += self.sock.recv(self.MAX_BUF_SIZE)
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
                   
                
    def recv_full(self, length):
        data = bytearray()
        while len(data) < length:
            try:
                if len(self.data_buffer) > 0:
                    data = self.data_buffer[:length]
                    self.data_buffer = self.data_buffer[length:]
                if len(data) == length:
                    break
                data += self.sock.recv(length-len(data))
            except socket.timeout:
                self.data_buffer += data
                return None
        return bytes(data)

    def receive_message(self):
        length = self.recv_full(4)

        # if a timeout occurred getting the data, we just wait til the next
        # loop iteration
        if length == None:
            return (None, False)

        packet_size = int.from_bytes(length, "big", signed=False)

        data = self.recv_full(packet_size)

        # for a timeout, we return the valid length value back to the buffer 
        # so on the next iteration we pull that from the buffer 
        if data == None:
            self.data_buffer += length
            return (None, False)

        recv_delimiter = self.recv_full(4)
        # for a timeout here we have to return both "data" and "length" values
        # to the buffer
        if recv_delimiter == None:
            self.data_buffer += data 
            self.data_buffer += length
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

    def recv(self, length):
        return self.sock.recv(length)


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
            s.connect(s.addr)
        
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

def main_acq_loop(cdh_pipe_in, cdh_pipe_out, data_queue):
    CHUNKSIZE = 1000
    daq_sock = DAQSocket()


    # setup buffers
    

    while True:
        #####################################################################
        #                       CDH HANDLING STEPS                          #
        #####################################################################
        while cdh_pipe_in.poll():
            command_in = query_in_pipe.recv()
            command_keys = command_ind.keys()

            if "INIT_CONN" in command_keys:
                (msg_id, (addr, en_channels)) = command_in["INIT_CONN"] 
                status = daq_sock.init_connection(addr, en_channels)
                new_dict_out = OrderedDict()
                new_dict_out["INIT_CONN"] = (msg_id, status)
                cdh_pipe_out.send(new_dict_out)


            elif "DISCONNECT" in command_keys:
                (msg_id, _) = command_in["DISCONNECT"] 
                daq_sock.close()
                new_dict_out = OrderedDict()
                new_dict_out["DISCONNECT"] = (msg_id, None)
                cdh_pipe_out.send(new_dict_out)


            elif "SEND_TRACE" in command_keys:
                (msg_id, en_channels) = command_in["SEND_TRACE"] 
                status = daq_sock.send_trace_config(en_channels)
                new_dict_out = OrderedDict()
                new_dict_out["SEND_TRACE"] = (msg_id, status)
                cdh_pipe_out.send(new_dict_out)


            else:
                print("INVALID CDH Object")


        #####################################################################
        #                  MAIN RANGELINE ACQUISITION                       #
        #####################################################################

        try:
            (radar_data, data_valid) = s.daq_sock.receive_message()
        except ConnectionResetError:
            s.daq_connected = False
            status_flag = "CONN_RESET"
            turn_flag = "DISABLED"
            break

        if debug:
            data_grab_start = time.time_ns()

        # check for returning none
        if data_valid == False:
            if debug:
                other_time_start = time.time_ns()
                loop_end = time.time_ns()
                print("daq_comms: data_valid == False")
            continue

        else:
            if radar_data.message_type == TLVPlotCmd.SEND_TRACE_DATA:
                s.tot_rangelines += 1
                az_val = float(
                    from_14_bit(
                        radar_data.get_by_tag(
                            TLVTracePCIeHTGZRF80002Tag.AZIMUTH_MOTOR_UINT
                        ).data,
                        True,))
                
                el_val = float(
                    from_14_bit(
                        radar_data.get_by_tag(
                            TLVTracePCIeHTGZRF80002Tag.ELEVATION_MOTOR_UINT
                        ).data,
                        False,))

                rangeline = np.frombuffer(
                    radar_data.get_by_tag(TLVPlotTag.DATA_DOUBLE).data, 
                        dtype=np.complex64)


                channel_val = int.from_bytes(
                    radar_data.get_by_tag(
                        TLVTracePCIeHTGZRF80002Tag.CHANNEL_UINT).data,
                    "big",
                    signed=False,)

                if debug:
                    other_time_start = time.time_ns()

                # setup the buffers now because you don't know the 
                # length of the rangeline until now
                if not buffer_setup:
                    len_rangeline = len(rangeline)
                    #rangelines_array = np.zeros((num_rangelines, 
                    #    len_rangeline), dtype=np.complex128)
                    rangelines_array = np.zeros((num_rangelines, 
                        len_rangeline), dtype=np.complex64)
                    az_array = np.zeros((num_rangelines))
                    el_array = np.zeros((num_rangelines))
                    ch_array = np.zeros((num_rangelines))
                    buffer_setup = True

                if len(rangeline) != len_rangeline:
                    status_flag = "RANGELINE_LEN_CHANGE"
                    s.state = "RESET"
                    break

    




