# =============================================================================
# Helpers
# =============================================================================
#
# Miscellaneous helper functions used throughout the code.
#


def https_variation(lru):
    if 's:http|' in lru:
        return lru.replace('s:http|', 's:https|', 1)
    if 's:https|' in lru:
        return lru.replace('s:https|', 's:http|', 1)
    return None


def lru_variations(lru):
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
