import sys
from traph import Traph
from traph.helpers import explain_token, parse_pagination_token, int_to_base4

WEBENTITY = [
    1,
    [
        's:http|h:org|h:regardscitoyens|',
        's:https|h:org|h:regardscitoyens|',
        's:https|h:org|h:regardscitoyens|h:www|',
        's:http|h:org|h:regardscitoyens|h:www|'
    ]
]

traph = Traph(folder=sys.argv[1], debug=True)

# for item in traph.webentity_page_nodes_iter(*WEBENTITY):
#     print(item[1])
token = None
results = []

while True:
    result = traph.paginate_webentity_pagelinks(
        *WEBENTITY,
        include_outbound=False,
        source_page_count=1,
        pagination_token=token
    )

    token = result.get('token')
    results.append(result)

    if token is None:
        break

    print 'Token:', token, explain_token(token), int_to_base4(parse_pagination_token(token)[1]), parse_pagination_token(token)

print sum(r['count_sourcepages'] for r in results)
print sum(r['count_pagelinks'] for r in results)
