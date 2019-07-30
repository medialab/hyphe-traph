# =============================================================================
# Twitter Family Unit Tests
# =============================================================================
#
# Simple use cases representing a family through Twitter accounts. Here we are
# just testing page & link addition as well as basic webentity creation.
#
from collections import defaultdict
from test.test_cases import TraphTestCase
from test.helpers import webentity_label_from_prefixes, legible_network

# TODO: reinstate unit tests with significantother full length!

PAGES = [
    's:http|h:com|h:twitter|p:daughter|',
    's:http|h:com|h:twitter|p:son|',
    's:http|h:com|h:twitter|p:niece|',
    's:http|h:com|h:twitter|p:nephew|',
    's:http|h:com|h:twitter|p:significantother|',
    's:http|h:com|h:twitter|p:ego|',
    's:http|h:com|h:twitter|p:sister|',
    's:http|h:com|h:twitter|p:cousin|',
    's:http|h:com|h:twitter|p:brotherinlaw|',
    's:http|h:com|h:twitter|p:brother|',
    's:http|h:com|h:twitter|p:dad|',
    's:http|h:com|h:twitter|p:mom|',
    's:http|h:com|h:twitter|p:uncle|',
    's:http|h:com|h:twitter|p:aunt|',
    's:http|h:com|h:twitter|p:grandpa|',
    's:http|h:com|h:twitter|p:grandma|'
]

LINKS = [
    ('s:http|h:com|h:twitter|p:daughter|', 's:http|h:com|h:twitter|p:ego|'),
    ('s:http|h:com|h:twitter|p:daughter|', 's:http|h:com|h:twitter|p:significantother|'),
    ('s:http|h:com|h:twitter|p:son|', 's:http|h:com|h:twitter|p:ego|'),
    ('s:http|h:com|h:twitter|p:son|', 's:http|h:com|h:twitter|p:significantother|'),
    ('s:http|h:com|h:twitter|p:niece|', 's:http|h:com|h:twitter|p:sister|'),
    ('s:http|h:com|h:twitter|p:niece|', 's:http|h:com|h:twitter|p:brotherinlaw|'),
    ('s:http|h:com|h:twitter|p:nephew|', 's:http|h:com|h:twitter|p:sister|'),
    ('s:http|h:com|h:twitter|p:nephew|', 's:http|h:com|h:twitter|p:brotherinlaw|'),
    ('s:http|h:com|h:twitter|p:ego|', 's:http|h:com|h:twitter|p:mom|'),
    ('s:http|h:com|h:twitter|p:ego|', 's:http|h:com|h:twitter|p:dad|'),
    ('s:http|h:com|h:twitter|p:brother|', 's:http|h:com|h:twitter|p:mom|'),
    ('s:http|h:com|h:twitter|p:brother|', 's:http|h:com|h:twitter|p:dad|'),
    ('s:http|h:com|h:twitter|p:sister|', 's:http|h:com|h:twitter|p:mom|'),
    ('s:http|h:com|h:twitter|p:sister|', 's:http|h:com|h:twitter|p:dad|'),
    ('s:http|h:com|h:twitter|p:cousin|', 's:http|h:com|h:twitter|p:aunt|'),
    ('s:http|h:com|h:twitter|p:mom|', 's:http|h:com|h:twitter|p:grandpa|'),
    ('s:http|h:com|h:twitter|p:mom|', 's:http|h:com|h:twitter|p:grandma|'),
    ('s:http|h:com|h:twitter|p:uncle|', 's:http|h:com|h:twitter|p:grandpa|'),
    ('s:http|h:com|h:twitter|p:uncle|', 's:http|h:com|h:twitter|p:grandma|'),
    ('s:http|h:com|h:twitter|p:aunt|', 's:http|h:com|h:twitter|p:grandpa|'),
    ('s:http|h:com|h:twitter|p:aunt|', 's:http|h:com|h:twitter|p:grandma|')
]

NETWORK = defaultdict(list)

for source, target in LINKS:
    NETWORK[source].append(target)


class TestTwitterFamily(TraphTestCase):

    def test_twitter_family(self):
        traph = self.get_traph()
        webentities = {}

        # Inserting pages
        for page in PAGES:
            report = traph.add_page(page)
            for weid, prefixes in report.created_webentities.items():
                webentities[weid] = webentity_label_from_prefixes(prefixes)

        self.assertEqual(len(webentities), 16)

        # Inserting links
        traph.add_links(LINKS)

        # Pages
        pages_in_traph = set(lru for _, lru in traph.pages_iter())

        self.assertEqual(pages_in_traph, set(PAGES))

        # Links
        links_in_traph = set(link for link in traph.links_iter())

        self.assertEqual(links_in_traph, set(LINKS))

        # Network
        network = traph.get_webentities_links()
        legible = legible_network(webentities, network)

        self.assertEqual(sum(len(targets) for targets in legible.values()), 21)
        self.assertEqual(len(legible), len(NETWORK))

        for source, targets in legible.items():
            self.assertTrue(source in NETWORK)
            self.assertEqual(set(targets), set(NETWORK[source]))

        for source, targets in network.items():
            for weight in targets.values():
                self.assertEqual(weight, 1)

        traph.close()
