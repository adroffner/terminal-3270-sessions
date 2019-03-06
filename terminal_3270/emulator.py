""" Emulator Plus

This EmulatorPlus class extends the standard py3270.Emulator to add common 3270 commands.
The extra methods provide important features.
"""

import logging

from py3270 import Emulator
from terminal_3270.wait_until import WaitUntil

log = logging.getLogger(__name__)


class EmulatorError(Exception):
    pass


class ScreenWaitError(EmulatorError):
    pass


class EmulatorPlus(Emulator):
    """ 3270 Emulator Plus

    This class extends the standard py3270.Emulator to add common 3270 commands.
    """

    def send_clear(self):
        self.exec_command('Clear()'.encode('ascii'))

    def send_pa_key(self, number):
        self.exec_command('PA({})'.format(number).encode('ascii'))

    def send_pf_key(self, number):
        self.exec_command('PF({})'.format(number).encode('ascii'))

    def send_tab(self):
        self.exec_command('Tab()'.encode('ascii'))

    def key_entry(self, text):
        """ Key Entry

        Type the key entry into a local field without sending it to the server.
        This must be done to enter text into a `protected field` such as a username or password.

        :param str text: this is the text to type into the local screen
        """

        for ch in text:
            self.exec_command('Key(U+{:04X})'.format(ord(ch)).encode('ascii'))

    def format_screen(self, screen_name):
        """ Format Screen

        Set the screen format, "/FOR <screen_name>".

        :param str screen_name: set the screen to this named format
        """

        self.send_clear()
        self.move_to(1, 1)
        self.key_entry("/FOR {}".format(screen_name))
        self.send_enter()

    def screen_command(self, command_name, cmd_row=1, cmd_column=10):
        """ Send Screen Command

        A current screen format, "/FOR <screen_name>" exists with a COMMAND buffer.
        The Emulator has made all the key_entry() values into fields.
        Now, enter the `command_name` and execute it.

        :param str command_name: send the command named this
        """

        self.move_to(cmd_row, cmd_column)
        self.key_entry(command_name)
        self.send_enter()

    def status_bar(self, terminator_strings=[], passing_strings=[], status_row=24):
        """ Status Bar

        Read the `status bar`, default row 24, after entering a command.
        This explains the screen status as a human readable string.

        Either...

        Match any of the `terminator_strings` to end a result-set with status as `False`.
        Search result tables use this to terminate the fetch-loop.

        OR...

        Match any of the `passing_strings` to validate the status as `True`.
        This let's the caller have a simple boolean test to prove the status is `ok`.

        :param list terminator_strings: when non-empty, set bool status to False
        :param list passing_strings: when non-empty, set bool status result
        :param int status_row: read the status row number, row 24 by default
        :returns: success or failure and the status bar
        :rtype: tuple, (bool, STATUS BAR string)
        """

        status_text = self.string_get(status_row, 1, 80)
        log.debug('STATUS-BAR: [{}]'.format(status_text))

        if terminator_strings:
            status_ok = not any([(v.upper() in status_text) for v in terminator_strings])
        elif passing_strings:
            status_ok = any([(v.upper() in status_text) for v in passing_strings])
        else:
            status_ok = True
        return (status_ok, status_text)

    def wait_for_screen(self, screen_str, row_loc, col_loc, time_limit=0.750):
        """ Wait for Screen to Render.

        Wait until the new screen renders the `screen_str` at location (row_loc, col_loc).
        This avoids race conditions where the terminal draws a new screen slowly,
        after the automation types into it.

        :param str screen_str: a string on the screen that should be ready
        :param int row_loc: row where string starts (1-based)
        :param int col_loc: col where string starts (1-based)
        :param float time_limit: a time limit in seconds to wait
        :raises: ScreenWaitError when the `time_limit` is reached
        """

        wait_until = WaitUntil(time_limit, self.string_found, *(row_loc, col_loc, screen_str))
        wait_until.poll()

        if wait_until.expired:
            raise ScreenWaitError('next screen did not appear in {} seconds'.format(time_limit))

    def get_special_char_str(self, ypos, xpos, length):
        """
            Get a string of `length` at screen co-ordinates `ypos`/`xpos`

            Co-ordinates are 1 based, as listed in the status area of the
            terminal.
        """
        # the screen's coordinates are 1 based, but the command is 0 based
        xpos -= 1
        ypos -= 1
        cmd = self.exec_command('Ascii({0},{1},{2})'.format(ypos, xpos, length).encode('latin-1'))
        # this usage of ascii should only return a single line of data
        print(cmd)
        assert len(cmd.data) == 1, cmd.data
        return cmd.data[0].decode('latin-1')