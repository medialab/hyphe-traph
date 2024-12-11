import random
from traph import Traph

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})'
}

default_webentity_creation_rule = webentity_creation_rules_regexp['domain']

webentity_creation_rules = {
    's:http|h:com|h:twitter|': webentity_creation_rules_regexp['path1'],
    's:http|h:com|h:facebook|': webentity_creation_rules_regexp['path1'],
    's:http|h:com|h:linkedin|': webentity_creation_rules_regexp['path2']
}

traph = Traph(overwrite=True, folder='./scripts/data/',
              default_webentity_creation_rule=default_webentity_creation_rule,
              webentity_creation_rules=webentity_creation_rules)

root_lru = 's:https|h:com|h:complete_website|p:base1|p:base2|'

K = 3000
D = 1

print('Expecting %i links' % (K * K * D))

batch_crawl = {}

for i in range(K):

    source_lru = '%sp:leaf%i|' % (root_lru, i)
    links = []

    for j in range(K):
        target_lru = '%sp:leaf%i|' % (root_lru, j)

        # NOTE: link duplication
        for _ in range(D):
            links.append(target_lru)

    random.shuffle(links)
    batch_crawl[source_lru] = links

traph.index_batch_crawl(batch_crawl)

print('Got %i links' % traph.link_store.count_links())
print('Max inlinks: %i' % traph.links_metrics()['max_inlinks_len'])
