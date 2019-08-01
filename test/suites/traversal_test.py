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
    's:http|h:com|h:world|': WEBENTITY_CREATION_RULES_REGEXES['path1'],
}


class TestTraversal(TraphTestCase):

    def test_dfs_iter(self):
        with self.open_traph(webentity_creation_rules=WEBENTITY_CREATION_RULES) as traph:
            trie = traph.lru_trie

            traph.add_page('s:http|h:com|h:world|p:europe|')
            traph.add_page('s:http|h:com|h:world|p:asia|')
            traph.add_page('s:http|h:com|h:world|p:africa|')
            traph.add_page('s:http|h:com|h:world|p:oceania|')

            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:france|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:romania|')

            traph.add_webentity_creation_rule(
                's:http|h:com|h:world|p:europe|',
                WEBENTITY_CREATION_RULES_REGEXES['path2']
            )

            full_dfs = list(node.stem() for node, _ in trie.dfs_iter())

            self.assertEqual(full_dfs, [
                's:http|',
                'h:com|',
                'h:world|',
                'p:europe|',
                'p:spain|',
                'p:france|',
                'p:romania|',
                'h:www|',
                'p:europe|',
                'p:spain|',
                'p:france|',
                'p:romania|',
                'p:asia|',
                'p:africa|',
                'p:oceania|',
                'p:asia|',
                'p:africa|',
                'p:oceania|',
                's:https|',
                'h:com|',
                'h:world|',
                'p:europe|',
                'p:spain|',
                'p:france|',
                'p:romania|',
                'h:www|',
                'p:europe|',
                'p:spain|',
                'p:france|',
                'p:romania|',
                'p:asia|',
                'p:africa|',
                'p:oceania|',
                'p:asia|',
                'p:africa|',
                'p:oceania|'
            ])

            starting_node = trie.lru_node('s:http|h:com|h:world|p:europe|')

            partial_dfs = list(node.stem() for node, _ in trie.dfs_iter(starting_node, 's:http|h:com|h:world|p:europe|'))

            self.assertEqual(partial_dfs, [
                'p:europe|',
                'p:spain|',
                'p:france|',
                'p:romania|'
            ])

    def test_webentity_dfs_iter(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page('s:http|h:com|h:world|p:europe|')
            traph.add_page('s:http|h:com|h:world|p:asia|')
            traph.add_page('s:http|h:com|h:world|p:africa|')
            traph.add_page('s:http|h:com|h:world|p:oceania|')

            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:france|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:romania|')

            prefix = 's:http|h:com|h:world|'

            prefix_node = trie.lru_node(prefix)

            # NOTE: beware, order is mostly arbitrary here
            webentity_dfs = [
                's:http|h:com|h:world|',
                's:http|h:com|h:world|p:europe|',
                's:http|h:com|h:world|p:europe|p:spain|',
                's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
                's:http|h:com|h:world|p:europe|p:spain|p:barcelona|',
                's:http|h:com|h:world|p:europe|p:spain|p:toledo|',
                's:http|h:com|h:world|p:europe|p:france|',
                's:http|h:com|h:world|p:europe|p:romania|',
                's:http|h:com|h:world|p:asia|',
                's:http|h:com|h:world|p:africa|',
                's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru in trie.webentity_dfs_iter(prefix_node, prefix)],
                webentity_dfs
            )

            traph.create_webentity(['s:http|h:com|h:world|p:europe|p:spain|'])

            webentity_dfs = [
                's:http|h:com|h:world|',
                's:http|h:com|h:world|p:europe|',
                's:http|h:com|h:world|p:europe|p:france|',
                's:http|h:com|h:world|p:europe|p:romania|',
                's:http|h:com|h:world|p:asia|',
                's:http|h:com|h:world|p:africa|',
                's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru in trie.webentity_dfs_iter(prefix_node, prefix)],
                webentity_dfs
            )

    def test_webentity_inorder_iter(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page('s:http|h:com|h:world|p:europe|')
            traph.add_page('s:http|h:com|h:world|p:asia|')
            traph.add_page('s:http|h:com|h:world|p:africa|')
            traph.add_page('s:http|h:com|h:world|p:oceania|')

            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:france|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:romania|')

            prefix = 's:http|h:com|h:world|'

            prefix_node = trie.lru_node(prefix)

            webentity_inorder = [
                's:http|h:com|h:world|',
                's:http|h:com|h:world|p:africa|',
                's:http|h:com|h:world|p:asia|',
                's:http|h:com|h:world|p:europe|',
                's:http|h:com|h:world|p:europe|p:france|',
                's:http|h:com|h:world|p:europe|p:romania|',
                's:http|h:com|h:world|p:europe|p:spain|',
                's:http|h:com|h:world|p:europe|p:spain|p:barcelona|',
                's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
                's:http|h:com|h:world|p:europe|p:spain|p:toledo|',
                's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru, _ in trie.webentity_inorder_iter(prefix_node, prefix)],
                webentity_inorder
            )

            traph.create_webentity(['s:http|h:com|h:world|p:europe|p:spain|'])

            webentity_inorder = [
                's:http|h:com|h:world|',
                's:http|h:com|h:world|p:africa|',
                's:http|h:com|h:world|p:asia|',
                's:http|h:com|h:world|p:europe|',
                's:http|h:com|h:world|p:europe|p:france|',
                's:http|h:com|h:world|p:europe|p:romania|',
                's:http|h:com|h:world|p:oceania|'
            ]

            self.assertEqual(
                [lru for node, lru, _ in trie.webentity_inorder_iter(prefix_node, prefix)],
                webentity_inorder
            )

    def test_paginated_webentity_inorder_iter(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page('s:http|h:com|h:world|p:europe|')
            traph.add_page('s:http|h:com|h:world|p:asia|')
            traph.add_page('s:http|h:com|h:world|p:africa|')
            traph.add_page('s:http|h:com|h:world|p:oceania|')

            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:france|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:romania|')

            prefix = 's:http|h:com|h:world|'

            prefix_node = trie.lru_node(prefix)

            webentity_inorder = [
                ('s:http|h:com|h:world|', ''),
                ('s:http|h:com|h:world|p:africa|', 'CLRL'),
                ('s:http|h:com|h:world|p:asia|', 'CLR'),
                ('s:http|h:com|h:world|p:europe|', 'C'),
                ('s:http|h:com|h:world|p:europe|p:france|', 'CCL'),
                ('s:http|h:com|h:world|p:europe|p:romania|', 'CCLR'),
                ('s:http|h:com|h:world|p:europe|p:spain|', 'CC'),
                ('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|', 'CCCL'),
                ('s:http|h:com|h:world|p:europe|p:spain|p:madrid|', 'CCC'),
                ('s:http|h:com|h:world|p:europe|p:spain|p:toledo|', 'CCCR'),
                ('s:http|h:com|h:world|p:oceania|', 'CR')
            ]

            for i, (pagination_lru, pagination_path) in enumerate(webentity_inorder):
                pagination_path = ops_to_base4(pagination_path)

                self.assertEqual(
                    [lru for node, lru, _ in trie.webentity_inorder_iter(prefix_node, prefix, pagination_path)],
                    [lru for lru, _ in webentity_inorder[i + 1:]]
                )

            # print
            # print
            # for node, lru in trie.webentity_inorder_iter(
            #     prefix_node, prefix, trie.lru_node('s:http|h:com|h:world|p:africa|'), 'clrl'
            # ):
            #     print lru, node
            # print
            # print

    def test_paginate_webentity_pages(self):

        with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
            trie = traph.lru_trie

            traph.add_page('s:http|h:com|h:world|p:europe|')
            traph.add_page('s:http|h:com|h:world|p:asia|')
            traph.add_page('s:http|h:com|h:world|p:africa|')
            traph.add_page('s:http|h:com|h:world|p:oceania|')

            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:toledo|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:france|')
            traph.add_page('s:http|h:com|h:world|p:europe|p:romania|')

            prefixes = ['s:http|h:com|h:world|']

            webentity_inorder = [
                ('s:http|h:com|h:world|p:africa|', 'CLRL'),
                ('s:http|h:com|h:world|p:asia|', 'CLR'),
                ('s:http|h:com|h:world|p:europe|', 'C'),
                ('s:http|h:com|h:world|p:europe|p:france|', 'CCL'),
                ('s:http|h:com|h:world|p:europe|p:romania|', 'CCLR'),
                ('s:http|h:com|h:world|p:europe|p:spain|', 'CC'),
                ('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|', 'CCCL'),
                ('s:http|h:com|h:world|p:europe|p:spain|p:madrid|', 'CCC'),
                ('s:http|h:com|h:world|p:europe|p:spain|p:toledo|', 'CCCR'),
                ('s:http|h:com|h:world|p:oceania|', 'CR')
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
                        {'lru': 's:http|h:com|h:world|p:africa|', 'crawled': False},
                        {'lru': 's:http|h:com|h:world|p:asia|', 'crawled': False}
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
                        {'lru': 's:http|h:com|h:world|p:europe|', 'crawled': False},
                        {'lru': 's:http|h:com|h:world|p:europe|p:france|', 'crawled': False}
                    ],
                    'token': build_pagination_token(0, ops_to_base4('CCL'))
                }
            )

            # Fetching more than one prefix
            self.assertEqual(
                traph.paginate_webentity_pages(
                    None, prefixes + ['s:https|h:com|h:world|'],
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
            traph.add_page('s:http|h:com|h:world|p:aaa|', crawled=True)

            self.assertEqual(
                traph.paginate_webentity_pages(None, prefixes, page_count=2),
                {
                    'done': False,
                    'count': 2,
                    'count_crawled': 1,
                    'pages': [
                        {'lru': 's:http|h:com|h:world|p:aaa|', 'crawled': True},
                        {'lru': 's:http|h:com|h:world|p:africa|', 'crawled': False}
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
                        {'lru': 's:http|h:com|h:world|p:aaa|', 'crawled': True}
                    ]
                }
            )
