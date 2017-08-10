from unittest import TestCase, mock

from terminal_3270.wait_until import WaitUntil

FOUND_ARGS = (1, 2, 'ok')
FOUND_KWARG = {'eat': 'shorts', 'qwerty': 12}


def generate_false(max_count=10000):
    for k in range(max_count):
        yield False


class TestWaitUntil(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_wait_until_found(self):

        mock_event = mock.MagicMock()
        mock_event.found_routine.side_effect = [False, False, True]

        time_limit = 0.725

        wu_runner = WaitUntil(time_limit, mock_event.found_routine, *FOUND_ARGS, **FOUND_KWARG)
        wu_runner.poll()

        mock_event.found_routine.mock_calls = [
            mock.call(*FOUND_ARGS, **FOUND_KWARG),  # False - continue
            mock.call(*FOUND_ARGS, **FOUND_KWARG),  # False - continue
            mock.call(*FOUND_ARGS, **FOUND_KWARG),  # True - stop!
        ]
        self.assertTrue(wu_runner.elapsed < time_limit)
        self.assertFalse(wu_runner.expired)

    def test_wait_until_time_limit(self):

        mock_event = mock.MagicMock()
        mock_event.found_routine.side_effect = generate_false()

        time_limit = 0.025  # 25 ms should finish before our side_effect!

        wu_runner = WaitUntil(time_limit, mock_event.found_routine, *FOUND_ARGS, **FOUND_KWARG)
        wu_runner.poll()

        mock_event.found_routine.mock_calls[-1] = mock.call(*FOUND_ARGS, **FOUND_KWARG)  # False - end on time limit
        self.assertTrue(wu_runner.elapsed >= time_limit)
        self.assertTrue(wu_runner.expired)

    def test_wait_until_bad_found_function(self):

        with self.assertRaisesRegexp(TypeError, r'^"found_callable"'):
            WaitUntil(0.1, "not_a_callable")

    def test_wait_until_bad_found_time_limit(self):

        with self.assertRaisesRegexp(ValueError, r'^"time_limit"'):
            WaitUntil(-120.1, int, *('38'))
