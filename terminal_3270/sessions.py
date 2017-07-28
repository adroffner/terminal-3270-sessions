""" TN3270 Terminal Session with py3270 library

Use the py3270 library on this Linux machine to run an IBM 3270 session.

IMPORTANT: This depends on the "x3270" or "s3270" command.

Make sure the Linux commands are installed on this machine:
    /usr/bin/s3270
OR
    /usr/bin/x3270

RHEL/YUM has RPM package(s) for x3270
"""

from .emulator import EmulatorPlus as Emulator


class LoginError(Exception):
    pass


class Session3270(object):
    """ User Session to an s3270 Terminal

    This class opens an s3270 logged-in terminal session.
    Create subclasses to perform the terminal session actions, and collect results.

        with MySession3270(username, password, HOST_3270, visible=False) as terminal:
            results = terminal.get_results()  # declared by your subclass!

        print(results)

    OR

        terminal = MySession3270(username, password, HOST_3270)
        terminal.connect()

        terminal.term_emulator.move_to(rownum, colnum)
        terminal.term_emulator.fill_field("text")
        ...

        terminal.disconnect()

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

        self.term_emulator = Emulator(visible=self.visible, timeout=10)
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
