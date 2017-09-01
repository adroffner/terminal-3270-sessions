""" TN3270 Terminal Session with py3270 library

Use the py3270 library on this Linux machine to run an IBM 3270 session.

IMPORTANT: This depends on the "x3270" or "s3270" command.

Make sure the Linux commands are installed on this machine:
    /usr/bin/s3270 (visible=True)
OR
    /usr/bin/x3270 (visible=False)

RHEL/YUM has RPM package(s) for x3270 -> "yum install x3270-x11"
"""

# from time import sleep
from .emulator import EmulatorPlus as Emulator
from terminal_3270.login_mixins import ACF2LoginMixin, RACFLoginMixin

import logging
log = logging.getLogger(__name__)

TIMEOUT_WAIT_SCREEN = 10
TIMEOUT_SIGNON_SCREEN = 1.350  # ms


class SessionError(Exception):
    pass


class LoginError(SessionError):
    pass


class SignOnError(SessionError):
    pass


class Session3270(object):
    """ User Session to an s3270 Terminal

    This class opens an s3270 logged-in terminal session.
    Create subclasses to perform the terminal session actions, and collect results.

        class MySession3270(Session3270):

            def login(self):
                # Go to LOGIN screen and enter (self.username, self.password)
                # ...
                pass

        with MySession3270(username, password, HOST_3270, visible=False) as session:
            results = session.get_results()  # declared by your subclass!

        print(results)

    OR

        terminal = MySession3270(username, password, HOST_3270)
        session.connect()

        session.term_emulator.move_to(rownum, colnum)
        session.term_emulator.fill_field("text")
        ...

        session.disconnect()

    """

    def __init__(self, username, password, app_id, host_3270, visible=False):
        """ New Session3270

        Start the terminal session and login.

        :param str username: login user for terminal
        :param str password: login password for terminal
        :param str app_id: login `application ID` sends user to the LOGIN screen
        :param str host_3270: enter the hostname to the 3270 server
        :param bool visible: default False, when True means open a visible X-Windows terminal
        """

        self.host_3270 = host_3270
        self.username = username
        self.password = password
        self.app_id = app_id
        self.visible = visible

        self.term_emulator = None

    def __enter__(self):
        """ Enter Context Manager """
        self.connect()
        return self

    def __exit__(self, *args):
        """ Exit Context Manager """
        self.disconnect()

    def login(self):
        """ login routine

        Login to the terminal session as required.
        Subclasses will need to override this for their 3270 host.

        :returns: True on success, False otherwise
        """

        raise NotImplementedError('Create your login procedure here!')

    def connect(self):
        """ Connect to Terminal

        Connect to host and start session.
        """

        self.term_emulator = Emulator(visible=self.visible, timeout=TIMEOUT_WAIT_SCREEN)
        self.term_emulator.connect(self.host_3270)

        if not self.login():
            raise LoginError('User "{}" could not login to "{}"!'.format(self.username, self.host_3270))

    def disconnect(self):
        """ Disconnect Terminal

        Disconnect from host and end session.
        """

        if self.term_emulator:
            self.term_emulator.terminate()
            self.term_emulator = None

# =============================================================================


class ACF2LoginSession(ACF2LoginMixin, Session3270):
    pass


class RACFLoginSession(RACFLoginMixin, Session3270):
    pass

# =============================================================================


class SignOnSession(Session3270):
    """ User Signon Session to a 3270 Terminal

    This class opens an s3270 logged-in terminal session.
    Then, the user passes a sigon screen to work on tasks.

        with MySignOnSession(username, password, app_id, signon_username, signon_password, HOST_3270, visible=False) as session:
            results = session.get_results()  # declared by your subclass!

        print(results)

    OR

        terminal = MySignOnSession(username, password, app_id, signon_username, signon_password, HOST_3270)
        session.connect()

        session.term_emulator.move_to(rownum, colnum)
        session.term_emulator.fill_field("text")
        ...

        session.disconnect()

    """

    # Set the signon name to match the "/FOR <signon_screen_name>" on the real server.
    signon_screen_name = "VOS1SIGN"

    # Wait for Screen Text:
    signon_screen_str = "WFAC SECURITY SIGNON"
    signon_screen_str_row = 2
    signon_screen_str_col = 23

    signon_passing_strings = ['SIGNON SUCCESSFUL', 'ALREADY SIGNED ON']
    signoff_passing_strings = ['SIGNOFF SUCCESSFUL']

    def __init__(self, username, password, app_id, signon_username, signon_password, host_3270, visible=False):
        """ New SignOnSession

        Some 3270 servers require a two-step authentication: LOGIN and SIGNON, in that order.
        This Session3270 subclass provides these steps.

        Start the terminal session. Then, login and signon.

        :param str username: login user for terminal
        :param str password: login password for terminal
        :param str app_id: login `application ID` sends user to the LOGIN screen
        :param str signon_username: signon user
        :param str signon_password: signon password
        :param str host_3270: enter the hostname to the 3270 server
        :param bool visible: default False, when True means open a visible X-Windows terminal
        """

        super(SignOnSession, self).__init__(username, password, app_id, host_3270, visible=visible)

        self.signon_username = signon_username
        self.signon_password = signon_password

    def send_signon_credentials(self):
        """ Send SIGNON Credentials

        Each SIGNON may require a different key to send the user and password fields to the server.
        Override the default ENTER in you subclass as needed.
        """

        self.term_emulator.send_enter()

    def signon(self):
        """ SIGNON

        Enter a secondary SIGNON step with its own user and password.

        :returns: success or failure and the status bar
        :rtype: tuple, (bool, STATUS BAR string)
        """

        self.term_emulator.format_screen(self.signon_screen_name)

        log.debug('Start SIGNON user/pass = {}/{}'.format(self.signon_username, self.signon_password))

        self.term_emulator.wait_for_screen(
            self.signon_screen_str,
            self.signon_screen_str_row,
            self.signon_screen_str_col,
            time_limit=TIMEOUT_SIGNON_SCREEN)

        # SIGNON USER @(*, *)
        self.term_emulator.wait_for_field()
        self.term_emulator.key_entry(self.signon_username)

        # SIGNON PASSWORD @(*, *)
        # Assume cursor automatically moves to the PASSWORD field.
        self.term_emulator.key_entry(self.signon_password)

        self.send_signon_credentials()

        (status_bool, status_bar) = self.term_emulator.status_bar(passing_strings=self.signon_passing_strings)

        # RESET: Sometimes the user is ALREADY SIGNED ON and goes straight to the last used screen.
        if not status_bool:
            self.term_emulator.send_clear()
            self.term_emulator.format_screen(self.signon_screen_name)
            self.term_emulator.send_enter()  # Double ENTER is on purpose
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

        self.term_emulator.wait_for_screen(
            self.signon_screen_str,
            self.signon_screen_str_row,
            self.signon_screen_str_col,
            time_limit=TIMEOUT_SIGNON_SCREEN)

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

# =============================================================================


class ACF2SignOnSession(ACF2LoginMixin, SignOnSession):
    pass


class RACFSignOnSession(RACFLoginMixin, SignOnSession):
    pass
