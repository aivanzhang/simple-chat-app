# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: main.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmain.proto\"@\n\x0bUserRequest\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\"\x1c\n\tUserReply\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x07\n\x05\x45mpty\"7\n\x13PendingMsgsResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x0f\n\x07isEmpty\x18\x02 \x01(\x08\x32h\n\x07\x43hatter\x12\"\n\x04\x43hat\x12\x0c.UserRequest\x1a\n.UserReply\"\x00\x12\x39\n\x17ListenToPendingMessages\x12\x06.Empty\x1a\x14.PendingMsgsResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'main_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERREQUEST._serialized_start=14
  _USERREQUEST._serialized_end=78
  _USERREPLY._serialized_start=80
  _USERREPLY._serialized_end=108
  _EMPTY._serialized_start=110
  _EMPTY._serialized_end=117
  _PENDINGMSGSRESPONSE._serialized_start=119
  _PENDINGMSGSRESPONSE._serialized_end=174
  _CHATTER._serialized_start=176
  _CHATTER._serialized_end=280
# @@protoc_insertion_point(module_scope)