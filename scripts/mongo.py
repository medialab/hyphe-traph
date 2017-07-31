# =============================================================================
# Mongo Script
# =============================================================================
#
# Attempting to load a corpus from MongoDB
#
from collections import defaultdict
from traph import Traph
from pymongo import MongoClient
from config import CONFIG

MONGO = CONFIG['mongo']

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

# Creating the Traph
traph = Traph(overwrite=True, folder='./scripts/data/',
              default_webentity_creation_rule=default_webentity_creation_rule,
              webentity_creation_rules=webentity_creation_rules)

# Reading from mongo
client = MongoClient(MONGO['host'], MONGO['port'])
collection = client[MONGO['db']][MONGO['collection']]

def links_generator(data):
    source = data['lru']

    for target in data['lrulinks']:
        yield source, target

links_multimap = defaultdict(list)

i = 0
links = []
for page in collection.find({}, {'lru': 1, 'lrulinks': 1}, sort=[('_job', 1)]):
    i += 1

    # links.extend(links_generator(page))

    links_multimap[page['lru']].extend(page['lrulinks'])

    # traph.add_links(links_generator(page))

    if i % 100 == 0:
        print '(%i) [%i] - %s' % (i, len(page['lrulinks']), page['lru'])

    # for link in page['lrulinks']:
    #     traph.add_page(link)

print 'Gathered links'
# traph.add_links(links)
# print links_multimap
# print links
# print len(links)
# print sum([len(i) for i in links_multimap.values()])
traph.index_batch_crawl(links_multimap)

traph.close()
