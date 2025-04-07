# This parses .dat files recorded by the radar arena GUI

import numpy as np
from dataclasses import dataclass, field
import sys
import ctypes

sync_word = 0X7F80000057535221

assert sys.byteorder == 'little', \
    "this module assumes little endian byte ordering"


class HeaderStruct(ctypes.LittleEndianStructure):
    sync: ctypes.c_uint64
    header_type: ctypes.c_uint32
    header_len: ctypes.c_uint32
    event_desc: ctypes.c_uint8
    channel_id: ctypes.c_uint8
    reserved_1: ctypes.c_uint16
    reserved_2: ctypes.c_uint32
    num_samps: ctypes.c_uint16
    rx_cfg_powcalc: ctypes.c_bool
    rx_cfg_fft: ctypes.c_bool
    rx_cfg_winfunc: ctypes.c_bool
    rx_cfg_ssdec: ctypes.c_bool
    rx_cfg_unused: ctypes.c_uint8
    decimation: ctypes.c_uint8
    fft_size: ctypes.c_uint8
    reserved_3: ctypes.c_uint8
    win_delay: ctypes.c_uint16
    event_ctr: ctypes.c_uint32
    reserved_4: ctypes.c_uint32
    event_clk_ctr: ctypes.c_uint64
    bri_ctr: ctypes.c_uint32
    reserved_5: ctypes.c_uint32
    pri_ctr: ctypes.c_uint32
    reserved_6: ctypes.c_uint32
    az_pos: ctypes.c_int16
    az_pad: ctypes.c_int16
    reserved_7: ctypes.c_uint16
    reserved_8: ctypes.c_uint32
    el_pos: ctypes.c_uint16
    el_pad: ctypes.c_uint16
    reserved_9: ctypes.c_uint16
    reserved_10: ctypes.c_uint32
    reserved_11: ctypes.c_uint64
    nbits_data_word: ctypes.c_uint8
    nbits_data_actual: ctypes.c_uint8
    iq_ordering: ctypes.c_bool
    complex_data: ctypes.c_bool
    signed_data: ctypes.c_bool
    floatpnt_data: ctypes.c_bool
    reserved_12: ctypes.c_uint16
    data_length: ctypes.c_uint32

    _pack_ = 1

    _fields_ = [('sync', ctypes.c_uint64, 64),
                ('header_type', ctypes.c_uint32, 32),
                ('header_len', ctypes.c_uint32, 32),
                ('event_desc', ctypes.c_ubyte, 8),
                ('channel_id', ctypes.c_ubyte, 8),
                ('reserved_1', ctypes.c_uint16, 16),
                ('reserved_2', ctypes.c_uint32, 32),
                ('num_samps', ctypes.c_uint16, 16),
                ('rx_cfg_powcalc', ctypes.c_ubyte, 1),
                ('rx_cfg_fft', ctypes.c_ubyte, 1),
                ('rx_cfg_winfunc', ctypes.c_ubyte, 1),
                ('rx_cfg_ssdec', ctypes.c_ubyte, 1),
                ('rx_cfg_unused', ctypes.c_ubyte, 4),
                ('decimation', ctypes.c_ubyte, 8),
                ('fft_size', ctypes.c_ubyte, 8),
                ('reserved_3', ctypes.c_ubyte, 8),
                ('win_delay', ctypes.c_uint16, 16),
                ('event_ctr', ctypes.c_uint32, 32),
                ('reserved_4', ctypes.c_uint32, 32),
                ('event_clk_ctr', ctypes.c_uint64, 64),
                ('bri_ctr', ctypes.c_uint32, 32),
                ('reserved_5', ctypes.c_uint32, 32),
                ('pri_ctr', ctypes.c_uint32, 32),
                ('reserved_6', ctypes.c_uint32, 32),
                ('az_pos', ctypes.c_int16, 14),
                ('az_pad', ctypes.c_int16, 2),
                ('reserved_7', ctypes.c_uint16, 16),
                ('reserved_8', ctypes.c_uint32, 32),
                ('el_pos', ctypes.c_uint16, 14),
                ('el_pad', ctypes.c_uint16, 2),
                ('reserved_9', ctypes.c_uint16, 16),
                ('reserved_10', ctypes.c_uint32, 32),
                ('reserved_11', ctypes.c_uint64, 64),
                # note the following is a bit of a hack. the ctypes
                # structure unfortunately fails the bit packing if
                # we try and use a c_ubyte here. so we'll use a
                # c_uint16 instead
                ('nbits_data_word', ctypes.c_uint16, 6),
                ('nbits_data_actual', ctypes.c_uint16, 6),
                ('iq_ordering', ctypes.c_uint16, 1),
                ('complex_data', ctypes.c_uint16, 1),
                ('signed_data', ctypes.c_uint16, 1),
                ('floatpnt_data', ctypes.c_uint16, 1),
                ('reserved_12', ctypes.c_uint16, 16),
                ('data_length', ctypes.c_uint32, 32)]

    def getlen_bytes(self):
        return round(sum([bits for name, type, bits in self._fields_])/8)

    def getdict(self) -> dict:
        return dict((f, getattr(self, f)) for f, _, __ in self._fields_)

    def print_hdr(self):
        d = self.getdict()
        for k, v in d.items():
            print(f'{k} : {v}')
        return


