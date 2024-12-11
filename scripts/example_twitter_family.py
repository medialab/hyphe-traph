# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: a genealogic tree of twitter accounts
# =============================================================================
#
# - Twitter-like pages with family roles as ids
# - A single WE creation rule, for twitter
# - Links from children to parents
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

# Constants
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
    ['s:http|h:com|h:twitter|p:daughter|',  's:http|h:com|h:twitter|p:ego|'],
    ['s:http|h:com|h:twitter|p:daughter|',  's:http|h:com|h:twitter|p:significantother|'],
    ['s:http|h:com|h:twitter|p:son|',       's:http|h:com|h:twitter|p:ego|'],
    ['s:http|h:com|h:twitter|p:son|',       's:http|h:com|h:twitter|p:significantother|'],
    ['s:http|h:com|h:twitter|p:niece|',     's:http|h:com|h:twitter|p:sister|'],
    ['s:http|h:com|h:twitter|p:niece|',     's:http|h:com|h:twitter|p:brotherinlaw|'],
    ['s:http|h:com|h:twitter|p:nephew|',    's:http|h:com|h:twitter|p:sister|'],
    ['s:http|h:com|h:twitter|p:nephew|',    's:http|h:com|h:twitter|p:brotherinlaw|'],
    ['s:http|h:com|h:twitter|p:ego|',       's:http|h:com|h:twitter|p:mom|'],
    ['s:http|h:com|h:twitter|p:ego|',       's:http|h:com|h:twitter|p:dad|'],
    ['s:http|h:com|h:twitter|p:brother|',   's:http|h:com|h:twitter|p:mom|'],
    ['s:http|h:com|h:twitter|p:brother|',   's:http|h:com|h:twitter|p:dad|'],
    ['s:http|h:com|h:twitter|p:sister|',    's:http|h:com|h:twitter|p:mom|'],
    ['s:http|h:com|h:twitter|p:sister|',    's:http|h:com|h:twitter|p:dad|'],
    ['s:http|h:com|h:twitter|p:cousin|',    's:http|h:com|h:twitter|p:aunt|'],
    ['s:http|h:com|h:twitter|p:mom|',       's:http|h:com|h:twitter|p:grandpa|'],
    ['s:http|h:com|h:twitter|p:mom|',       's:http|h:com|h:twitter|p:grandma|'],
    ['s:http|h:com|h:twitter|p:uncle|',     's:http|h:com|h:twitter|p:grandpa|'],
    ['s:http|h:com|h:twitter|p:uncle|',     's:http|h:com|h:twitter|p:grandma|'],
    ['s:http|h:com|h:twitter|p:aunt|',      's:http|h:com|h:twitter|p:grandpa|'],
    ['s:http|h:com|h:twitter|p:aunt|',      's:http|h:com|h:twitter|p:grandma|']
]

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})'
}

default_webentity_creation_rule = webentity_creation_rules_regexp['domain']

webentity_creation_rules = {
    's:http|h:com|h:twitter|': webentity_creation_rules_regexp['path1'],
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

# Store data
print('Store pages...')
for page in PAGES:
    report = traph.add_page(page)
    webentity_store.data['webentities'].update(report.created_webentities)
    # print report

print('Store links...')
links_report = traph.add_links(LINKS)
webentity_store.data['webentities'].update(links_report.created_webentities)
# print links_report

print('...data stored.')

# Log result
print('\nPages:')
for node, lru in traph.pages_iter():
    print(' - '+lru)

print('\nPage Links:')
for source_lru, target_lru in traph.links_iter():
    print(' - %s\t->  %s' % (source_lru, target_lru))

print('\nWebentities:')
for weid, prefixes in list(webentity_store.data['webentities'].items()):
    print(' - Webentity %s\t%s + %s other prefixes' % (weid, prefixes[0], len(prefixes)-1))

# import networkx as nx

# g = nx.Graph()

# w = traph.get_webentities_links()

# for source, targets in w.items():
#     source_label = webentity_store.data['webentities'][source][1]
#     g.add_node(source, label=source_label)

#     for target in targets:
#         target_label = webentity_store.data['webentities'][target][1]
#         g.add_node(target, label=target_label)
#         g.add_edge(source, target)

# nx.write_gexf(g, './scripts/data/dump.gexf')

traph.close()
