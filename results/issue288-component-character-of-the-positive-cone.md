# 288 — the positive-cone component character, and the comparison that stopped it

Stage 1, under #280. The consumer result: `L.component_character()` on an indefinite
lattice returns the character $O(L) \to \{\pm 1\}$ whose kernel is $O^+(L)$, and
`g.preserves_positive_cone()` returns a Boolean. $\Gamma_{Co} = O^+(T_{Co})^*$ is cut
out by this character, so #286's $\tilde O^+$ rows need it.

## What was red

On `main` at `a0d9ad37`, the two tests named by the issue:

```
tests/lattices/test_definite.sage::test_positive_cone_character_and_real_spinor_norm_are_independent_computations
tests/lattices/test_definite.sage::test_the_component_character_is_multiplicative_and_cuts_out_the_cone_subgroup
2 failed, 23 deselected in 1.13s
```

`test_positive_cone_character_and_real_spinor_norm_are_independent_computations` stops
first, in `preserves_positive_cone`:

```
tests/lattices/test_definite.sage:313: in test_positive_cone_character_and_real_spinor_norm_are_independent_computations
    assert positive_reflection.preserves_positive_cone() is False
src/sage_extensions/categories/lattice_morphisms.py:2092: in preserves_positive_cone
    if positive != integers.one() or negative < integers.one():
AttributeError: type object 'Cardinalities.parent_class' has no attribute 'one'
```

`test_the_component_character_is_multiplicative_and_cuts_out_the_cone_subgroup` stops
at the same expression through the lattice owner:

```
tests/lattices/test_definite.sage:341: in test_the_component_character_is_multiplicative_and_cuts_out_the_cone_subgroup
    character = lattice.component_character()
src/sage_extensions/categories/lattices.py:4299: in component_character
    if positive != integers.one() or negative < integers.one():
AttributeError: type object 'Cardinalities.parent_class' has no attribute 'one'
```

Three sites carried the same three lines — those two and `positive_cone_subgroup`, which
both failing tests also call, so repairing only the two named ones would have moved the
failure rather than removed it.

## The cause, measured

`signature_pair()` returns an object of `Card × Card` (`categories/_lattice.py`,
`signature_pairs()`), so each entry is a **cardinal**, not a ring element. Measured:

```
signature: (1, 1)  <class '...category_constructions._ProductCategory.parent_class'>
first:     1       <class '...categories.sets.cardinals.Cardinalities.parent_class'>
first.parent():    <class '...categories.sets.cardinals.Cardinalities.parent_class'>
first.parent() is a class:  True
Cardinalities() has one:    True
first.is_finite():          True
first.finite_value():       1
int(cardinal(Infinity)):    TypeError: cannot convert infinite cardinal ℵ_0 to integer
```

So `positive.parent()` is the *element class*, which has no unit; the unit lives on the
category instance `Cardinalities()`, and even that unit is a cardinal, not a threshold to
compare a count against. "The signature is $(1,n)$ with $n \ge 1$" is a statement about
**integers**, and the counts have to be read as integers from the type the signature owner
returns.

## The repair

One comparison, at one owner, used by every site that states it:
`Lattices.ParentMethods.has_two_component_positive_cone()` in
`categories/lattices.py`, beside `component_character`:

```python
signature = self.signature_pair()
positive, negative = signature.first(), signature.second()
if positive.is_finite() is not True or negative.is_finite() is not True:
    return False
return int(positive) == 1 and int(negative) >= 1
```

`int` of a finite cardinal is its count (`Cardinals.finite_value`); an infinite entry is
not this case, and the `is_finite()` guard is what keeps `int` from raising `TypeError` on
$\aleph_0$ — the signature owner's own docstring admits infinite inertia
($\mathbf Z^{(\mathbf N)}$ has $(p,q) = (\aleph_0, 0)$). No comparison against a cardinal
and none against a ring's unit survives.

The five sites that stated the condition now call it:

