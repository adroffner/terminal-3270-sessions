from unittest import TestCase, mock

from terminal_3270.login_mixins import (
    ACF2LoginMixin,
    RACFLoginMixin
)
from terminal_3270.sessions import Session3270

# Session3270: dummy parameters
test_user = 'login_userid'
test_passwd = 'login_password'
test_app_id = 'TST01'
test_host = 'fake.host.org'


class StubACF2Session(ACF2LoginMixin, Session3270):
    pass


class StubRACFSession(RACFLoginMixin, Session3270):
    pass


class TestLoginMixins(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_conduct_acf2_login(self):

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator_class:
            session = StubACF2Session(test_user, test_passwd, test_app_id, test_host)

            # REJECTED is False and login succeeds.
            session.term_emulator = mock_emulator_class()
            session.term_emulator.string_found.return_value = False

            login_bool = session.login()

            self.assertIsInstance(session.term_emulator, mock.MagicMock)

            # 1) Enter REGION
            session.term_emulator.wait_for_field.assert_called_with()
            session.term_emulator.fill_field.assert_called_with(1, 3, session.region, len(session.region))
            session.term_emulator.send_enter.assert_called_with()

            # 2) Type in the USERID and PASSWORD fields.

            # USERID @(*, *)
            session.term_emulator.wait_for_field.assert_called_with()
            session.term_emulator.key_entry.mock_calls[0].assert_called_with(session.username)
            session.term_emulator.send_tab.assert_called_with()

            # PASSWORD @(*, *)
            session.term_emulator.key_entry.mock_calls[1].assert_called_with(session.password)
            session.term_emulator.send_enter.assert_called_with()

            # Login Status: Look for a status message
            session.term_emulator.string_found.assert_called_with(2, 2, 'REJECTED')
            self.assertTrue(login_bool)

    def test_conduct_acf2_login_failure(self):

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator_class:
            session = StubACF2Session(test_user, test_passwd, test_app_id, test_host)

            # REJECTED is True and login fails.
            session.term_emulator = mock_emulator_class()
            session.term_emulator.string_found.return_value = True

            login_bool = session.login()

            # Login Status: Look for a status message
            session.term_emulator.string_found.assert_called_with(2, 2, 'REJECTED')
            self.assertFalse(login_bool)

    def test_conduct_racf_login(self):

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator_class:
            session = StubRACFSession(test_user, test_passwd, test_app_id, test_host)

            # REJECTED is False and login succeeds.
            session.term_emulator = mock_emulator_class()
            session.term_emulator.string_found.return_value = False

            login_bool = session.login()

            self.assertIsInstance(session.term_emulator, mock.MagicMock)

            # 1) Type in the APPLICATION field.
            session.term_emulator.wait_for_field.assert_called_with()
            session.term_emulator.move_to.assert_called_with(session.racf_app_row, session.racf_app_column)
            session.term_emulator.key_entry.mock_calls[0].assert_called_with(session.app_id)
            session.term_emulator.send_enter.assert_called_with()

            # 2) Type in the USERID and PASSWORD fields.

            # USERID @(*, *)
            session.term_emulator.wait_for_field.assert_called_with()
            session.term_emulator.key_entry.mock_calls[1].assert_called_with(session.username)
            session.term_emulator.send_tab.assert_called_with()

            # PASSWORD @(*, *)
            session.term_emulator.key_entry.mock_calls[2].assert_called_with(session.password)
            session.term_emulator.send_enter.assert_called_with()

            # Login Status: Look for a status message
            session.term_emulator.string_found.assert_called_with(17, 2, 'REJECTED')
            self.assertTrue(login_bool)

    def test_conduct_racf_login_failure(self):

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator_class:
            session = StubRACFSession(test_user, test_passwd, test_app_id, test_host)

            # REJECTED is True and login fails.
            session.term_emulator = mock_emulator_class()
            session.term_emulator.string_found.return_value = True

            login_bool = session.login()

            # Login Status: Look for a status message
            session.term_emulator.string_found.assert_called_with(17, 2, 'REJECTED')
            self.assertFalse(login_bool)
