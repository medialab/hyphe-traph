# =============================================================================
# Unit Tests Endpoint
# =============================================================================
#
# Gathering the unit tests in order to run them.
#
from test.test_cases import TraphTestCase


class TestTraph(TraphTestCase):

    def test_clear(self):
        traph = self.get_traph()
        traph.add_page('s:http|h:fr|h:sciences-po|h:medialab|')

        self.assertEqual(traph.count_pages(), 1)

        traph.clear()

        self.assertEqual(traph.count_pages(), 0)
