# =============================================================================
# LRU Helpers Unit Tests
# =============================================================================
#
import unittest

LRUS = [
    's:http|h:fr|h:sciences-po|h:medialab|',
    's:https|h:com|h:twitter|p:paulanomalie|',
    's:https|h:192.168.0.1|p:paulanomalie|'
]

class TestLRUHelpers(unittest.TestCase):

    def test_lru_stems_iterator(self):
        self.assertTrue(True)
