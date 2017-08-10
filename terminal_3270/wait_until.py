from timeit import default_timer as timer


class WaitUntil(object):
    """ Wait Until an Event Occurs or Time Limit.

    The WaitUntil object is an easy way to poll until a change is met.
    Eventually, the `time_limit` will be reached to indicate failure.

        found_callable(*args, **kwargs) returns True when it meets the condition.
    """

    def __init__(self, time_limit, found_callable, *args, **kwargs):
        """ Create WaitUntil poller.

        :param float time_limit: maximum time limit in fractional seconds
        :param callable found_callable: a callable that returns True when it finds the state
        :param tuple args: found_callable args parameters
        :param dict kwargs: found_callable kwargs parameters
        :raises: TypeError or ValueError for invalid found_callable or time_limit, respectively
        """

        if not callable(found_callable):
            raise TypeError('"found_callable" must be a bool callable function')

        if time_limit <= 0.0:
            raise ValueError('"time_limit" must be positive number, e.g. 0.725 seconds')

        self.time_limit = time_limit
        self.found_callable = found_callable
        self.call_args = args
        self.call_kwargs = kwargs

        self.start_t = 0.0
        self.end_t = 0.0

    def poll(self):
        """ Poll Until Found.

        Poll this WaitUntil object until the found state or time limit.
        """

        self.start_t = timer()

        while not self.found_callable(*self.call_args, **self.call_kwargs):
            curr_t = timer()
            if (curr_t - self.start_t) >= self.time_limit:
                break

        self.end_t = timer()

    @property
    def elapsed(self):
        return (self.end_t - self.start_t)

    @property
    def expired(self):
        return (self.elapsed > self.time_limit)


if __name__ == '__main__':  # pragma: no cover

    class Clicker(object):
        """ Clicker Example

        Run a counting clicker until it reaches a a number.
        """

        def __init__(self):
            self.counter = 0

        def click_button(self, *args, **kwargs):
            self.counter += 1
            print('Click! counter=%d call(args=%r, kwargs=%r)' % (self.counter, args, kwargs))
            return (self.counter > 3000 * 100)

    clicker = Clicker()

    wu_runner = WaitUntil(0.725, clicker.click_button, *(1, 2, 'ok'), **{'eat': 'shorts', 'qwerty': 12})
    wu_runner.poll()

    print('WaitUntil gives time elapsed={}'.format(wu_runner.elapsed))
