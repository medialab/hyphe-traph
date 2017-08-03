# -*- coding: utf-8 -*-
# =============================================================================
# Traph Unit Tests
# =============================================================================
#
# Testing the Traph class itself.
#
from test.test_cases import TraphTestCase


class TestTraph(TraphTestCase):

    def test_add_page(self):
        with self.open_traph() as traph:
            report = traph.add_page('s:http|h:fr|h:sciences-po|h:medialab|')

            self.assertEqual(report.nb_created_pages, 1)
            self.assertEqual(traph.count_pages(), 1)

            # Re-adding pages should not have an effect
            report = traph.add_page('s:http|h:fr|h:sciences-po|h:medialab|')

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(traph.count_pages(), 1)
            self.assertEqual(traph.count_links(), 0)

    def test_add_links(self):
        with self.open_traph() as traph:

            report = traph.add_links([
                (
                    's:http|h:fr|h:sciences-po|h:medialab|',
                    's:https|h:com|h:twitter|p:paulanomalie|'
                )
            ])

            self.assertEqual(report.nb_created_pages, 2)
            self.assertEqual(traph.count_pages(), 2)
            self.assertEqual(traph.count_links(), 1)

            # Re-adding pages should not have an effect
            report = traph.add_links([
                (
                    's:http|h:fr|h:sciences-po|h:medialab|',
                    's:https|h:com|h:twitter|p:paulanomalie|'
                )
            ])

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(traph.count_pages(), 2)
            self.assertEqual(traph.count_links(), 1)

    def test_index_batch_crawl(self):
        with self.open_traph() as traph:

            report = traph.index_batch_crawl({
                's:http|h:fr|h:sciences-po|h:medialab|': [
                    's:https|h:com|h:twitter|p:paulanomalie|',
                    's:http|h:com|h:twitter|p:pépé|yesterday|'
                ]
            })

            self.assertEqual(report.nb_created_pages, 3)
            self.assertEqual(traph.count_pages(), 3)
            self.assertEqual(traph.count_links(), 2)

            # Re-adding pages should not have an effect
            report = traph.index_batch_crawl({
                's:http|h:fr|h:sciences-po|h:medialab|': [
                    's:https|h:com|h:twitter|p:paulanomalie|',
                    's:http|h:com|h:twitter|p:pépé|yesterday|'
                ]
            })

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(traph.count_pages(), 3)
            self.assertEqual(traph.count_links(), 2)

    def test_prefix_methods(self):
        with self.open_traph() as traph:

            # Potential prefix
            prefix = traph.get_potential_prefix('s:http|h:fr|h:sciences-po|h:medialab|')
            self.assertEqual(prefix, 's:http|h:fr|h:sciences-po|')

    def test_long_stems(self):
        with self.open_traph() as traph:

            traph.add_page('s:http|h:fr|h:sciences-po|p:thisisaveryveryveryverylooooooooooooooooongstem|p:thisalsoisquitethelongstemisntitnotsomuchtobehonest|')
            traph.add_page('s:http|h:fr|h:sciences-po|p:sooooooofunnnnnnyyyyyyyyyyyyyyyyyyyyy|')

            pages_in_traph = [lru for _, lru in traph.pages_iter()]

            self.assertEqual(
                set(pages_in_traph),
                set([
                    's:http|h:fr|h:sciences-po|p:thisisaveryveryveryverylooooooooooooooooongstem|p:thisalsoisquitethelongstemisntitnotsomuchtobehonest|',
                    's:http|h:fr|h:sciences-po|p:sooooooofunnnnnnyyyyyyyyyyyyyyyyyyyyy|'
                ])
            )

    def test_cluttered_root(self):
        with self.open_traph() as traph:
            traph.add_page('s:http|h:fr|h:sciences-po|')
            traph.add_page('s:https|h:fr|h:sciences-po|')
            traph.add_page('s:httpl|h:fr|h:sciences-po|')
            traph.add_page('s:httpf|h:fr|h:sciences-po|')
            traph.add_page('s:httpe|h:fr|h:sciences-po|')
            traph.add_page('s:httpa|h:fr|h:sciences-po|')
            traph.add_page('s:httpt|h:fr|h:sciences-po|')

            pages_in_traph = [lru for _, lru in traph.pages_iter()]

            self.assertEqual(
                set(pages_in_traph),
                set([
                    's:http|h:fr|h:sciences-po|',
                    's:https|h:fr|h:sciences-po|',
                    's:httpl|h:fr|h:sciences-po|',
                    's:httpf|h:fr|h:sciences-po|',
                    's:httpe|h:fr|h:sciences-po|',
                    's:httpa|h:fr|h:sciences-po|',
                    's:httpt|h:fr|h:sciences-po|'
                ])
            )

    def test_clear(self):
        with self.open_traph() as traph:
            traph = self.get_traph()
            traph.add_page('s:http|h:fr|h:sciences-po|h:medialab|')

            self.assertEqual(traph.count_pages(), 1)

            traph.clear()

            self.assertEqual(traph.count_pages(), 0)
