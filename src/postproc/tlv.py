from enum import IntEnum, auto
from typing import List


class TLVPlotCmd(IntEnum):
    UNDEFINED = 0
    SEND_CONFIG = auto()
    SEND_TRACE_CONFIG = auto()
    SEND_TRACE_DATA = auto()
    SEND_TRIGGER = auto()
    MAX = auto()


class TLVPlotTag(IntEnum):
    UNDEFINED = 0
    RETURN_RESULT = auto()
    NAME_STRING = auto()
    CONFIGXML_STRING = auto()
    CONFIGSXML_STRING = auto()
    DATA_DOUBLE = auto()
    AUXXML_STRING = auto()
    TRIGGER_INT = auto()
    MAX = auto()


class TLVTracePCIeHTGZRF80002Tag(IntEnum):
    DESCRIPTOR_UINT = TLVPlotTag.MAX
    CHANNEL_UINT = auto()
    PROFILECNTR_ULONG = auto()
    RELTIMECNTR_ULONG = auto()
    AZIMUTH_MOTOR_UINT = auto()
    ELEVATION_MOTOR_UINT = auto()


class TLVType(IntEnum):
    UNKNOWN = 0
    CHAR_ARRAY = auto()
    INT8 = auto()
    INT16 = auto()
    INT32 = auto()
    INT64 = auto()
    MAX = auto()


class TLV:
    # data must be big endian
    def __init__(self, tag: int, tlv_type: TLVType, data: bytes):
        self.tag = tag
        self.tlv_type = tlv_type
        self.data = data

    def encode(self):
        buffer = bytearray()
        tag_type = ((self.tlv_type & 0xFFFF) << 16) | (self.tag & 0xFFFF)

        buffer += tag_type.to_bytes(4, "big", signed=False)
        buffer += len(self.data).to_bytes(4, "big", signed=False)

        buffer += self.data

        return buffer

    def encoded_length(self):
        # 4 (tag/type) + 4 (length) + length (data)
        return 8 + len(self.data)

    # self.data will be big endian
    @classmethod
    def decode(cls, data: memoryview):
        if len(data) < 8:
            raise ValueError("Invalid data length A")

        tag_type = int.from_bytes(data[:4], "big", signed=False)
        length = int.from_bytes(data[4:8], "big", signed=False)

        tag = tag_type & 0xFFFF
        tlv_type = (tag_type >> 16) & 0xFFFF

        if len(data) < 8 + length:
            raise ValueError("Invalid data length B")

        value_data = data[8 : 8 + length]

        return cls(tag, tlv_type, value_data)


class TLVMessage:
    def __init__(self, message_type: int, tlvs: List[TLV] = None):
        if tlvs is None:
            tlvs = []
        self.message_type = message_type
        self.tlvs = tlvs

    def add_tlv(self, tlv: TLV):
        self.tlvs.append(tlv)

    def encode(self):
        buffer = bytearray()

        buffer += self.message_type.to_bytes(4, "big", signed=False)
        buffer += len(self.tlvs).to_bytes(4, "big", signed=False)
        for tlv in self.tlvs:
            buffer += tlv.encode()

        return buffer

    def get_by_tag(self, tag):
        for tlv in self.tlvs:
            if tlv.tag == tag:
                return tlv
        return None

    @classmethod
    def decode(cls, data: memoryview):
        message_type = int.from_bytes(data[:4], "big", signed=False)
        tlv_count = int.from_bytes(data[4:8], "big", signed=False)

        data_i = 8
        tlvs: List[TLV] = []
        for _ in range(tlv_count):
            tlvs.append(TLV.decode(data[data_i:]))
            data_i += tlvs[-1].encoded_length()

        return cls(message_type, tlvs)
