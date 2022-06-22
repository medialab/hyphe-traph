from __future__ import print_function

import sys
from traph import Traph

traph = Traph(folder=sys.argv[1], debug=True)
metrics = traph.metrics()

for name, metrics in metrics.items():
    print(name)

    for k, v in metrics.items():
        print('  ', k, v)

    print()
