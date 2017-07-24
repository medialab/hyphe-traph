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
            1: boeing_prefixes
        })
        self.assertWebentities(traph, webentities)

        '''
        Step 2 - Create a "Airbus HTTPS" webentity with only 2 prefix variations (WWW case).
        Expected: Creates the entity with the 2 prefixes.
        '''
        airbus_https_prefixes = [
            's:https|h:com|h:airbus|',
            's:https|h:com|h:airbus|h:www|'
        ]

        airbus_http_prefixes = [
            's:http|h:com|h:airbus|',
            's:http|h:com|h:airbus|h:www|'
        ]

        report = traph.create_webentity(airbus_https_prefixes)
        webentities.update(report.created_webentities)

        self.assertWebentities(traph, {
            1: boeing_prefixes,
            2: airbus_https_prefixes
        })
        self.assertWebentities(traph, webentities)

        '''
        Step 3 - Remove the "Boeing" webentity
        Expected: Only Airbus remains
        '''
        traph.delete_webentity(1, webentities[1])
        del webentities[1]

        self.assertWebentities(traph, {
            2: airbus_https_prefixes
        })
        self.assertWebentities(traph, webentities)

        '''
        Step 4 - Add the "Airbus/blog" page
        Expected: Create the NON-HTTPS Airbus webentity
        '''
        report = traph.add_page('s:http|h:com|h:airbus|p:blog|')
        webentities.update(report.created_webentities)

        self.assertWebentities(traph, {
            2: airbus_https_prefixes,
            3: airbus_http_prefixes
        })
        self.assertWebentities(traph, webentities)

        webentity = traph.retrieve_webentity('s:http|h:com|h:airbus|p:blog|')
        prefix = traph.retrieve_prefix('s:http|h:com|h:airbus|p:blog|')

        self.assertEqual(webentity, 3)
        self.assertEqual(prefix, 's:http|h:com|h:airbus|')

        '''
        Step 5 - Move the NON-HTTPS prefixes to the HTTPS Airbus entity
        Expected: A single Airbus webentity
        '''
        for prefix in airbus_http_prefixes:
            traph.move_prefix_to_webentity(prefix, 2)

        del webentities[3]
        webentities[2].extend(airbus_http_prefixes)

        self.assertWebentities(traph, {
            2: airbus_https_prefixes + airbus_http_prefixes
        })
        self.assertWebentities(traph, webentities)

        webentity = traph.retrieve_webentity('s:http|h:com|h:airbus|p:blog|')
        prefix = traph.retrieve_prefix('s:http|h:com|h:airbus|p:blog|')

        self.assertEqual(webentity, 2)
        self.assertEqual(prefix, 's:http|h:com|h:airbus|')

        traph.close()