@dataclass
class RadarData:
    headers: list[HeaderStruct] = field(default_factory=list)
    rangelines: list[np.ndarray] = field(default_factory=list)


prfhdr_len = HeaderStruct().getlen_bytes()
# print('header length: ', prfhdr_len)
prfhdr_len_8bytes = prfhdr_len//8
# print('header length (8 bytes): ', prfhdr_len_8bytes)


def parse_data(fpaths: list) -> RadarData:
    if isinstance(fpaths, str):
        fpaths = [fpaths]

    # Next we want to identify which pairs of sequential files in the list are
    # part of a contiguous run set. We'll utilize the rigid structure of the
    # .dat file id to accomplish this.
    fid_list = [x.split('/')[-1] for x in fpaths]
    datdate = [int(x[:8]) for x in fid_list]
    dattime = [int(x[9:15]) for x in fid_list]
    dattag = [int(x[-10:-6]) for x in fid_list]
    contiguous_mrkr = [
        (datdate[i] == datdate[i+1])*(dattime[i] == dattime[i+1]) *
        (dattag[i]+1 == dattag[i+1]) for i in range(len(datdate)-1)
    ]
    assert all(contiguous_mrkr), \
        """
        The list of files provided does not constitute a contiguous set.
        """

    radar_data = RadarData()
    bindat = b''

    for j, fid in enumerate(fpaths):
        with open(fid, 'rb') as f:
            bindat += f.read()

    payload_array = np.frombuffer(bindat, dtype='<u8')

    len_payload_array = len(payload_array)
    sync_inds = np.where(payload_array == sync_word)[0]
    sync_inds = np.append(sync_inds, len_payload_array)
    ind_arr = sync_inds[0]
    sync_cnt = 0

    while ind_arr < len_payload_array:
        if ind_arr+prfhdr_len_8bytes > len_payload_array:
            # we're at the end of the binary data and there are not enough
            # bytes to fit in a full header
            ind_arr = sync_inds[sync_cnt+1]
            sync_cnt += 1
            continue

        # Now parse the header for the current profile
        cur_hdr = HeaderStruct.from_buffer_copy(
            payload_array[ind_arr:ind_arr+prfhdr_len_8bytes]
        )

        # Done parsing header - increment current ind_arr start index by
        # the header length in bytes
        ind_arr += prfhdr_len_8bytes

        cur_dat_len = cur_hdr.data_length
        cur_dat_len_8bytes = cur_dat_len//8

        if ind_arr+cur_dat_len_8bytes > len_payload_array:
            # In this case we've reached the end of the data and there are not
            # enough bytes to fit the entire profile
            ind_arr = sync_inds[sync_cnt+1]
            sync_cnt += 1
            continue

        elif ind_arr+cur_dat_len_8bytes != sync_inds[sync_cnt+1]:
            print('Bad profile******************************')
            print('Expected next sync pulse position: ',
                  ind_arr+cur_dat_len_8bytes)
            print('Actual sync pulse position: ', sync_inds[sync_cnt+1])
            print('Current profile header: ', cur_hdr)
            ind_arr = sync_inds[sync_cnt+1]
            sync_cnt += 1
            continue

        ind_prof_end = ind_arr+cur_dat_len_8bytes

        assert ~cur_hdr.iq_ordering, \
            """
            The parser is expecting the iq ordering scheme with q as MSW and i
            as LSW.
            """
        if cur_hdr.complex_data:
            # in this case we should expect fixed point 32 bit complex data
            # because numpy does not have a complex integer type, we will
            # first have to recast the data array as float32s and then can
            # view it as a complex single
            curprof_int32 = payload_array[ind_arr:ind_prof_end].view(np.int32)
            curprof = curprof_int32.astype(np.float32).view(dtype=np.csingle)
        else:
            curprof = payload_array[ind_arr:ind_prof_end].view(np.float32)
        radar_data.headers.append(cur_hdr)
        radar_data.rangelines.append(curprof)

        ind_arr = sync_inds[sync_cnt+1]
        sync_cnt += 1

    return radar_data
