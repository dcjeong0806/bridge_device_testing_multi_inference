# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63ommon.proto\x12\x06\x63ommon\";\n\x04Size\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\x12\r\n\x05width\x18\x03 \x01(\x05\x12\x0e\n\x06heigth\x18\x04 \x01(\x05\"\x07\n\x05\x45mpty\"\x1d\n\x05Point\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05*8\n\nEventClass\x12\n\n\x06person\x10\x00\x12\x07\n\x03\x62\x61g\x10\x01\x12\x0b\n\x07vehicle\x10\x02\x12\x08\n\x04\x66ire\x10\x03*\x8e\x02\n\tEventType\x12\x08\n\x04None\x10\x00\x12\r\n\tLoitering\x10\x01\x12\r\n\tIntrusion\x10\x02\x12\x0c\n\x08\x46\x61llDown\x10\x03\x12\x0e\n\nCongestion\x10\n\x12\x0c\n\x08LongStay\x10\x0c\x12\x0c\n\x08WrongWay\x10\x0f\x12\r\n\tLineEnter\x10\x10\x12\t\n\x05\x46ight\x10\x18\x12\x0e\n\nAbandonded\x10(\x12\r\n\tSpeedGate\x10\x64\x12\x0c\n\x08TailGate\x10\x65\x12\x12\n\rAbandoned4Tnm\x10\xc9\x01\x12\x15\n\x10LoiteringPPE4Tnm\x10\xca\x01\x12\x15\n\x10RoadBlockCar4Tnm\x10\xcb\x01\x12\x16\n\x11TailgatingCar4Tnm\x10\xcc\x01\x42+\n\x14io.grpc.nextk.commonB\x0b\x43ommonProtoP\x01\xa2\x02\x03RFPb\x06proto3')

_EVENTCLASS = DESCRIPTOR.enum_types_by_name['EventClass']
EventClass = enum_type_wrapper.EnumTypeWrapper(_EVENTCLASS)
_EVENTTYPE = DESCRIPTOR.enum_types_by_name['EventType']
EventType = enum_type_wrapper.EnumTypeWrapper(_EVENTTYPE)
person = 0
bag = 1
vehicle = 2
fire = 3
globals()['None'] = 0
Loitering = 1
Intrusion = 2
FallDown = 3
Congestion = 10
LongStay = 12
WrongWay = 15
LineEnter = 16
Fight = 24
Abandonded = 40
SpeedGate = 100
TailGate = 101
Abandoned4Tnm = 201
LoiteringPPE4Tnm = 202
RoadBlockCar4Tnm = 203
TailgatingCar4Tnm = 204


_SIZE = DESCRIPTOR.message_types_by_name['Size']
_EMPTY = DESCRIPTOR.message_types_by_name['Empty']
_POINT = DESCRIPTOR.message_types_by_name['Point']
Size = _reflection.GeneratedProtocolMessageType('Size', (_message.Message,), {
  'DESCRIPTOR' : _SIZE,
  '__module__' : 'common_pb2'
  # @@protoc_insertion_point(class_scope:common.Size)
  })
_sym_db.RegisterMessage(Size)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'common_pb2'
  # @@protoc_insertion_point(class_scope:common.Empty)
  })
_sym_db.RegisterMessage(Empty)

Point = _reflection.GeneratedProtocolMessageType('Point', (_message.Message,), {
  'DESCRIPTOR' : _POINT,
  '__module__' : 'common_pb2'
  # @@protoc_insertion_point(class_scope:common.Point)
  })
_sym_db.RegisterMessage(Point)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\024io.grpc.nextk.commonB\013CommonProtoP\001\242\002\003RFP'
  _EVENTCLASS._serialized_start=125
  _EVENTCLASS._serialized_end=181
  _EVENTTYPE._serialized_start=184
  _EVENTTYPE._serialized_end=454
  _SIZE._serialized_start=24
  _SIZE._serialized_end=83
  _EMPTY._serialized_start=85
  _EMPTY._serialized_end=92
  _POINT._serialized_start=94
  _POINT._serialized_end=123
# @@protoc_insertion_point(module_scope)
