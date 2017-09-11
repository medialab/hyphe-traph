# -*- coding: utf-8 -*-
# =============================================================================
# Traph Unit Tests
# =============================================================================
#
# Testing the Traph class itself.
#
from test.test_cases import TraphTestCase
from traph.traph import TraphException


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

    def test_index_batch_crawl_crawled_pages(self):
        with self.open_traph() as traph:
            traph.create_webentity(['s:http|h:fr|h:sciences-po|h:medialab|'])

            traph.index_batch_crawl({
                's:http|h:fr|h:sciences-po|h:medialab|': [
                    's:http|h:fr|h:sciences-po|h:medialab|p:publications|',
                    's:http|h:fr|h:sciences-po|h:medialab|p:people|'
                ]
            })

            pages = traph.get_webentity_crawled_pages(1, ['s:http|h:fr|h:sciences-po|h:medialab|'])
            self.assertEqual([item['lru'] for item in pages], ['s:http|h:fr|h:sciences-po|h:medialab|'])

            traph.index_batch_crawl({
                's:http|h:fr|h:sciences-po|h:medialab|p:publications|': [
                    's:http|h:fr|h:sciences-po|h:medialab|',
                    's:http|h:fr|h:sciences-po|h:medialab|p:people|'
                ],
                's:http|h:fr|h:sciences-po|h:medialab|p:people|': [
                    's:http|h:fr|h:sciences-po|h:medialab|p:publications|',
                    's:http|h:fr|h:sciences-po|h:medialab|'
                ]
            })

            pages = traph.get_webentity_crawled_pages(1, ['s:http|h:fr|h:sciences-po|h:medialab|'])
            self.assertEqual(set([item['lru'] for item in pages]), set([
                's:http|h:fr|h:sciences-po|h:medialab|p:people|',
                's:http|h:fr|h:sciences-po|h:medialab|p:publications|',
                's:http|h:fr|h:sciences-po|h:medialab|'
            ]))

    def test_index_and_retrieve_pages(self):
        wiki_prefixes = [
            's:https|h:org|h:wikipedia|h:www|',
            's:http|h:org|h:wikipedia|',
            's:http|h:org|h:wikipedia|h:www|',
            's:https|h:org|h:wikipedia|'
        ]

        with self.open_traph() as traph:
            report = traph.create_webentity(wiki_prefixes)

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(len(report.created_webentities), 1)

            report = traph.index_batch_crawl({
                's:https|h:org|h:wikipedia|h:www|': [
                    's:https|h:org|h:wikipedia|h:fr|',
                    's:https|h:org|h:wikipedia|h:en|'
                ]
            })

            self.assertEqual(report.nb_created_pages, 3)
            self.assertEqual(len(report.created_webentities), 0)
            self.assertEqual(traph.count_pages(), 3)
            self.assertEqual(traph.count_links(), 2)

            for lru, prefix, isPrefix in [
                ('s:https|h:org|h:wikipedia|', 's:https|h:org|h:wikipedia|', True),
                ('s:https|h:org|h:wikipedia|h:en|', 's:https|h:org|h:wikipedia|', False),
                ('s:https|h:org|h:wikipedia|h:en|p:wiki|p:Crawl|', 's:https|h:org|h:wikipedia|', False),
                ('s:https|h:org|h:wikipedia|h:www|', 's:https|h:org|h:wikipedia|h:www|', True),
                ('s:https|h:org|h:wikipedia|h:www|p:wiki|p:Crawl|', 's:https|h:org|h:wikipedia|h:www|', False)
            ]:
                self.assertEqual(traph.retrieve_prefix(lru), prefix)
                self.assertEqual(traph.retrieve_webentity(lru), 1)
                try:
                    self.assertTrue(traph.get_webentity_by_prefix(lru) == 1 and isPrefix)
                except TraphException:
                    self.assertFalse(isPrefix)

            crawled_pages = traph.get_webentity_crawled_pages(1, wiki_prefixes)

            self.assertEqual(set(page['lru'] for page in crawled_pages), set(['s:https|h:org|h:wikipedia|h:www|']))

            pages = traph.get_webentity_pages(1, wiki_prefixes)

            self.assertEqual(set(page['lru'] for page in pages), set(['s:https|h:org|h:wikipedia|h:www|', 's:https|h:org|h:wikipedia|h:fr|', 's:https|h:org|h:wikipedia|h:en|']))

    def test_prefix_methods(self):
        with self.open_traph() as traph:

            # 1) Potential prefix when the traph is empty
            prefix = traph.get_potential_prefix('s:http|h:fr|h:sciences-po|h:medialab|')
            self.assertEqual(prefix, 's:http|h:fr|h:sciences-po|')

            # 2) Test with existing webentity on path
            traph.create_webentity(['s:http|h:fr|h:sciences-po|h:medialab|'])
            prefix = traph.get_potential_prefix('s:http|h:fr|h:sciences-po|h:medialab|p:www|p:publications|')
            self.assertEqual(prefix, 's:http|h:fr|h:sciences-po|h:medialab|')

            # 3) With an upper webentity
            traph.create_webentity(['s:http|h:fr|h:sciences-po|'])
            prefix = traph.get_potential_prefix('s:http|h:fr|h:sciences-po|h:medialab|p:www|p:publications|')
            self.assertEqual(prefix, 's:http|h:fr|h:sciences-po|h:medialab|')

            # 4) Identity case
            prefix = traph.get_potential_prefix('s:http|h:fr|h:sciences-po|h:medialab|')
            self.assertEqual(prefix, 's:http|h:fr|h:sciences-po|h:medialab|')

    def test_long_stems(self):
        with self.open_traph() as traph:

            traph.add_page('s:http|h:fr|h:sciences-po|p:thisisaveryveryveryverylooooooooooooooooongstem|p:thisalsoisquitethelongstemisntitnotsomuchtobehonest|')
            traph.add_page('s:http|h:fr|h:sciences-po|p:sooooooofunnnnnnyyyyyyyyyyyyyyyyyyyyy|')

            pages_in_traph = [lru for _, lru in traph.pages_iter()]
            for node in traph.lru_trie.nodes_iter():
                pass
            self.assertEqual(
                set(pages_in_traph),
                set([
                    's:http|h:fr|h:sciences-po|p:thisisaveryveryveryverylooooooooooooooooongstem|p:thisalsoisquitethelongstemisntitnotsomuchtobehonest|',
                    's:http|h:fr|h:sciences-po|p:sooooooofunnnnnnyyyyyyyyyyyyyyyyyyyyy|'
                ])
            )

    def test_clear(self):
        with self.open_traph() as traph:
            traph = self.get_traph()
            traph.add_page('s:http|h:fr|h:sciences-po|h:medialab|')

            self.assertEqual(traph.count_pages(), 1)

            traph.clear()

            self.assertEqual(traph.count_pages(), 0)
