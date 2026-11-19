# The transporter is a coset, and the stabilizer is not a substitute for one

## The call

`isotropic_orbits.py:2009` `_isotropic_equivalence_witness(orthogonal_group, left, right, *, flag=False)`
returns `orthogonal_group.one()` when `_same_subobject(left, right)` holds and,
for every other pair, hands the question to the indefinite port:

    from sage_indefinite_port.indefinite.marked_lattices import isometry
    category = _marked_isotropic_category(orthogonal_group.domain(), ...)
    return isometry(category, _marked_isotropic_object(left, ...), _marked_isotropic_object(right, ...))

That port call is the open cost of this issue: one matched cusp's transporter
did not return in 355 s.  It is reached from `_CuspEngine.__eq__`
(`isotropic_orbits.py:768`), which asks for a transporter between two *distinct*
representatives, and from the incidence owner's
`transport_isotropic_object` (`:1143`, `:1150`), which builds the witness
`plane_transporter * ~line_transporter` an edge is certified by.

## The lemma

Let `G` act on a set, and let `x`, `y` lie in one orbit.  For any one
transporter `T` with `T x = y`,

    {g in G : g x = y} = T . Stab_G(x).

**Proof.**  If `g x = y = T x` then `T^-1 g` fixes `x`, so `g` lies in
`T . Stab_G(x)`; conversely every `T s` with `s` fixing `x` carries `x` to `y`. ∎

**Measured**, `L = U + U(2) + <−2>` (rank 5, signature (2,3), even), with
`P = <e_0, e_2>` and `Q = <e_0, e_3>` the two mixed totally isotropic planes,
port `991b88b0`:

| step | result | time |
|---|---|---|
| transporter witness `P -> Q` | exists, carries `P` into `Q` | 0.342 s |
| radical of `P` | 7 generators, fixing `P` pointwise | 0.067 s |
| `witness * s` for each of the 7 | all seven carry `P` into `Q` | (in the 0.5 s) |
| the same seven on `Q` | some move `Q`, so the coset is proper | (as above) |

So the transporter set is the coset and not a single element, and the seven
radical elements give seven distinct members of it.

## Refutation of the route the last round proposed

`results/issue603-the-completed-chamber-route.md`'s last section says the
transporter question "reduces to a stabilizer, and the stabilizer now has a
library-owned two-factor family".  By the lemma that is false as stated: a
generating set of `Stab_G(x)` produces no transporter, and it determines the
transporter set only once one transporter is in hand.  Replacing the port's
`isometry` by the library's stabilizer families removes nothing from this call;
what it could do is shorten the *coset*, not produce a point of it.

## What composition does give

Transporters compose: if `T` carries `x` to `y` and `S` carries `y` to `z`,
then `S T` carries `x` to `z`, and by the lemma every transporter is of that
form.  So the cost is one port call per pair of *orbit representatives* that an
edge actually needs, whenever the caller reuses the transporter it has.  The
cusps are orbit representatives and `_CuspEngine.__eq__` caches per pair, so the
355 s figure is per pair and not per plane; the warning that the `T_Co` kernel
rows must not be dispatched stands for the number of pairs those rows ask for.

## What remains

One cheap transporter between two *distinct* plane representatives of `T_Co`.
The library's only cheap case is `_same_subobject`.  Either the port's
`isometry` becomes cheap at a rank-eleven plane marking, or the library
constructs a transporter between distinct planes -- for which, by the lemma, a
stabilizer family is necessary and not sufficient.

Not dispatched this round: the `T_Co` kernel rows, which this issue's own
record forbids; the measurement above is on the five-dimensional specimen.
