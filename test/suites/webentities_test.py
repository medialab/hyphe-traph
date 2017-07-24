# =============================================================================
# Webentities Tests
# =============================================================================
#
# Testing webentities creation and updates.
#
from collections import defaultdict
from test.test_cases import TraphTestCase


def gather_webentities_from_traph(traph):
    webentities = defaultdict(list)

    for node, lru in traph.webentity_prefix_iter():
        webentities[node.webentity()].append(lru)

    return webentities


def compare_webentities(actual, expected):
    if len(actual) != len(expected):
        return False

    for key in expected:
        if key not in actual:
            return False

        if len(expected[key]) != len(actual[key]):
            return False

        if set(expected[key]) != set(actual[key]):
            return False

    return True


class TestWebentities(TraphTestCase):

    def assertWebentities(self, traph, expected):
        return self.assertTrue(compare_webentities(
            gather_webentities_from_traph(traph),
            expected
        ))

    def test_webentities(self):
        traph = self.get_traph()
        webentities = {}

        '''
        Step 1 - Create a "Boeing" webentity with the 4 prefix variations (WWW and HTTPS cases).
        Expected: Creates the entity with the 4 prefixes. This is the typical use case.
        '''
        boeing_prefixes = [
            's:http|h:com|h:boeing|',
            's:http|h:com|h:boeing|h:www|',
            's:https|h:com|h:boeing|',
            's:https|h:com|h:boeing|h:www|'
        ]

        report = traph.create_webentity(boeing_prefixes)
        webentities.update(report.created_webentities)

        self.assertWebentities(traph, {
            1: [
                's:http|h:com|h:boeing|',
                's:http|h:com|h:boeing|h:www|',
                's:https|h:com|h:boeing|',
                's:https|h:com|h:boeing|h:www|'
            ]
        })

        traph.close()
