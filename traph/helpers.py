# =============================================================================
# Helpers
# =============================================================================
#
# Miscellaneous helper functions used throughout the code.
#
import math
import string

BASE64 = string.digits + string.ascii_letters + '-_'
BASE64_INDEX = {}

for i, c in enumerate(BASE64):
    BASE64_INDEX[c] = i

assert len(BASE64) == 64

BASE4_TO_OPS = {
    '1': 'L',
    '2': 'C',
    '3': 'R'
}

OPS_TO_BASE4 = {
    'L': '1',
    'C': '2',
    'R': '3'
}


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
    if len(hosts) == 1:
        return(variations)
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


def lru_dirname(lru):
    return ''.join(list(lru_iter(lru))[:-1])


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


def base4_append(p, n):
    return p * 4 + n


def base4_int(s):
    return int(s, 4)


def int_to_base4(x):
    if x == 0:
        return BASE64[0]

    digits = []

    while x:
        digits.append(BASE64[x % 4])
        x = x >> 2

    digits.reverse()

    return ''.join(digits)


def int_to_base64(x):
    if x == 0:
        return BASE64[0]

    digits = []

    while x:
        digits.append(BASE64[x % 64])
        x = x >> 6

    digits.reverse()

    return ''.join(digits)


def base64_to_int(s):
    l = len(s)
    p = 1
    x = 0

    for i in xrange(l - 1, -1, -1):
        c = s[i]
        v = BASE64_INDEX[c]

        x += v * p
        p = p * 64

    return x


def base4_to_ops(n):
    if n == 0:
        return ''

    return ''.join(BASE4_TO_OPS[i] for i in int_to_base4(n))


def ops_to_base4(s):
    if len(s) == 0:
        return 0

    return base4_int(''.join(OPS_TO_BASE4[op] for op in s))


def build_pagination_token(i, path):
    return '%i#%s' % (
        i,
        int_to_base64(path)
    )


def parse_pagination_token(token):
    i, b64_path = token.split('#')

    return int(i), base64_to_int(b64_path)


def explain_token(token):
    _, int_token = parse_pagination_token(token)
    return base4_to_ops(int_token)
