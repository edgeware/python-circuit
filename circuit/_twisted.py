# Copyright 2012 Edgeware AB.
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

from circuit.breaker import CircuitBreaker, CircuitBreakerSet
try:
    from twisted.internet import defer
except ImportError:
    pass


class TwistedCircuitBreaker(CircuitBreaker):
    """Circuit breaker that know that L{defer.inlineCallbacks} use
    exceptions in its internal workings.
    """

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is defer._DefGen_Return:
            exc_type, exc_val, tb = None, None, None
        return CircuitBreaker.__exit__(self, exc_type, exc_val, tb)


class TwistedCircuitBreakerSet(CircuitBreakerSet):
    """Circuit breaker that supports twisted."""

    def __init__(self, reactor, logger, **kwargs):
        kwargs.update({'factory': TwistedCircuitBreaker})
        CircuitBreakerSet.__init__(self, reactor.seconds, logger, **kwargs)
