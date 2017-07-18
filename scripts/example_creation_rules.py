# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: websites similar to localities
# =============================================================================
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})',
    'path3':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){3})',
    'path4':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){4})'
}

default_webentity_creation_rule = webentity_creation_rules_regexp['domain']

# Instanciate traph with a custom rule: split after 'world' (continents)
print '\n"Continents" rule given at traph init (continents should be entities)'
webentity_creation_rules = {
    's:http|h:com|h:world|': webentity_creation_rules_regexp['path1'],
}

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

# Operation 1
print '\n:: Operation 1: Add the "Madrid" page, matching the rule given at traph init'
print 'Expected: "Europe" webentity created, "World" not created'

report = traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult: existing webentities'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1)

# Operation 2
print '\n:: Operation 2: Remove the "Continents" rule and add the "Tokyo" page'
print 'Expected: "World" webentity created, "Asia" not created'

traph.remove_webentity_creation_rule('s:http|h:com|h:world|')
report = traph.add_page('s:http|h:com|h:world|p:asia|p:japan|p:tokyo|')
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult: existing webentities'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1)

# Operation 3
print '\n:: Operation 3: Add the "Spanish City" rule'
print 'Expected: "Madrid" webentity created'

report = traph.add_webentity_creation_rule('s:http|h:com|h:world|p:europe|p:spain|', webentity_creation_rules_regexp['path3'])
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult: existing webentities'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1)

# Operation 4
print '\n:: Operation 4: Add the "Country" rule'
print 'Expected: "Japan" should not be created, but not "Spain", since the "Madrid" page'
print '          already is in a more precise web entity ("Madrid" too).'

report = traph.add_webentity_creation_rule('s:http|h:com|h:world|', webentity_creation_rules_regexp['path2'])
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult: existing webentities'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1)

# # Operation 5
print '\n:: Operation 5: Add the "Paris" page'
print 'Expected: Create "France" by the "Country" rule'

report = traph.add_page('s:http|h:com|h:world|p:europe|p:france|p:paris|')
webentity_store.data['webentities'].update(report.created_webentities)

print '\nResult: existing webentities'
for weid, prefixes in webentity_store.data['webentities'].items():
    print ' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1) 

traph.close()
