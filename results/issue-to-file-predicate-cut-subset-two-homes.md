# Issue to file: the subset cut out by a predicate has two constructions, and only one is a subobject

Not filed by a push: this project's GitHub connection reads issues and cannot create
them, so the orchestrator posts this body. Parent: **#518**. #546 repairs the consumer
(the integral lift locus) and does not repair this owner.

## Title

`Sets().condition_set` and `P(X).from_predicate` are two constructions of one subset, and
only the second is a subobject of `X`

## Body

`Sets().condition_set(universe, predicate)` (`set_categories.py:1369`, through
`_condition_set`, `:4230`) answers the set `{x in X : P(x)}` as an object of `Sets()` with
a predicate engine: a *set*, not a subobject of `X`.  `P(X).from_predicate(predicate)`
(`:3454`) answers the same subset as an object of `Sets().Subobjects(X)`: its inclusion
into `X` is the subobject it is.

`SET-05` requires one parent for canonically identical constructions, and #546 states the
identity the two spellings split: "the subsets of a set `X` are the points of `P(X)`".  On
`main` at `762126c` the split is observable on every set:

    sage: NN.condition_set(lambda n: n > 3) in Sets().Subobjects(NN)
    False
    sage: NN.power_set().from_predicate(lambda n: n > 3) in Sets().Subobjects(NN)
    True

and the first answers `False` rather than an undecided proposition, because a bare set is
not an arrow of the slice at all.  #546's consumer needed the subobject spelling and took
it; a consumer that asks for the set spelling still gets an object that is not a subset of
anything, and the same subset is then two parents with two emptiness hooks.

## What the owner should decide

Which of the two is the construction, and what the other becomes:

1. `condition_set` is the construction and `from_predicate` is `P(X)`'s element constructor
   over it (the shape `from_predicate` has today: it reads the inclusion of
   `condition_set`'s answer and hands it to `Sets().Subobjects(X)`); then a bare
   `condition_set` answer is an intermediate object that no public route returns, and the
   route should say so — `Sets().condition_set` would stop being public, or would answer
   the subobject.
2. `from_predicate` is the construction and `condition_set` is the set-level reading of it
   (`from_predicate` answers a subobject; the set is the subobject's domain); then
   `condition_set` must not be a second construction, and the emptiness and cardinality
   hooks live at one of the two.

Either way one of the two spellings is a *view* of the other, not a parallel
construction, and `Sets().condition_set`'s callers (`set_categories.py:1603`, `:1728`,
`:2876`, `:2886`; `affine_fibres.py:56`, `:122`; `lattices.py:990`, `:1036`, `:9142`,
`:9828`, `:9858`, `:12281`, `:12302`, `:12545`; `form_modules.py:2382`;
`isotropic_lifts.py:269` at `762126c`) are the set of sites that decide which.

## Why #546 does not repair it

The consumer change is one line — `power_set().from_predicate(in_residue)` — and it is
made at `isotropic_lifts.py`.  Moving the owner is a decision about the public set API
with fifteen call sites in four packages, and #546's acceptance is about the locus.
