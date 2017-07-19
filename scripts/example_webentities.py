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
boeing_weid = report.created_webentities.keys()[0] # Used for a step below

print '\nResult - Existing webentities:'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s:' % (weid)
    for prefix in prefixes:
        print '\t\t' + prefix

# Step 2
print '\n:: Step 2 - Create a "Airbus HTTPS" webentity with only 2 prefix variations (WWW case).'
print 'Expected: Creates the entity with the 2 prefixes.'

airbus_prefixes = [
    's:https|h:com|h:airbus|',
    's:https|h:com|h:airbus|h:www|'
]
report = traph.create_webentity(airbus_prefixes)
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult - Existing webentities:'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s:' % (weid)
    for prefix in prefixes:
        print '\t\t' + prefix

# Step 3
print '\n:: Step 3 - Remove the "Boeing" webentity'
print 'Expected: Only Airbus remains'

traph.delete_webentity(boeing_weid, webentity_store.data['webentities'][boeing_weid])
del webentity_store.data['webentities'][boeing_weid]

print '\nResult - Existing webentities:'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s:' % (weid)
    for prefix in prefixes:
        print '\t\t' + prefix

# Step 4
print '\n:: Step 4 - Add the "Airbus/blog" page'
print 'Expected: Create the NON-HTTPS Airbus webentity'

report = traph.add_page('s:http|h:com|h:airbus|p:blog|')
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult - Existing webentities:'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s:' % (weid)
    for prefix in prefixes:
        print '\t\t' + prefix


traph.close()
