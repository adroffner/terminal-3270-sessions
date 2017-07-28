from time import sleep
from terminal_3270.sessions import Session3270

import logging

log = logging.getLogger(__name__)


class SignOnError(ValueError):
    """ SIGNON Error.

    The SIGNON step failed.
    """
    pass


class SignOnSession(Session3270):
    """ User Signon Session to a 3270 Terminal

    This class opens an s3270 logged-in terminal session.
    Then, the user passes a sigon screen to work on tasks.

        with MySignOnSession(username, password, app_id, signon_username, signon_password, HOST_3270, visible=False) as terminal:
            results = terminal.get_results()  # declared by your subclass!

        print(results)

    OR

        terminal = MySignOnSession(username, password, app_id, signon_username, signon_password, HOST_3270)
        terminal.connect()

        terminal.term_emulator.move_to(rownum, colnum)
        terminal.term_emulator.fill_field("text")
        ...

        terminal.disconnect()

    """

    # Set the signon name to match the "/FOR <signon_screen_name>" on the real server.
    signon_screen_name = "VOS1SIGN"

    signon_passing_strings = ['SIGNON SUCCESSFUL', 'ALREADY SIGNED ON']
    signoff_passing_strings = ['SIGNOFF SUCCESSFUL']

    def __init__(self, username, password, app_id, signon_username, signon_password, host_3270, visible=False):
        """ New SignOnSession

        Some 3270 servers require a two-step authentication: LOGIN and SIGNON, in that order.
        This Session3270 subclass provides these steps.

        Start the terminal session. Then, login and signon.

        :param str username: login user for terminal
        :param str password: login password for terminal
        :param str app_id: login `application ID` sends user to the SIGNON section
        :param str signon_username: signon user
        :param str signon_password: signon password
        :param str host_3270: enter the hostname to the 3270 server
        :param bool visible: default False, when True means open a visible X-Windows terminal
        """

        super(SignOnSession, self).__init__(username, password, host_3270, visible=visible)
        self.app_id = app_id

        self.signon_username = signon_username
        self.signon_password = signon_password

    def signon(self):
        """ SIGNON

        Enter a secondary SIGNON step with its own user and password.

        :returns: success or failure and the status bar
        :rtype: tuple, (bool, STATUS BAR string)
        """

        self.term_emulator.format_screen(self.signon_screen_name)

        log.debug('Start SIGNON user/pass = {}/{}'.format(self.signon_username, self.signon_password))

        sleep(3)

        # SIGNON USER @(*, *)
        self.term_emulator.wait_for_field()
        self.term_emulator.key_entry(self.signon_username)

        # SIGNON PASSWORD @(*, *)
        # Assume cursor automatically moves to the PASSWORD field.
        self.term_emulator.key_entry(self.signon_password)
        self.term_emulator.send_enter()

        (status_bool, status_bar) = self.term_emulator.status_bar(passing_strings=self.signon_passing_strings)
        return (status_bool, status_bar)

    def signoff(self, field_row=12, field_col=16):
        """ SIGNOFF

        If the server has a secondary SIGNON step, then this remains until a SIGNOFF.
        Enter a SIGNOFF at the end of the session.

        :returns: success or failure and the status bar
        :rtype: tuple, (bool, STATUS BAR string)
        """

        #  SIGNOFF screen should be the same as SIGNON.
        self.term_emulator.format_screen(self.signon_screen_name)

        sleep(3)

        # SIGNOFF USER @(field_row, field_col) with "Y"
        self.term_emulator.wait_for_field()
        self.term_emulator.move_to(field_row, field_col)
        self.term_emulator.key_entry("Y")
        self.term_emulator.send_enter()

        (status_bool, status_bar) = self.term_emulator.status_bar(passing_strings=self.signoff_passing_strings)
        return (status_bool, status_bar)

    def connect(self):
        """ Connect to Terminal

        Connect to host and signon; start session.
        """

        super(SignOnSession, self).connect()

        (signon_flag, status_bar) = self.signon()
        log.info('SIGNON={} status=[{}]'.format(signon_flag, status_bar))
        if not signon_flag:
            raise SignOnError(
                'User "{}" could not complete SIGNON to "{}"! status=[{}]'.format(
                    self.signon_username, self.host_3270, status_bar.strip()))

    def disconnect(self):
        """ Disconnect Terminal

        Disconnect from host and signon; end session.
        """

        (signoff_flag, status_bar) = self.signoff()
        log.info('SIGNOFF={} status=[{}]'.format(signoff_flag, status_bar))

        super(SignOnSession, self).disconnect()
