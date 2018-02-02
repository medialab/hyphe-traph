# It's a Tree... It's a Graph... It's a Traph!

<center>
  <span class="red-title">
    Designing an on-file multi-level graph index for the Hyphe web crawler
  </span>
</center>

<br>

<center>
  <small>
    Mathieu Jacomy • Paul Girard • Benjamin Ooghe-Tabanou • Guillaume Plique
  </small>
</center>

===

<center>
  <img alt="logo médialab" src="img/medialab-logo.svg" />
</center>

===

<h2>
  <span class="red-number">I.</span><br>Hyphe
</h2>

===

TODO: demo hyphe, web entities, lrus

===

<h2>
  <span class="red-number">II.</span><br>Before: Lucene
</h2>

===

TODO: limits

TODO: operations: pages by prefix, page's webentity, ability to dynamically change webentities. NOT queries + dynamic changes => recache index slow

SCHEMA: for NOT queries => illustrate using Wikipedia

TODO: plus various caveats

TODO: mea culpa

TODO: it works, but it's slow (indexation is slower than the web...)

===

<h2>
  <span class="red-number">III.</span><br>A battle to the death
</h2>

TODO: vs. Lucene/Neo4J/Traph
* [Java Tree POC](https://github.com/medialab/hyphe-java-tree-poc)
* [Neo4J POC](https://github.com/medialab/hyphe-neo4j-poc)

===

<h2>
  <span class="red-number">IV.</span><br>Prototype A - Neo4j
</h2>

* example schema LRUS/Wes stockées dans neo4J
* Complexité à écrire certaines requetes
 + WECreationRules -> [complex but OK](https://github.com/medialab/hyphe-neo4j-poc/blob/master/queries/core.cypher#L66-L164)
 + Query WELinks... [10 versions](https://github.com/medialab/hyphe-neo4j-poc/blob/master/queries/core.cypher#L183-L289), même Procédures stockées
  => #fail

===

TODO: we have a graph, let's use Neo4j

TODO: UNWIND big win

TODO: mettre une grosse requete qui tache

SCHEMA: benj schema neo4j des lrus

===

<h2>
  <span class="red-number">V.</span><br>Prototype B - The Traph
</h2>

===

<center>
  ![its-a-traph](img/its-a-traph.png)
</center>

===

# Designing our own on-file index

<center class="red">
  To store a somewhat complicated multi-level graph of URLs
</center>

===

## People told us NOT to do it

===

### It certainly seems crazy...

* Building an on-file structure from scratch is not easy.
* Why would you do that instead of relying on some already existing solution?
* What if it crashes?
* What if your server unexpectedly shuts down?
* What if a thermonuclear war eradicates mankind?

\[\[ Insert a lot of other perfectly reasonable concerns \]\]

===

### Not so crazy

* You cannot get faster than a tailored data structure (that's a fact).
* We don't need deletions (huge win!).
* No need for an **ACID** database (totally overkill).

===

### We just need an index

* An index does not store any "original" data because...
* ...a MongoDB already stores the actual data in a reliable way.
* \[ insert joke about MongoDB being bad \]
* This means the index can be completely recomputed and its utter destruction does not mean we can lose information.

===

# So let's build this index!

===

# We'll call it the Traph!

===

# But, seriously, what is a Traph?

===

The traph is a "subtle" mix between a <u>Trie</u> and a <u>Graph</u>.

<small>Hence the incredibly innovative name...</small>

===

## A Trie of LRUs

SCHEMA: schema of character level lrus.

===

## Storing a Trie on file

Using fixed-size blocks of binary data (ex: 10 bytes).

We can read specific ones using pointers in a random access fashion.

===

SCHEMA: schema of binary lru trie block.

===

SCHEMA: schema of the Trie with blocks.

===

We can now insert & query pages in `O(m)`.

===

## A Graph of pages

The second part of the structure is a distinct file storing links between pages.

We need to store both out links and in links.

```cypher
(A)->(B)

(A)<-(B)
```

===

## Storing links on file

Once again: using fixed-sized blocks of binary data.

We'll use those blocks to represent a bunch of linked list of stubs.

===

SCHEMA: schema of binary lru store block

===

### Linked lists of stubs

```large
{LRUTriePointer} => [targetA, weight] -> [targetB, weight] -> ø
```

===

We can now store our links.

We have a graph of pages!

===

## What about the multi-level graph?

What we want is the graph of **webentities** sitting above the graph of pages.

===

We "just" need to flag our Trie's nodes for webentities' starting points.

SCHEMA: trie with webentities boundaries' & flag

===

So now, finding the webentity to which belongs a page is obvious when traversing the Trie.

What's more, we can bubble up in `O(m)`, if we need to, when following pages' links (this can also be easily cached).

===

REUSE EARLIER SCHEMA

===

What's more, if we want to compute the webentities' graph, one just needs to perform a DFS on the Trie.

This seems costly but:

* No other way since we need to scan the whole index at least once.
* The datastructure is quite lean and you won't read so much.

===

## But was it worth it?

===

## Our benchmark

10% sample of a sizeable corpus about privacy.

* Number of pages: **1 840 377**
* Number of links: **5 395 253**
* Number of webentities: **20 003**
* Number of webentities' links: **30 490**

===

## Results - Indexation time

* **Lucene** • 1 hour & 55 minutes
* **Neo4j** • 1 hour & 4 minutes
* **Traph** • 16 minutes

===

## Results - Graph processing time

* **Lucene** • 45 minutes
* **Neo4j** • 6 minutes
* **Traph** • 1 minute 35 seconds

===

## Results - Disk space

* **Lucene** • 740 megabytes
* **Neo4j** • 1.5 gigabytes
* **Traph** • 1 gigabytes

===

OK.

Neo4j seems to win the disk space battle.

===

Not for long.

===

Implémentation python

TODO: trie organized with children as linked lists

TODO: stems + losing lots of space due to pointers - issue - ternary search tree - balancing

TODO: compare bench again (see my notes for size & speed)

===

## Takeaway bonus: varchars(255)

Sacrificing one byte to have the string's length will always be faster than manually dropping null bytes.

===

<!-- .slide: data-background="img/varchars.png" -->

===

**Huge win!** - 2x boost in performance.

===

TODO: we used lucene badly but still + stored procedures in Neo4j

===

<center>
  Here we are now.
</center>

<br>

<center>
  <img src="img/crawl-index.png" height="300px" />
</center>

<br>

<center>
  The web is the bottleneck again!
</center>

===

The current version of [Hyphe](https://github.com/medialab/hyphe) uses this index!

===

# But...

===

We are confident we can further improve the structure.

And that people here can help us do so!

===

<center>
  Thanks for your attention.
</center>
