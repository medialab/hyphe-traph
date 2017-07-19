# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: famous websites
# =============================================================================
#
# - No links in this example
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

# Step 1
print '\n:: Step 1 - Create a "Boeing" webentity with the 4 prefix variations (WWW and HTTPS cases).'
print 'Expected: Creates the entity with the 4 prefixes. This is the typical use case.'

boeing_prefixes = [
    's:http|h:com|h:boeing|',
    's:http|h:com|h:boeing|h:www|',
    's:https|h:com|h:boeing|',
    's:https|h:com|h:boeing|h:www|'
]
report = traph.create_webentity(boeing_prefixes)
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult - Existing webentities:'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s:' % (weid)
    for prefix in prefixes:
        print '\t\t' + prefix


traph.close()
