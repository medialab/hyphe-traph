# -*- coding: utf-8 -*-
# =============================================================================
# Traversal Unit Tests
# =============================================================================
#
# Testing the traversal methods whenever needed.
#
from test.test_cases import TraphTestCase
from test.config import WEBENTITY_CREATION_RULES_REGEXES

from traph.helpers import ops_to_base4, build_pagination_token

WEBENTITY_CREATION_RULES = {
    b's:http|h:com|h:world|': WEBENTITY_CREATION_RULES_REGEXES['path1'],
}


def straigthen_pagelinks(pagelinks):
    return sorted(tuple(link) for link in pagelinks)


class TestTraversal(TraphTestCase):

    def assertPaginationResultEqual(self, p1, p2):
        self.assertEqual(p1['count_pagelinks'], p2['count_pagelinks'])
        self.assertEqual(p1['count_sourcepages'], p2['count_sourcepages'])
        self.assertEqual(p1['done'], p2['done'])

        pg1 = straigthen_pagelinks(p1['pagelinks'])
        pg2 = straigthen_pagelinks(p2['pagelinks'])

        self.assertEqual(pg1, pg2)

    def test_dfs_iter(self):
        with self.open_traph(webentity_creation_rules=WEBENTITY_CREATION_RULES) as traph:
            trie = traph.lru_trie

            traph.add_page(b's:http|h:com|h:world|p:europe|')
            traph.add_page(b's:http|h:com|h:world|p:asia|')
            traph.add_page(b's:http|h:com|h:world|p:africa|')
            traph.add_page(b's:http|h:com|h:world|p:oceania|')

            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:france|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:romania|')

            traph.add_webentity_creation_rule(
                b's:http|h:com|h:world|p:europe|',
                WEBENTITY_CREATION_RULES_REGEXES['path2']
            )

            full_dfs = list(node.stem() for node, _ in trie.dfs_iter())

            self.assertEqual(full_dfs, [
                b's:http|',
                b'h:com|',
                b'h:world|',
                b'p:europe|',
                b'p:spain|',
                b'p:france|',
                b'p:romania|',
                b'h:www|',
                b'p:europe|',
                b'p:spain|',
                b'p:france|',
                b'p:romania|',
                b'p:asia|',
                b'p:africa|',
                b'p:oceania|',
                b'p:asia|',
                b'p:africa|',
                b'p:oceania|',
                b's:https|',
                b'h:com|',
                b'h:world|',
                b'p:europe|',
                b'p:spain|',
                b'p:france|',
                b'p:romania|',
                b'h:www|',
                b'p:europe|',
                b'p:spain|',
                b'p:france|',
                b'p:romania|',
                b'p:asia|',
                b'p:africa|',
                b'p:oceania|',
                b'p:asia|',
                b'p:africa|',
                b'p:oceania|'
            ])

            starting_node = trie.lru_node(b's:http|h:com|h:world|p:europe|')

            partial_dfs = list(node.stem() for node, _ in trie.dfs_iter(starting_node, b's:http|h:com|h:world|p:europe|'))

            self.assertEqual(partial_dfs, [
                b'p:europe|',
                b'p:spain|',
                b'p:france|',
                b'p:romania|'
            ])

    def test_webentity_dfs_iter(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page(b's:http|h:com|h:world|p:europe|')
            traph.add_page(b's:http|h:com|h:world|p:asia|')
            traph.add_page(b's:http|h:com|h:world|p:africa|')
            traph.add_page(b's:http|h:com|h:world|p:oceania|')

            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:france|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:romania|')

            prefix = b's:http|h:com|h:world|'

            prefix_node = trie.lru_node(prefix)

            # NOTE: beware, order is mostly arbitrary here
            webentity_dfs = [
                b's:http|h:com|h:world|',
                b's:http|h:com|h:world|p:europe|',
                b's:http|h:com|h:world|p:europe|p:spain|',
                b's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
                b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|',
                b's:http|h:com|h:world|p:europe|p:spain|p:toledo|',
                b's:http|h:com|h:world|p:europe|p:france|',
                b's:http|h:com|h:world|p:europe|p:romania|',
                b's:http|h:com|h:world|p:asia|',
                b's:http|h:com|h:world|p:africa|',
                b's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for _, lru in trie.webentity_dfs_iter(prefix_node, prefix)],
                webentity_dfs
            )

            traph.create_webentity([b's:http|h:com|h:world|p:europe|p:spain|'])

            webentity_dfs = [
                b's:http|h:com|h:world|',
                b's:http|h:com|h:world|p:europe|',
                b's:http|h:com|h:world|p:europe|p:france|',
                b's:http|h:com|h:world|p:europe|p:romania|',
                b's:http|h:com|h:world|p:asia|',
                b's:http|h:com|h:world|p:africa|',
                b's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru in trie.webentity_dfs_iter(prefix_node, prefix)],
                webentity_dfs
            )

    def test_webentity_inorder_iter(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page(b's:http|h:com|h:world|p:europe|')
            traph.add_page(b's:http|h:com|h:world|p:asia|')
            traph.add_page(b's:http|h:com|h:world|p:africa|')
            traph.add_page(b's:http|h:com|h:world|p:oceania|')

            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:france|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:romania|')

            prefix = b's:http|h:com|h:world|'

            prefix_node = trie.lru_node(prefix)

            webentity_inorder = [
                b's:http|h:com|h:world|',
                b's:http|h:com|h:world|p:africa|',
                b's:http|h:com|h:world|p:asia|',
                b's:http|h:com|h:world|p:europe|',
                b's:http|h:com|h:world|p:europe|p:france|',
                b's:http|h:com|h:world|p:europe|p:romania|',
                b's:http|h:com|h:world|p:europe|p:spain|',
                b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|',
                b's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
                b's:http|h:com|h:world|p:europe|p:spain|p:toledo|',
                b's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru, _ in trie.webentity_inorder_iter(prefix_node, prefix)],
                webentity_inorder
            )

            traph.create_webentity([b's:http|h:com|h:world|p:europe|p:spain|'])

            webentity_inorder = [
                b's:http|h:com|h:world|',
                b's:http|h:com|h:world|p:africa|',
                b's:http|h:com|h:world|p:asia|',
                b's:http|h:com|h:world|p:europe|',
                b's:http|h:com|h:world|p:europe|p:france|',
                b's:http|h:com|h:world|p:europe|p:romania|',
                b's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru, _ in trie.webentity_inorder_iter(prefix_node, prefix)],
                webentity_inorder
            )

    def test_paginated_webentity_inorder_iter(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page(b's:http|h:com|h:world|p:europe|')
            traph.add_page(b's:http|h:com|h:world|p:asia|')
            traph.add_page(b's:http|h:com|h:world|p:africa|')
            traph.add_page(b's:http|h:com|h:world|p:oceania|')

            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:france|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:romania|')

            prefix = b's:http|h:com|h:world|'

            prefix_node = trie.lru_node(prefix)

            webentity_inorder = [
                (b's:http|h:com|h:world|', ''),
                (b's:http|h:com|h:world|p:africa|', 'CLRL'),
                (b's:http|h:com|h:world|p:asia|', 'CLR'),
                (b's:http|h:com|h:world|p:europe|', 'C'),
                (b's:http|h:com|h:world|p:europe|p:france|', 'CCL'),
                (b's:http|h:com|h:world|p:europe|p:romania|', 'CCLR'),
                (b's:http|h:com|h:world|p:europe|p:spain|', 'CC'),
                (b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|', 'CCCL'),
                (b's:http|h:com|h:world|p:europe|p:spain|p:madrid|', 'CCC'),
                (b's:http|h:com|h:world|p:europe|p:spain|p:toledo|', 'CCCR'),
                (b's:http|h:com|h:world|p:oceania|', 'CR')
            ]

            for i, (pagination_lru, pagination_path) in enumerate(webentity_inorder):
                pagination_path = ops_to_base4(pagination_path)

                self.assertEqual(
                    [lru for node, lru, _ in trie.webentity_inorder_iter(prefix_node, prefix, pagination_path)],
                    [lru for lru, _ in webentity_inorder[i + 1:]]
                )

            # print
            # print
            # for node, lru, path in trie.webentity_inorder_iter(
            #     prefix_node, prefix, 'clrl'
            # ):
            #     print lru, node, base4_to_ops(path)
            # print
            # print

    def test_paginate_webentity_pages(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page(b's:http|h:com|h:world|p:europe|')
            traph.add_page(b's:http|h:com|h:world|p:asia|')
            traph.add_page(b's:http|h:com|h:world|p:africa|')
            traph.add_page(b's:http|h:com|h:world|p:oceania|')

            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:france|')
            traph.add_page(b's:http|h:com|h:world|p:europe|p:romania|')

            prefixes = [b's:http|h:com|h:world|']

            webentity_inorder = [
                (b's:http|h:com|h:world|p:africa|', 'CLRL'),
                (b's:http|h:com|h:world|p:asia|', 'CLR'),
                (b's:http|h:com|h:world|p:europe|', 'C'),
                (b's:http|h:com|h:world|p:europe|p:france|', 'CCL'),
                (b's:http|h:com|h:world|p:europe|p:romania|', 'CCLR'),
                (b's:http|h:com|h:world|p:europe|p:spain|', 'CC'),
                (b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|', 'CCCL'),
                (b's:http|h:com|h:world|p:europe|p:spain|p:madrid|', 'CCC'),
                (b's:http|h:com|h:world|p:europe|p:spain|p:toledo|', 'CCCR'),
                (b's:http|h:com|h:world|p:oceania|', 'CR')
            ]

            # Fetching everything
            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes),
                {
                    'done': True,
                    'count': len(webentity_inorder),
                    'count_crawled': 0,
                    'pages': [
                        {'lru': lru, 'crawled': False}
                        for lru, _ in webentity_inorder
                    ]
                }
            )

            # Fetching perfect count
            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, page_count=len(webentity_inorder)),
                {
                    'done': True,
                    'count': len(webentity_inorder),
                    'count_crawled': 0,
                    'pages': [
                        {'lru': lru, 'crawled': False}
                        for lru, _ in webentity_inorder
                    ]
                }
            )

            # Fetching more than there is
            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, page_count=50),
                {
                    'done': True,
                    'count': len(webentity_inorder),
                    'count_crawled': 0,
                    'pages': [
                        {'lru': lru, 'crawled': False}
                        for lru, _ in webentity_inorder
                    ]
                }
            )

            # Fetching first two
            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, page_count=2),
                {
                    'done': False,
                    'count': 2,
                    'count_crawled': 0,
                    'pages': [
                        {'lru': b's:http|h:com|h:world|p:africa|', 'crawled': False},
                        {'lru': b's:http|h:com|h:world|p:asia|', 'crawled': False}
                    ],
                    'token': build_pagination_token(0, ops_to_base4('CLR'))
                }
            )

            # Fetching second two
            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, page_count=2, pagination_token=build_pagination_token(0, ops_to_base4('CLR'))),
                {
                    'done': False,
                    'count': 2,
                    'count_crawled': 0,
                    'pages': [
                        {'lru': b's:http|h:com|h:world|p:europe|', 'crawled': False},
                        {'lru': b's:http|h:com|h:world|p:europe|p:france|', 'crawled': False}
                    ],
                    'token': build_pagination_token(0, ops_to_base4('CCL'))
                }
            )

            # Fetching more than one prefix
            self.assertEqual(
                traph.paginate_webentity_pages(
                    None, prefixes + [b's:https|h:com|h:world|'],
                    page_count=20, pagination_token=build_pagination_token(0, ops_to_base4('CLR'))
                ),
                {
                    'done': True,
                    'count': len(webentity_inorder) - 2,
                    'count_crawled': 0,
                    'pages': [
                        {'lru': lru, 'crawled': False}
                        for lru, _ in webentity_inorder[2:]
                    ]
                }
            )

            # Fetching three by three
            token = None
            calls = 0

            while True:
                result = traph.paginate_webentity_pages(
                    None, prefixes,
                    page_count=3, pagination_token=token
                )
                calls += 1

                if 'token' in result:
                    token = result['token']
                else:
                    break

            self.assertEqual(calls, 4)

            # Crawled
            traph.add_page(b's:http|h:com|h:world|p:aaa|', crawled=True)

            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, page_count=2),
                {
                    'done': False,
                    'count': 2,
                    'count_crawled': 1,
                    'pages': [
                        {'lru': b's:http|h:com|h:world|p:aaa|', 'crawled': True},
                        {'lru': b's:http|h:com|h:world|p:africa|', 'crawled': False}
                    ],
                    'token': build_pagination_token(0, ops_to_base4('CLRL'))
                }
            )

            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, crawled_only=True),
                {
                    'done': True,
                    'count': 1,
                    'count_crawled': 1,
                    'pages': [
                        {'lru': b's:http|h:com|h:world|p:aaa|', 'crawled': True}
                    ]
                }
            )

    def test_paginate_webentity_pagelinks(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:

            batch_links = {
                b's:http|h:com|h:world|p:europe|': [
                    b's:http|h:com|h:world|p:europe|p:spain|',
                    b's:http|h:com|h:world|p:europe|p:france|',
                    b's:http|h:com|h:world|p:europe|p:romania|',
                    b's:http|h:com|h:world|p:europe|p:france|'
                ],
                b's:http|h:com|h:world|': [
                    b's:http|h:com|h:upsidedown|p:demogorgon|',
                    b's:http|h:com|h:world|p:europe|',
                    b's:http|h:com|h:world|p:asia|',
                    b's:http|h:com|h:world|p:africa|',
                    b's:http|h:com|h:world|p:oceania|',
                ],
                b's:http|h:com|h:world|p:europe|p:romania|': [],
                b's:http|h:com|h:world|p:europe|p:spain|': [
                    b's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
                    b's:http|h:com|h:world|p:europe|p:spain|p:toledo|',
                    b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|',
                    b's:http|h:com|h:upsidedown|p:eleven|',
                    b's:http|h:com|h:upsidedown|p:will|',
                ],
            }

            print(list(batch_links.keys()))

            traph.index_batch_crawl(batch_links)

            prefixes = [b's:http|h:com|h:world|']

            pagelinks_inorder = [
                [b's:http|h:com|h:world|', b's:http|h:com|h:world|p:europe|', 1],
                [b's:http|h:com|h:world|', b's:http|h:com|h:world|p:asia|', 1],
                [b's:http|h:com|h:world|', b's:http|h:com|h:world|p:africa|', 1],
                [b's:http|h:com|h:world|', b's:http|h:com|h:world|p:oceania|', 1],
                [b's:http|h:com|h:world|p:europe|', b's:http|h:com|h:world|p:europe|p:spain|', 1],
                [b's:http|h:com|h:world|p:europe|', b's:http|h:com|h:world|p:europe|p:france|', 2],
                [b's:http|h:com|h:world|p:europe|', b's:http|h:com|h:world|p:europe|p:romania|', 1],
                [b's:http|h:com|h:world|p:europe|p:spain|', b's:http|h:com|h:world|p:europe|p:spain|p:madrid|', 1],
                [b's:http|h:com|h:world|p:europe|p:spain|', b's:http|h:com|h:world|p:europe|p:spain|p:toledo|', 1],
                [b's:http|h:com|h:world|p:europe|p:spain|', b's:http|h:com|h:world|p:europe|p:spain|p:barcelona|', 1]
            ]
            outlinks = [
                [b's:http|h:com|h:world|', b's:http|h:com|h:upsidedown|p:demogorgon|', 1]
            ]

            outlinks_2 = [
                [b's:http|h:com|h:world|p:europe|p:spain|', b's:http|h:com|h:upsidedown|p:eleven|', 1],
                [b's:http|h:com|h:world|p:europe|p:spain|', b's:http|h:com|h:upsidedown|p:will|', 1]
            ]

            # Fetching everything
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(1, prefixes),
                {
                    'done': True,
                    'count_sourcepages': 3,
                    'count_pagelinks': 10,
                    'pagelinks': pagelinks_inorder[:]
                }
            )

            # Fetching perfect count
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(1, prefixes, source_page_count=3),
                {
                    'done': True,
                    'count_sourcepages': 3,
                    'count_pagelinks': 10,
                    'pagelinks': pagelinks_inorder[:]
                }
            )

            # Fetching more than there is
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(1, prefixes, source_page_count=50),
                {
                    'done': True,
                    'count_sourcepages': 3,
                    'count_pagelinks': 10,
                    'pagelinks': pagelinks_inorder[:]
                }
            )

            # Fetching first two
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(1, prefixes, source_page_count=2),
                {
                    'done': False,
                    'count_sourcepages': 2,
                    'count_pagelinks': 7,
                    'pagelinks': pagelinks_inorder[:7],
                    'token': build_pagination_token(0, ops_to_base4('CCLR'))
                }
            )

            # Fetching second two
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=2,
                    pagination_token=build_pagination_token(0, ops_to_base4('CCLR'))
                ),
                {
                    'done': True,
                    'count_sourcepages': 1,
                    'count_pagelinks': 3,
                    'pagelinks': pagelinks_inorder[7:]
                }
            )

            batch_links_2 = {
                b's:https|h:com|h:world|': [
                    b's:https|h:com|h:world|p:europe|',
                    b's:https|h:com|h:world|p:asia|'
                ],
                b's:https|h:com|h:world|p:europe|': [
                    b's:https|h:com|h:world|p:europe|p:spain|'
                ]
            }
            traph.index_batch_crawl(batch_links_2)

            prefixes.append(b's:https|h:com|h:world|')

            pagelinks_inorder_2 = [
                [b's:https|h:com|h:world|', b's:https|h:com|h:world|p:europe|', 1],
                [b's:https|h:com|h:world|', b's:https|h:com|h:world|p:asia|', 1],
                [b's:https|h:com|h:world|p:europe|', b's:https|h:com|h:world|p:europe|p:spain|', 1]
            ]

            # Fetching more than one prefix all at once
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(1, prefixes, source_page_count=5),
                {
                    'done': True,
                    'count_sourcepages': 5,
                    'count_pagelinks': 13,
                    'pagelinks': (pagelinks_inorder + pagelinks_inorder_2),
                }
            )

            # Fetching more than one prefix all at once 2 sourcepages by 2
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(1, prefixes, source_page_count=2),
                {
                    'done': False,
                    'count_sourcepages': 2,
                    'count_pagelinks': 7,
                    'pagelinks': (pagelinks_inorder + pagelinks_inorder_2)[0:7],
                    'token': build_pagination_token(0, ops_to_base4('CCLR'))
                }
            )

            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=2,
                    pagination_token=build_pagination_token(0, ops_to_base4('CCLR'))
                ),
                {
                    'done': False,
                    'count_sourcepages': 2,
                    'count_pagelinks': 5,
                    'pagelinks': (pagelinks_inorder + pagelinks_inorder_2)[7:12],
                    'token': build_pagination_token(1, ops_to_base4('CRL'))
                }
            )

            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=2,
                    pagination_token=build_pagination_token(1, ops_to_base4('CRL'))
                ),
                {
                    'done': True,
                    'count_sourcepages': 1,
                    'count_pagelinks': 1,
                    'pagelinks': (pagelinks_inorder + pagelinks_inorder_2)[12:]
                }
            )

            # Fetching outbound links also
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=10, include_outbound=True
                ),
                {
                    'done': True,
                    'count_sourcepages': 5,
                    'count_pagelinks': 16,
                    'pagelinks': outlinks + pagelinks_inorder + outlinks_2 + pagelinks_inorder_2
                }
            )

            # Fetching outbound links only, at once
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=2,
                    include_outbound=True, include_internal=False
                ),
                {
                    'done': True,
                    'count_sourcepages': 2,
                    'count_pagelinks': 3,
                    'pagelinks': outlinks + outlinks_2
                }
            )

            # Fetching outbound links only, paginated
            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=1,
                    include_outbound=True, include_internal=False
                ),
                {
                    'done': False,
                    'count_sourcepages': 1,
                    'count_pagelinks': 1,
                    'pagelinks': outlinks,
                    'token': build_pagination_token(0, ops_to_base4('CCLR'))
                }
            )

            self.assertPaginationResultEqual(
                traph.paginate_webentity_pagelinks(
                    1, prefixes, source_page_count=1,
                    include_outbound=True, include_internal=False,
                    pagination_token=build_pagination_token(0, ops_to_base4('CCLR'))
                ),
                {
                    'done': True,
                    'count_sourcepages': 1,
                    'count_pagelinks': 2,
                    'pagelinks': outlinks_2
                }
            )

            # print
            # print
            # for prefix in prefixes:
            #     prefix_node = trie.lru_node(prefix)
            #     for _, lru, path in trie.webentity_inorder_iter(
            #         prefix_node, prefix
            #     ):
            #         print lru, base4_to_ops(path)
            # print
            # print
