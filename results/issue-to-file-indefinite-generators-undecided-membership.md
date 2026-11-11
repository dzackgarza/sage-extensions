# To file: every indefinite-lattice generator family raises "membership ... is undecided"

**Introduced by `158c170385aae1be06a6234b4a871528e8064bdf`** ("fix: Admit a free cover's
word values into its generated subgroup", #287), which is on `main` from
`a79d3e1ca555533cb2094e4ff914dbf2de60d289`. Two public calls that returned before it now
raise, and both are on the `2U`-envelope branch of the indefinite port, which is *every*
indefinite lattice that does not split two hyperbolic planes:

```
NamedLattices.TEn.O().discriminant_image()
NamedLattices.Tco.Aut().group_generators()
```

## Reproduction

`T_En` (rank 12, signature (2, 10)), one process, port at `/work`:

```
tests/lattices/test_the_orthogonal_group_of_ten_has_a_discriminant_image.sage:60:
    assert frozenset(orthogonal.group_generators()) == frozenset(
src/sage_extensions/categories/group/groups.py:5676: in group_generators
    return self.selected_group_resolution().generators(
src/sage_extensions/categories/group/groups.py:5654: in selected_group_resolution
src/sage_extensions/categories/abstract_categories/objects.py:383: in selected_resolution
src/sage_extensions/categories/group/groups.py:1174: in selected_resolution
    generators = generating_set()
src/sage_extensions/categories/abstract_categories/arrow_categories.py:2390: in <lambda>
src/sage_extensions/categories/lattices.py:2267: in _core_automorphism_generators
src/sage_extensions/categories/lattice_morphisms.py:3998: in _computed_group_generators
    for generator in automorphism_group_generators(category, lattice)
/work/src/sage_indefinite_port/indefinite/marked_lattices.py:111:
/work/src/sage_indefinite_port/indefinite/recursive.py:834: _generation_step
/work/src/sage_indefinite_port/indefinite/recursive.py:852:
    return model.approximate_generators() + ...
/work/src/sage_indefinite_port/indefinite/eichler.py:901: approximate_generators
    for generator in envelope.stabilizer_of_lattice().stabilizer().group_generators():
...
src/sage_extensions/categories/sets/set_categories.py:4296: _retain_admitted_member
    point = self.universe()(element)
src/sage_extensions/categories/group/groups.py:1559: __call__ -> _element_constructor_
src/sage_extensions/categories/group/groups.py:1571:
    if element not in self:
src/sage_extensions/categories/group/groups.py:1594: __contains__
    raise TypeError(f"membership of {value} in {self} is undecided; supply a word witness to membership_decision")
TypeError: membership of Morphism from Lattice of rank 12 and signature (2, 10) to
Lattice of rank 12 and signature (2, 10) in Subgroup of Orthogonal group O(Lattice of
rank 12 and signature (2, 10)) is undecided; supply a word witness to membership_decision
```

`1 failed in 149.51s`. The `T_Co` call fails identically after 94.78 s
(`1 failed in 98.02s` in the run of #289's test), with rank 11 and signature (2, 9) in
the same two messages.

## Where the two revisions stand

| tree | `TEn.O().discriminant_image()` | `Tco.Aut().group_generators()` |
| --- | --- | --- |
| `7519715` (with `T_En`'s test) | 1 passed in 338.76 s | — |
| `698e661` | — | 1 passed in 173.17 s |
| `a79d3e1` (this report) | 1 failed in 149.51 s | 1 failed in 98.02 s |

`698e661` and `a79d3e1` differ only by `641f869`, `158c170`, `a79d3e1`; of those, only
`158c170` touches `src/sage_extensions/categories/group/groups.py`, and the failing frames
are the ones it added or changed (`_evaluate_reduced_word`'s new `retain(value)` call,
`GeneratedSubgroups.membership_decision` becoming reachable, and
`_retain_admitted_member`).

## The gap, precisely

`IndexedFreeGroupMorphism._evaluate_reduced_word` computes the value of a word and then
calls `codomain._retain_admitted_member(value)` to record that the value is in the
subgroup by the map's range law. `SetMethods._retain_admitted_member` (`set_categories.py:4283-4300`)
opens with `point = self.universe()(element)` — the *universe* here is the generated
subgroup itself — and `GeneratedSubgroups._element_constructor_` asks `element not in
self` before it can return anything. For an infinite generated subgroup that question is
`membership_decision`, which raises while the record that would answer it has not been
written yet. The record is therefore unreachable for exactly the subgroups the commit was
written for: the admission has to be retained *without* first coercing the value through
the group's constructor (retain the representative and its identity key), or the
constructor has to consult the admitted-members record before it asks the predicate.

The commit's own message records an adjacent instance of the same `TypeError`
(`GeneratedSubgroups._engine_subgroup` calling `group(generator)`); this report's two
calls reach it through `eichler.py:901`'s `stabilizer_of_lattice().stabilizer().group_generators()`,
so they are on the same shape and are not the "supplied stabilizer family" case.

## Why this file, not an issue

This connection reads issues and cannot create them; the body above is ready to post.
