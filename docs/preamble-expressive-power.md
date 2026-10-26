# Preamble completeness: mathematical constructions and composition

The inspected preamble has gaps in effective image factorizations, finite
limits and colimits, quotients, and preservation of the categories justified
by a construction. The gaps differ between groups, modules and sets;
several module constructions already supply actual objects and universal
maps. A foundational semantic defect affects several
stabilizer constructions: string labels occupy fields that should retain
actual represented actions. The subgroups exist, but their defining
mathematical structure is incomplete. Computed generating data also fail
to return mathematical families.

## Standard of completeness

A public construction must return the mathematical object or morphism it
promises, in its preamble category. It must retain the defining data and
structural maps required by that construction. Those results must be accepted
by the other applicable public constructions.

For example:

- A subgroup is an object with a monomorphism into its ambient group.
- A generating family is represented by its index set and generator map,
  or by the resulting free-group epimorphism.
- An image supplies its inclusion and the factorization of the original map.
- A section is a morphism with a specified right-inverse equation.
- A quotient supplies its projection and universal factorization.
- A product or equalizer supplies its universal cone and factorization.

A primitive Python container is private computation data. A public result
containing preamble elements in such a container still lacks the mathematical
family or morphism that the operation promises.

Source tracing below establishes what
the constructors retain and return. It does not certify their answers.

## Image objects, presentations and category placement

For `f: M -> N` in `R-Mod`, the required image is an actual submodule
`I = im(f) <= N`, with maps

\[
M\xrightarrow{e}I\xrightarrow{i}N,\qquad i\circ e=f,
\]

where `e` is surjective and `i` is the submodule inclusion. If selected
generators of `M` are supplied, their images generate `I`. When `I` is
finitely presented, selected generators and relations define a finite
presentation `R^a -> R^b ->> I`. These are mathematical data of the
submodule; the API must return that submodule and its maps.

The group requirement is the same image factorization, with a subgroup
inclusion. Finite generation of the source supplies finite generators of
its image. Finite presentation of the result requires its own hypotheses
and relations.

Each limit or colimit must retain its diagram, cone or cocone, and universal
factorization. Products and coproducts require projections and injections.
Kernels require inclusions; cokernels and quotients require quotient maps.
General finite diagrams compose products with equalizers, or coproducts
with coequalizers, under the applicable existence hypotheses.

