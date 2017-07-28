from unittest import TestCase, mock

from terminal_3270.sessions import Session3270, LoginError

# Session3270: dummy parameters
test_user = 'login_userid'
test_passwd = 'login_password'
test_app_id = 'TST01'
test_host = 'fake.host.org'


class TestSession3270(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # mock login() assumes success
    @mock.patch('terminal_3270.sessions.Session3270.login', mock.MagicMock(return_value=True))
    def test_conduct_session(self):

        with mock.patch('terminal_3270.sessions.Emulator') as mock_emulator_class:
            session = Session3270(test_user, test_passwd, test_app_id, test_host)
            session.connect()

            mock_emulator_class.assert_called_with(visible=False, timeout=10)
            self.assertIsInstance(session.term_emulator, mock.MagicMock)

            session.term_emulator.connect.assert_called_with(test_host)
            self.assertTrue(session.login.called)

            mock_emulator_object = session.term_emulator
            session.disconnect()

            self.assertIsNone(session.term_emulator)
            self.assertTrue(mock_emulator_object.terminate.called)

    # mock login() assumes failure
    @mock.patch('terminal_3270.sessions.Session3270.login', mock.MagicMock(return_value=False))
    def test_conduct_session_with_login_failure(self):

        with self.assertRaisesRegex(LoginError, r'^User "[^"]*" could not login to "[^"]*"!'):
            with mock.patch('terminal_3270.sessions.Emulator'):
                session = Session3270(test_user, test_passwd, test_app_id, test_host)
                session.connect()

    def test_conduct_session_login_not_implemented(self):
        " Session3270.login() raises NotImplementedError() so subclasses make server-specific ones "

        with self.assertRaisesRegex(NotImplementedError, r'^Create your login procedure here!'):
            with mock.patch('terminal_3270.sessions.Emulator'):
                session = Session3270(test_user, test_passwd, test_app_id, test_host)
                session.connect()

    def test_conduct_session_using_with_context_block(self):
        " Session3270 allows a context manager, or with Session3270(...) as session: block "

        with mock.patch('terminal_3270.sessions.Session3270.connect') as mock_sess3270_connect:
            with mock.patch('terminal_3270.sessions.Emulator'):

                # We are testing this with-block!
                with Session3270(test_user, test_passwd, test_app_id, test_host) as session:
                    self.assertTrue(mock_sess3270_connect.called)
                    self.assertIsInstance(session, Session3270)
