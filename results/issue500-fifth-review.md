# The fifth review of #500 answered: the torsion reading, a topological sort, and the prose

The review named `6578c33cff` and its red state `27d76f3982`, and the tree it was
answered on is `a106d23`.  Five commits, in this order:

| commit | what it does |
| --- | --- |
| `f2af38e` | the tests, red on `a106d23` for the two answers the torsion predicate owed |
| `030a528` | the framed branch of the algebra level restored, and `is_torsion_free`'s reading stated once |
| `476f87c` | the provider order built with `graphlib.TopologicalSorter` |
| `587aabd` | the refusal rewritten in the caller's terms, and four sentences that narrated the repair deleted |
| `6e4e097` | the merge of the remote main that moved while this was being written (`1cc2481`) |

#530's body is already satisfied on `a106d23` and is not touched here:
`Modules.ParentMethods.dual_module` is the internal Mor `Hom_R(M, R)` alone,
`_dual_product_construction` and `dual_evaluation_image_generators` do not exist,
and the commutativity assertion appears once, at `modules.py:3125`.

## 1. The regression from `77d29f2107`

`Z[x]/(x^2)` is `AlgebrasWithChosenFinitePresentation(Z).an_object()`, and it is
in `FramedFreeModules(Z)` as well.  The two categories are incomparable, so which
of them declares `_torsion_freeness_decision` is the category order's to say, and
the order puts this level first: on `a106d23` the algebra level answers, its body
constructs `TensorAlgebras(Z)` and `SymmetricAlgebras(Z)` before it can look at
the framed category, and that construction re-enters the class being built --
`RecursionError`.

The branch is restored ahead of those constructions.  The paragraph that said a
framed free algebra "is not this level's case ... a subcategory, and therefore
the provider the category order names first" was false twice over -- the
categories are incomparable and the level is reached -- and it is replaced by the
argument the branch uses.

Which class answers, and with what:

```
Z[x]/(x^2)   AlgebrasWithChosenFinitePresentation.ParentMethods   True
Z/4[x]       FramedFreeModules.ParentMethods                      True
Z[x]         FramedFreeModules.ParentMethods                      True
Q(i)         FramedFreeModules.ParentMethods                      True
```

## 2. The order relation

`_precedes(P, Q)` is neither transitive nor antisymmetric, so the insertion loop
was a linear extension only where the relation happened to be a strict partial
order.  The classes are now the nodes of a `graphlib.TopologicalSorter` graph;
a cycle is `CycleError` with the nodes in it.  Two classes the relation leaves
unordered keep the walk's order: of the classes the sort has released, the one
the walk reaches first is taken next.

The relation is also **reflexive**, which the loop never saw because it never
compared a provider with itself.  Feeding a self-edge is not harmless: it is a
cycle to the sorter, and with the self-edges in it `tests/categories` failed
eight tests with `CycleError` -- `_OppositeCategory.ParentMethods` listed once
against itself -- the pullback, span and presheaf tests among them.  The guard
`if not sources or sources[-1] is not cat` is deleted with the `setdefault` it
served: `all_super_categories(proper=False)` yields distinct categories, so it
never fired.

What the change does and does not move, measured on twenty-six constructed
objects (the twenty-five of the provider probe plus `Z[x]/(x^2)`), each of
`ParentMethods`, `ElementMethods` and `MorphismMethods`, over nine runs:

* the two orders differ on 0, 1 or 2 of those 78 pairs, and the pair that moves
  is `Modules.FinitelyGenerated` against `FramedFreeModules` in `QQ(i)`'s
  `ParentMethods` -- a difference the **base** tree shows too, from run to run,
  because the walk itself is not stable across processes there;
* in every run, **no name any provider declares is answered by a different
  provider**, and the answering level of twelve public operations on the same
  twenty-five objects is identical to the base's.

## 3. The other changed answers

`Q[x]`, `Z[x, y]` and `Q(i)` answer `is_torsion_free()` True and `annihilator()`
the zero ideal of the base ring, which is what nonzero free modules over a field
or a domain are.  `Z/4[x]` answers True, and that is the reading question.

Over a ring with zero divisors, "torsion" has two readings and they disagree
here: an element killed by a **non-zero-divisor**, or an element killed by any
nonzero scalar.  The predicate is the first: it is the one the library's own
`torsion_submodule` computes (`ker(M -> Frac(R) tensor M)` over a domain, Stacks
Project Definition 15.22.1 and Lemma 15.22.2), it is the one `is_primitive` and
`is_flat` and the lattice quotients rely on, and it makes a free module
torsion-free over any ring -- the hypothesis is on the scalar, and a
non-zero-divisor kills no coefficient.  So `Z/4[x]` is torsion-free although
`2 * (2x) = 0`: `2` is a zero-divisor.  The second reading would refute it, and
the general level would still have to answer "undecided", which is the two
answers the review objected to.

