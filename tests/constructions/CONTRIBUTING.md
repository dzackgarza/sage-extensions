# The construction tests

This subtree records what a mathematician expects to be able to build in a
session, and what they expect to be able to ask of it.  The preamble is
measured against these expectations.  The expectations are not measured
against the preamble.

## Why it exists

A test written beside an implementation exercises the path the
implementation took.  Such tests are necessary, and they are not enough: a
whole suite of them can be green while `KahlerDifferentials(ZZ)` raises, and
while modules over every principal ideal domain but $\mathbb Z$ have never
been asked for, because nobody wrote the line that asks.  A mathematician
opening a notebook or a REPL finds those dead ends in the first minute: a
construction that does not build, an operation that raises, a placement
that is wrong, a word the universe lacks.

This subtree is the survey of the available mathematics that finds them
first.  Its purpose is to fire on surprise.  Asserting known values is how
a test states what it expects; it is not the point.  A test whose only
claim is that the natural construction runs, and that the natural
operations on the result run, is already doing the job.  Runtime errors are
findings of the same rank as wrong answers.

## What a test here is

A test here is one expectation, written the way it would be typed into a
notebook by someone who knows the mathematics and has never read the
preamble's source:

```python
def test_the_group_algebra_of_the_symmetric_group(build, name) -> None:
    algebra = GroupAlgebra(build(name), Groups.S(3))
    assert algebra.module_rank() == 6
    assert algebra.center().module_rank() == 3
```

It constructs the object, then runs nontrivial operations on it: the
invariants, the morphisms, the subobjects, the further constructions a
session would go on to make.  Construction alone exercises one line; the
operations exercise the end-to-end path a working session follows.  The
claims are known truths: a textbook value, a standard identity, or a
relation between two constructions that holds over every ring.  The
spelling is the natural one.  Whether the preamble has a name for the
construction, accepts the input, or returns the right answer is exactly
what the test finds out.

## The rules

**Write from the mathematics, never from the implementation.**  Do not read
the preamble's source to learn what it accepts, what it refuses, what
restrictions it places on inputs, or how it spells things.  The test is
written with zero knowledge of all of that.  The exported names and the
generated megadoc (`docs/preamble-megadoc.md`) are the vocabulary a session
offers, and they may be consulted the way a user consults documentation.
When the natural spelling of a construction is absent from that vocabulary,
write the natural spelling anyway.  The star import of
`sage_extensions.all` lets an undefined name fail inside its own
test, and that failure is the finding: the universe lacks a word.  The
vocabulary is never a filter on which expectations get written.

**Use the notebook spelling.**  Integer literals are integers.  `QQ[G]` is a
group algebra, `M / N` is a quotient, `M.Mor(N)` is a Mor module,
`K.class_group()` is the class group.  Do not wrap, cast, or translate an
input into a form the implementation happens to want.  A test that has to
say `ring(ZZ(2))` to be accepted has recorded a defect in the ring, not in
the test.

**Spell every operation on its category or its object; never as a
standalone function.**  A standalone name says nothing about where the
mathematics lives, and a session full of them has no structure to navigate.
One rule per kind:

- A *functor* is a method of its domain category, named by the
  construction, taking only what fixes the codomain:
  `Modules(ZZ[H]).induction(G)`, `FiniteGSets(G).orbits_functor()`,
  `Groups().abelianization()`, `Algebras(R).Associative().Unital().Commutative().spectrum()`.
- An *adjunction* is a method of the left adjoint's domain category, named
  by the pair: `Modules(ZZ[H]).induction_restriction_adjunction(G)`,
  `FiniteSets().free_underlying_adjunction(G)`.
- A *construction on objects* is a method of the category that owns them,
  or of the object when one argument is distinguished: `M.tensor_product(N)`,
  `M.Mor(N)`, `M.ext(N, n)`, `C.cohomology(n)`, `M.free_resolution()`.
- An *object constructor* is the category applied to the object's data:
  `FiniteGSets(G)(points, action)`, `Modules(ZZ[G])(M, action)`,
  `Subgroups(G)(predicate, description)`, `CochainComplexes(R)(pieces, differentials)`.

Group modules are modules over the group ring: `Modules(R[G])`, never a
category of their own.  Induction, coinduction and restriction along
`H ≤ G` are scalar change along `ZZ[H] → ZZ[G]`; the trivial action,
invariants and coinvariants are scalar change along the augmentation
`ZZ[G] → ZZ`.  These functors are stated over `ZZ`, the initial ring, and
preserve the finer scalars an `R[G]`-module carries.

