# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: known websites
# =============================================================================
#
# - No links in this example
# - Remarkably, also no pages!
# - Webentities definitions only
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})',
}

default_webentity_creation_rule = webentity_creation_rules_regexp['domain']

webentity_creation_rules = {}

# Webentity store is necessary to keep track of web entities' prefixes.
# Though the traph could retrieve them, it would not be efficient.
# In a real situation, these would be tracked elsewhere.
# That's what we are simulating with this store.
webentity_store = WebEntityStore('./scripts/data/webentities.json')
webentity_store.data['webentities'] = {}

# Instanciate the traph
traph = Traph(overwrite=True, folder='./scripts/data/',
              default_webentity_creation_rule=default_webentity_creation_rule,
              webentity_creation_rules=webentity_creation_rules)

print '\n:: Setup'

print '- Create a "Twitter" webentity with the 4 prefix variations (WWW and HTTPS cases)'
twitter_prefixes = [
    's:http|h:com|h:twitter|',
    's:http|h:com|h:twitter|h:www|',
    's:https|h:com|h:twitter|',
    's:https|h:com|h:twitter|h:www|'
]
report = traph.create_webentity(twitter_prefixes)
webentity_store.data['webentities'].update(report.created_webentities)
twitter_weid = report.created_webentities.keys()[0] # Used below

print '- Create a "Ego" webentity with ego.com (4 prefixes) as well as a Twitter account (additional 4 prefixes)'
ego_prefixes = [
    's:http|h:com|h:ego|',
    's:http|h:com|h:ego|h:www|',
    's:https|h:com|h:ego|',
    's:https|h:com|h:ego|h:www|',
    's:http|h:com|h:twitter|p:ego',
    's:http|h:com|h:twitter|h:www|p:ego',
    's:https|h:com|h:twitter|p:ego',
    's:https|h:com|h:twitter|h:www|p:ego'
]
report = traph.create_webentity(ego_prefixes)
webentity_store.data['webentities'].update(report.created_webentities)
ego_weid = report.created_webentities.keys()[0] # Used below

print '- Create a "Cheese" webentity with cheese.ego.com, Tweets about cheese  and cheese.fr (12 prefixes)'
cheese_prefixes = [
    's:http|h:fr|h:cheese|',
    's:http|h:fr|h:cheese|h:www|',
    's:https|h:fr|h:cheese|',
    's:https|h:fr|h:cheese|h:www|',
    's:http|h:com|h:ego|h:cheese',
    's:http|h:com|h:ego|h:www|h:cheese',
    's:https|h:com|h:ego|h:cheese',
    's:https|h:com|h:ego|h:www|h:cheese',
    's:http|h:com|h:twitter|p:ego|q:cheese',
    's:http|h:com|h:twitter|h:www|p:ego|q:cheese',
    's:https|h:com|h:twitter|p:ego|q:cheese',
    's:https|h:com|h:twitter|h:www|p:ego|q:cheese'
]
report = traph.create_webentity(cheese_prefixes)
webentity_store.data['webentities'].update(report.created_webentities)
cheese_weid = report.created_webentities.keys()[0] # Used below

print '\n:: Stats'
print '- %s webentities in the Store' % (len(webentity_store.data['webentities']))
webentities = set()
for node, lru in traph.webentity_prefix_iter():
    webentities.add(node.webentity())
print '- %s webentities in the Traph' % (len(webentities))
pages = []
for node, lru in traph.lru_trie.dfs_iter():
    if node.is_page():
        pages.append(lru)
print '- %s pages in the Traph' % (len(pages))


print '\n:: Results - Breakdown by webentity'
for weid in webentities:
    print '\nWebentity %s' % (weid)
    we_prefixes = webentity_store.data['webentities'][weid]
    print ' - %s prefixes (store)' % (len(we_prefixes))
    for prefix in we_prefixes:
        print ' \t- %s' % (prefix)
    parent_webentities = traph.get_webentity_parent_webentities(weid, we_prefixes)
    print ' - %s parent webentities (traph)' % (len(parent_webentities))
    for parent_weid in parent_webentities:
        print ' \t- webentity %s' % (parent_weid)


traph.close()
