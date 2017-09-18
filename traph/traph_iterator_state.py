# =============================================================================
# Traph Iterator State Class
# =============================================================================
#
#


class TraphIteratorState(object):

    def __init__(self):
        self.done = False
        self.result = None
        self.n_iterations = 0

    def should_yield(self, yield_frequency=1000):
        self.n_iterations += 1
        return not self.n_iterations % yield_frequency

    def finalize(self, result):
        self.done = True
        self.result = result
        return self


def run_iterator(iterator):
    for state in iterator:
        pass
    return state.result
