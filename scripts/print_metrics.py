import sys
from traph import Traph

traph = Traph(folder=sys.argv[1], debug=True)
metrics = traph.metrics()

for name, metrics in list(metrics.items()):
    print(name)

    for k, v in list(metrics.items()):
        print("  ", k, v)

    print()
