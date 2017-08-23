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
