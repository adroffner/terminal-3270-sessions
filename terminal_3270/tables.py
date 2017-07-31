""" tn3270 Search Results Table Generator.

This module works out how to screen-scrape a 3270 search results table.
A search results screen has a table defined by row (top..bottom).
Multiple screens may be needed to show enough tables for all results.
"""


class ScreenTableNotFoundError(ValueError):
    """ Screen Table Results Not Found Error.

    A ScreenTable status bar indicated there are no valid results.
    This error does not apply to the end-of-results condition.
    """
    pass


class ScreenTable(object):
    """ Screen Table

    Read a 3270 screen as a table of search results.
    Create a generator that reads it page-by-page.
    """

    def __init__(self, emulator, top_row, bottom_row,
                 status_row=24, status_found='FIND SUCCESSFUL', status_end='LAST PAGE',
                 row_processor=None):
        """ New Screen Table

        :param emulator: a py3270.Emulator instance set to a search results screen.
        :param int top_row: the top row in the table on this screen, columns 1..80 are assumed
        :param int bottom_row: the bottom row in the table on this screen
        :param int status_row: a status bar to show more results or terminate
        :param str status_found: a status bar string to prove next results-set was found
        :param str status_end: a status bar string to terminate the results-set
        :param callable row_processor: optional function to parse each row into fields
        """

        self.emulator = emulator
        self.top_row = top_row
        self.bottom_row = bottom_row
        self.status_row = status_row
        self.status_found = status_found
        self.status_end = status_end
        self.row_processor = row_processor

        self._table_data = []
        self._more_pages = True

    @property
    def has_more_results(self):
        return bool(self._more_pages or self._table_data)

    def next_result_set(self):
        self.emulator.send_pf_key(2)

    def fetch_results(self):
        """ Fetch Results Generator

        This method returns a python generator on the screen's results-set.

        :returns: a generator to return results as row lists
        :rtype: generator
        """

        while self.has_more_results:
            if not self._table_data:
                self.get_table_page(self.top_row, self.bottom_row)

            row = self._table_data.pop(0)
            yield row

    def get_table_page(self, top_row, bottom_row):
        """ Get Screen Table Page

        Get the current screen's table as one page in the results-set.

        :param int top_row: the top row in the table on this screen, columns 1..80 are assumed
        :param int bottom_row: the bottom row in the table on this screen
        :returns: a nested list of row lists for the whole page
        """

        self._table_data = []

        # Prove that current result-set is valid.
        (status_found, status_bar) = self.emulator.status_bar(passing_strings=[self.status_found], status_row=self.status_row)
        if not status_found:
            raise ScreenTableNotFoundError(status_bar)

        for row in range(top_row, bottom_row + 1):
            line = self.emulator.string_get(row, 1, 80)
            if line.strip():
                # parse line into fields.
                if callable(self.row_processor):
                    self._table_data.append(self.row_processor(line))
                else:
                    self._table_data.append(line.strip().split())
            else:
                break  # blank-line ends table data

        # STATUS: Is this the end-of-data?
        (status_bool, status_bar) = self.emulator.status_bar(terminator_strings=[self.status_end], status_row=self.status_row)
        self._more_pages = status_bool

        # NEXT PAGE OF RESULTS: Move to the next page before returning results.
        if self._more_pages:
            self.next_result_set()

        # Return the original page's result-set after moving to the next page.
        return self._table_data
