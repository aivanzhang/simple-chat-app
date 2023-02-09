# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import main_pb2 as main__pb2


class ChatterStub(object):
    """The chat service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Chat = channel.unary_unary(
                '/Chatter/Chat',
                request_serializer=main__pb2.UserRequest.SerializeToString,
                response_deserializer=main__pb2.UserReply.FromString,
                )
        self.ListenToPendingMessages = channel.unary_unary(
                '/Chatter/ListenToPendingMessages',
                request_serializer=main__pb2.Empty.SerializeToString,
                response_deserializer=main__pb2.PendingMsgsResponse.FromString,
                )


class ChatterServicer(object):
    """The chat service definition.
    """

    def Chat(self, request, context):
        """Starts a chat with the server
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListenToPendingMessages(self, request, context):
        """Starts a listener on the server to receive messages
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Chat': grpc.unary_unary_rpc_method_handler(
                    servicer.Chat,
                    request_deserializer=main__pb2.UserRequest.FromString,
                    response_serializer=main__pb2.UserReply.SerializeToString,
            ),
            'ListenToPendingMessages': grpc.unary_unary_rpc_method_handler(
                    servicer.ListenToPendingMessages,
                    request_deserializer=main__pb2.Empty.FromString,
                    response_serializer=main__pb2.PendingMsgsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Chatter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Chatter(object):
    """The chat service definition.
    """

    @staticmethod
    def Chat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Chatter/Chat',
            main__pb2.UserRequest.SerializeToString,
            main__pb2.UserReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListenToPendingMessages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Chatter/ListenToPendingMessages',
            main__pb2.Empty.SerializeToString,
            main__pb2.PendingMsgsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)