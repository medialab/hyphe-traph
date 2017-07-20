# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: Lorem ipsum and pokemons. Makes no sense.
# =============================================================================
#
# - This example is deterministic
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore
import random

SOURCE_PAGES = [
    's:http|h:com|h:bulbasaur|',
    's:http|h:com|h:charmander|',
    's:http|h:com|h:squirtle|',
    's:http|h:com|h:professor|p:augustine|p:sycamore|'
]

TARGET_PAGES = [
    's:http|h:com|h:sit|p:sit|',
    's:http|h:com|h:amet|p:hodor|',
    's:http|h:com|h:hodor|p:dolor|p:dolor|',
    's:http|h:com|h:amet|p:consectetur|p:ipsum|',
    's:http|h:com|h:amet|p:consectetur|p:consectetur|',
    's:http|h:com|h:hodor|p:dolor|',
    's:http|h:com|h:ipsum|p:dolor|p:lorem|p:amet|',
    's:http|h:com|h:lorem|p:sit|p:hodor|p:lorem|',
    's:http|h:com|h:lorem|p:dolor|p:consectetur|p:consectetur|',
    's:http|h:com|h:hodor|p:amet|p:dolor|p:amet|',
    's:http|h:com|h:consectetur|p:ipsum|',
    's:http|h:com|h:amet|p:dolor|p:dolor|p:ipsum|',
    's:http|h:com|h:lorem|p:sit|p:hodor|p:consectetur|',
    's:http|h:com|h:consectetur|p:consectetur|p:dolor|p:hodor|',
    's:http|h:com|h:lorem|p:consectetur|p:hodor|',
    's:http|h:com|h:sit|p:consectetur|p:ipsum|p:hodor|',
    's:http|h:com|h:consectetur|p:sit|',
    's:http|h:com|h:lorem|p:amet|p:dolor|',
    's:http|h:com|h:dolor|p:sit|p:sit|',
    's:http|h:com|h:amet|p:ipsum|p:hodor|p:lorem|',
    's:http|h:com|h:dolor|p:amet|p:sit|p:lorem|',
    's:http|h:com|h:dolor|p:ipsum|',
    's:http|h:com|h:sit|p:sit|',
    's:http|h:com|h:lorem|p:amet|p:dolor|',
    's:http|h:com|h:sit|p:consectetur|',
    's:http|h:com|h:lorem|p:consectetur|p:dolor|p:sit|',
    's:http|h:com|h:consectetur|p:amet|p:amet|p:sit|',
    's:http|h:com|h:ipsum|p:consectetur|p:dolor|p:hodor|',
    's:http|h:com|h:dolor|p:consectetur|',
    's:http|h:com|h:sit|p:lorem|p:hodor|',
    's:http|h:com|h:lorem|p:sit|',
    's:http|h:com|h:sit|p:lorem|p:dolor|p:sit|',
    's:http|h:com|h:sit|p:hodor|',
    's:http|h:com|h:dolor|p:dolor|p:hodor|',
    's:http|h:com|h:ipsum|p:dolor|p:hodor|p:sit|',
    's:http|h:com|h:lorem|p:ipsum|p:ipsum|p:dolor|',
    's:http|h:com|h:sit|p:ipsum|p:hodor|',
    's:http|h:com|h:lorem|p:dolor|',
    's:http|h:com|h:ipsum|p:sit|p:consectetur|',
    's:http|h:com|h:sit|p:lorem|',
    's:http|h:com|h:lorem|p:lorem|p:dolor|p:lorem|',
    's:http|h:com|h:dolor|p:ipsum|',
    's:http|h:com|h:sit|p:dolor|p:consectetur|',
    's:http|h:com|h:consectetur|p:amet|p:dolor|',
    's:http|h:com|h:consectetur|p:amet|',
    's:http|h:com|h:consectetur|p:consectetur|p:hodor|p:hodor|',
    's:http|h:com|h:consectetur|p:sit|',
    's:http|h:com|h:lorem|p:amet|',
    's:http|h:com|h:hodor|p:lorem|',
    's:http|h:com|h:dolor|p:dolor|p:amet|',
    's:http|h:com|h:amet|p:amet|',
    's:http|h:com|h:sit|p:amet|',
    's:http|h:com|h:hodor|p:consectetur|p:amet|',
    's:http|h:com|h:hodor|p:lorem|p:ipsum|',
    's:http|h:com|h:lorem|p:consectetur|p:hodor|',
    's:http|h:com|h:hodor|p:hodor|',
    's:http|h:com|h:dolor|p:dolor|p:hodor|',
    's:http|h:com|h:sit|p:ipsum|p:sit|p:ipsum|',
    's:http|h:com|h:amet|p:dolor|',
    's:http|h:com|h:dolor|p:hodor|p:consectetur|p:amet|',
    's:http|h:com|h:consectetur|p:lorem|',
    's:http|h:com|h:hodor|p:hodor|p:amet|p:sit|',
    's:http|h:com|h:dolor|p:amet|',
    's:http|h:com|h:amet|p:consectetur|p:amet|',
    's:http|h:com|h:consectetur|p:sit|p:sit|p:consectetur|',
    's:http|h:com|h:lorem|p:ipsum|p:dolor|p:amet|',
    's:http|h:com|h:lorem|p:ipsum|p:sit|',
    's:http|h:com|h:dolor|p:dolor|p:lorem|',
    's:http|h:com|h:hodor|p:consectetur|',
    's:http|h:com|h:hodor|p:consectetur|',
    's:http|h:com|h:hodor|p:sit|p:ipsum|',
    's:http|h:com|h:amet|p:dolor|p:sit|',
    's:http|h:com|h:amet|p:dolor|p:sit|',
    's:http|h:com|h:hodor|p:hodor|p:amet|p:consectetur|',
    's:http|h:com|h:sit|p:sit|',
    's:http|h:com|h:consectetur|p:consectetur|p:lorem|',
    's:http|h:com|h:amet|p:ipsum|p:dolor|',
    's:http|h:com|h:sit|p:hodor|p:sit|p:hodor|',
    's:http|h:com|h:ipsum|p:hodor|',
    's:http|h:com|h:dolor|p:sit|',
    's:http|h:com|h:sit|p:lorem|p:consectetur|',
    's:http|h:com|h:ipsum|p:sit|',
    's:http|h:com|h:consectetur|p:consectetur|p:hodor|p:hodor|',
    's:http|h:com|h:ipsum|p:consectetur|p:hodor|p:consectetur|',
    's:http|h:com|h:hodor|p:dolor|p:dolor|',
    's:http|h:com|h:ipsum|p:ipsum|p:dolor|',
    's:http|h:com|h:lorem|p:lorem|p:lorem|p:dolor|',
    's:http|h:com|h:ipsum|p:lorem|p:amet|',
    's:http|h:com|h:sit|p:hodor|',
    's:http|h:com|h:ipsum|p:hodor|p:sit|p:sit|',
    's:http|h:com|h:ipsum|p:hodor|p:ipsum|p:consectetur|',
    's:http|h:com|h:ipsum|p:amet|',
    's:http|h:com|h:ipsum|p:dolor|p:sit|',
    's:http|h:com|h:lorem|p:consectetur|p:lorem|p:amet|',
    's:http|h:com|h:dolor|p:amet|p:lorem|p:dolor|',
    's:http|h:com|h:sit|p:amet|',
    's:http|h:com|h:amet|p:dolor|p:sit|',
    's:http|h:com|h:sit|p:amet|p:consectetur|',
    's:http|h:com|h:consectetur|p:dolor|',
    's:http|h:com|h:dolor|p:ipsum|'
]

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

