# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: Lorem ipsum based random entities
# =============================================================================
#
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore
import random
import time

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})',
}

print 'Default creation rule: subdomain'
default_webentity_creation_rule = webentity_creation_rules_regexp['subdomain']

print 'Custom creation rules: "Hodor" is path-2 platform and "Lorem Ipsum" is path-1 platform'
webentity_creation_rules = {
    's:http|h:com|h:hodor|': webentity_creation_rules_regexp['path2'],    
    's:http|h:com|h:lorem|h:ipsum|': webentity_creation_rules_regexp['path1'],    
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

# LRU generation process
def random_lru(voc, domain_sizes, path_sizes):
    host_size = random.choice(domain_sizes)
    path_size = random.choice(path_sizes)
    protocol = 's:http|'
    tld = 'h:com|'
    host = ''
    for h in range(host_size):
        host += 'h:%s|' % (random.choice(voc))
    path = ''
    for p in range(path_size):
        path += 'p:%s|' % (random.choice(voc))
    return protocol + tld + host + path

voc = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'hodor', 'consectetur']
path_sizes = [1,2,3,4,5]
domain_sizes = [1,2,3]
links_per_page = [0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,5,5,5,5,6,6,6,7,7,7,8,8,9,10,16,25,75]

# Generate random pages
pages_count = 100000
crawled_pages = set()
for i in range(pages_count):
    lru = random_lru(voc, domain_sizes, path_sizes)
    crawled_pages.add(lru)

print '\n:: %s pages generated. Generate and add links...' % (len(crawled_pages))
add_links_start = time.time()
links_count = 0
for lru in crawled_pages:
    report = traph.add_page(lru)
    webentity_store.data['webentities'].update(report.created_webentities)
    
    link_count = random.choice(links_per_page)
    target_pages = set()
    for i in range(link_count):
        target_pages.add(random_lru(voc, domain_sizes, path_sizes))
    links = []
    for target_lru in target_pages:
        links.append([lru, target_lru])
    links_report = traph.add_links(links)
    webentity_store.data['webentities'].update(links_report.created_webentities)
    links_count += len(links)

    # print '%s links for \t%s' % (len(links), lru)

add_links_duration = time.time() - add_links_start
print '\t...%s page links added in %s ms' % (format(links_count, ',.0f'), format(1000*add_links_duration, ',.0f') )

print '\n:: Stats'
print ' - %s webentities (from Store)' % (format(len(webentity_store.data['webentities']), ',.0f'))

print '\n:: Get network...'
get_network_start = time.time()
webentities_network = traph.get_webentities_links()
get_network_duration = time.time() - get_network_start
webentity_links_count = 0
for source, targets in webentities_network.items():
    webentity_links_count += len(targets)
print '\t...%s webentity links obtained in %s ms' % (format(webentity_links_count, ',.0f'), format(1000*get_network_duration, ',.0f') )

# print '\n:: Breakdown by webentity'
# webentities = set()
# for node, lru in traph.webentity_prefix_iter():
#     webentities.add(node.webentity())
# for weid in webentities:
#     print '\nWebentity %s' % (weid)

#     we_prefixes = webentity_store.data['webentities'][weid]
#     print ' - %s prefixes (store)' % (len(we_prefixes))

#     for prefix in we_prefixes:
#         print ' \t- %s' % (prefix)

#     we_pages = traph.get_webentity_pages(weid, we_prefixes)
#     print ' - %s pages (traph)' % (len(we_pages))

#     for lru in we_pages:
#         print ' \t- %s' % (lru)

#     we_crawled_pages = traph.get_webentity_crawled_pages(weid, we_prefixes)
#     print ' - %s crawled pages (traph)' % (len(we_crawled_pages))

#     for lru in we_crawled_pages:
#         print ' \t- %s' % (lru)

#     we_most_linked_pages = traph.get_webentity_most_linked_pages(weid, we_prefixes, 3)
#     print ' - %s most linked pages (traph, max 3)' % (len(we_most_linked_pages))

#     for lru in we_most_linked_pages:
#         print ' \t- %s' % (lru)

#     pagelinks = traph.get_webentity_pagelinks(weid, we_prefixes)
#     print ' - %s page links (traph, excluding internal)' % (len(pagelinks))

#     for source_lru, target_lru, weight in pagelinks:
#         print ' \t- weight %s: %s  \t->  \t%s' % (weight, source_lru, target_lru)


traph.close()
