# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function

import logging

import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import sys



def run(filename):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name=filename))
        print("client received: " + response.message)



def secure_run(filename):
    with open('key.pem.pub', 'rb') as f:
        creds = grpc.ssl_channel_credentials(f.read())
    channel = grpc.secure_channel('127.0.0.1:443', creds)
    stub = helloworld_pb2.GreeterStub(channel)
    response = stub.SayHello(helloworld_pb2.HelloRequest(name=filename))
    print("client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        print(f'don\'t be a smarty (get the reference?), just give us a filename would you?')
        sys.exit(-1)
    filename = sys.argv[1]
    print(filename)
    #secure_run(str(filename))
    run(filename)
pass
