# =============================================================================
# Mongo Script
# =============================================================================
#
# Attempting to load a corpus from MongoDB
#
from traph import Traph
from pymongo import MongoClient
from config import CONFIG

MONGO = CONFIG['mongo']

# Truncating the file for our purpose
lru_trie_file = open('./scripts/data/lru_trie.dat', 'wb+')
link_store_file = open('./scripts/data/link_store.dat', 'wb+')

traph = Traph(lru_trie_file=lru_trie_file, link_store_file=link_store_file)
trie = traph.lru_trie
links = traph.link_store

# Reading from mongo
client = MongoClient(MONGO['host'], MONGO['port'])
collection = client[MONGO['db']][MONGO['collection']]

batch = traph.batch()

i = 0
for page in collection.find({}, {'lru': 1, 'lrulinks': 1}, sort=[("_job", 1)]):
    i += 1

    batch.add_page_with_links(page['lru'], page['lrulinks'])

    if i % 100 == 0:
        print '(%i) [%i] - %s' % (i, len(page['lrulinks']), page['lru'])

    # for link in page['lrulinks']:
    #     traph.add_page(link)

lru_trie_file.close()
link_store_file.close()
