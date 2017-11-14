# Design History of the Structure

The Traph is the combination of two data structure:

* The `lru_trie` is a ternary search tree (a specific implementation of a Trie) storing the URL hierarchy as well as the webentity position in this hierarchy.
* The `link_store` is a collection of linked lists representing hyperlinks as stubs (we only get the target of the link).

## From character level to stem level

At first, to keep fixed-size binary blocks, we had a trie at character level. But this was rather inefficient (while still being orders of magnitude faster than our previous Lucene option and even our Neo4j POC) and consumed a lot of space.

The idea was therefore to switch to a trie of stems (logical parts composing the URLs such as the host, the tld, the path etc.).

To keep fixed-size binary blocks (which are handy, harder to corrupt etc.), we designed a system of tail blocks to store stem characters that would not fit in the arbitrary number of characters we chose for the blocks.

But soon, tests proved our new implementation to be inefficient. Its observed complexity was quadratic, while our old implementation had a linear one. In fact, we stumbled upon a Schlemiel syndrom whose reason was that our siblings' linked lists were not bound to a precise limit anymore.

Indeed, at character level, it's impossible for the siblings' linked list to be larger than 255 elements (empirically, it's even improbable that it would be larger than 30 elements). While, at stem level, a linked list could grow to become very large (the tld stem nodes, for instance, could have thousands of siblings very easily), hence the quadratic complexity.

The solution to this problem was in fact quite simple: we had to implement a ternary search tree. That is to say, a trie whose siblings are stored as a binary search tree (BST) to guarantee a logarithmic access complexity.

## Concerning BST balancing

One fear we had, now using binary search trees to store a node's siblings, was to end up with unbalanced trees degenerating as mere linked list with linear access time.

So we tried to balance the trees using two different schemes: a traditional Red-Black tree and a Treap.

Results were that writing became twice slower (which was to be expected) while reading was the same (which was a bit more surprising).

As it seems, the order the crawler feeds the Traph with urls generates enough entropy not to produce unbalanced trees. We therefore rolled back and don't use balanced BSTs.

What's more, balanced BSTs are complex beasts and not having to clutter the codebase with their implementation details is a clear win.

## Varchars

One "funny" performance bottleneck was the need to right strip null characters of the binary blocks' string for stems not filling the allowed space completely.

It turns out that using a varchar(255) (with one byte representing the size of the string) is way faster.
