python -m grpc_tools.protoc -I wire_protocol/protos --python_out=wire_protocol/grpc --pyi_out=wire_protocol/grpc --grpc_python_out=wire_protocol/grpc wire_protocol/protos/main.proto
