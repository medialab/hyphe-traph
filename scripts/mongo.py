# =============================================================================
# Mongo Script
# =============================================================================
#
# Attempting to load a corpus from MongoDB
#
import os
from traph import Traph
from pymongo import MongoClient

# Creating data folder
if not os.path.isdir('./scripts/data'):
    os.makedirs('./scripts/data')

# Truncating the file for our purpose
lruTrieFile = open('./scripts/data/lru_trie.dat', 'wb+')

traph = Traph(lru_trie_file=lruTrieFile)

# Reading from mongo
client = MongoClient('localhost', 27017)
collection = client['hyphe']['AXA.pages']

i = 0
for page in collection.find({}, sort=[("_job", 1)]):
    i += 1

    traph.add_page(page['lru'])

    if i % 1000 == 0:
        print '(%i) [%i] - %s' % (i, len(page['lrulinks']), page['lru'])

    # for link in page['lrulinks']:
    #     traph.add_page(link)

lruTrieFile.close()
