# -*- coding: utf-8 -*-
'''
Encrypted CoAP server with multiple resources.
Only /counter requires AES-encrypted token.
'''

import sys
import datetime
import base64
from twisted.internet import defer, reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# AES Configuration (MUST match client)
SECURITY_TOKEN = "s3cr3t"
AES_KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32 bytes for AES-256
AES_IV = b'InitializationVe'                   # 16 bytes

def decrypt_payload(ciphertext_b64):
    encrypted = base64.b64decode(ciphertext_b64)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted.decode()

# Resource: Counter (Encrypted access)
class CounterResource(resource.CoAPResource):
    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.counter = start
        self.visible = True
        self.addParam(resource.LinkParam("title", "Encrypted Counter Resource"))

    def render_GET(self, request):
        try:
            token = decrypt_payload(request.payload.decode())
        except Exception:
            response = coap.Message(code=coap.UNAUTHORIZED, payload="Decryption failed")
            return defer.succeed(response)

        if token != SECURITY_TOKEN:
            response = coap.Message(code=coap.UNAUTHORIZED, payload="Invalid token")
            return defer.succeed(response)

        payload = str(self.counter)
        self.counter += 1
        response = coap.Message(code=coap.CONTENT, payload=payload)
        return defer.succeed(response)

# Resource: Block
class BlockResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.addParam(resource.LinkParam("title", "Simple Message String Resource"))

    def render_GET(self, request):
        payload = "Welcome to NUS School of Computing..."
        response = coap.Message(code=coap.CONTENT, payload=payload)
        return defer.succeed(response)

    def render_PUT(self, request):
        log.msg('PUT payload: %s' % request.payload)
        response = coap.Message(code=coap.CHANGED, payload="Updated")
        return defer.succeed(response)

# Resource: Separate Large Payload
class SeparateLargeResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.addParam(resource.LinkParam("title", "Large Text Resource"))

    def render_GET(self, request):
        d = defer.Deferred()
        reactor.callLater(3, self.responseReady, d)
        return d

    def responseReady(self, d):
        payload = "Seek what you know as the highest..."
        response = coap.Message(code=coap.CONTENT, payload=payload)
        d.callback(response)

# Resource: Time (Observable)
class TimeResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True
        self.addParam(resource.LinkParam("title", "Time Now"))
        self.notify()

    def notify(self):
        self.updatedState()
        reactor.callLater(1, self.notify)

    def render_GET(self, request):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = coap.Message(code=coap.CONTENT, payload=now)
        return defer.succeed(response)

# Resource: Core Discovery
class CoreResource(resource.CoAPResource):
    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)

# Set up the CoAP resource tree
log.startLogging(sys.stdout)
root = resource.CoAPResource()

# /.well-known/core
well_known = resource.CoAPResource()
core = CoreResource(root)
well_known.putChild('core', core)
root.putChild('.well-known', well_known)

# /counter (encrypted)
counter = CounterResource(5000)
root.putChild('counter', counter)

# /time (observable)
time = TimeResource()
root.putChild('time', time)

# /other/block and /other/separate
other = resource.CoAPResource()
block = BlockResource()
separate = SeparateLargeResource()
other.putChild('block', block)
other.putChild('separate', separate)
root.putChild('other', other)

# Start server
endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))
reactor.run()