**Do not run the tests to shape them.**  Running them while writing invites
the one failure this subtree exists to avoid: adjusting the expectation to
what the implementation does, which reproduces the happy-path suite under
another name.  The only mistakes inspection cannot catch are syntax errors,
so the one check to run is a syntax check:

```bash
python3 -m py_compile tests/constructions/*.py
```

Everything else is caught by reading the test as a mathematician.

**Red is the deliverable.**  A failing test is a dead end a working
mathematician would hit.  Never weaken, skip, mark expected-failure, or
delete a test because it fails.  Never add a fallback to make a line pass:
no `or` between two spellings, no `hasattr`, no branch on what the object
turned out to be.  A test goes green when, and only when, the preamble meets
the expectation.  Commits to this subtree are red proofs and bypass the
commit gate as such; the suite's colour is the report.

**One expectation per red line.**  Bundle related claims about one object
in one test, but split off anything whose failure would hide the rest.  A
red row must name one construction or one operation, so the person reading
the failure knows the single thing that is missing.

**Prefer relations to tables.**  `coker(R \xrightarrow{2} R) \cong R/2R`
is one line that is true over every commutative ring; a table of
cardinalities per ring is many lines that are each true once.  Use a table
when the value is a fact about one object (the order of $O(E_8)$, the class
number of $\mathbb Q(\sqrt{-23})$), and a relation when the value is a
consequence of the definition.

**Range over the catalogue.**  `tests/conftest.py` holds named specimen
families, every member built by the session's own constructors: fields,
discrete valuation rings, principal ideal domains, Dedekind domains,
Noetherian domains, non-domains, noncommutative rings, and the local,
complete, Artinian, finite, number-field and maximal-order families that
cut across them.  A test asks for a family by its fixture name (`pid`,
`field`, `local_ring`, ...) and runs once per member.  A construction
expected over every principal ideal domain is written once and tried over
$\mathbb Z$, $\mathbb Q[x]$, $\mathbb Z[i]$, $\mathbb Z_p$ and the rest.
Members are added to a family because the mathematics puts them there,
never because the implementation handles them; a member that fails to build
is a finding, not a row to drop.  The same shape is wanted for every kind of
object: monoids, groups, sets (finite, countable, uncountable), modules over
each principal ideal domain, lattices over each of $\mathbb Z$, $\mathbb Z_p$,
$\mathbb F_p$, $\mathbb R$, $\mathbb Q$, $\mathbb Q_p$, $\mathbb C$, and
so on; the ring families are the first of these, not the last.

The catalogue is a seed.  Its proper home is the preamble, where it can be
discovered from a session and grow with the mathematics.  Every owned
category answers `an_object()` today; the intended contract is that a
category exhibits an object, exhibits several (`some_objects()`), and that
each exhibited object produces elements, with these declared as abstract
methods so that a category cannot be initialized without supplying them.
Named families (the principal ideal domains, the Dedekind domains, the
finite fields, the countable sets, ...) belong on the categories that own
them under names a mathematician can guess.  When that surface exists, the
fixtures here draw from it, and the sweep in
`test_categories_inhabited.py` is the test that it holds.

**Compose.**  Breadth is the whole value of the survey, and the dead ends
that matter most sit where one construction is fed into another: a lattice
over an order, a polynomial ring over a quotient, the spectrum of a
localization, the trace form of a number field as a lattice, the pushout of
two algebras as a fiber product of schemes.  Every family of constructions
is also an input to every other; predicting what a mathematician might
combine is the writer's job.

**Parameterize.**  Two modes, both wanted.  By natural parameters: an
integer, a root of an integer, a simple algebraic integer, a rational, a
real, a complex number, a Gram matrix, a Cartan type, a defining polynomial.
By category objects: the families above.  A test that takes a parameter and
states what it determines covers a whole family at once.

**Generate the parameters.**  Where a claim is uniform in its parameter,
let Hypothesis draw the parameter instead of choosing a few by hand.
`construction_strategies.py` holds the strategies for both modes: integers,
primes, squarefree radicands, rationals, symmetric Gram matrices, ranks,
Cartan types, and `family(names)` for a catalogue member drawn by name.
`test_properties_construct.py` is the pattern:

