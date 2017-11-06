[![Build Status](https://travis-ci.org/medialab/hyphe-traph.svg)](https://travis-ci.org/medialab/hyphe-traph)

# hyphe-traph

The `Traph` is an on-file index structure designed to store [hyphe](https://github.com/medialab/hyphe)'s network of pages & webentities.

Under the hood, the `Traph` is the combination of a [ternary search tree](https://en.wikipedia.org/wiki/Ternary_search_tree) of URL stems and [linked lists](https://en.wikipedia.org/wiki/Linked_list) of pages' hyperlinks (hence the portmanteau name).

## Development

`hyphe-traph` was written to work with the `2.7` version of Python.

```
# Install dev dependencies (preferably in a virtual env)
pip install -r requirements.txt

# Run the tests
make test

# Run the linter
make lint
```

