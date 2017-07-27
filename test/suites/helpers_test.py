# -*- coding: utf-8 -*-
# =============================================================================
# Helpers Unit Tests
# =============================================================================
#
# Testing the helper functions.
#
from unittest import TestCase
from traph.helpers import lru_variations, lru_iter, chunks_iter


class TestHelpers(TestCase):

    def test_lru_variations(self):
        self.assertEqual(
            set(lru_variations('s:http|h:fr|h:sciences-po|h:medialab|')),
            set([
                's:http|h:fr|h:sciences-po|h:medialab|',
                's:https|h:fr|h:sciences-po|h:medialab|',
                's:http|h:fr|h:sciences-po|h:medialab|h:www|',
                's:https|h:fr|h:sciences-po|h:medialab|h:www|'
            ])
        )

    def test_lru_iter(self):
        self.assertEqual(
            list(lru_iter('s:http|h:fr|h:sciences-po|h:medialab|')),
            ['s:http|', 'h:fr|', 'h:sciences-po|', 'h:medialab|']
        )

    def test_chunks_iter(self):
        self.assertEqual(
            list(chunks_iter(5, 's:http|h:fr|h:sciences-po|h:medialab|')),
            ['s:htt', 'p|h:f', 'r|h:s', 'cienc', 'es-po', '|h:me', 'diala']
        )

        self.assertEqual(
            list(chunks_iter(7, 's:http|h:fr|h:sciences-po|h:medialab|')),
            ['s:http|', 'h:fr|h:', 'science', 's-po|h:', 'mediala']
        )
