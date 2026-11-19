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

## The registry already retains a transporter, and nothing reads it

`orthogonal_quotients.py:2902` `register_isotropic_lift(plane, lift, parabolic_generators, discriminant_image, *, spelling=None)`
says in its own words what it keeps: "``lift`` carries the source plane ...
**to ``plane``**", keyed by `_span_key(plane)` (`:2944`), and
`_registered_isotropic_split_of_span` (`:2958`) reads it back by span.  So for
every registered plane `P` -- with one source plane `P_0` per registry -- the
registry holds an isometry `g_P` with `g_P(P_0) = P`.

Nothing in the transporter path reads it.  `_PrimitiveIsotropicSublatticeOrbitDecompositionEngine.transporter`
(`isotropic_orbits.py:256`) calls `self.group().isotropic_equivalence_witness(source, target)`,
which is `_isotropic_equivalence_witness` (`:2009`), which is the port for any
two distinct subobjects; and `register_isotropic_lift`,
`_registered_isotropic_split` and `_registered_isotropic_split_of_span` appear
only in `orthogonal_quotients.py` -- not in `isotropic_orbits.py`, not in
`lattice_morphisms.py`, and not in the incidence row script.

**Lemma.**  Let `g_i` and `g_j` be the registered lifts of two planes `P_i`,
`P_j` of one registry, so `g_i(P_0) = P_i` and `g_j(P_0) = P_j`.  Then

    g_j g_i^-1  carries  P_i  to  P_j,

and every transporter of `P_i` to `P_j` is `g_j s g_i^-1` with `s` fixing `P_0`.

**Proof.**  `g_j g_i^-1(P_i) = g_j(P_0) = P_j`.  If `h` carries `P_i` to `P_j`
then `g_j^-1 h g_i` carries `P_0` to `P_0`, which is the previous section's
coset statement. ∎

**Consequence: the port call is not necessary, only current.**  For two
registered planes a transporter is the composite of two retained lifts.  The
355 s is a property of the routing
(`transporter -> isotropic_equivalence_witness -> port`), not of the
mathematics, and the retained data that would replace it already sits one owner
away.

**What remains, sharpened.**  Route the transporter through the registry:
return `g_j g_i^-1` when both spans are registered and fall back to the port
otherwise.  The read is by span (`_registered_isotropic_split_of_span`), and a
cusp's whole datum is its span, so the two ends fit without a new key.  What is
not yet checked is whether the incidence rows register the plane cusps they
then ask transporters for -- the #381 record says the row registers its lifts by
span, and that read is the thing to verify before the routing change is made.

Not measured this round beyond the coset numbers above: whether the row's own
planes are registered needs the row's construction, which is its own run.

## The check: what a registry entry is relative to, and why the composite needs it

The routing change this record proposed last round needs one thing verified
first, and the answer changes the proposal: **an entry is a lift of *its own
row's* representative, and the record does not keep the representative.**

`register_isotropic_lift` stores, at `_span_key(plane)`
(`orthogonal_quotients.py:2944`),

    ( lift or its spelling,  tuple(parabolic_generators),  discriminant_image )

and the walk that fills it registers the plane it transported with the element
that carried that row's `representative` there:

    transported = splitting.transport_isotropic_object(representative)
    quotient.register_isotropic_lift(transported, splitting, family, ...)

(`_iter_transported_planes`, `:4425`-`:4430`), while the representative itself
is registered with `quotient.supergroup.one()` (`:4361`, `:4383`).  So every
entry's lift carries *that row's representative* to its plane, and the
representative is not among the three recorded fields.

**The corrected lemma.**  For two planes `P`, `Q` registered against the *same*
representative `P_0`, the composite `g_Q g_P^-1` carries `P` to `Q`.  For two
planes registered against different representatives `P_0 != P_0'` it carries
`P` to `g_Q(P_0)`, which need not be `Q` at all.

