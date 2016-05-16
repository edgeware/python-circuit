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

"""Test cases for the circuit breaker."""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mockito import mock

from circuit import breaker, CircuitOpenError


class Clock(object):
    now = 0.0

    def time(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class CircuitBreakerTestCase(unittest.TestCase):
    """Test cases for the circuit breaker."""

    def setUp(self):
        self.clock = Clock()
        self.log = mock()
        self.maxfail = 2
        self.reset_timeout = 10
        self.time_unit = 60
        self.breaker = breaker.CircuitBreaker(self.clock.time, self.log,
                                              [IOError], self.maxfail,
                                              self.reset_timeout,
                                              self.time_unit)

    def test_passes_through_unhandled_errors(self):
        try:
            with self.breaker:
                raise RuntimeError("error")
        except RuntimeError:
            self.assertEquals(len(self.breaker.errors), 0)
        else:
            self.assertTrue(False, "exception not raised")

    def test_catches_handled_errors(self):
        try:
            with self.breaker:
                raise IOError("error")
        except IOError:
            self.assertEquals(len(self.breaker.errors), 1)
        else:
            self.assertTrue(False, "exception not raised")

    def test_opens_breaker_on_errors(self):
        self.breaker.error()
        self.breaker.error()
        self.breaker.error()
        self.assertEquals(self.breaker.state, 'open')

    def test_allows_unfrequent_errors(self):
        for i in range(10):
            self.breaker.error()
            self.clock.advance(30)
        self.assertEquals(self.breaker.state, 'closed')

    def test_closes_breaker_on_successful_transaction(self):
        self.test_opens_breaker_on_errors()
        self.clock.advance(self.reset_timeout)
        self.assertEquals(self.breaker.test(), 'half-open')
        self.breaker.success()
        self.assertEquals(self.breaker.test(), 'closed')

    def test_raises_circuit_open_when_open(self):
        self.test_opens_breaker_on_errors()
        self.assertRaises(breaker.CircuitOpenError, self.breaker.test)

    def test_context_exit_without_exception_resets_circuit(self):
        self.breaker.state = 'half-open'
        with self.breaker:
            pass
        self.assertEquals(self.breaker.state, 'closed')

    def test_context_exit_with_exception_marks_error(self):
        def test():
            with self.breaker:
                raise IOError("error")
        self.assertRaises(IOError, test)
        self.assertEquals(len(self.breaker.errors), 1)

    def test_exponential_backoff_timeout(self):
        self.breaker = breaker.CircuitBreaker(self.clock.time, self.log,
                                              [IOError], self.maxfail,
                                              self.reset_timeout,
                                              self.time_unit,
                                              64, with_jitter=False)

        # Test that the failure after first reset_timeout * 1 bumps the
        # failure counter
        self.test_opens_breaker_on_errors()
        self.clock.advance(self.reset_timeout)
        self.assertEquals(self.breaker.test(), 'half-open')
        self.breaker.error()
        self.assertEquals(self.breaker.test_fail_count, 1)

        # Test that it does not recover before the 2 ** 1 * reset_timeout
        # period
        self.clock.advance(self.reset_timeout)
        raised_e = None
        try:
            self.breaker.test()
        except CircuitOpenError as e:
            raised_e = e
        self.assertIsNotNone(raised_e)
        self.assertEquals(self.breaker.test_fail_count, 1)

        # test that after the 2 ** 1 * reset_timeout the circuit half-opens
        self.clock.advance(self.reset_timeout)
        self.assertEquals(self.breaker.test(), 'half-open')

        # then another error bumps up the fail counter again
        self.breaker.error()
        self.assertEquals(self.breaker.test_fail_count, 2)
        self.clock.advance(self.reset_timeout)
        self.breaker.error()
        self.assertEquals(self.breaker.test_fail_count, 2)

        self.clock.advance(self.reset_timeout * 4)
        self.assertEquals(self.breaker.test(), 'half-open')
        self.breaker.success()
        self.assertEquals(self.breaker.test_fail_count, 0)

    def test_backoff_with_jitter(self):
        self.breaker = breaker.CircuitBreaker(self.clock.time, self.log,
                                              [IOError], self.maxfail,
                                              self.reset_timeout,
                                              self.time_unit,
                                              64, with_jitter=True)
        self.test_opens_breaker_on_errors()
        self.clock.advance(self.reset_timeout)
        self.breaker.test()
        self.breaker.error()
        self.assertEquals(self.breaker.test_fail_count, 1)
        self.clock.advance(self.reset_timeout * 2)
        self.breaker.test()
        self.breaker.error()
        self.assertEquals(self.breaker.test_fail_count, 2)
        # Should have a reset_time of:
        # [0, 4 * reset_timeout] * random.random(), mean = 2 * reset_timeout.
        # 99th percentile value of count of failures
        failure_count = 0
        self.clock.advance(self.reset_timeout * 2)
        for _ in range(1000):
            try:
                self.breaker.test()
                self.breaker.open()
                self.clock.advance(self.reset_timeout * 2)
            except CircuitOpenError:
                failure_count += 1

        # .999999999 chance of falling in this range
        self.assertGreater(failure_count, 400)

        self.assertLess(failure_count, 600)
