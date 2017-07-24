# =============================================================================
# Unit Tests Endpoint
# =============================================================================
#
# Gathering the unit tests in order to run them.
#
from test.test_cases import TraphTestCase

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
    ('s:http|h:com|h:twitter|p:daughter|',  's:http|h:com|h:twitter|p:ego|'),
    ('s:http|h:com|h:twitter|p:daughter|',  's:http|h:com|h:twitter|p:significantother|'),
    ('s:http|h:com|h:twitter|p:son|',       's:http|h:com|h:twitter|p:ego|'),
    ('s:http|h:com|h:twitter|p:son|',       's:http|h:com|h:twitter|p:significantother|'),
    ('s:http|h:com|h:twitter|p:niece|',     's:http|h:com|h:twitter|p:sister|'),
    ('s:http|h:com|h:twitter|p:niece|',     's:http|h:com|h:twitter|p:brotherinlaw|'),
    ('s:http|h:com|h:twitter|p:nephew|',    's:http|h:com|h:twitter|p:sister|'),
    ('s:http|h:com|h:twitter|p:nephew|',    's:http|h:com|h:twitter|p:brotherinlaw|'),
    ('s:http|h:com|h:twitter|p:ego|',       's:http|h:com|h:twitter|p:mom|'),
    ('s:http|h:com|h:twitter|p:ego|',       's:http|h:com|h:twitter|p:dad|'),
    ('s:http|h:com|h:twitter|p:brother|',   's:http|h:com|h:twitter|p:mom|'),
    ('s:http|h:com|h:twitter|p:brother|',   's:http|h:com|h:twitter|p:dad|'),
    ('s:http|h:com|h:twitter|p:sister|',    's:http|h:com|h:twitter|p:mom|'),
    ('s:http|h:com|h:twitter|p:sister|',    's:http|h:com|h:twitter|p:dad|'),
    ('s:http|h:com|h:twitter|p:cousin|',    's:http|h:com|h:twitter|p:aunt|'),
    ('s:http|h:com|h:twitter|p:mom|',       's:http|h:com|h:twitter|p:grandpa|'),
    ('s:http|h:com|h:twitter|p:mom|',       's:http|h:com|h:twitter|p:grandma|'),
    ('s:http|h:com|h:twitter|p:uncle|',     's:http|h:com|h:twitter|p:grandpa|'),
    ('s:http|h:com|h:twitter|p:uncle|',     's:http|h:com|h:twitter|p:grandma|'),
    ('s:http|h:com|h:twitter|p:aunt|',      's:http|h:com|h:twitter|p:grandpa|'),
    ('s:http|h:com|h:twitter|p:aunt|',      's:http|h:com|h:twitter|p:grandma|')
]


class TestTwitterFamily(TraphTestCase):

    def test_twitter_family(self):
        traph = self.get_traph()
        webentities = {}

        # Inserting pages
        for page in PAGES:
            report = traph.add_page(page)
            webentities.update(report.created_webentities)

        self.assertEqual(len(webentities), 16)

        # Inserting links
        traph.add_links(LINKS)

        # Pages
        pages_in_traph = set(lru for _, lru in traph.pages_iter())

        self.assertTrue(pages_in_traph == set(PAGES))

        # Links
        links_in_traph = set(link for link in traph.links_iter())

        self.assertTrue(links_in_traph == set(LINKS))