So the previous round's "the two ends fit without a new key" is **too strong**:
the key says which plane an entry is about, and says nothing about which plane
its lift starts from.  Two entries of one registry can be relative to different
sources, and then the composite is not a transporter.

**What is recoverable, and at what cost.**  The source is *implicitly* in the
record: the recorded family generates the source plane's parabolic, whose fixed
isotropic plane is the source.  So a reader could group entries by "same fixed
plane" -- by comparing the recorded families.  That is a group-generation
comparison per pair, not a lookup, and it is the very kind of computation this
route exists to avoid.  Within one row the grouping is free (one family object),
which is the case the incidence rows are in when both of their cusps come from
the same walk -- and the row's own note says the drawn representative is not
reproduced by a second process, so across rows it is not.

**What to do instead.**  Record the source span in the entry -- a fourth field
beside the lift, the family and the finite element -- and the composite becomes
a lookup: `g_Q g_i^-1` where both entries name the same source, and the port
otherwise.  That is a change at the registry's owner and one read in the
transporter, with the port kept as the fallback for planes of different
sources.  It is not made in this round: the registry is shared machinery, and
the change wants its own test on a lattice whose row registers at least two
planes.

## The registry exists only where a character quotient does

Run of the `O` row on `U+U(2)+<-2>` (rank 5, signature `(2, 3)`) at port
`991b88b0`, through the row's own entry points:

    [O] the row's route: certificate, taken because it is the ambient orthogonal
        group, which retains no character quotient and so carries no
        divided-class datum (decided in 0.0 s)
    [O] line cusp 0: ((1, 0, 0, 0, 0),)      [O] line cusp 1: ((0, 0, 0, 1, 0),)
    [O] plane cusp 0: ((1, 0, 0, 0, 0), (0, 0, 0, 1, 0))
    [O] edge 1: L1 < P0; plane=((0, 1, 0, 0, 0), (0, 0, 0, 1, 0))
    [O] decided: 2 edges over 2 line cusps and 1 plane cusps          (42.16 s)

and `subgroup.finite_character_quotient()` **raises** for the ambient group
(`predicate_subgroups.py:507` answers only a subgroup whose characters are
known complete).

So the registry, which lives on `OrthogonalCharacterQuotient`, does not exist
for the `O` rows at all: the ambient rows carry no divided-class datum and no
lift registry, and their plane transporters go to the port by construction.
The registry route is available only for `Gamma_{Co,2}`, `Otilde` and
`Otilde+`, whose quotients do exist and are cached, so one registry persists per
subgroup object.

**Consequence for the routing change.**  It is scoped: it can remove the port
call for the three character rows and cannot touch the ambient `O` rows.  The
355 s figure was recorded as "one matched cusp" without naming the row, so the
first thing the next round needs is that name: on a character row the registry
route pays, on an `O` row it is irrelevant and the remaining route is the
certificate route's own plane transporter, which this note does not cover.

**What the small row also shows.**  At rank five the whole `O` row decides in
42.16 s, two edges over two line cusps and one plane cusp, and the second edge's
plane has a different span from the cusp's -- so a transporter between distinct
planes is genuinely used, and the port answers it in seconds at that size.  The
355 s is a rank-eleven figure, and nothing here measures its split between the
port's two halves.

## The source is already recorded, in the registry the kernel rows use

The 355 s figure is not in this tree: it is the session record's sentence that
"the kernel rows on `T_Co` stay unrunnable (189720 planes × 355 s +)".  So the
row is a **kernel** row, `Otilde` or `Otilde+`, and those are exactly the rows
that have a character quotient.  Running them at `U+U(2)+<-2>` (rank 5) through
the driver's own entry points, port `991b88b0`:

    [Otilde]  the row's route: divided-class ... decided in 0.0 s
    [Otilde]  3 line cusps, 2 plane cusps, 4 edges, calls returned in 25.6 s
    [Otilde]  the quotient retains 4 carried-object transport datums ... each
              holding the object, its source and the isometry that placed it
    [Otilde]  decided: 4 edges over 3 line cusps and 2 plane cusps      (36.67 s)
    [Otilde+] the same relation, calls in 4.7 s                          (index 4)

