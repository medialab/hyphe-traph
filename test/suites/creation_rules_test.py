# =============================================================================
# Creation Rules Unit Tests
# =============================================================================
#
# Here we are testing advanced use cases related to webentity creation rules.
#
from test.test_cases import TraphTestCase
from test.config import WEBENTITY_CREATION_RULES_REGEXES
from test.helpers import webentity_label_from_prefixes

WEBENTITY_CREATION_RULES = {
    's:http|h:com|h:world|': WEBENTITY_CREATION_RULES_REGEXES['path1'],
}


def compare_webentities(actual, expected):
    webentities = set()

    for prefixes in actual.values():
        webentities.add(webentity_label_from_prefixes(prefixes))

    return webentities == set(expected)


class TestCreationRules(TraphTestCase):

    def assertWebentities(self, actual, expected):
        return self.assertTrue(compare_webentities(actual, expected))

    def test_creation_rules(self):
        traph = self.get_traph(webentity_creation_rules=WEBENTITY_CREATION_RULES)
        webentities = {}

        '''
        Step 1: Add the "Madrid" page
        Expected: "Europe" webentity created (matching the rule given at init), "World" not created
        '''
        report = traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|'
        ])

        '''
        Step 2: Remove the "Continents" rule and add the "Tokyo" page
        Expected: "World" webentity created, "Asia" not created
        '''
        traph.remove_webentity_creation_rule('s:http|h:com|h:world|')
        report = traph.add_page('s:http|h:com|h:world|p:asia|p:japan|p:tokyo|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|'
        ])

        '''
        Step 3: Add the "Spanish City" rule
        Expected: "Madrid" webentity created
        '''
        report = traph.add_webentity_creation_rule(
            's:http|h:com|h:world|p:europe|p:spain|',
            WEBENTITY_CREATION_RULES_REGEXES['path3']
        )
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|'
        ])

        '''
        Step 4: Add the "Country" rule
        Expected: "Japan" should be created, but not "Spain", since the "Madrid" page
        already is in a more precise web entity ("Madrid" too).
        '''
        report = traph.add_webentity_creation_rule(
            's:http|h:com|h:world|',
            WEBENTITY_CREATION_RULES_REGEXES['path2']
        )
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:asia|p:japan|'
        ])

        '''
        Step 5: Add the "Paris" page
        Expected: Create "France" (by the "Country" rule)
        '''
        report = traph.add_page('s:http|h:com|h:world|p:europe|p:france|p:paris|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:asia|p:japan|',
            's:http|h:com|h:world|p:europe|p:france|'
        ])

        '''
        Step 6: Remove the "Country" rule and add the "City" rule
        Expected: Create "Paris" and "Tokyo" ("Madrid" already exists)
        '''
        traph.remove_webentity_creation_rule('s:http|h:com|h:world|')
        report = traph.add_webentity_creation_rule(
            's:http|h:com|h:world|',
            WEBENTITY_CREATION_RULES_REGEXES['path3']
        )
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:asia|p:japan|',
            's:http|h:com|h:world|p:europe|p:france|',
            's:http|h:com|h:world|p:europe|p:france|p:paris|',
            's:http|h:com|h:world|p:asia|p:japan|p:tokyo|'
        ])

        '''
        Step 7: Add the "European Country" rule
        Expected: No entity should be created since all pages are in smaller
        webentities (cities). "Spain" still does not exist.
        '''
        report = traph.add_webentity_creation_rule(
            's:http|h:com|h:world|p:europe|',
            WEBENTITY_CREATION_RULES_REGEXES['path2']
        )
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:asia|p:japan|',
            's:http|h:com|h:world|p:europe|p:france|',
            's:http|h:com|h:world|p:europe|p:france|p:paris|',
            's:http|h:com|h:world|p:asia|p:japan|p:tokyo|'
        ])

        '''
        Step 8: Add the "Berlin" page
        Expected: The "Berlin" webentity is created. Note that the "European Country" rule is defined
        at a lower level (continent) that the "City" rule (world level), but both rules should
        be evaluated and the "European Country" rule creates a higher level level prefix
        (country) than the "City" rule, so the "City" rule should prevail.
        '''
        report = traph.add_page('s:http|h:com|h:world|p:europe|p:germany|p:berlin|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:asia|p:japan|',
            's:http|h:com|h:world|p:europe|p:france|',
            's:http|h:com|h:world|p:europe|p:france|p:paris|',
            's:http|h:com|h:world|p:asia|p:japan|p:tokyo|',
            's:http|h:com|h:world|p:europe|p:germany|p:berlin|'
        ])

        '''
        Step 9: Add the "Barcelona" page
        Expected: The "Barcelona" webentity is created. We currently have two rules doing the same
        thing: "City" rule and "Spanish City" rule. "Barcelona" should be created only once.
        '''
        report = traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|p:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:asia|p:japan|',
            's:http|h:com|h:world|p:europe|p:france|',
            's:http|h:com|h:world|p:europe|p:france|p:paris|',
            's:http|h:com|h:world|p:asia|p:japan|p:tokyo|',
            's:http|h:com|h:world|p:europe|p:germany|p:berlin|',
            's:http|h:com|h:world|p:europe|p:spain|p:barcelona|'
        ])

        # Testing the inserted pages
        pages_in_traph = set(lru for _, lru in traph.pages_iter())

        self.assertTrue(pages_in_traph == set([
            's:http|h:com|h:world|p:europe|p:spain|p:madrid|',
            's:http|h:com|h:world|p:europe|p:spain|p:barcelona|',
            's:http|h:com|h:world|p:europe|p:france|p:paris|',
            's:http|h:com|h:world|p:europe|p:germany|p:berlin|',
            's:http|h:com|h:world|p:asia|p:japan|p:tokyo|'
        ]))

        traph.close()
        self.tearDown()

        '''
        Step 10: Test a traph with the "subdomain" default creation rule
        Expected: Webentities are created at the subdomain level
        '''
        traph = self.get_traph(default_webentity_creation_rule=WEBENTITY_CREATION_RULES_REGEXES['subdomain'])
        webentities = {}
        report = traph.add_page('s:http|h:com|h:world|h:europe|p:spain|p:barcelona|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|h:europe|'
        ])

        # Testing the inserted pages
        pages_in_traph = set(lru for _, lru in traph.pages_iter())

        self.assertTrue(pages_in_traph == set([
            's:http|h:com|h:world|h:europe|p:spain|p:barcelona|'
        ]))

        report = traph.add_page('s:http|h:com|h:world|p:sea|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|h:europe|',
            's:http|h:com|h:world|'
        ])

        report = traph.add_page('s:http|h:com|h:world|h:asia|p:china|')
        webentities.update(report.created_webentities)

        self.assertWebentities(webentities, [
            's:http|h:com|h:world|h:europe|',
            's:http|h:com|h:world|',
            's:http|h:com|h:world|h:asia|'
        ])

        report = traph.index_batch_crawl({
            's:http|h:com|h:world|h:europe|p:neighbors|': [
                's:https|h:com|h:world|h:unitedkingdom|p:london|',
                's:http|h:com|h:world|h:oceania|p:australia|',
                's:http|h:com|h:world|p:sea|',
                's:https|h:com|h:world|',
                's:http|h:com|h:world|h:asia|p:russia|',
                's:https|h:com|h:world|h:africa|p:senegal|',
                's:http|h:com|h:world|h:africa|h:maghreb|p:morocco|'
            ]
        })

        self.assertTrue(report.nb_created_pages == 7)

        self.assertWebentities(report.created_webentities, [
            's:http|h:com|h:world|h:unitedkingdom|',
            's:http|h:com|h:world|h:oceania|',
            's:http|h:com|h:world|h:africa|',
            's:http|h:com|h:world|h:africa|h:maghreb|'
        ])

        traph.close()
