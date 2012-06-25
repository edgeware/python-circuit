A circuit breaker according to the logic outline in Michael T. Nygard's 
great book [Release It!](http://www.amazon.com/Release-It-Production-Ready-Pragmatic-Programmers/dp/0978739213).

Read: http://en.wikipedia.org/wiki/Circuit_breaker_design_pattern

The circuit breaker monitors communication with a remote peer and in
the case of a high error rate may break the circuit and not allow
further communication for a short period.  After a while the breaker
will let through a single request to probe to see if the peer feels
better.  If it does, it will close the circuit and allow requests once
again.  If not, it will open the circuit again.

A `CircuitBreakerSet` can handle the state for multiple peers at the
same time.  Use the `context` method to pick which peer to track.  The
first argument is used to identify the peer.  Make it a string of some
kind, since it will be used to identify the peer in logs.

Below is a small example of how the circuit breaker can be used:

    from circuit import CircuitBreakerSet
    import logging, time

    circuit_breaker = CircuitBreakerSet(time.time, logging.getLogger(
        'circuit-breaker'))
    circuit_breaker.handle_error(ValueError)

    def fn(circuit_breaker):
        try:
            with circuit_breaker.context('my-remote-peer'):
               raise ValueError('oh no')
        except CircuitOpenError:
            # the circuit was open so we did not even try to communicate
            # with the remote service.
            raise

If you call `fn` often enough the circuit breaker will open and
`CircuitOpenError` will be raised.

The `CircuitBreakerSet` class takes a few keyword arguments:

* `time_unit` (default 60) -- Number of seconds to sample seconds over.
* `maxfail` (default 3) -- Number of seconds that is allowed over a time unit.
* `reset_timeout` (default 10) -- Seconds that the circuit is open before
   going into half-open mode.

It is also possible to create a single instance of a circuit breaker.  The
`circuit.CircuitBreaker` class takes the following arguments:

* `clock` -- A callable that returns the time in seconds.
* `log` -- a `logging.Logger` object used for logging.
* `error_types` -- A list of error types that are treated as errors.
* `maxfail` -- Number of seconds that is allowed over a time unit.
* `reset_timeout` -- Seconds that the circuit is open before
   going into half-open mode.
* `time_unit` -- Number of seconds to sample seconds over.


# Twisted Support #

There's also support for using the circuit breaker with Twisted.  Note that
the circuit breaker still use pythons standard logging framework. Example:

    from circuit import TwistedCircuitBreakerSet
    import logger

    circuit_breaker = TwistedCircuitBreakerSet(reactor, logging.getLogger(
        'circuit-breaker'))

(The `TwistedCircuitBreakerSet` adds support for `defer.returnValue`
which uses exceptions internally.)

# Thanks #

* Michael Nygard, http://www.michaelnygard.com/, for writing the Release It!
  book that outlines the circuit breaker pattern

* Edgeware, http://www.edgeware.tv/, for sponsoring the development of
  python-circuit.