and `_isotropic_lift_registry` -- the certificate route's registry, the one the
three earlier sections of this note are about -- is **empty** for both: four
registered spans, zero, because the kernel rows do not take the certificate
route.

**The correcting fact.**  `orthogonal_quotients.py:2860` `transport_covering`
composes exactly the element this note's lemma builds:

    move = lift * ~reference_lift

"the composite that carries the reference plane onto the target", and the
registry behind it, `_isotropic_covering_registry`, records per plane
`(source, span, lift, flags)` (`:2844`, `:2857`) -- **the source field whose
absence the previous section reported, under another name, already populated by
the route the kernel rows take.**

So the sharpened position is:

* the source *is* recorded, and the composite *is* implemented, for coverings
  (`transport_covering`), and `isotropic_lift_of(other)` reads the registered
  lift that carries the covering's source plane onto `other`;
* what is missing is only the transporter's route: `transporter(source, target)`
  asks the port, while `lift_target * ~lift_source` would answer it whenever
  both planes are registered against one covering source;
* the earlier "add a fourth field to `register_isotropic_lift`" is **withdrawn**:
  it would duplicate a field the covering registry already keeps.

**Next.**  Route `_PrimitiveIsotropicSublatticeOrbitDecompositionEngine.transporter`
through the covering registry: if both spans are registered against the same
covering source, return `lift_target * ~lift_source`; otherwise the port.  The
test that this is worth doing is the one the kernel rows already pass at rank
five (36.67 s and 4.7 s for four edges); the cost it removes is the one the
session records at rank eleven.

## The routed transporter on the cheap consumers

The Coble consumers of the change did not finish locally -- the two row files
were still on their first test at the 1200 s cap -- so the first collected
evidence for the route is the incidental consumers of the module it lives in,
at port `991b88b0`, load 2.80:

    tests/lattices/test_pointwise_levi_images.sage
    tests/lattices/test_the_pointwise_radical_of_a_primitive_isotropic_line.sage

    8 passed in 38.52 s; slowest call 5.55 s
    (test_the_odd_nonreflective_line_has_an_integral_levi_lift)

two of those calls on the plane case of the split lift
(`test_split_pointwise_levi_lift_over_an_infinite_quotient[plane]`), which is
where a transporter between two distinct planes is asked.  Collection took
27.87 s against the 6 s ceiling, as it does on this tree under load.

The rank-eleven measurement the route exists for -- the `Otilde` row on `T_Co`
under its own cap, which is what fills the covering registry there -- is
bounded and was still inside its cap when this was written; its result is the
next thing to land, as either the measurement that closes this issue's cost or
the refutation that sends it to the cross-row bridge.

## At rank eleven the row dies before the registry is written

The bounded run this record asked for: the `Otilde` row on `T_Co` (rank 11,
signature `(2, 9)`), row cap 600 s, port `991b88b0`, load 2.80 at start:

    [Otilde] the row's route: divided-class, taken because its lines carry
             divided classes and its covering is carried from one plane to the
             others (decided in 1.8 s)
    [  604.52s] outcome: [Otilde] undecided: the row did not return inside its 600 s cap
    [  604.52s] registered transports: 0

Peak tree RSS 1486 MiB, inside the 6144 MiB guard.

**The covering registry is empty when the cap fires.**  The row does not reach
the point where a covering, and with it a transport, is registered, so the
transporter route cannot help it -- not because the composite is wrong (it is
proved, and green at rank five where the same rows decide with and without it),
but because there is nothing registered to compose.  The guard added in the
transporter falls through to the port exactly as designed, and the port is not
what the row is spending its time in.