print '\n:: Simulate a crawl:'
print ' - Create webentity for "s:http|h:com|h:professor|p:augustine|p:sycamore|"'
professor_prefixes = [
    's:http|h:com|h:professor|p:augustine|p:sycamore|',
    's:http|h:com|h:professor|h:www|p:augustine|p:sycamore|',
    's:https|h:com|h:professor|p:augustine|p:sycamore|',
    's:https|h:com|h:professor|h:www|p:augustine|p:sycamore|'
]
report = traph.create_webentity(professor_prefixes)
webentity_store.data['webentities'].update(report.created_webentities)

print ' - Simulate page crawls with links to the list of target pages'

use_index_batch_crawl=True

if use_index_batch_crawl:
    data = {}
    for i in range(len(SOURCE_PAGES)):
        lru = SOURCE_PAGES[i]

        # build links
        links = []
        for j in range(len(TARGET_PAGES)):
            if j%4 == i:
                links.append(TARGET_PAGES[j])

        data[lru] = links
    report = traph.index_batch_crawl(data)
    webentity_store.data['webentities'].update(report.created_webentities)

else:
    for i in range(len(SOURCE_PAGES)):
        lru = SOURCE_PAGES[i]

        # add page
        report = traph.add_page(lru)
        webentity_store.data['webentities'].update(report.created_webentities)

        # build links
        links = []
        for j in range(len(TARGET_PAGES)):
            if j%4 == i:
                links.append([lru, TARGET_PAGES[j]])
        
        # add links
        links_report = traph.add_links(links)
        webentity_store.data['webentities'].update(links_report.created_webentities)


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

print '\n:: Traph: LRU trie'
print traph.lru_trie.representation()

print '\n:: Breakdown by webentity'
for weid in webentities:
    print '\nWebentity %s' % (weid)

    we_prefixes = webentity_store.data['webentities'][weid]
    print ' - %s prefixes (store)' % (len(we_prefixes))

    for prefix in we_prefixes:
        print ' \t- %s' % (prefix)

    we_pages = traph.get_webentity_pages(weid, we_prefixes)
    print ' - %s pages (traph)' % (len(we_pages))

    for lru in we_pages:
        print ' \t- %s' % (lru)

    we_crawled_pages = traph.get_webentity_crawled_pages(weid, we_prefixes)
    print ' - %s crawled pages (traph)' % (len(we_crawled_pages))

    for lru in we_crawled_pages:
        print ' \t- %s' % (lru)

    we_most_linked_pages = traph.get_webentity_most_linked_pages(weid, we_prefixes, 3)
    print ' - %s most linked pages (traph, max 3)' % (len(we_most_linked_pages))

    for lru in we_most_linked_pages:
        print ' \t- %s' % (lru)

    internal_pagelinks = traph.get_webentity_pagelinks(weid, we_prefixes)
    print ' - %s internal page links (traph)' % (len(internal_pagelinks))

    for source_lru, target_lru, weight in internal_pagelinks:
        print ' \t- weight %s: %s  \t->  \t%s' % (weight, source_lru, target_lru)

    inbound_pagelinks = traph.get_webentity_pagelinks(weid, we_prefixes, include_inbound=True, include_internal=False, include_outbound=False)
    print ' - %s inbound page links (traph)' % (len(inbound_pagelinks))

    for source_lru, target_lru, weight in inbound_pagelinks:
        print ' \t- weight %s: %s  \t->  \t%s' % (weight, source_lru, target_lru)

    outbound_pagelinks = traph.get_webentity_pagelinks(weid, we_prefixes, include_inbound=False, include_internal=False, include_outbound=True)
    print ' - %s outbound page links (traph)' % (len(outbound_pagelinks))

    for source_lru, target_lru, weight in outbound_pagelinks:
        print ' \t- weight %s: %s  \t->  \t%s' % (weight, source_lru, target_lru)


traph.close()
