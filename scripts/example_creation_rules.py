# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: websites similar to localities
# =============================================================================
#
# - No links in this example
# - The LRUs follow this kind of pattern: continent/country/city
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
print('\n"Continents" rule given at traph init (continents should be entities)')
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

# Step 1
print('\n:: Step 1: Add the "Madrid" page')
print('Expected: "Europe" webentity created (matching the rule given at init), "World" not created')

report = traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:madrid|')
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 2
print('\n:: Step 2: Remove the "Continents" rule and add the "Tokyo" page')
print('Expected: "World" webentity created, "Asia" not created')

traph.remove_webentity_creation_rule('s:http|h:com|h:world|')
report = traph.add_page('s:http|h:com|h:world|p:asia|p:japan|p:tokyo|')
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 3
print('\n:: Step 3: Add the "Spanish City" rule')
print('Expected: "Madrid" webentity created')

report = traph.add_webentity_creation_rule('s:http|h:com|h:world|p:europe|p:spain|', webentity_creation_rules_regexp['path3'])
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 4
print('\n:: Step 4: Add the "Country" rule')
print('Expected: "Japan" should be created, but not "Spain", since the "Madrid" page')
print('          already is in a more precise web entity ("Madrid" too).')

report = traph.add_webentity_creation_rule('s:http|h:com|h:world|', webentity_creation_rules_regexp['path2'])
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 5
print('\n:: Step 5: Add the "Paris" page')
print('Expected: Create "France" (by the "Country" rule)')

report = traph.add_page('s:http|h:com|h:world|p:europe|p:france|p:paris|')
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

print('\nResult - Existing pages:')
for node, lru in traph.pages_iter():
    print(' - '+lru)

# Step 6
print('\n:: Step 6: Remove the "Country" rule and add the "City" rule')
print('Expected: Create "Paris" and "Tokyo" ("Madrid" already exists)')

traph.remove_webentity_creation_rule('s:http|h:com|h:world|')
report = traph.add_webentity_creation_rule('s:http|h:com|h:world|', webentity_creation_rules_regexp['path3'])
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 7
print('\n:: Step 7: Add the "European Country" rule')
print('Expected: No entity should be created since all pages are in smaller')
print('          webentities (cities). "Spain" still does not exist.')

report = traph.add_webentity_creation_rule('s:http|h:com|h:world|p:europe|', webentity_creation_rules_regexp['path2'])
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 8
print('\n:: Step 8: Add the "Berlin" page')
print('Expected: The "Berlin" webentity is created. Note that the "European Country" rule is defined')
print('          at a lower level (continent) that the "City" rule (world level), but both rules should')
print('          be evaluated and the "European Country" rule creates a higher level level prefix')
print('          (country) than the "City" rule, so the "City" rule should prevail.')

report = traph.add_page('s:http|h:com|h:world|p:europe|p:germany|p:berlin|')
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# Step 9
print('\n:: Step 9: Add the "Barcelona" page')
print('Expected: The "Barcelona" webentity is created. We currently have two rules doing the same')
print('          thing: "City" rule and "Spanish City" rule. "Barcelona" should be created only once.')

report = traph.add_page('s:http|h:com|h:world|p:europe|p:spain|p:barcelona|')
webentity_store.data['webentities'].update(report.created_webentities)

print('\nResult - Existing webentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

print('\nResult - Existing pages:')
for node, lru in traph.pages_iter():
    print(' - '+lru)

traph.close()
