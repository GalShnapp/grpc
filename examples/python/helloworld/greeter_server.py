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
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
import logging

import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import hashlib
import json
import os.path
from os import path


PTMD_FILE_PATH = 'persistence/dict.json'
PATH_TO_MD5_DICT = {}

def persist_ptmd():
    _json = json.dumps(PATH_TO_MD5_DICT)
    f = open(PTMD_FILE_PATH,"w")

    # write json object to file
    f.write(_json)

    # close file
    f.close()

def load_ptmd():
    with open(PTMD_FILE_PATH, "r") as file:
        PATH_TO_MD5_DICT = json.load(file)
    

def write_kv_to_ptmd(fname: str, md5: str): 
    PATH_TO_MD5_DICT[fname] = md5

def write_to_ptmv_and_persist(fname: str, md5: str):
    write_kv_to_ptmd(fname, md5)
    try:
        persist_ptmd()
    except Exception as e:
        print(e)

def get_val_from_ptmd(filename: str) -> str:
    return PATH_TO_MD5_DICT.get(filename, None)

def calc_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return f'{hash_md5.hexdigest()}'


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        fname = request.name
        if not path.exists(fname):
            return helloworld_pb2.HelloReply(message=f'error: file {fname} does not exist')
        try:
            md5 = calc_md5(fname)
        except TypeError as te: 
            return helloworld_pb2.HelloReply(message=f'type error {te}')

        known_md5 = get_val_from_ptmd(fname)
        write_to_ptmv_and_persist(fname, md5)
        return helloworld_pb2.HelloReply(message=f'f:{fname}, m_0: {known_md5} m_1:{md5} res {known_md5 != md5}')   
           



def secure_serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    with open('key.pem', 'rb') as f:
        private_key = f.read()
    with open('key.pem.pub', 'rb') as f:
        certificate_chain = f.read()
    server_credentials = grpc.ssl_server_credentials( ( (private_key, certificate_chain), ) )
    
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    
    server.add_secure_port('127.0.0.1:443', server_credentials)
    server.start()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #secure_serve()
    serve()
