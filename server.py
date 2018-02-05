from concurrent import futures

import grpc
import time

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        self.chats = []
        pass

    def ChatStream(self, request_iterator, context):
        lastindex = 0
        while True:
            while len(self.chats) > lastindex:
                n = chat.Note()
                n.name = self.chats[lastindex].name
                n.message = self.chats[lastindex].message
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        print("[{}] {}".format(request.name, request.message))
        self.chats.append(request)
        return chat.Empty()


if __name__ == '__main__':
    port = 11912
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    rpc.add_ChatServerServicer_to_server(ChatServer(), server)

    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)
