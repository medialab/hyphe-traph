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
lruTrieFile = open('./scripts/data/lru_trie.dat', 'wb+')

traph = Traph(lru_trie_file=lruTrieFile)

# Reading from mongo
client = MongoClient(MONGO['host'], MONGO['port'])
collection = client[MONGO['db']][MONGO['collection']]

i = 0
for page in collection.find({}, {'lru': 1, 'lrulinks': 1}, sort=[("_job", 1)]):
    i += 1

    traph.add_page(page['lru'])

    if i % 1000 == 0:
        print '(%i) [%i] - %s' % (i, len(page['lrulinks']), page['lru'])

    # for link in page['lrulinks']:
    #     traph.add_page(link)

lruTrieFile.close()