```python
@settings(max_examples=25r, deadline=None)
@given(gram=nondegenerate_gram_2x2)
def test_rank_two_lattices_from_gram_matrices(gram) -> None:
    lattice = Lattices(ZZ)(gram)
    assert lattice.determinant() == determinant_2x2(gram)
    assert lattice.signature_pair() == signature_pair(*signature_2x2(gram))
```

The expected value on the right comes from `natural_parameters.py`: pure
Python arithmetic of the parameter (primality, Euler's function, the
discriminant of $\mathbb Q(\sqrt d)$, Sylvester's criterion for a
$2 \times 2$ Gram matrix), written with PEP 316 contracts so that CrossHair
proves it symbolically:

```bash
uvx --from crosshair-tool crosshair check --analysis_kind=PEP316 tests/constructions/natural_parameters.py
```

That is the division of labour.  CrossHair sees through pure Python and
nothing Sage-backed, so it certifies the side of the comparison the test
supplies; Hypothesis drives the side the session supplies through many
inputs, and a failure names a concrete counterexample.  Hypothesis is a
dependency of the test interpreter (`hypothesis` in the `dev` group of
`pyproject.toml`, installed into the Sage interpreter that runs the suite);
its example database `.hypothesis/` is ignored by git.  Deadlines are
disabled because the session's operations are slow by construction, and
example counts are kept small because every example is a full mathematical
object.

**Every map is stated; nothing is coerced implicitly.**  An element of one
object enters another only through an explicit conversion into the target
(`QQ(1) + QQ(1/2)`, `RR(4) / pi**2`) or a named morphism applied to it.  An
expression that combines elements of two different objects and leaves the
session to choose a map between them is not written here.  Combining
elements needs a morphism, and the morphism is data even where it is
unique (the unit `ZZ -> R` of a ring), so the test states it.  Actions are
not coercions and stay as they are: `n * x` for an integer and an element of
an abelian group, and `r * m` for a scalar and an element of an `R`-module,
are the structure of those objects.  This is the convention the category
core the preamble is expected to adopt enforces, and these files set the
example for it (owner ruling, 2026-09-25).

## What does not belong here

- A test of how the preamble does something.  Internals, class names,
  storage, backends and helper functions are not expectations.
- A test derived from current behaviour.  If the only reason a line asserts
  a value is that the implementation returns it, the line is not a
  mathematical claim.
- A test that compares the preamble against Sage.  The oracle is the
  mathematics; Sage is an engine the preamble may use.
- A skipped or expected-failure test.

## The files are locked

Every test file in this subtree takes its names from the session by the star import `from sage_extensions.all import *` and never imports a preamble name individually, so a test can only ever speak the session's vocabulary or fail for lacking a word.

Every test file in this subtree, in `tests/user_simulations/`, and the
shared `tests/conftest.py` is read-only on disk.  An expectation, once
written, is not edited to follow the implementation: not when a category is
renamed, not when a constructor's signature changes, not when a red row is
inconvenient.  If the implementation moves, the test stays and reports the
move.  The lock is a local file mode, so it must be reapplied after a fresh
checkout:

```bash
chmod a-w tests/conftest.py tests/constructions/* tests/user_simulations/*
```

Unlocking a file is a decision that the expectation itself was wrong as
mathematics, made deliberately and recorded in the commit that changes it.

## Growing the subtree

Add a test the moment you find yourself expecting something of a session
that no test asks for.  Add a family fixture when a class of objects appears
in several expectations.  Adding a name or a capability to the preamble
never requires touching a test; a test that turns green stays exactly as it
was, because it is now a proof that the expectation is met.

A correction to how tests are written changes the method, not the scope.
The subtree is extensive by design, and a pass that stops at the core
objects after a correction has not finished.

## The sibling subtree

`tests/user_simulations/` follows the same rules in a different form, and
deliberately departs from the shape of an ordinary test.  Each test there is
one long research session that a mathematician might carry out in a
notebook, parameterized over natural inputs or over the families above.
The model is: construct a number field, take its ring of integers, print
the ramification of the first few primes, localize at the first prime that
comes to hand, complete there, and render every object along the way as the
notebook would.  Most of the proof is that the session runs to the end; the
assertions are the values the mathematician would have checked by eye.
Both subtrees share the catalogue in `tests/conftest.py`.
