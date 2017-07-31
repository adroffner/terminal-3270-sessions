from unittest import TestCase  # , mock

from terminal_3270.tables import ScreenTable


LAST_SCREEN = """ COMMAND                WFAC: ORDER - CWL INFORMATION (OSSCWL)     /FOR
 GO TO PAGE:                                     07/24/17 11:03 CDT PAGE 0001 L

 ORD OKC229369          B  CKT C JU101/GE1N  /HUGOOKEE0AW/HUGOOKMA0BW
 TRK OKC229369001  ACT A   CTL ENOC1CENTER     EVT ITEM DT 06/20/17
 EVT DVA           ST  IE  A HUGOOKEE0AW           ITEM DD 06/27/17
 CAC CXP7BJ3       TSP     Z HUGOOKMA0BW  HO END D/T
 RMK
                                                                         GOC OPS
 C  WK     LOC     CWL  END I CTYPE WT HO CMP DATE ID JEOPARDIES   MFC   S T S T
       HUGOOKEE0AW 1     A                                                   F N
       HUGOOKMA                                                              F N
       HUGOOKMA    AEQP                                                      F N
       HUGOOKMA    AFRM                                                      F N









 SSC725I  FIND SUCCESSFUL - LAST PAGE OF OUTPUT DISPLAYED
"""


def row_parser(record):
    row = 'PARSED:{}'.format(record)
    return row


class MockEmulator(object):
    """ Mock py3270.Emulator

    This represents the Emulator object for testing.
    """

    def __init__(self, screen_text):
        self.lines = screen_text.split('\n')
        self.is_terminated = False

    def status_bar(self, passing_strings=[], terminator_strings=[], status_row=24):
        if passing_strings:
            if passing_strings[0] in 'FIND SUCCESSFUL':
                return (True, 'FIND SUCCESSFUL')
            else:
                return (False, '******')  # unknown error event
        elif terminator_strings:
            if terminator_strings[0] in 'TEST LAST PAGE':
                return (False, 'TEST LAST PAGE')
            else:
                return (True, 'TEST MORE PAGES')

    def string_get(self, row, col, length):
        print("return self.lines[{}][{}:({})]".format(row - 1, col - 1, (length + col - 1)))
        return self.lines[row - 1][col - 1:(length + col - 1)]


class TestScreenTable(TestCase):

    def setUp(self):
        self.top_row = 11
        self.bottom_row = 23

        self.emulator = MockEmulator(LAST_SCREEN)

    def tearDown(self):
        # Pretend to shut down Emulator.
        self.emulator.is_terminated = True

    def test_fetch_results_last_page(self):
        " Fetch results from the last screen "

        screen_table = ScreenTable(self.emulator, self.top_row, self.bottom_row, status_row=24, status_end='LAST PAGE', row_processor=row_parser)
        results = [r for r in screen_table.fetch_results()]

        # Cut off "PARSED:" and it should match the original screen line.
        self.assertEqual(len(results), 4)
        for idx, line in enumerate(self.emulator.lines[10:(10 + 4)]):
            self.assertEqual(results[idx][len("PARSED:"):], line)

    def test_fetch_results_last_page_no_row_processor(self):
        " Fetch results from the last screen with no row_processor "

        screen_table = ScreenTable(self.emulator, self.top_row, self.bottom_row, status_row=24, status_end='LAST PAGE', row_processor=None)
        results = [r for r in screen_table.fetch_results()]

        # The results should match the original screen line, when parsed.
        self.assertEqual(len(results), 4)
        for idx, line in enumerate(self.emulator.lines[10:(10 + 4)]):
            self.assertEqual(results[idx], line.strip().split())
