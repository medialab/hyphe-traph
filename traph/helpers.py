# =============================================================================
# Helpers
# =============================================================================
#
# Miscellaneous helper functions used throughout the code.
#
import math


def https_variation(lru):
    '''
    Returning the http(s) variation of the given lru
    '''

    if 's:http|' in lru:
        return lru.replace('s:http|', 's:https|', 1)
    if 's:https|' in lru:
        return lru.replace('s:https|', 's:http|', 1)
    return None


def lru_variations(lru):
    '''
    Returning the www/http(s) variations of the given lru
    '''
    variations = [lru]

    if not lru:
        return variations

    https_var = https_variation(lru)
    if https_var:
        variations.append(https_var)
    stems = lru.split('|')
    hosts = [s for s in stems if s.startswith('h:')]
    hosts_str = '|'.join(hosts) + '|'
    if len(hosts) == 1:
        return variations
    if hosts[-1] == 'h:www':
        hosts.pop(-1)
    else:
        hosts.append('h:www')
    www_hosts_var = '|'.join(hosts) + '|'
    variations.append(lru.replace(hosts_str, www_hosts_var, 1))
    if https_var:
        variations.append(https_var.replace(hosts_str, www_hosts_var, 1))
    return variations


def lru_iter(lru):
    '''
    Returning an iterator over a lru's stems.
    '''
    last = 0
    for i in xrange(len(lru)):
        if lru[i] == '|':
            yield lru[last:i + 1]
            last = i + 1


def detailed_chunks_iter(chunk_size, string):
    '''
    Returning an iterator over a string's chunks of the given size.
    '''
    if len(string) <= chunk_size:
        yield True, string

    nb_chunks = int(math.ceil(len(string) / float(chunk_size)))

    for chunk in xrange(nb_chunks):
        start = chunk * chunk_size
        yield chunk == nb_chunks - 1, string[start:start + chunk_size]


def chunks_iter(chunk_size, string):
    for _, chunk in detailed_chunks_iter(chunk_size, string):
        yield chunk


def parse_pagination_token(token):
    prefix_index, starting_block = token.split('&')

    return int(prefix_index), int(starting_block)


def build_pagination_token(prefix_index, block):
    return '%i&%i' % (prefix_index, block)
