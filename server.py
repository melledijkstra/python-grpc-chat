from concurrent import futures

import grpc
import time

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self):
        # List with all the chat history
        self.chats = []

    # The stream which will be used to send new messages to clients
    def ChatStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        """
        This method is called when a clients sends a Note to the server.

        :param request:
        :param context:
        :return:
        """
        # this is only for the server console
        print("[{}] {}".format(request.name, request.message))
        # Add it to the chat history
        self.chats.append(request)
        return chat.Empty()  # something needs to be returned required by protobuf language, we just return empty msg


if __name__ == '__main__':
    port = 11912  # a random port for the server to run on
    # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
    # then no more clients able to connect to the server.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)  # register the server to gRPC
    # gRPC basically manages all the threading and server responding logic, which is perfect!
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (in another thread) so keep waiting
    # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # from the server won't continue to work and stop the server
    while True:
        time.sleep(64 * 64 * 100)
