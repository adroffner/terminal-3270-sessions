from unittest import TestCase, mock

from terminal_3270.signon_sessions import (
    SignOnError,
    SignOnSession
)

# SignOnSession: dummy parameters
test_user = 'login_userid'
test_passwd = 'login_password'
app_id = 'TST01'
test_signon_user = 'signon_user'
test_signon_passwd = 'signon_password'
test_host = 'fake.host.org'


class TestSignOnSession(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_conduct_session(self):

        with mock.patch('terminal_3270.signon_sessions.SignOnSession.signon', return_value=(True, 'FAKE STATUS BAR')):
            with mock.patch('terminal_3270.signon_sessions.SignOnSession.signoff', return_value=(True, 'FAKE STATUS BAR')):
                with mock.patch('terminal_3270.sessions.Emulator'):
                    session = SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host)
                    session.connect()

                    session.term_emulator.connect.assert_called_with(test_host)
                    self.assertTrue(session.login.called)
                    self.assertTrue(session.signon.called)

                    session.disconnect()

                    self.assertIsNone(session.term_emulator)
                    self.assertTrue(session.signoff.called)

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_conduct_session_using_with_context_block(self):
        " SignOnSession allows a context manager, or with SignOnSession(...) as session: block "

        with mock.patch('terminal_3270.signon_sessions.SignOnSession.signon', return_value=(True, 'FAKE STATUS BAR')) as mock_session_signon:
            with mock.patch('terminal_3270.signon_sessions.SignOnSession.signoff', return_value=(True, 'FAKE STATUS BAR')):
                with mock.patch('terminal_3270.sessions.Emulator'):

                    # We are testing this with-block!
                    with SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host) as session:
                        self.assertTrue(mock_session_signon.called)
                        self.assertIsInstance(session, SignOnSession)

    # =========================================================================
    # SIGN-ON Tests
    # =========================================================================

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_signon(self):
        " SIGNON succeeds "

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator:
            with mock.patch('terminal_3270.signon_sessions.SignOnSession.signoff', return_value=(True, 'FAKE STATUS BAR')):
                session = SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host)

                session.term_emulator = mock_emulator()
                session.term_emulator.status_bar = mock.MagicMock(return_value=(True, 'GOT SIGNON SUCCESSFUL'))

                session.login()
                session.signon()

                # SIGNON Call
                session.term_emulator.format_screen.assert_called_with(SignOnSession.signon_screen_name)

                # SIGNON USER @(*, *)
                session.term_emulator.wait_for_field.assert_called_with()
                session.term_emulator.key_entry.mock_calls[0].assert_called_with(session.signon_username)

                # SIGNON PASSWORD @(*, *)
                session.term_emulator.key_entry.mock_calls[0].assert_called_with(session.signon_password)
                session.term_emulator.send_enter.assert_called_with()

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_signon_already_in_effect(self):
        " SIGNON is already in effect since the last login "

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator:
            with mock.patch('terminal_3270.signon_sessions.SignOnSession.signoff', return_value=(True, 'FAKE STATUS BAR')):
                session = SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host)

                session.term_emulator = mock_emulator()
                session.term_emulator.status_bar = mock.MagicMock(return_value=(True, 'GOT ALREADY SIGNED ON'))

                session.login()
                session.signon()

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_signon_failed(self):
        " SIGNON failed and SignOnError was raised "

        with self.assertRaisesRegex(SignOnError, r'User "[^"]*" could not complete SIGNON'):
            with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator:
                with mock.patch('terminal_3270.sessions.Session3270.connect'):
                    with mock.patch('terminal_3270.signon_sessions.SignOnSession.signoff', return_value=(True, 'FAKE STATUS BAR')):
                        session = SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host)

                        session.term_emulator = mock_emulator()
                        session.term_emulator.status_bar = mock.MagicMock(return_value=(False, 'INVALID SIGNON OR NEARLY ANYTHING ELSE'))

                        session.connect()  # Calls SignOnSession.signon() and tests outcome.

    # =========================================================================
    # SIGN-OFF Tests
    # =========================================================================

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_signoff(self):
        " SIGNOFF succeeds "

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator:
            with mock.patch('terminal_3270.signon_sessions.SignOnSession.signon', return_value=(True, 'FAKE STATUS BAR')):
                session = SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host)

                session.term_emulator = mock_emulator()
                session.term_emulator.status_bar = mock.MagicMock(return_value=(True, 'GOT SIGNOFF SUCCESSFUL'))

                session.signoff()

                # SIGNOFF Call
                session.term_emulator.format_screen.assert_called_with(SignOnSession.signon_screen_name)

                # SIGNOFF USER @(field_row, field_col) with "Y"
                session.term_emulator.wait_for_field.assert_called_with()
                # session.term_emulator.move_to.assert_called_with(field_row, field_col)
                session.term_emulator.key_entry.assert_called_with("Y")
                session.term_emulator.send_enter.assert_called_with()

    # mock login() assumes success
    @mock.patch('terminal_3270.signon_sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_signoff_failure(self):
        " SIGNOFF fails "

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator:
            with mock.patch('terminal_3270.signon_sessions.SignOnSession.signon', return_value=(True, 'FAKE STATUS BAR')):
                session = SignOnSession(test_user, test_passwd, app_id, test_signon_user, test_signon_passwd, test_host)

                session.term_emulator = mock_emulator()
                session.term_emulator.status_bar = mock.MagicMock(return_value=(False, 'GOT BAD SIGNOFF STATUS'))

                session.signoff()
