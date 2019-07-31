# -*- coding: utf-8 -*-
# =============================================================================
# Helpers Unit Tests
# =============================================================================
#
# Testing the helper functions.
#
from unittest import TestCase
from traph.helpers import (
    lru_variations,
    lru_iter,
    chunks_iter,
    lru_dirname,
    base4_int,
    base4_append,
    int_to_base64,
    base64_to_int,
    int_to_base4,
    base4_to_ops,
    ops_to_base4
)


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

    def test_lru_dirname(self):
        self.assertEqual(
            lru_dirname('s:http|h:fr|h:sciences-po|h:medialab|'),
            's:http|h:fr|h:sciences-po|'
        )

    def test_chunks_iter(self):
        self.assertEqual(
            list(chunks_iter(5, 's:http|h:fr|h:sciences-po|h:medialab|')),
            ['s:htt', 'p|h:f', 'r|h:s', 'cienc', 'es-po', '|h:me', 'diala', 'b|']
        )

        self.assertEqual(
            list(chunks_iter(7, 's:http|h:fr|h:sciences-po|h:medialab|')),
            ['s:http|', 'h:fr|h:', 'science', 's-po|h:', 'mediala', 'b|']
        )

    def test_base4_append(self):
        n = base4_int('13213')

        self.assertEqual(
            n,
            487
        )

        self.assertEqual(
            base4_append(n, 2),
            base4_int('132132')
        )

    def test_int_to_base64(self):
        tests = [
            ('1321313231221323312121332313133232311', '1VTJFXSp-TvKR'),
            ('13213', '7D'),
            ('12313313232132331323133132313', '6TTKuZXvuT')
        ]

        for s, b in tests:
            n = base4_int(s)
            b64 = int_to_base64(n)

            self.assertEqual(b64, b)
            self.assertEqual(int_to_base4(n), s)
            self.assertEqual(base64_to_int(b64), n)

    def test_ops_conversions(self):

        tests = [
            ('133231', 'LRRCRL'),
            ('32111', 'RCLLL'),
            ('32', 'RC')
        ]

        for s, ops in tests:
            n = base4_int(s)

            self.assertEqual(base4_to_ops(n), ops)
            self.assertEqual(
                ops_to_base4(base4_to_ops(n)),
                n
            )