**One departure from the review, on evidence.**  The review asked the restored
branch to decide "on the base being a domain".  Gating it on `IntegralDomains`
would answer `Z/4[x]` True from the framed level and refuse `Z/4[x]/(x^2)` --
the same object over the same ring, one quotient away -- with an assertion from
the algebra level: one name, two answers again, moved one object over.  The
branch therefore asks for no domain, and says why; both objects are pinned by
the test.

## 4. Text

* The order-ideal refusal said "selected", "presentation", "this library holds
  none", and called the values of the functionals "the linear functionals".  It
  now states the object, the ideal it is, the one thing it needs and why.
* The framed-level test said the *members* of `Z[x]` annihilate nothing (scalars
  annihilate) and recorded that `annihilator()` had been undecided (it raised);
  both sentences are replaced by the claim.
* "the order is stated once ... this file does not restate it" (three files) and
  "(its own issue)" are deleted.

## 5. Regression

Twelve directories and the five root test modules, one pytest process per
target, on this tree and on a clean worktree at the base commit, FAILED **ids**
compared and never counts:

| target | this tree `6e4e097` | base `1cc2481` | FAILED/ERROR ids |
| --- | --- | --- | --- |
| `tests/categories` | 41 failed, **45 passed**, 38 errors | 41 failed, 42 passed, 38 errors | 79 / 79 |
| `tests/algebras` | 45 failed, 44 passed, 124 errors | 45 failed, 44 passed, 124 errors | 169 / 169 |
| `tests/modules` | 68 failed, 175 passed, 69 errors | 68 failed, 175 passed, 69 errors | 137 / 137 |
| `tests/rings` | 52 failed, 134 passed, 153 errors | 52 failed, 134 passed, 153 errors | 205 / 205 |
| `tests/foundations` | 1 failed, 6 passed, 1 error | 1 failed, 6 passed, 1 error | 2 / 2 |
| `tests/sets` | 10 failed, 62 passed, 92 errors | 10 failed, 62 passed, 92 errors | 102 / 102 |
| `tests/objects` | 95 failed, 152 passed, 79 errors | 95 failed, 152 passed, 79 errors | 174 / 174 |
| `tests/functions` | 38 failed, 15 passed, 10 errors | 38 failed, 15 passed, 10 errors | 48 / 48 |
| `tests/tensors` | 11 failed, 12 passed, 20 errors | 11 failed, 12 passed, 20 errors | 31 / 31 |
| `tests/engineering` | 11 failed, 9 passed | 11 failed, 9 passed | 11 / 11 |
| `tests/divisors` | 42 failed, 25 passed | 42 failed, 25 passed | 42 / 42 |
| `tests/topology` | 1 failed | 1 failed | 1 / 1 |
| `tests/test_*.py` (five modules) | 4 passed, 21 errors | 4 passed, 21 errors | 21 / 21 |
| `tests/lattices/test_lattice_surfaces.sage` | 3 failed, 7 passed | 3 failed, 7 passed | 3 / 3 |

No id appears on one side only, anywhere.  The one count that differs is
`tests/categories`' three new tests, which is what this round adds.
`tests/lattices` is not run as a directory on this host -- a run took 5.6 GiB
and had not finished at 25 minutes -- so the one file under it that reads
`is_torsion_free` is run on its own, above.

Every run blanks `addopts` and loads `sage_extensions.testing.suite_budget` and
`sage_extensions.testing.test_lint` by name: this host's venv has no
`pytest-timeout`, so `just test`'s own `addopts` fails before a test is
collected (`unrecognized arguments: --timeout=60 --timeout-method=signal`).

## Not repaired, reported

* `Z[x]/(x^2).algebra_generator("x")` raises `RecursionError`, on the base tree
  as on this one.  The test builds the algebra from `ZZ["x"]` and does not call
  it; it is a separate defect and it is not this review's.
* The provider order is not stable across processes, on **both** trees: the walk
  for `QQ(i)`'s `ParentMethods` puts `Modules.FinitelyGenerated` before or after
  `FramedFreeModules` depending on the run.  This round's order inherits that
  because the walk is its tie-break; it does not add to it, and no answering
  provider moves.  Reported, not repaired: a stable walk is the category
  construction's to give.
