# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: Lorem ipsum based random entities
# =============================================================================
#
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore
import random

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

# Generate random pages
pages_count = 100
print '\n:: Generate %s lorem-ipsum-based pages' % (pages_count)
voc = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'hodor', 'consectetur']
path_sizes = [1,2,3]
for i in range(pages_count):
    path_size = random.choice(path_sizes)
    protocol = 's:http|'
    tld = 'h:com|'
    host = 'h:%s|' % (random.choice(voc))
    path = ''
    for p in range(path_size):
        path += 'p:%s|' % (random.choice(voc))
    lru = protocol + tld + host + path
    # print lru
    report = traph.add_page(lru)
    webentity_store.data['webentities'].update(report.created_webentities)

print '\n:: Webentities'
print '\nExisting webentities from Store:'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s:' % (weid)
    for prefix in prefixes:
        print '\t\t' + prefix

print '\nPrefixes from Traph:'
for node, lru in traph.webentity_prefix_iter():
    print ' - (%s) \t%s' % (node.webentity(), lru)


traph.close()
