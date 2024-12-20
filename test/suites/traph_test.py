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
            report = traph.add_page(b"s:http|h:fr|h:sciences-po|h:medialab|")

            self.assertEqual(report.nb_created_pages, 1)
            self.assertEqual(traph.count_pages(), 1)
            self.assertEqual(traph.count_crawled_pages(), 0)

            # Re-adding pages should not have an effect, except on crawled flag
            report = traph.add_page(
                b"s:http|h:fr|h:sciences-po|h:medialab|", crawled=True
            )

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(traph.count_pages(), 1)
            self.assertEqual(traph.count_crawled_pages(), 1)
            self.assertEqual(traph.count_links(), 0)

    def test_add_links(self):
        with self.open_traph() as traph:
            report = traph.add_links(
                [
                    (
                        b"s:http|h:fr|h:sciences-po|h:medialab|",
                        b"s:https|h:com|h:twitter|p:paulanomalie|",
                    )
                ]
            )

            self.assertEqual(report.nb_created_pages, 2)
            self.assertEqual(traph.count_pages(), 2)
            self.assertEqual(traph.count_links(), 1)

            # Re-adding pages should not have an effect, except for weight
            report = traph.add_links(
                [
                    (
                        b"s:http|h:fr|h:sciences-po|h:medialab|",
                        b"s:https|h:com|h:twitter|p:paulanomalie|",
                    )
                ]
            )

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(traph.count_pages(), 2)
            self.assertEqual(traph.count_links(), 2)

    def test_index_batch_crawl(self):
        with self.open_traph() as traph:
            report = traph.index_batch_crawl(
                {
                    b"s:http|h:fr|h:sciences-po|h:medialab|": [
                        b"s:https|h:com|h:twitter|p:paulanomalie|",
                        "s:http|h:com|h:twitter|p:pépé|yesterday|".encode(),
                    ]
                }
            )

            self.assertEqual(report.nb_created_pages, 3)
            self.assertEqual(traph.count_pages(), 3)
            self.assertEqual(traph.count_links(), 2)

            # Re-adding pages should not have an effect, except for weight
            report = traph.index_batch_crawl(
                {
                    b"s:http|h:fr|h:sciences-po|h:medialab|": [
                        b"s:https|h:com|h:twitter|p:paulanomalie|",
                        "s:http|h:com|h:twitter|p:pépé|yesterday|".encode(),
                    ]
                }
            )

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(traph.count_pages(), 3)
            self.assertEqual(traph.count_links(), 4)

    def test_index_batch_crawl_crawled_pages(self):
        with self.open_traph() as traph:
            traph.create_webentity([b"s:http|h:fr|h:sciences-po|h:medialab|"])

            traph.index_batch_crawl(
                {
                    b"s:http|h:fr|h:sciences-po|h:medialab|": [
                        b"s:http|h:fr|h:sciences-po|h:medialab|p:publications|",
                        b"s:http|h:fr|h:sciences-po|h:medialab|p:people|",
                    ]
                }
            )

            pages = traph.get_webentity_crawled_pages(
                1, [b"s:http|h:fr|h:sciences-po|h:medialab|"]
            )
            self.assertEqual(
                [item["lru"] for item in pages],
                [b"s:http|h:fr|h:sciences-po|h:medialab|"],
            )

            traph.index_batch_crawl(
                {
                    b"s:http|h:fr|h:sciences-po|h:medialab|p:publications|": [
                        b"s:http|h:fr|h:sciences-po|h:medialab|",
                        b"s:http|h:fr|h:sciences-po|h:medialab|p:people|",
                    ],
                    b"s:http|h:fr|h:sciences-po|h:medialab|p:people|": [
                        b"s:http|h:fr|h:sciences-po|h:medialab|p:publications|",
                        b"s:http|h:fr|h:sciences-po|h:medialab|",
                    ],
                }
            )

            pages = traph.get_webentity_crawled_pages(
                1, [b"s:http|h:fr|h:sciences-po|h:medialab|"]
            )
            self.assertEqual(
                set([item["lru"] for item in pages]),
                set(
                    [
                        b"s:http|h:fr|h:sciences-po|h:medialab|p:people|",
                        b"s:http|h:fr|h:sciences-po|h:medialab|p:publications|",
                        b"s:http|h:fr|h:sciences-po|h:medialab|",
                    ]
                ),
            )

    def test_index_and_retrieve_pages(self):
        wiki_prefixes = [
            b"s:https|h:org|h:wikipedia|h:www|",
            b"s:http|h:org|h:wikipedia|",
            b"s:http|h:org|h:wikipedia|h:www|",
            b"s:https|h:org|h:wikipedia|",
        ]

        with self.open_traph() as traph:
            report = traph.create_webentity(wiki_prefixes)

            self.assertEqual(report.nb_created_pages, 0)
            self.assertEqual(len(report.created_webentities), 1)

            report = traph.index_batch_crawl(
                {
                    b"s:https|h:org|h:wikipedia|h:www|": [
                        b"s:https|h:org|h:wikipedia|h:fr|",
                        b"s:https|h:org|h:wikipedia|h:en|",
                    ]
                }
            )

            self.assertEqual(report.nb_created_pages, 3)
            self.assertEqual(len(report.created_webentities), 0)
            self.assertEqual(traph.count_pages(), 3)
            self.assertEqual(traph.count_links(), 2)

            for lru, prefix, isPrefix in [
                (b"s:https|h:org|h:wikipedia|", b"s:https|h:org|h:wikipedia|", True),
                (
                    b"s:https|h:org|h:wikipedia|h:en|",
                    b"s:https|h:org|h:wikipedia|",
                    False,
                ),
                (
                    b"s:https|h:org|h:wikipedia|h:en|p:wiki|p:Crawl|",
                    b"s:https|h:org|h:wikipedia|",
                    False,
                ),
                (
                    b"s:https|h:org|h:wikipedia|h:www|",
                    b"s:https|h:org|h:wikipedia|h:www|",
                    True,
                ),
                (
                    b"s:https|h:org|h:wikipedia|h:www|p:wiki|p:Crawl|",
                    b"s:https|h:org|h:wikipedia|h:www|",
                    False,
                ),
            ]:
                self.assertEqual(traph.retrieve_prefix(lru), prefix)
                self.assertEqual(traph.retrieve_webentity(lru), 1)
                try:
                    self.assertTrue(
                        traph.get_webentity_by_prefix(lru) == 1 and isPrefix
                    )
                except TraphException:
                    self.assertFalse(isPrefix)

            crawled_pages = traph.get_webentity_crawled_pages(1, wiki_prefixes)

            self.assertEqual(
                set(page["lru"] for page in crawled_pages),
                set([b"s:https|h:org|h:wikipedia|h:www|"]),
            )

            pages = traph.get_webentity_pages(1, wiki_prefixes)

            self.assertEqual(
                set(page["lru"] for page in pages),
                set(
                    [
                        b"s:https|h:org|h:wikipedia|h:www|",
                        b"s:https|h:org|h:wikipedia|h:fr|",
                        b"s:https|h:org|h:wikipedia|h:en|",
                    ]
                ),
            )

    def test_prefix_methods(self):
        with self.open_traph() as traph:
            # 1) Potential prefix when the traph is empty
            prefix = traph.get_potential_prefix(
                b"s:http|h:fr|h:sciences-po|h:medialab|"
            )
            self.assertEqual(prefix, b"s:http|h:fr|h:sciences-po|")

            # 2) Test with existing webentity on path
            traph.create_webentity([b"s:http|h:fr|h:sciences-po|h:medialab|"])
            prefix = traph.get_potential_prefix(
                b"s:http|h:fr|h:sciences-po|h:medialab|p:www|p:publications|"
            )
            self.assertEqual(prefix, b"s:http|h:fr|h:sciences-po|h:medialab|")

            # 3) With an upper webentity
            traph.create_webentity([b"s:http|h:fr|h:sciences-po|"])
            prefix = traph.get_potential_prefix(
                b"s:http|h:fr|h:sciences-po|h:medialab|p:www|p:publications|"
            )
            self.assertEqual(prefix, b"s:http|h:fr|h:sciences-po|h:medialab|")

            # 4) Identity case
            prefix = traph.get_potential_prefix(
                b"s:http|h:fr|h:sciences-po|h:medialab|"
            )
            self.assertEqual(prefix, b"s:http|h:fr|h:sciences-po|h:medialab|")

    def test_long_stems(self):
        with self.open_traph() as traph:
            traph.add_page(
                b"s:http|h:fr|h:sciences-po|p:thisisaveryveryveryverylooooooooooooooooongstem|p:thisalsoisquitethelongstemisntitnotsomuchtobehonest|"
            )
            traph.add_page(
                b"s:http|h:fr|h:sciences-po|p:sooooooofunnnnnnyyyyyyyyyyyyyyyyyyyyy|"
            )

            pages_in_traph = [lru for _, lru in traph.pages_iter()]
            for node in traph.lru_trie.nodes_iter():
                pass
            self.assertEqual(
                set(pages_in_traph),
                set(
                    [
                        b"s:http|h:fr|h:sciences-po|p:thisisaveryveryveryverylooooooooooooooooongstem|p:thisalsoisquitethelongstemisntitnotsomuchtobehonest|",
                        b"s:http|h:fr|h:sciences-po|p:sooooooofunnnnnnyyyyyyyyyyyyyyyyyyyyy|",
                    ]
                ),
            )

    def test_get_webentity_child_webentities(self):
        with self.open_traph() as traph:
            lru_trie = traph.lru_trie

            report = traph.add_page(b"s:http|h:com|h:twitter|")
            report += traph.add_page(b"s:http|h:com|h:twitter|p:yomgui|")
            report += traph.add_page(b"s:http|h:com|h:twitter|p:boo|")
            report += traph.add_page(b"s:http|h:com|h:twitter|p:boo|p:photos|")

            child_webentities = traph.get_webentity_child_webentities(
                1, [b"s:http|h:com|h:twitter|"]
            )

            self.assertEqual(set(child_webentities), set([2, 3]))

            flag_tests = [
                (b"s:http|", True),
                (b"s:http|h:com|", True),
                (b"s:http|h:com|h:twitter|", True),
                (b"s:http|h:com|h:twitter|p:yomgui|", False),
                (b"s:http|h:com|h:twitter|p:boo|", False),
                (b"s:http|h:com|h:twitter|p:boo|p:photos|", False),
            ]

            for lru, flag in flag_tests:
                self.assertEqual(
                    lru_trie.lru_node(lru).can_have_child_webentities(), flag
                )

            twitter_prefix = b"s:http|h:com|h:twitter|"
            twitter_node = lru_trie.lru_node(twitter_prefix)

            self.assertEqual(
                not any(
                    node == "p:photos|"
                    for node, _ in lru_trie.dfs_iter(
                        twitter_node, twitter_prefix, skip_childless_paths=True
                    )
                ),
                True,
            )

    def test_get_webentity_pages(self):
        with self.open_traph() as traph:
            traph.add_page(b"s:http|h:fr|h:sciences-po|h:medialab|")

            self.assertEqual(
                traph.get_webentity_pages(
                    1, [b"s:http|h:fr|h:sciences-po|h:medialab|"]
                ),
                [{"crawled": False, "lru": b"s:http|h:fr|h:sciences-po|h:medialab|"}],
            )

            traph.add_page(b"s:http|h:fr|h:sciences-po|h:medialab|p:people|")

            self.assertEqual(
                traph.get_webentity_pages(
                    1, [b"s:http|h:fr|h:sciences-po|h:medialab|"]
                ),
                [
                    {"crawled": False, "lru": b"s:http|h:fr|h:sciences-po|h:medialab|"},
                    {
                        "crawled": False,
                        "lru": b"s:http|h:fr|h:sciences-po|h:medialab|p:people|",
                    },
                ],
            )

    def test_hyphe_issue354(self):
        from test.config import WEBENTITY_CREATION_RULES_REGEXES

        with self.open_traph(
            default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES[
                "subdomain"
            ]
        ) as traph:
            traph.add_page(b"s:http|h:fr|h:sciences-po|h:medialab|")

            traph.index_batch_crawl(
                {
                    b"s:http|h:fr|h:sciences-po|h:medialab|": [
                        b"s:http|h:fr|h:sciences-po|h:bibli|"
                    ]
                }
            )

            self.assertEqual(
                traph.get_webentity_pages(
                    1, [b"s:http|h:fr|h:sciences-po|h:medialab|"]
                ),
                [{"crawled": True, "lru": b"s:http|h:fr|h:sciences-po|h:medialab|"}],
            )

            self.assertEqual(
                traph.get_webentity_pages(2, [b"s:http|h:fr|h:sciences-po|h:bibli|"]),
                [{"crawled": False, "lru": b"s:http|h:fr|h:sciences-po|h:bibli|"}],
            )

    def test_hyphe_issue444(self):
        with self.open_traph() as traph:
            traph.add_page(b"s:http|h:fr|h:sciences-po|h:medialab|")

            report = traph.index_batch_crawl(
                {b"s:http|h:fr|h:sciences-po|h:medialab|": [b"s:http|h:org|h:www|"]}
            )

            self.assertEqual(len(report.created_webentities), 1)

            self.assertEqual(
                list(report.created_webentities.items())[0][1],
                [b"s:http|h:org|h:www|", b"s:https|h:org|h:www|"],
            )

    def test_clear(self):
        with self.open_traph() as traph:
            traph.add_page(b"s:http|h:fr|h:sciences-po|h:medialab|")

            self.assertEqual(traph.count_pages(), 1)

            traph.clear()

            self.assertEqual(traph.count_pages(), 0)
