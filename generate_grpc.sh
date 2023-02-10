python -m grpc_tools.protoc -I grpc_stubs/protos --python_out=grpc_stubs --pyi_out=grpc_stubs --grpc_python_out=grpc_stubs grpc_stubs/protos/main.proto
