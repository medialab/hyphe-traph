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

<h2>
  <span class="red-number">I.</span><br>Hyphe
</h2>

===

<h2>
  <span class="red-number">II.</span><br>A Lucene story
</h2>

===

<h2>
  <span class="red-number">III.</span><br>A battle to the death
</h2>

===

<h2>
  <span class="red-number">IV.</span><br>A Neo4j prototype
</h2>

===

<h2>
  <span class="red-number">V.</span><br>What on earth is a Traph?
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

### Isn't that what crazy people do?

* Building an on-file structure from scratch is not easy.
* Why would you do that instead of relying on some already existing solution?
* What if it crashes?
* What if your server unexpectedly shuts down?
* What if humanity ceases to exist?

\[\[ Insert a lot of other perfectly reasonable concerns \]\]

===

### Not so crazy

* You cannot get faster than a tailored data structure (that's a fact).
* We don't need deletions (huge win!).
* No need for an **ACID** database (totally overkill).

===

### We just need an index

* An index does not store any "original" data because...
* ...a MongoDB stores the data in a reliable way.
* \[ insert joke about MongoDB being bad \]
* This means the index can be completely recomputed and its utter destruction does not mean we can lose data.

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

## A Trie

The **Trie** is a prefix tree.

===

<center>
  Thanks for your attention.
</center>