**So the 355 s transporter is not the first obstacle at `T_Co`.**  Whatever the
divided-class route does before it registers its first covering is, and the
row's own log names that step: "its covering is carried from one plane to the
others".  The first covering -- the flags over one plane, and the line orbits
within it -- is computed before any transport exists, and that is where the
rank-eleven run sits at 600 s.

**What this does to the last four rounds.**  The routing change stands on its
own measurement: at rank five the kernel rows decide with their calls in 17.0 s
and 3.4 s instead of 25.6 s, and `isotropic_transport_between` is the library's
own implementation of the coset lemma.  But it does **not** make the `T_Co`
kernel rows runnable, and the sentence that "the port is the remaining cost"
was wrong for that lattice: the covering computation comes first.

**Next.**  Instrument the first covering of one plane at `T_Co` -- which step
of it is running at the cap -- rather than the transporter.  Nothing else about
this issue can be measured at rank eleven until that step is named.

## The step, named by stack dumps

The row was run at `T_Co` under a 240 s cap with `faulthandler.dump_traceback_later(30, repeat=True)`;
eight dumps came back at port `991b88b0`, load 1.15.  They are two stacks, not
one, and neither is the transporter.

**Stack A -- the cusps, through the port's cell machinery** (in six of the
eight dumps):

    tests/.../coble_gamma_co_2_incidence_rows.py:477 row_relation
    predicate_subgroups.py:1259  tits_building_incidence_by_divided_classes
    predicate_subgroups.py:803   cusps
    orthogonal_quotients.py:4736 _yield_subgroup_isotropic_orbit_representatives
    lattice_morphisms.py:5507    isotropic_orbit_representatives
    isotropic_orbits.py:2019     _isotropic_orbit_representatives
    isotropic_orbits.py:1821     _isotropic_plane_orbit_representatives
    isotropic_orbits.py:1781     _planes_through_line
    port isotropic_induction.py:75/100  isotropic_vector_classes
    port lorentzian_cells.py:3433       global_orbits
                                       -> local_stabilizer_orbits (3368)
                                       -> cell_primitive_rays (1173)
                                       -> cell_cone (1020)
    polyhedral_cones.py:336/159   from_rays -> PPL polyhedron construction

So the cusps themselves are what the column cannot afford: the planes through a
line are produced by the port's Vinberg-cell enumeration at rank eleven, and
the row is inside `Polyhedron` for whole dump intervals.  This is why the
covering registry is empty at the cap -- no plane is cusped yet, so no covering
is carried and no transport is registered.

**Stack B -- word evaluation paying source introspection** (three of eight):

    groups.py:4792/4795 _evaluate_reduced_word -> _signed_generator_image
      -> _admitted_generator_image (4728) -> groups.py:3784 __call__
      -> lattice_morphisms.py:3620 one()
      -> mor_foundation.py:441/359 __get__ / _copy_operation_metadata
      -> sageinspect.py:2493 sage_getsourcelines -> inspect.getsourcelines

Every realized generator pays `sage_getsourcelines`, i.e. a source-file read and
parse, because `_copy_operation_metadata` reads `reading.__doc__` inside a
`try` and the docstring's own note says that read runs `sage_getsourcelines` on
a generated class: it is documented as a *correctness* workaround ("that
failure made `O(T_En).one()` raise") and it is also what the dumps catch.

**What that changes.**  The remaining cost of the `T_Co` kernel rows is (A) the
cusp enumeration through the port's cell machinery, and (B) a library-side
introspection bill on every realized word.  (B) is small and local --
`_copy_operation_metadata` can skip the descriptor read rather than pay it and
catch -- and it is the only one of the two that is this library's to fix; (A) is
the port's cell walk, which is a different owner's cost.

**Next.**  Take (B) first: measure one realized word with and without the
`__doc__` read, and if the dumps are telling the truth it is a one-line
change with its own test.  (A) is then a question for the port, not this issue.
