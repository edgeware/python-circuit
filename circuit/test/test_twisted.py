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

from mockito import mock, when
import unittest

from twisted.internet import task, defer

from circuit import TwistedCircuitBreakerSet


class TwistedCircuitBreakerTestCase(unittest.TestCase):

    def setUp(self):
        self.clock = task.Clock()
        self.log = mock()
        when(self.log).getChild('ctxt').thenReturn(self.log)
        self.circuit_breaker = TwistedCircuitBreakerSet(self.clock,
           self.log)

    def test_context_exit_with_inline_callbacks_resets_circuit(self):
        @defer.inlineCallbacks
        def test():
            with self.circuit_breaker.context('ctxt') as breaker:
                breaker.state = 'half-open'
                yield defer.succeed(None)
                defer.returnValue(None)
        test()
        self.assertEquals(self.circuit_breaker.circuits['ctxt'].state,
                          'closed')
