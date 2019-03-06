from unittest import TestCase, mock

from terminal_3270.emulator import EmulatorPlus, ScreenWaitError


class TestEmulatorPlus(TestCase):

    def setUp(self):
        self.emulator = EmulatorPlus(app=mock.MagicMock())

    def tearDown(self):
        # Pretend to shut down Emulator.
        self.emulator.is_terminated = True

    def test_send_clear(self):

        with mock.patch('terminal_3270.emulator.Emulator.exec_command') as mock_exec_command:
            self.emulator.send_clear()
            mock_exec_command.assert_called_with('Clear()'.encode('ascii'))

    def test_send_pf_key(self):

        with mock.patch('terminal_3270.emulator.Emulator.exec_command') as mock_exec_command:
            number = 12
            self.emulator.send_pf_key(number)
            mock_exec_command.assert_called_with('PF({})'.format(number).encode('ascii'))

    def test_send_tab(self):

        with mock.patch('terminal_3270.emulator.Emulator.exec_command') as mock_exec_command:
            self.emulator.send_tab()
            mock_exec_command.assert_called_with('Tab()'.encode('ascii'))

    def test_key_entry(self):

        with mock.patch('terminal_3270.emulator.Emulator.exec_command') as mock_exec_command:
            text_str = 'example'
            self.emulator.key_entry(text_str)

            expected_exec_cmds = [mock.call('Key(U+{:04X})'.format(ord(ch)).encode('ascii')) for ch in text_str]
            self.assertEqual(mock_exec_command.mock_calls, expected_exec_cmds)

    def test_format_screen(self):

        with mock.patch('terminal_3270.emulator.Emulator.exec_command') as mock_exec_command:
            screen_name = 'NEW4SCREEN'
            self.emulator.format_screen(screen_name)

            expected_exec_cmds = [
                mock.call('Clear()'.encode('ascii')),
                mock.call('MoveCursor(0, 0)'.encode('ascii')),
            ]
            expected_exec_cmds.extend([
                mock.call('Key(U+{:04X})'.format(ord(ch)).encode('ascii')) for ch in "/FOR {}".format(screen_name)
            ])
            expected_exec_cmds.append(mock.call('Enter'.encode('ascii')))
            self.assertEqual(mock_exec_command.mock_calls, expected_exec_cmds)

    def test_screen_command(self):

        with mock.patch('terminal_3270.emulator.Emulator.exec_command') as mock_exec_command:
            command_name = 'TST'
            self.emulator.screen_command(command_name)

            expected_exec_cmds = [
                mock.call('MoveCursor(0, 9)'.encode('ascii')),
            ]
            expected_exec_cmds.extend([
                mock.call('Key(U+{:04X})'.format(ord(ch)).encode('ascii')) for ch in command_name
            ])
            expected_exec_cmds.append(mock.call('Enter'.encode('ascii')))
            self.assertEqual(mock_exec_command.mock_calls, expected_exec_cmds)

    def test_status_bar_read_only(self):
        " Read STATUS BAR without passing_strings and assume True "

        expected_status_bar = 'TEST BAR'

        with mock.patch('terminal_3270.emulator.Emulator.string_get', return_value=expected_status_bar) as mock_string_get:
            passing_strings = []  # empty list is the default value.
            (status_bool, status_bar) = self.emulator.status_bar(passing_strings=passing_strings, status_row=13)

            mock_string_get.assert_called_with(13, 1, 80)  # Capture status_row=13
            self.assertTrue(status_bool)  # passing_strings irrelevant
            self.assertEqual(expected_status_bar, status_bar)

    def test_status_bar_passing_strings_match(self):

        expected_status_bar = 'TEST BAR'

        with mock.patch('terminal_3270.emulator.Emulator.string_get', return_value=expected_status_bar) as mock_string_get:
            passing_strings = ['Test', 'OTHER', 'bar']
            (status_bool, status_bar) = self.emulator.status_bar(passing_strings=passing_strings)

            mock_string_get.assert_called_with(24, 1, 80)  # Capture line 24
            self.assertTrue(status_bool)  # 2 of the three passing_strings match
            self.assertEqual(expected_status_bar, status_bar)

    def test_status_bar_passing_strings_failure(self):

        expected_status_bar = 'TEST BAR'

        with mock.patch('terminal_3270.emulator.Emulator.string_get', return_value=expected_status_bar) as mock_string_get:
            passing_strings = ['Detest', 'ANOTHER', 'rebar']
            (status_bool, status_bar) = self.emulator.status_bar(passing_strings=passing_strings)

            mock_string_get.assert_called_with(24, 1, 80)  # Capture line 24
            self.assertFalse(status_bool)  # none of the three passing_strings match
            self.assertEqual(expected_status_bar, status_bar)

    # =========================================================================

    def test_status_bar_terminator_strings_found(self):
        " Status Bar found terminator_strings and is False to stop. "

        expected_status_bar = 'END TEST BAR'

        with mock.patch('terminal_3270.emulator.Emulator.string_get', return_value=expected_status_bar) as mock_string_get:
            terminator_strings = ['end']
            (status_bool, status_bar) = self.emulator.status_bar(terminator_strings=terminator_strings)

            mock_string_get.assert_called_with(24, 1, 80)  # Capture line 24
            self.assertFalse(status_bool)
            self.assertEqual(expected_status_bar, status_bar)

    def test_status_bar_terminator_strings_not_found(self):
        " Status Bar did not find terminator_strings and is True to continue. "

        expected_status_bar = 'CONTINUE TEST BAR'

        with mock.patch('terminal_3270.emulator.Emulator.string_get', return_value=expected_status_bar) as mock_string_get:
            terminator_strings = ['end']
            (status_bool, status_bar) = self.emulator.status_bar(terminator_strings=terminator_strings)

            mock_string_get.assert_called_with(24, 1, 80)  # Capture line 24
            self.assertTrue(status_bool)
            self.assertEqual(expected_status_bar, status_bar)

    # =========================================================================

    def test_wait_for_screen_found(self):

        mock_wait_until = mock.MagicMock()
        mock_expired_property = mock.PropertyMock(return_value=False)
        type(mock_wait_until).expired = mock_expired_property

        with mock.patch('terminal_3270.emulator.WaitUntil', return_value=mock_wait_until) as mock_wait_until_class:

            expected_str = 'SIGNON SCREEN HERE'
            expected_row = 5
            expected_col = 12

            self.emulator.wait_for_screen(expected_str, expected_row, expected_col)

            mock_wait_until_class.assert_called_with(0.750, self.emulator.string_found, *(expected_row, expected_col, expected_str))
            self.assertTrue(mock_wait_until.poll.called)
            self.assertTrue(mock_expired_property.called)

    def test_wait_for_screen_exception(self):

        mock_wait_until = mock.MagicMock()
        mock_expired_property = mock.PropertyMock(return_value=True)
        type(mock_wait_until).expired = mock_expired_property

        with self.assertRaises(ScreenWaitError):
            with mock.patch('terminal_3270.emulator.WaitUntil', return_value=mock_wait_until) as mock_wait_until_class:

                expected_str = 'SIGNON SCREEN HERE'
                expected_row = 5
                expected_col = 12

                self.emulator.wait_for_screen(expected_str, expected_row, expected_col)

                mock_wait_until_class.assert_called_with(0.750, self.emulator.string_found, *(expected_row, expected_col, expected_str))
                self.assertTrue(mock_wait_until.poll.called)
                self.assertTrue(mock_expired_property.called)

    def test_get_special_char_str(self):
        xpos = 2
        ypos = 4
        length = 10
        with mock.patch('terminal_3270.emulator.Emulator.exec_command', side_effect=mock.Mock()) as mock_exec:
            mock_exec.data = ["data"]
            result = self.emulator.get_special_char_str(ypos, xpos, length)
            print(result)

