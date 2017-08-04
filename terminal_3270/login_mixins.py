""" Session3270 Login Mixins

The `Session3270` and `SignOnSession` classes do not not implement a login().
Use these mixins to provide common login procedures.

    class MyACF2Session(ACF2LoginMixin, Session3270):
        pass

    OR

    class MyRCAFSession(RACFLoginMixin, SignOnSession):
        # APPLICATION Field is (racf_app_row, racf_app_column).
        racf_app_row = 3
        racf_app_column = 15
"""

from time import sleep

TIMEOUT_LOGIN_SCREEN = 0.3  # 300 ms


class ACF2LoginMixin:
    """ ACF2 Login Session to a 3270 Terminal

    This mixin adds the ACF2 login process to a Session3270 class.
    """

    @property
    def region(self):
        return self.app_id

    def login(self):
        """ login routine

        Login to the terminal session as required.

        Screen 1: Enter the REGION field
        Screen 2: Type in the USERID and PASSWORD fields

        :returns: True on success, False otherwise
        """

        # 1) Enter REGION
        self.term_emulator.wait_for_field()
        self.term_emulator.fill_field(1, 3, self.region, len(self.region))
        self.term_emulator.send_enter()

        sleep(TIMEOUT_LOGIN_SCREEN)

        # 2) Type in the USERID and PASSWORD fields.

        # USERID @(*, *)
        self.term_emulator.wait_for_field()
        self.term_emulator.key_entry(self.username)
        self.term_emulator.send_tab()

        # PASSWORD @(*, *)
        self.term_emulator.key_entry(self.password)
        self.term_emulator.send_enter()

        # Login Status: Look for a status message
        if self.term_emulator.string_found(2, 2, 'REJECTED'):
            return False
        else:
            return True


class RACFLoginMixin:
    """ RACF Login Session to a 3270 Terminal

    This mixin adds the RACF login process to a Session3270 class.
    """

    racf_app_row = 3
    racf_app_column = 15

    def login(self):
        """ login routine

        Login to the terminal session as required.

        Screen 1: Enter the APPLICATION field
        Screen 2: Type in the USERID and PASSWORD fields

        :returns: True on success, False otherwise
        """

        # 1) Type in the APPLICATION field.
        self.term_emulator.wait_for_field()
        # self.term_emulator.fill_field(3, 15, self.app_id, len(self.app_id))
        if self.racf_app_row is not None:
            self.term_emulator.move_to(self.racf_app_row, self.racf_app_column)
        self.term_emulator.key_entry(self.app_id)
        self.term_emulator.send_enter()

        sleep(TIMEOUT_LOGIN_SCREEN)

        # 2) Type in the USERID and PASSWORD fields.

        # USERID @(*, *)
        self.term_emulator.wait_for_field()
        self.term_emulator.key_entry(self.username)
        self.term_emulator.send_tab()

        # PASSWORD @(*, *)
        self.term_emulator.key_entry(self.password)
        self.term_emulator.send_enter()

        # Login Status: Look for a status message
        if self.term_emulator.string_found(17, 2, 'REJECTED'):
            return False
        else:
            return True