* `lattices.py`, `component_character` and `positive_cone_subgroup` (the two that raised);
* `lattice_morphisms.py`, `preserves_positive_cone` (the third that raised);
* `hyperbolic_geometry.py`, `PositiveConeComponents.__init__` and its `ParentMethods.__init__`
  — the same condition, already written with `int(...)` and therefore not raising, kept in
  one place from now on.

Each site keeps its own message and its own spelling of the refusal (`ValueError` where it
raised one, `assert` in the parameterized category); only the comparison moved. Measured on
the repaired tree: `U` `(1,1)` true, `A2` `(0,2)` false, `E8` `(0,8)` false, `3I_3` `(3,0)`
false, `U \oplus U` `(2,2)` false, the rank-one `<3>` false.

## Green

The two named tests, assertions unchanged:

```
tests/lattices/test_definite.sage::test_positive_cone_character_and_real_spinor_norm_are_independent_computations
tests/lattices/test_definite.sage::test_the_component_character_is_multiplicative_and_cuts_out_the_cone_subgroup
2 passed, 23 deselected in 1.02s
```

## Gate

The modules that call `component_character`, `preserves_positive_cone` or the cone subgroup
they feed, run on the touched tree and again on a clean worktree at the same base commit
`a0d9ad37`, so the failing id sets are compared and not the counts. One pytest process per
batch, `-o addopts= -p qc_sage_session -p sage_extensions.testing.suite_budget
-p sage_extensions.testing.test_lint -q --tb=long --durations=0`:

| batch | touched tree | clean `a0d9ad37` |
|---|---|---|
| `test_definite.sage` | `7 failed, 18 passed in 176.76s` | `9 failed, 16 passed in 171.27s` |
| `test_cusp_lattices`, `test_hyperbolic_chambers`, `test_hyperbolic_space` | `5 failed, 12 passed in 26.12s` | `6 failed, 11 passed in 23.88s` |
| `test_rational_polyhedral_cones`, `test_reduction_complex_exploration` | `1 failed, 10 passed in 1.88s` | `1 failed, 10 passed in 2.01s` |

Exactly three ids change, each from red to green, and they are the three sites the
comparison lived in:

* `test_definite.sage::test_positive_cone_character_and_real_spinor_norm_are_independent_computations`
  and `::test_the_component_character_is_multiplicative_and_cuts_out_the_cone_subgroup` — the
  two the issue names, through `preserves_positive_cone` and `component_character`;
* `test_cusp_lattices.sage::test_minus_one_and_the_cone_character_split_a_lorentzian_group` —
  through `positive_cone_subgroup`, the site the issue does not name, which both named tests
  also call and which failed with the same `AttributeError` on the base commit.

No id is gained. Every remaining failure is equal on both trees and unrelated to the cone:
`RecursionError` in the theta and CVP tests, `KeyError: 'is_cyclic'` and
`AttributeError: ... has no attribute 'is_cyclic'`, a `tuple` without `cardinality`, two
cardinalities the constructions do not supply (one homset and one predicate subset),
`AttributeError: ... has no attribute 'hyperbolic_space'` / `'weyl_group'` /
`'positive_cone_component'`, one Hilbert-basis ray comparison, and
`test_the_four_quadrants_pair_every_facet_and_their_transporters_generate_O_of_I2`.

Run conditions, since one of them is a guard and not a result: one attempt at the base
commit's `test_definite.sage` was stopped at the runtime's peak-RSS guard
(`SMOKE: tree RSS 6163 MiB exceeded 6144 MiB`, exit 143) and the rerun under the same guard
completed at 171.27 s. The guard was not widened.

## Boundary

The predicate states the condition the callers state, signature $(1,n)$ with $n \ge 1$. It
does not claim that a rank-one positive lattice has no cone character: $\{x : x^2 > 0\} =
\mathbf R \setminus \{0\}$ has two components and $O(\langle 3\rangle) = \{\pm 1\}$ acts on
them, but none of these callers offers that case — `preserves_positive_cone` needs a
positive vector to pair against and `PositiveConeComponents` needs a chamber — so `<3>` is
refused and says why. Signature $(n,1)$ is likewise not accepted: the callers say $(1,n)$,
and `hyperbolic_lattices.py` is where the sign-insensitive spelling lives.
