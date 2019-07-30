# -*- coding: utf-8 -*-
# =============================================================================
# Traversal Unit Tests
# =============================================================================
#
# Testing the traversal methods whenever needed.
#
from test.test_cases import TraphTestCase
from test.config import WEBENTITY_CREATION_RULES_REGEXES

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
                [lru for node, lru in trie.webentity_inorder_iter(prefix_node, prefix)],
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
                [lru for node, lru in trie.webentity_inorder_iter(prefix_node, prefix)],
                webentity_inorder
            )

    # def test_paginated_webentity_inorder_iter(self):

    #     with self.open_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['domain']) as traph:
    #         trie = traph.lru_trie

    #         traph.add_page('s:http|h:com|h:world|p:europe|')
    #         traph.add_page('s:http|h:com|h:world|p:asia|')
    #         traph.add_page('s:http|h:com|h:world|p:africa|')
    #         traph.add_page('s:http|h:com|h:world|p:oceania|')

    #         traph.add_page('s:http|h:com|h:world|p:europe|p:spain|')
    #         traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
    #         traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:toledo|')
    #         traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
    #         traph.add_page('s:http|h:com|h:world|p:europe|p:france|')
    #         traph.add_page('s:http|h:com|h:world|p:europe|p:romania|')

    #         prefix = 's:http|h:com|h:world|'

    #         prefix_node = trie.lru_node(prefix)

    #         pagination_node = trie.lru_node('s:http|h:com|h:world|p:europe|p:romania|')

    #         print
    #         print
    #         for node, lru in trie.webentity_inorder_iter(
    #             prefix_node, prefix, pagination_node, 'cclr'
    #         ):
    #             print lru, node
    #         print
    #         print
