# -*- coding: utf-8 -*-
'''
Encrypted CoAP client that securely accesses /counter
'''

import sys
import base64
from ipaddress import ip_address

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

# Shared values (must match server)
SECURITY_TOKEN = "s3cr3t"
AES_KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32 bytes
AES_IV = b'InitializationVe'                   # 16 bytes

def encrypt_payload(plaintext):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(plaintext.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode()

class Agent:
    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = ['counter']
        encrypted_token = encrypt_payload(SECURITY_TOKEN)
        request.payload = encrypted_token.encode()
        request.remote = (ip_address("127.0.0.1"), coap.COAP_PORT)
        d = self.protocol.request(request)
        d.addCallback(self.handleResponse)
        d.addErrback(self.handleError)

    def handleResponse(self, response):
        print("Server response:", response.payload)

    def handleError(self, failure):
        print("Request failed:", failure)

log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)

reactor.listenUDP(61616, protocol)
reactor.run()