The result must also carry every mathematical structure that the
construction preserves. Closure hypotheses matter. Over a coherent
commutative ring, finitely presented modules form an abelian category;
over a Noetherian ring, finitely generated modules do too. Their images,
kernels and cokernels then remain in those categories. See the
[Stacks Project, coherent rings](https://stacks.math.columbia.edu/tag/05CU)
and [abelian categories of modules](https://stacks.math.columbia.edu/tag/0AZ5).
An ambient kernel that is not finitely generated cannot be assigned to the
category of finitely generated objects merely because its endpoints lie
there.

## Missing or defective parts of the public constructions

Source paths in this table are relative to
`sage_extensions/categories/`.

| Primitive | Required mathematical output | Observed defect |
| --- | --- | --- |
| Image of a group morphism | `G ->> I -> H`, with `I` a subgroup of `H` and the composite equal to the input map | The ordinary image route requires a GAP realization even for an evaluable map with known source generators. It returns the subgroup, but the inspected factorization method accepts only monomorphisms. A general image factorization is not supplied by that route. |
| Section of a surjection in sets | `s: U(I) -> U(G)` with `U(e) s = id` | A public method computes selected preimages but returns a dictionary. The corresponding section is absent from its output. |
| Generating data for a subgroup | A represented family in the subgroup and its generating epimorphism `F(S) ->> P` | Public Schreier methods return tuples. The computed family and augmentation are not supplied as preamble objects attached to the subgroup. |
| Retention of mathematical defining data | Actual objects, morphisms and functors, with their defining diagrams | Several stabilizer constructors retain string labels as their defining actions. This foundational semantic defect prevents composition through the promised action datum. The subgroup objects and inclusions do exist. |
| Group products and coproducts | Actual groups, projections or injections, and universal factorization maps | Both routes require nonempty families of finite groups. They exclude infinite finitely presented factors. |
| Group equalizers and coequalizers | Equalizer subgroups or quotient groups, with universal maps | No category-level realization was found in the inspected group owners. Normal-closure quotients from chosen finite presentations already exist. |
| Group cokernels | The quotient by the normal closure of the image, with its quotient map | The inspected route accepts finite codomains or subgroup inclusions into abelian groups. |
| Pullbacks and pushouts | The apex, both legs and universal factorization | The general methods return equalizer or coequalizer results without selected pullback or pushout cones. |
| Quotient of a represented set by a relation | A quotient set, projection and universal factorization | The general set coequalizer implementation requires finite source and target sets. It does not represent the quotient of an infinite relation by that route. |
| Class set of a represented groupoid | The quotient of objects by isomorphism, with its class projection | The inspected core retains objects and isomorphisms. Genus enumeration returns lattice representatives without a distinct class projection or representative section. The general quotient route has the preceding finiteness restriction. |
| Image of a module morphism | An actual image submodule, inclusion and induced surjection | The inspected finite-generator route returns an actual submodule. Its factorization composes with the existing module `factor_through` operation. The image method rejects infinite selected generating families. |
| Empty module products and coproducts | The zero module with its universal maps | The biproduct constructor rejects the empty family. The product constructor uses the general module route for the empty family and rejects stricter module categories. |
| Preservation of category structure | One result carrying the structures preserved by the construction | General submodule joins and meets do not retain ideal structure; ideal specializations maintain separate implementations. |

The following sections give the construction traces and boundaries of these
findings.

## Group images and explicit morphisms

For an established group morphism `f: G -> H`, if
`G = <g_1,...,g_n>`, then

\[
I=\operatorname{im}(f)=\langle f(g_1),\ldots,f(g_n)\rangle\leq H.
\]

Forming this generated subgroup supplies the image. Its mathematical
construction also includes `i: I -> H` and `e: G -> I`, with
`i e = f`. Computing relations, enumerating elements and selecting
preimages are further operations. GAP's
[homomorphism handbook, §40.3](https://gap-system.github.io/gap/doc/ref/chap40.html)
describes image computation by mapping a source generating set.

The source has construction paths for parts of this structure:

- `groups.py:1441` constructs a generated subgroup from preamble generators.
- `GeneratedSubgroups` at `:4562` retains an owned generating set and
  constructs a selected free-group augmentation.
- `Subgroups.inclusion` at `:4502` constructs a group Mor.
- `IndexedFreeGroupMorphism.image` at `:1888` maps its finite free basis
  and calls the generated-subgroup constructor.
- `Subgroups.image_under` at `:4509` maps subgroup generators and returns
  a generated subgroup of the target.

The ordinary `GroupMorphism.image` at `:2291` instead calls
`_gap_morphism_crossing`. That method at `:2167` rejects a morphism
constructed only by an elementwise rule. Thus a known generating family and
an evaluable group map do not compose through this public image operation,
although the generated-subgroup construction exists.

The nearby `factor_through` route at `:2336-2371` requires both input maps
to be known injective. It therefore cannot supply the image factorization of
a general noninjective map. The missing part at this owner is the general
factorization, together with uniform construction of the generated image
from the map's retained data.

Generator-defined morphisms at `:2049-2128` retain their generator images
and use the source's private presentation to evaluate words and check
relations. This establishes that the generator-map construction exists.
Whether its selected source presentation supports effective word decomposition
is a further computational question; it is not needed to
form an image from already given generator images.

## Sections and subgroup generating data

For the image surjection `e: G -> I`, chosen preimages define

\[
s:U(I)\longrightarrow U(G),\qquad U(e)\circ s=\operatorname{id}_{U(I)},
\]

where `U: Groups -> Sets` is the underlying-set functor. This is a
morphism in sets. Multiplication preservation is additional structure and
cannot be inferred from the choice of preimages.

`groups.py:3479-3563` computes a finite table of such choices and returns
a dictionary. The public mathematical output must be the section in its
set Hom. A table can realize that section privately. GAP provides selected
element preimages through
[`PreImagesRepresentative`, §32.5-4](https://gap-system.github.io/gap/doc/ref/chap32.html).

There is an existing example of the correct output form:
`OrbitRepresentativeSets.section` at `group/g_sets.py:1054` returns
`Sets().Mor(...)(representative)`. Thus sections are already expressible
as actual morphisms; the table-producing group operation fails to return
one.

The same boundary appears in computed generating data:

- `PredicateSubgroups.finite_index_schreier_generators` returns a tuple
  at `group/predicate_subgroups.py:162`.
- Kernel and inverse-image Schreier methods return tuples at `:517`
  and `:646`.

Their elements belong to the preamble subgroup, but the tuple is not a
represented generating family or epimorphism. The existing
`GeneratedSubgroups` construction shows how to retain those mathematical
data. The computed data must be presented for the actual subgroup, with
its existing inclusion, so that subsequent group maps can consume them.

## Mathematical data replaced by string labels

A label cannot supply the mathematical object it names. Where a construction
requires an action, its defining datum must be the represented action, with
its acted-on object and maps. The same requirement applies to morphisms,
functors and structural inclusions. Descriptive text supplies no such data.

The default `GObjects.stabilizer` route at `group/g_objects.py:1115`
does construct a preamble subgroup:

1. It calls `StabilizerSubgroups(G)`.
2. That construction inherits `PredicateSubgroups(G)`, which inherits
   `Subgroups(G)` (`predicate_subgroups.py:37,411,653`).
3. It constructs the object through `_object_of`, retaining the ambient
   group and the membership predicate.
4. The subgroup inherits its ambient group operations and
   `Subgroups.inclusion`, whose result is a group Mor
   (`groups.py:1851,4502`).

This trace establishes the subgroup result and its inclusion.

`GObjects.stabilizer` passes `"pointwise"` as its action argument.
`StabilizerSubgroups.stabilizer_action` returns that argument
(`predicate_subgroups.py:653-698`). The actual action remains inside the
membership closure. This is a foundational loss of defining data, recorded
in the original source audit; the later stabilizer-owner repair replaces these
labels with represented actions, while terminal execution remains outstanding.

The defect recurs in normalizers (`groups.py:3603`), lattice stabilizers
(`lattice_morphisms.py:2029,2048,2079`) and finite decomposition groups
(`group/profinite/galois_decomposition.py:129`). Their action fields contain
`"conjugation"`, `"pointwise"`, `"setwise"` or `"prime ideal"`.
For embedded subobjects, the lattice constructors also retain only the source
module as the stabilized object, leaving the embedding in the membership
computation.

The retained construction must expose the actual action and stabilized
point or subobject, with the subgroup inclusion. Otherwise its defining
diagram, action restrictions and transport cannot compose through that
datum. The general action owner already exposes actual `action_functor`
and `action` maps (`group/g_objects.py:995,1022`); these provide existing
mathematical structure for the stabilizer construction to retain.

Generator computation for this subgroup has the public-output defect
described above. A generating description must remain data of the same
subgroup and compose with its inclusion and applicable group morphisms.

## Finite limits, colimits, cokernels and quotients

The group product constructor at `groups.py:2997-3067` constructs an
actual product group, group-morphism projections and a
`SelectedLimitConstruction` for nonempty finite families of finite
groups. This supplies real structure in that case. Its explicit assertions
exclude the empty family and any factor not known to be finite.

The coproduct constructor at `groups.py:3068` supplies the free product
and its injections, but imposes the same restrictions on the factors. Thus
both category operations exclude infinite finitely presented groups even
though finite presentations give the usual constructions. For example,
from `G = <x | R>` and `H = <y | S>`, the free product has presentation
`<x,y | R,S>`, and the direct product adds the relations `[x_i,y_j]=1`.

No category-level equalizer or coequalizer realization was found in the
inspected group owner files. This is a gap in the general group operations,
not evidence that quotient construction is wholly absent:
`quotient_by_relators` at `groups.py:3468` uses existing free-group or
finite-presentation quotients. For parallel group maps `a,b: G -> H`,
their coequalizer is the quotient of `H` by the normal closure of
`a(g)b(g)^-1`. A generating family of `G` suffices for these relations.

The later 2026-10-14 source delivery supplies group equalizers,
coequalizers, empty diagrams, finite (co)products involving chosen
finite presentations, and selected pullback/pushout cones. The product
and free-product *universal factor maps* now use owned legs and the
chosen factor embeddings or presentation generators rather than
requiring a GAP model of their arbitrary cone/cocone apex. Their
object computation retains the explicitly admitted presentation
hypotheses. Independent runtime acceptance awaits terminal T.

The group cokernel route at `groups.py:2383-2415` supplies a quotient group
and projection for finite codomains and for subgroup inclusions into abelian
groups. It rejects other cases, including the general chosen-presentation
case for which normal-closure quotient construction already exists.

At the general category owner,
`Cat.fiber_product` (`abstract_categories/cat.py:840`) constructs a
product and returns the equalizer of the two induced maps. It does not
retain the cospan as a selected pullback construction with both legs and
universal factorization. Dually, `Cat.pushout` at `:901` returns a
coequalizer result. Both composite constructions need their own universal
cones or cocones. The pullback work is owned by `pullbacks-in-every-category`.

The general diagram owner at `abstract_categories/products.py:1592-1836`
already constructs finite limits from products and equalizers, and finite
colimits from coproducts and coequalizers. The missing category operations
therefore obstruct those existing compositions.

### Modules

The module owners already implement these constructions:

| Operation | Construction at the inspected owner |
| --- | --- |
| Product | `modules/pure/modules.py:744` constructs a finite biproduct for selected free or finite-presentation data, or a module of tuples through the underlying-set functor. It retains the product cone and universal factorization. |
| Finite coproduct | `:798` uses the biproduct, retaining injections and universal factorization. The biproduct computation accepts chosen free bases or finite presentations (`:4928`). |
| Equalizer | `:829` constructs `ker(f-g)` for chosen finite presentations, or the submodule where the underlying maps agree, with its inclusion and universal cone. |
| Coequalizer | `:916` constructs `coker(f-g)`, with its quotient map and universal cocone. Its effective coverage depends on the cokernel computation. |
| Cokernel | `modules/module_morphisms/module_morphisms.py:1939` returns an actual quotient module; `:1964` returns its quotient map. Selected finite-presentation computation adds the generator images as relations. |

Their coverage is incomplete, rather than uniformly absent. The finite
biproduct constructor rejects an empty family (`modules/pure/modules.py:4928`).
For an empty product, the product constructor selects the general module
construction and asserts that the requested category is all modules
(`:744,4470`). This excludes the zero object from that route in stricter
module categories, including finitely presented modules. The chosen
finite-presentation cokernel route requires finite selected source
generators and a chosen finite presentation of the target
(`framed/finitely_generated/finitely_presented_modules.py:2803`).

The source construction of a kernel from chosen finite presentations selects
PID, CAP or Singular computations (`:2265`). The presence of this route
does not establish algorithm coverage over every base ring. The relevant
data are the ring, module generators, relations, maps and hypotheses of the
chosen computation.

### Sets and class quotients

For sets, `_categorical_coequalizer_construction` at
`sets/set_categories.py:1178` returns an actual quotient and a
`SelectedColimitConstruction`, but requires both the relation source and
the target set to be finite. A finite quotient can have an infinite relation
source, so finiteness of the answer does not satisfy that restriction.

The action owner already supplies a more general represented quotient:
`_OrbitSet` and `_orbit_set` (`group/g_sets.py:567,632`) retain the
action and return a preamble orbit set with a set-morphism projection.
Enumeration is restricted separately to finite acted-on sets. The general
set quotient construction must admit general relation diagrams and retain
its universal maps.

The 2026-10-14 source delivery now introduces a generated-equivalence
quotient retaining the actual parallel maps, projection and universal
factorization for arbitrary relation source sets; finite enumerated cases
retain the selected disjoint-set algorithm. Effective equality and class
cardinality for nonenumerated generated relations, including computing
the finite parity quotient from black-box maps on an infinite source,
remain outstanding. The construction does not assert a finite class
count without a certified classification.

For the source-defined integer translations `t_d(n)=n+d`, selected
displacement data now provide that classification without sampling:
`coeq(id_ZZ,t_d)=ZZ/(d)` as sets, and a wide family of selected
translations is `ZZ/(d_i-d_0)_i`. The ordinary ring quotient computes
the ideal, congruence classes, cardinality and chosen representative
for universal factorization. The unresolved statement above concerns
only arbitrary black-box set callbacks and unrelated infinite generated
equivalence relations, for which no translation law is certified.

For a represented small groupoid `C`, its class set is the coequalizer
of source and target on its arrows:

\[
\operatorname{Arr}(C)\rightrightarrows\operatorname{Ob}(C)
\longrightarrow\pi_0(C).
\]

The 2026-10-14 source composition exposes this coequalizer at
`Cat.ParentMethods.class_set_construction` for categories with a selected
finite object set and complete owned arrow set. For the one-object
groupoid `BG`, its original `Mor_BG(*,*)` supplies the arrow set even
if `G` is infinite, and the quotient of the singleton object set is
the singleton itself. The construction retains source, target,
projection and universal factorization; no enumeration is inferred
from an abstract groupoid without selected objects and arrows.

This is a composition of category data and the set quotient primitive.
The core constructor at `abstract_categories/arrow_categories.py:2035`
supplies invertible arrows, not this quotient. In the genus facade,
`lattices.py:776-807` enumerates selected lattices and admits arbitrary
lattices of the genus as members. It supplies no separate class projection
or representative section.

The formal class set already exists in `lean-categories`:
`Lattices/Valued/Mass.lean:92-104` defines `genusClassSet`,
`GenusClass` and `classNumber`. The presentation gap is at the quotient
and genus owners; a list of representative lattices does not supply the
formal class-set maps. The existing
`genus-finiteness-parity-and-classification` node owns the genus presentation.

## Module images and arithmetic constructions

`ModuleMorphism.image` at
`modules/module_morphisms/module_morphisms.py:1204` constructs an image
submodule from the images of a finite selected generating family.
`ModuleSubobjects` (`modules/pure/modules.py:2996`) retains its actual
ambient inclusion. The selected finite-presentation `subobject_on` route
constructs the submodule from a free cover and the kernel of its spanning
map (`framed/finitely_generated/finitely_presented_modules.py:718`).

For this case, the induced surjection can be constructed by
`f.factor_through(f.image().inclusion())`.
The module factorization route at
`module_morphisms/module_morphisms.py:1510-1544` accepts a noninjective
source map and returns an actual module morphism. Thus these inspected
module operations already compose to supply the image factorization.
The image method itself asserts that the selected generating family is
finite; outside that case, it returns no image submodule through this route.

This limitation propagates into the otherwise mathematical intersection
construction at `modules/pure/modules.py:3105`: it composes a biproduct,
a kernel, projections and an image. Its applicability therefore depends on
whether those operations supply actual submodules and maps for the input
modules, with their selected data and hypotheses.

### Preservation of mathematical categories

Category placement is a separate requirement from obtaining an isomorphic
abstract result. A preserved structure must remain attached to the same
constructed object, with its maps and inherited operations.

An observed example is the sum and intersection of commutative ideals.
These are the general sum and intersection of submodules of the regular
module, and their results are again ideals. The general module-subobject
constructions return only module subobjects; the ideal owners preserve ideal
structure by maintaining separate computations. The existing
[source-audit finding](#preservation-of-mathematical-categories)
records this failure to transport the preserved category structure. A later
source repair (2026-10-14) installs the structure-preserving realization at
`ModuleSubobjects` and routes the ideal specialization through its protected
construction contract, preserving the selected localization, quotient-source
and exact engine ideal computations. The source specimens are banked; no
execution claim is made before terminal T. This does not establish closure
of other arbitrary structural subobject categories.

### Arithmetic maps

The lattice owner supplies actual maps for some arithmetic constructions.
For example, `lattices.py:3476-3574` builds an integral extension and
returns an embedding in `self.Emb(enlarged)`, with images in the target
lattice. The public result is the inclusion, not the private Gram data.

The public isometry and automorphism-generator constructions have an
unfulfilled local computation dependency. Their indefinite branches at
`lattice_morphisms.py:2215,2593` import
`sage_indefinite_port.indefinite.recursive`. That module was not found in
the inspected local port source. A selected isometry must be an element of
the isometry Mor; computed automorphism generators must be represented
generating data of the automorphism group. These construction cases remain
unestablished in the inspected provider comparison.

## Compositions

The general primitives above must support expressions such as:

- Restricting a group morphism along a subgroup inclusion and forming its
  generated image.
- Taking an inverse-image subgroup and using its computed generating
  epimorphism in another group map.
- Restricting an action along a subgroup inclusion.
- Forming a pullback from products and equalizers.
- Taking a groupoid's class quotient and composing its class projection
  with another invariant.
- Selecting representatives by a section and evaluating other maps on them.

Finite double cosets are an orbit quotient for
`(h,k).g = h g k^-1`. They compose group products, actions and quotient
sets; they do not require a separate mathematical primitive. The source has
finite group products, permutation-image computation for finite actions,
and represented orbit sets with projections
(`groups.py:2997`; `g_sets.py:263,567`).
GAP also supplies the private
[DoubleCosets computation](https://gap-system.github.io/gap/doc/ref/chap39_mj.html).

## Evidence boundary

This audit is dated 2026-10-11. It inspects the named research owners at
`68261c6bfb`, local `lean-categories` at `29ff4adef9`, and local
`sage-indefinite-port` at `993029fe54`.

The findings are construction and return-value facts established from
these source paths. Runtime behavior, algorithm completeness and the
released formal registry were not checked. The subgroup result is
established by its construction trace; arithmetic correctness remains
subject to the independent mathematical acceptance suite.
