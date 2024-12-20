# -*- coding: utf-8 -*-
# =============================================================================
# Traph Networks Unit Tests
# =============================================================================
#
# Testing the networks generated by the Traph.
#
from test.test_cases import TraphTestCase
from test.helpers import webentity_label_from_prefixes, legible_network
from test.config import WEBENTITY_CREATION_RULES_REGEXES


class TestNetwork(TraphTestCase):
    def test_network(self):
        creation_rules = {
            b"s:http|h:com|h:world|": WEBENTITY_CREATION_RULES_REGEXES["path1"]
        }

        webentities = {}

        with self.open_traph(webentity_creation_rules=creation_rules) as traph:
            report = traph.index_batch_crawl(
                {
                    b"s:http|h:com|h:world|p:europe|p:spain|": [
                        b"s:http|h:com|h:world|p:europe|p:spain|p:madrid|",
                        b"s:http|h:com|h:world|p:america|",
                    ],
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:asia|"
                    ],
                }
            )

            for weid, prefixes in report.created_webentities.items():
                webentities[weid] = webentity_label_from_prefixes(prefixes)

            # Normal network
            network = traph.get_webentities_links()

            self.assertEqual(network[1]["pages_crawled"], 1)  # europe/spain
            self.assertEqual(network[1]["pages_uncrawled"], 1)  # europe/spain/madrid
            self.assertEqual(network[2]["pages_crawled"], 1)  # america
            self.assertEqual(network[2]["pages_uncrawled"], 0)  #
            self.assertEqual(network[3]["pages_crawled"], 0)  #
            self.assertEqual(network[3]["pages_uncrawled"], 1)  # asia

            legible = legible_network(webentities, network)

            self.assertIdenticalMultimaps(
                legible,
                {
                    b"s:http|h:com|h:world|p:europe|": [
                        b"s:http|h:com|h:world|p:america|"
                    ],
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:asia|"
                    ],
                },
            )

            # Keeping auto-links
            network = legible_network(
                webentities, traph.get_webentities_links(include_auto=True)
            )

            self.assertIdenticalMultimaps(
                network,
                {
                    b"s:http|h:com|h:world|p:europe|": [
                        b"s:http|h:com|h:world|p:america|",
                        b"s:http|h:com|h:world|p:europe|",
                    ],
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:asia|"
                    ],
                },
            )

            # Inlinks
            network = legible_network(
                webentities, traph.get_webentities_links(out=False)
            )

            self.assertIdenticalMultimaps(
                network,
                {
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:europe|"
                    ],
                    b"s:http|h:com|h:world|p:asia|": [
                        b"s:http|h:com|h:world|p:america|"
                    ],
                },
            )

            report = traph.add_pages(
                [
                    b"s:http|h:com|h:world|p:africa|",
                    b"s:http|h:com|h:world|p:oceania|",
                ]
            )

            for weid, prefixes in report.created_webentities.items():
                webentities[weid] = webentity_label_from_prefixes(prefixes)

            traph.add_links(
                [
                    (
                        b"s:http|h:com|h:world|p:america|",
                        b"s:http|h:com|h:world|p:africa|p:raba|",
                    ),
                    (
                        b"s:http|h:com|h:world|p:asia|",
                        b"s:http|h:com|h:world|p:africa|p:raba|",
                    ),
                    (
                        b"s:http|h:com|h:world|p:europe|p:spain|p:madrid|",
                        b"s:http|h:com|h:world|p:africa|p:raba|",
                    ),
                    (
                        b"s:http|h:com|h:world|p:asia|",
                        b"s:http|h:com|h:world|p:africa|p:tunis|",
                    ),
                    (
                        b"s:http|h:com|h:world|p:europe|p:spain|p:madrid|",
                        b"s:http|h:com|h:world|p:africa|p:tunis|",
                    ),
                    (
                        b"s:http|h:com|h:world|p:europe|p:spain|p:madrid|",
                        b"s:http|h:com|h:world|p:africa|p:bamako|",
                    ),
                ]
            )

            network = legible_network(webentities, traph.get_webentities_links())

            self.assertEqual(traph.count_pages(), 9)

            self.assertIdenticalMultimaps(
                network,
                {
                    b"s:http|h:com|h:world|p:europe|": [
                        b"s:http|h:com|h:world|p:america|",
                        b"s:http|h:com|h:world|p:africa|",
                    ],
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:africa|",
                        b"s:http|h:com|h:world|p:asia|",
                    ],
                    b"s:http|h:com|h:world|p:asia|": [
                        b"s:http|h:com|h:world|p:africa|"
                    ],
                },
            )

            europe_pages = traph.get_webentity_pages(
                1, [b"s:http|h:com|h:world|p:europe|"]
            )

            self.assertEqual(
                set(page["lru"] for page in europe_pages),
                set(
                    [
                        b"s:http|h:com|h:world|p:europe|p:spain|p:madrid|",
                        b"s:http|h:com|h:world|p:europe|p:spain|",
                    ]
                ),
            )

            most_linked_pages = traph.get_webentity_most_linked_pages(
                4, [b"s:http|h:com|h:world|p:africa|"]
            )

            self.assertEqual(
                set((page["lru"], page["indegree"]) for page in most_linked_pages),
                set(
                    [
                        (b"s:http|h:com|h:world|p:africa|p:raba|", 3),
                        (b"s:http|h:com|h:world|p:africa|p:tunis|", 2),
                        (b"s:http|h:com|h:world|p:africa|", 1),
                        (b"s:http|h:com|h:world|p:africa|p:bamako|", 1),
                    ]
                ),
            )

            most_linked_pages = traph.get_webentity_most_linked_pages(
                4, [b"s:http|h:com|h:world|p:africa|"], pages_count=2
            )

            self.assertEqual(
                set((page["lru"], page["indegree"]) for page in most_linked_pages),
                set(
                    [
                        (b"s:http|h:com|h:world|p:africa|p:raba|", 3),
                        (b"s:http|h:com|h:world|p:africa|p:tunis|", 2),
                    ]
                ),
            )

            most_linked_pages = traph.get_webentity_most_linked_pages(
                4, [b"s:http|h:com|h:world|p:africa|"], max_depth=0
            )

            self.assertEqual(
                set((page["lru"], page["indegree"]) for page in most_linked_pages),
                set([(b"s:http|h:com|h:world|p:africa|", 1)]),
            )

    def test_network_with_multiple_root_stems(self):
        creation_rules = {
            b"s:http|h:com|h:world|": WEBENTITY_CREATION_RULES_REGEXES["path1"]
        }

        webentities = {}

        with self.open_traph(webentity_creation_rules=creation_rules) as traph:
            report = traph.index_batch_crawl(
                {
                    b"s:http|h:com|h:world|p:europe|p:spain|": [
                        b"s:http|h:com|h:world|p:europe|p:spain|p:madrid|",
                        b"s:http|h:com|h:world|p:america|",
                    ],
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:asia|",
                        b"s:https|h:com|h:world|p:africa|",
                    ],
                }
            )

            for weid, prefixes in report.created_webentities.items():
                webentities[weid] = webentity_label_from_prefixes(prefixes)

            # Normal network
            network = legible_network(webentities, traph.get_webentities_links())

            self.assertIdenticalMultimaps(
                network,
                {
                    b"s:http|h:com|h:world|p:europe|": [
                        b"s:http|h:com|h:world|p:america|"
                    ],
                    b"s:http|h:com|h:world|p:america|": [
                        b"s:http|h:com|h:world|p:asia|",
                        b"s:http|h:com|h:world|",
                    ],
                },
            )
