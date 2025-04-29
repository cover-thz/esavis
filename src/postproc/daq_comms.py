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
import ipdb
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
class DAQSocket:
    def __init__(self):
        self.sock = None

    def connect(self, addr):
        self.sock = socket.socket()
        self.sock.connect((addr, 10001))
        self.sock.settimeout(0.25)
        self.data_buffer = bytearray()

    def close(self):
        self.sock.close()

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

#############################################################################
#############################################################################




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
    daq_sock            = None
    en_channels         = None 
    daq_connected       = False
    rangeline_buffer    = None
    state               = "RESET"

    def __init__(s):
        s.daq_sock = DAQSocket()
        s.tot_rangelines = 0
        s.en_channels = []

    def setup_comms(s, addr, ch0_en, ch1_en):
        s.addr = addr
        s.set_en_channels(ch0_en, ch1_en, send_trace=False)
        status = s.init_connection()
        return status


    def set_en_channels(s, ch0_en, ch1_en, send_trace=True):
        en_channels = []
        if ch0_en:
            en_channels.append(0)
        if ch1_en:
            en_channels.append(1)
        s.en_channels = copy.copy(en_channels)
        if send_trace:
            s.send_trace_config()


    def init_connection(s):
        try:
            s.daq_sock.connect(s.addr)
        except IOError as e:
            s.daq_connected = False
            s.daq_sock.close()
            #print("Failed to connect to DAQ socket")
            #s.warning_made.emit(["Failed to connect to DAQ socket"])
            #print(e)
            return False

        s.daq_connected = True
        print("Connected")

        # receive configs (and do nothing with them)
        s.daq_sock.receive_message()
        s.send_trace_config()
        return True


    def disconnect(s):
        if s.daq_connected:
            s.daq_sock.close()
            s.daq_connected = False


    # need to call this at the beginning and whenever we change the number of 
    # channels.  I think.
    def send_trace_config(s):
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
        for channel in s.en_channels:
            traces.append(trace_template.replace("{{channel}}", str(channel)))
        full_config = "<configs>\n{{traces}}\n</configs>\x00"
        full_config = full_config.replace("{{traces}}", "\n".join(traces))
        trace_tlv = TLV(
            TLVPlotTag.CONFIGSXML_STRING,
            TLVType.CHAR_ARRAY,
            bytes(full_config, "utf-8"),
        )

        trace_message = TLVMessage(TLVPlotCmd.SEND_TRACE_CONFIG, [trace_tlv])
        s.daq_sock.send_message(trace_message)


    # main workhorse function
    def get_daq_data(s, num_rangelines, turnaround_mode, turn_hyst, min_az, 
                     max_az, ch0_offset, ch1_offset, timeout=3):
                                              
        start_time = time.time()
        
        if not turnaround_mode:
            s.state = "RESET"
            turn_flag = "DISABLED"


        buffer_setup = False
        status_flag = "OK"
        rangelines_array = None
        az_array = None
        el_array = None
        ch_array = None
        prev_az = None
        az_diff_pos = None
        reset_in_array = False

        # index of the rangeline.  Also doubles as number of rangelines 
        # captureed
        i = 0 
        while True:

            if not s.daq_connected:
                turn_flag = "DISABLED"
                status_flag = "DAQ_NOT_CONNECTED"
                break

            if buffer_setup:
                if i == num_rangelines:
                    break

            # this is if there's a timeout
            if time.time() - start_time > timeout:
                turn_flag = "DISABLED" 
                status_flag = "TIMEOUT"
                break

            try:
                (radar_data, data_valid) = s.daq_sock.receive_message()
            except ConnectionResetError:
                s.daq_connected = False
                status_flag = "CONN_RESET"
                turn_flag = "DISABLED"
                break

            # check for returning none
            if data_valid == False:
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


                    # setup the buffers now because you don't know the 
                    # length of the rangeline until now
                    if not buffer_setup:
                        len_rangeline = len(rangeline)
                        rangelines_array = np.zeros((num_rangelines, 
                            len_rangeline), dtype=np.complex128)
                        az_array = np.zeros((num_rangelines))
                        el_array = np.zeros((num_rangelines))
                        ch_array = np.zeros((num_rangelines))
                        buffer_setup = True

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


                        
                else:
                    print("Warning: Received non-plot command data")
                    continue

        return (rangelines_array, az_array, el_array, ch_array, 
                i, turn_flag, reset_in_array, status_flag)


