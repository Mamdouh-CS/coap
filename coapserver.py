'''
Created on 30-05-2019
CoAP server runs in official IANA assigned CoAP port 5683.
@author: Bhojan Anand   (adapted from sample codes)
'''


import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap


class CounterResource (resource.CoAPResource):     #extends CoAPRecource class
    """
    Example Resource which supports only GET method. Response is a
    simple counter value.

    Name render_<METHOD> is required by convention. Such method should
    return a Deferred. [Python-differ module provides a small framework for asynchronous programming. The Deferred allows to chain callbacks.
    There are two type of callbacks: normal callbacks and errbacks, which handle an exception in a normal callback.] If the result is available immediately it's best
    to use Twisted method defer.succeed(msg).
    """
   #isLeaf = True

    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.counter = start
        self.visible = True
        self.addParam(resource.LinkParam("title", "Simple Counter Resource"))

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload='%d' % (self.counter,))
        self.counter += 1
        return defer.succeed(response)


class BlockResource (resource.CoAPResource):
    """
    Example Resource which supports GET, and PUT methods. It sends large
    responses, which trigger blockwise transfer (>64 bytes for normal
    settings).

    As before name render_<METHOD> is required by convention.
    """
     

    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.addParam(resource.LinkParam("title", "Simple Message String Resource"))

    def render_GET(self, request):
        payload=" Welcome to NUS school of computing. In this course you will learn Secured Internet of Things application development and Analytics"
        response = coap.Message(code=coap.CONTENT, payload=payload)
        return defer.succeed(response)

    def render_PUT(self, request):
        log.msg('PUT payload: %s', request.payload)
        payload = "Just do it!."
        response = coap.Message(code=coap.CHANGED, payload=payload)
        return defer.succeed(response)


class SeparateLargeResource(resource.CoAPResource):
    """
    Example Resource which supports GET method. It uses callLater
    to force the protocol to send empty ACK first and separate response
    later. Sending empty ACK happens automatically after coap.EMPTY_ACK_DELAY.
    No special instructions are necessary.

    Notice: txThings sends empty ACK automatically if response takes too long.

    Method render_GET returns a deferred. This allows the protocol to
    do other things, while the answer is prepared.

    Method responseReady uses d.callback(response) to "fire" the deferred,
    and send the response.
    """
     

    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.addParam(resource.LinkParam("title", "Some Large Text Resource."))

    def render_GET(self, request):
        d = defer.Deferred()
        reactor.callLater(3, self.responseReady, d, request)
        return d

    def responseReady(self, d, request):
        log.msg('response ready. sending...')
        payload = "Seek what you know as the highest. It does not matter whether it is going to happen or not - living with a vision itself is a very elevating process."
        response = coap.Message(code=coap.CONTENT, payload=payload)
        d.callback(response)

class TimeResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify()
        self.addParam(resource.LinkParam("title", "Time now"))

    def notify(self):
        log.msg('TimeResource: trying to send notifications')
        self.updatedState()
        reactor.callLater(1, self.notify)

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        return defer.succeed(response)

class CoreResource(resource.CoAPResource):
    """
    Example Resource that provides list of links hosted by a server.
    Normally it should be hosted at /.well-known/core

    Resource should be initialized with "root" resource, which can be used
    to generate the list of links.

    For the response, an option "Content-Format" is set to value 40,
    meaning "application/link-format". Without it most clients won't
    be able to automatically interpret the link format.

    Notice that self.visible is not set - that means that resource won't
    be listed in the link format it hosts.
    """

    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        log.msg("%s", payload)
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)

# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()

well_known = resource.CoAPResource()
root.putChild('.well-known', well_known)
core = CoreResource(root)
well_known.putChild('core', core)

counter = CounterResource(5000)
root.putChild('counter', counter)

time = TimeResource()
root.putChild('time', time)

other = resource.CoAPResource()
root.putChild('other', other)

block = BlockResource()
other.putChild('block', block)

separate = SeparateLargeResource()
other.putChild('separate', separate)

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
