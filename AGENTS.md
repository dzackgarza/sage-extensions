# Agent rules

These rules govern writing the mathematical library.

## Preamble coding prerequisites

Read the normative [preamble architecture specification](CONTRIBUTING.md#preamble-architecture-specification)
before changing preamble construction, representation, or engine integration.
It owns the intended architecture; the TODO owns only the unfinished work.
Read the relevant issues in the [native issue tree](https://github.com/dzackgarza/research/issues/46)
for observed foundational gaps and papercuts. Each issue owns its requirements,
evidence, acceptance, dependencies, and closure.

When the owner calls an engineering move "standard", "the usual way" or "how it is done", the standard is this repository's own `CONTRIBUTING.md`, this file and the terminology dictionary before it is anything external (for mathematics the standard is `lean-categories`): look the move up there first, and survey prior art only for what they do not state. On 2026-09-17 the qualified-predicate rule (`LEX-02`) was looked up in Sage, which has no such notion, instead of in `CONTRIBUTING.md`, which does.

Before writing or editing code under `src/dzack_research/preamble/` or in sage-extensions (`sage_extensions`), first read the root [TODO.md](https://github.com/dzackgarza/research/blob/main/TODO.md). It contains only unfinished work, its priorities, mathematical contracts, dependencies, acceptance criteria, and active file reservations. Use it according to the rules below.

Use [COMPLEXITY.md](https://github.com/dzackgarza/research/blob/main/COMPLEXITY.md) to score work and select a model and reasoning effort.
The [TODO workstream table](https://github.com/dzackgarza/research/blob/main/TODO.md#workstreams) records the DAG task scores and their reasons.
Apply the guide to the responsibility actually assigned, including any shared contract design or orchestration it requires.

Read the megadoc's usage guide and the affected entries as routed by the [reading index](https://github.com/dzackgarza/research/blob/main/docs/edit-reading-index.md#generated-reference-lookup) before writing code. Reading `src/dzack_research/utilities/megadoc.py`, the generator script, does **not** satisfy this requirement. When execution is authorized, regenerate a stale megadoc with `just preamble-megadoc` and read the affected entries. While `DEV-58` suspends execution, use the existing megadoc as an index, inspect live source for the affected owners, and retain regeneration under terminal T. The prerequisite never overrides the execution phase.

`just preamble-megadoc` surveys a live session, so it also writes `docs/preamble-graph.json` — every category with its supercategories, subcategories, ancestry and the operations it introduces, plus every functor's domain and codomain — and `docs/preamble-graph.dot` with the rendered `docs/preamble-graph.html`. Query the JSON with `jq` for the questions the prose cannot index, such as which category owns a given operation.

These are implementation prerequisites: use them to identify already-planned remediation, existing mathematical constructions, known architectural failures, and outstanding archive-port work before adding or changing code.

## Construction and engine boundaries (always-on)

**The preamble's primary engineering purpose is presenting `lean-categories`'
mathematics and organizing existing implementations behind it, not inventing
another CAS.** Read the
[design philosophy](CONTRIBUTING.md#preamble-design-philosophy) together with the
architecture specification. Interpret an ordinary feature request as integrating
existing capabilities through shared preamble constructions. Local code supplies
the actual missing semantic integration; a genuinely new algorithm requires the
demonstrated gap and explicit engineering decision in `ENG-06`, and is an
untrusted computation like every other.

This applies to shared categorical computation as well as specialized theories.
Moving bespoke logic into the framework or an adapter does not make it reuse.
Conversely, using an upstream algorithm never authorizes exposing its objects:
the public interface and every constituent remain preamble objects.

**Present all public mathematics through preamble objects; reuse maintained
computation privately.** Apply
`OWN-01` through `OWN-14` in the
[architecture specification](CONTRIBUTING.md#preamble-architecture-specification).
Neither correct numerical output nor private naming excuses a different path.

- **Enter where `lean-categories` places the operation.** Locate the category/object method
  and defining constructor before editing a consumer. Direct construction,
  notation, functor images, catalogue examples, and raised engine results must
  establish the same defining datum. Public morphisms use `Mor`. An importable
  global factory or concrete implementation class is not a sanctioned alternative.
- **Thread every structure.** Each level constructs through its immediate
  mathematical owners and introduces only its own datum. Elements, endpoints,
  actions, differentials, inclusions, projections, and inherited operations must
  agree with that construction. A category label is not missing construction data.
- **Raise every constituent.** Public results, lazy family values, coefficients,
  base rings, representatives, maps, and arithmetic results are preamble objects.
  Returning a preamble parent containing publicly reachable foreign mathematics
  violates the boundary. No public raw-engine ingress or egress is authorized.
- **Keep private access at its owner.** Ordinary mathematical code calls preamble
  operations, never another object's engine accessor or storage. A protected
  protocol requires the declaration-side contract in `OWN-05`; an underscore,
  import, helper extraction, or comment at the call site does not grant access.
- **Reuse algorithms at the right level.** Search existing preamble constructions
  and maintained computational packages before adding logic. Inspect the result
  and map contract, not just the method name. A low-level library call inside a
  locally rebuilt standard algorithm does not satisfy reuse. Framework suitability
  and computational suitability are separate decisions.
- **Repair the prerequisite.** If the sanctioned route cannot express the needed
  construction, repair that exact owner before extending its consumer; if what is
  missing is mathematics, request it from `lean-categories` and park the consumer. Do not add
  an unchecked constructor, raw representation route, or local algorithm to keep
  the diff small. Report a genuine scope/authority obstruction without supplying
  the wrong object. Do not turn this into an unrelated framework rewrite.
- **Review the route as well as the answer.** Read from the public entrypoint
  through its defining data and private adapter to the preamble result and
  induced maps. Use specimens to distinguish the promised object from its
  convenient substitute; source review establishes architectural reuse. Both are
  engineering review and certify nothing about correctness, which only the
  `lean-cas-dsl` acceptance suite judges.
  Follow `DEV-58` for the execution phase, not a new local checking workflow.

The architecture specification also owns the required construction factorizations
and upstream discovery references. Update that contract when the user decides an
architectural change; do not make a TODO, comment, or local example a competing
specification. These rules bind existing consumers as well as new code. Earlier
source or archive examples are not permission to reproduce a boundary violation.

## Threaded specialization and universal constructions (always-on)

**A specialization inherits or composes the general construction; it never
maintains a parallel implementation.** Apply
[`OWN-14`](CONTRIBUTING.md#own-14-specializations-inherit-or-compose-their-general-construction).
Honest inheritance establishes the general defining data and keeps inherited
operations usable. Composition stores an actual owned instance of the general
construction and delegates to it. Category labels, copied methods, equivalent
answers, or a diagram attached after independent construction do not qualify.
The general datum, maps and operations have one authority; the specialization
adds its own structure and a realization a `lean-categories` theorem justifies,
not another general API.

For limits, colimits, systems, completions, and related constructions, first read
the normative
[limits and colimits contract](CONTRIBUTING.md#limits-colimits-and-structured-specialization).
It fixes the general diagram language, universal maps, construction theorems,
restriction directions, and mathematical distinctions required below.

- Place arbitrary represented indexing categories, functors, cones/cocones,
  restrictions and induced maps at the common categorical owner. Directed and
  inverse systems specialize that language; they do not define it by sequences.
- Use products/equalizers and coproducts/coequalizers under their existence
  hypotheses. Category-specific operations specialize that same construction;
  do not compute a second generic result or recurse through the same constructor
  merely to demonstrate threading.
- Retain each construction's diagram and universal cone/cocone even when a
  maintained engine realizes its result. Preserve every constituent as a preamble
  object, including lazy stages. Do not store caller-specific presentation
  data on a shared result object or duplicate it in a leaf implementation.
- Expose finite restrictions of the represented system with their indexing
  maps. Keep the full object, restricted diagram, stage and element precision
  distinct. No finite prefix substitutes for an infinite object; no arbitrary
  directed index is silently replaced by the natural numbers.
- Distinguish existence, representation and effective computation. Preserve the
  correct category and universal property even when a particular computation
  is unsupported. Ordinary, homotopy and higher-categorical constructions must
  retain their own maps and coherence; a strict formula is not a universal
  homotopical shortcut.

These are mathematical threading requirements for the selected consumer, not
authorization to build every conceivable foundation first. Record actual gaps
under `DEV-59`, request missing mathematics from `lean-categories`, and implement
the remaining shared presentation with its consumer.

# Mathematical structure as implementation compression

An advisor can compress a large mathematical correction into one short
question.  The student must unfold the structure that makes the correction
true.  The question is not a request for the smallest compatible patch.

Consider an integral domain \(R\) and its fraction field
\(K=\operatorname{Frac}(R)\).  The advisor asks why ideals are not presented as
\(R\)-submodules of the regular module \(R\).  The advisor also asks why an
integral basis is not an \(R\)-basis of the relevant integral \(R\)-algebra.
These are not two method requests.  They expose one missing mathematical
foundation.

Scalar extension relates the algebra and module categories:

```text
Alg_R  -- K tensor_R (-) -->  Alg_K
 | U_R                         | U_K
 v                             v
Mod_R  -- K tensor_R (-) -->  Mod_K
```

The vertical functors take the underlying modules.  The horizontal functors
change scalars.  Their compatibility explains how algebra structure, module
structure, bases, subobjects, and morphisms move together.

For an integral \(R\)-algebra \(O\), its base change can give a
\(K\)-algebra \(A\):

\[
K\otimes_R O \cong A.
\]

The integral basis then belongs to the underlying \(R\)-module of \(O\).
It is not a new tuple-valued operation attached directly to \(A\).  The same
base-change structure gives \(K\otimes_R R[x]\cong K[x]\).  Polynomial rings
and number-field algebras therefore belong to one scalar-change theory.

This theory is implementation compression.  Ideals can use module and
subobject operations.  Bases can use the free-module structure.  Algebra
morphisms can move through scalar extension.  Many apparent missing methods
become consequences of structures that `lean-categories` formalizes and the
repository already presents.

The failed trajectory hears only the word "basis".  It asks PARI for
elements and returns a tuple in \(A\).  It can also take a chosen
\(K\)-basis and clear denominators.  Both actions produce local data while
leaving the algebra and functors absent.

Clearing denominators selects a presentation-dependent \(R\)-lattice.  It
does not by itself select the integral closure or a maximal order.  It gives
no coherent action on morphisms.  It therefore cannot explain later basis,
ideal, or transport operations.

Rejecting a Sage order wrapper does not remove the mathematical order.  It
makes ownership of the integral \(R\)-algebra more important.  PARI can
compute data used to construct that object.  PARI cannot replace the object
or the functorial structure around it.

The advisor's question reveals why dozens of methods remain missing.  Their
absence is not necessarily a backlog of local implementations.  It can show
that one theoretical foundation is absent.  Once that foundation exists,
the apparently difficult work can become generic and small.

The lesson is not a rule that functors always precede methods.  The lesson is
to recognize mathematical compression.  A deep correction can change which
work exists at all.  Preserving the old implementation with a cheap
workaround preserves the misunderstanding that created the work.

# Search the formalization corpus first (always-on)

`lean-reference-corpus` checks out and
indexes the pinned Mathlib, every registered Lean formalization repository, the Reservoir packages,
and the Rocq and Agda port sources as one searchable tree. One query asks the whole formal
literature: *has this been stated, and where?*

```sh
curl -s https://formalization-corpus.dzackgarza.com/api/search \
  -H 'Content-Type: application/json' \
  -d '{"Q": "IsometryEquiv file:\\.lean$", "Opts": {"MaxDocDisplayCount": 20, "ChunkMatches": true}}' \
  | jq -r '.Result.Files[] | "\(.Repository)  \(.FileName)"'
```

The keys are capitalized (`Q`, `Opts`). `NumContextLines` and `Whole` return context or whole files; `/api/list` lists the indexed sources.

**It is the first approximation for mathematical work of every kind here, not only Lean.** Sage
code, preamble categories, notebooks and prose all state mathematics that somebody has probably
already written down precisely, and a formal statement is the most precise form the literature
has: it fixes the hypotheses, the codomain, and the generality that a paper leaves to context.
Search it, with `lean-categories`, before deciding what a definition says, before adopting a
name, and before filing a `lean-categories` request. No notion is this project's to invent,
and this project writes no proofs.

A miss is a dated, scoped result — *not found in the corpus at the index it currently holds* —
and never the claim that nobody has formalized this. Widen to upstream Mathlib, Loogle, LeanSearch
and GitHub before recording a negative, the way the reuse gate in `lean-categories` does.

**The corpus locates a notion; it does not rule on a field it has barely formalized.** Lattice
theory over number fields (duals, `A`-modularity, genera, discriminant forms) is thin and partly
wrong in Mathlib. There the authority is `lean-categories`' formalization of the number-theory
literature — arXiv papers, Kirschmer, O'Meara — and a notion it lacks is requested there with
those sources. The maintained implementations in Hecke/Oscar are untrusted computations and
never an authority on what a notion is. A Mathlib definition is cited for such a notion only
when it agrees with those sources.

# Performance claims (always-on)

**Never report a call count as an efficiency metric.** Not "2,502 constructions",
not "~3 million calls to `coordinate_ring`", not "it runs 484 times". A count is
not a cost: a million cheap calls can be free and four hundred expensive ones can
be the whole run, so the number carries no information about what to fix and
invites optimising the wrong thing.

Report **wall time as a function of \(n\)** — how the cost grows with rank,
order, number of generators, size of the input — or report nothing. A single wall
time for one specimen is a data point, not a claim about efficiency; it becomes
one only when a second size shows the shape. Where a profile is the evidence,
quote its *time* columns, never its `ncalls`.

Call counts remain legitimate as **diagnosis**: they locate a recursion, name the
function that repeats, and prove a cascade exists. Use them to say what is
happening, never to say how expensive it is.

A claim about *why* something is slow is held to the same standard as a claim
about how slow it is. A named cause with no measurement behind it is fabrication
unless it is written as a hypothesis in words that cannot be read as a result.
`DEV-62` owns the rule; *Every task is an instrument* below owns the moment it
applies.

# What optimization is for (always-on)

The dominating concerns are legibility, auditability by a mathematician,
elegance, cohesion with the preamble's style, and doing the mathematically
principled thing rather than raw numerics. If that costs performance, so be it.

Never take apart code that reads as the correct mathematical sequence of steps in
order to make it faster. A method whose body a mathematician can check against the
definition is worth more than a fast one they cannot.

Optimize **waste**, which is a different thing entirely:

- needless recomputation — the same value derived again because nothing carried it;
- needless enumeration — ranging over an object where generators, a presentation,
  or a matrix identity answers (see the enumeration rule);
- needless verification — re-deriving a theorem, a definition, or a fact the
  caller already established;
- a general algorithm applied where the object's own structure has a better one —
  the fix there is to give the structure its own category and let placement pick
  the algorithm, never to special-case inside a general method.

Removing waste usually makes the code *more* legible, because what remains is the
mathematics. That is the tell that it was waste.

Caching is the default shape of a method that computes a datum of an object
(*Construction is instant* below), not an optimization. A genuine hot path that
needs `case`/`match` dispatch is a design change: propose it and discuss it
explicitly first. Reaching for a cache to make one slow call fast, or for a
literature constant in place of a computation, before finding out *why*
something is slow, is not optimization — it is hiding the defect. Reaching for a
different library is the same move with a worse consequence: it also deletes
the site where the cost would have been measured (`ENG-07`, `ENG-08`).

**Test specimens are small by default.** A test of invariants,
coinvariants, or \(O(L)\) does not need \(E_8\), a K3 lattice, or an Enriques
lattice. \(U\) has the swap involution; powers of \(U\) already give interesting
combinations; their orthogonal groups are finite and their invariants and
coinvariants are quick. Reach for a large specimen only when the claim is about
that specimen.

# Construction is instant; checking is asked for; loops are tensors (always-on)

The preamble is a symbolic system. It proves nothing, so construction has
nothing to establish. The caller who places an object in a category, or builds
a morphism from its data, is trusted to have supplied data with the properties
the category states. Every construction in the tree moves to this shape;
`OWN-22` and `OWN-24` are the reviewable rules.

- **Construction is almost instant.** It stores the defining datum and fixes
  the category, and nothing else. It computes no invariant, no inverse, no
  group generators, no presentation and no check.
- **Computation is lazy and cached.** A datum of an object (`O(L)`'s group
  generators, an inverse, a Gram matrix of a sublattice, a genus symbol) is
  computed on the first request, cached on the object, and reused by every
  method that needs it.
- **Checking is a validator, never inline.** A well-definedness condition
  (linearity, isometry, equivariance, injectivity, an algebra's relations) is a
  validator method of the object. Construction calls the validators once,
  after the object exists, and each validator returns at once unless the
  global strict-checking flag is on. The pattern is pydantic's post-init
  validator with an early bail. Anyone can call a validator by hand, for a
  critical result or for extra assertion guarding. No check is written into
  `__init__`, an element constructor or a computation.
- **The strict flag is global and is for exploration.** One session-wide
  setting turns every validator on. It is off by default, and no code turns it
  on for its own benefit.
- **A loop over pairings is a tensor contraction.** Mathematics written as an
  imperative loop is almost always one tensor operation done slowly: the
  pairings of many vectors are one contraction, and `f` preserves forms when
  the pullback `f^* b_W` equals `b_V`. Write the tensor equation. Numerical
  optimization lives behind the tensor interface (vectors, covectors,
  matrices, morphism tensors), never in the mathematical code that calls it.
- **Coordinate conventions exist only inside `preamble/tensors/`.** Which side
  a matrix acts on, and where a transpose falls, is fixed once there.
  `Tensor.pullback` holds the only `A^t G A`. Everywhere else, code states
  pullback, composition `f * g`, inverse `~f` and application `f(v)`, so
  `M^t G M` and `M G M^t` cannot be written, and no call site chooses between
  them. An owned morphism's framing-dependent `transpose()` is a morphism
  operation, not a Sage coordinate transpose. `just tensor-boundary` rejects
  recognizable unowned coordinate operations outside the package. A green
  textual gate does not prove categorical ownership. Identify the actual
  tensor or form morphism, selected family and map, their source and target,
  and the owner of the pullback or contraction. An `einsum` replacing a raw
  matrix product at the consumer is still the same architectural violation.
  Conversely, a genuine typed morphism `transpose()` stays at its Mor owner,
  even if a syntax-only checker mistakes it for an engine matrix operation.
  Fix checker classifications using that provenance; never ask the owner to
  choose between relocating a mathematically correct public API, suppressing
  its semantics, or accepting an unreviewed bypass.

Some conditions cannot be checked at all. The Fourier transform is an isometry
of `L^2(RR)`, and no finite computation confirms it. A construction that
checked its laws could not build that morphism, so a construction never checks
its laws.

*The false belief:* "constructing an object verifies it". It makes every
construction pay for a proof the system cannot give, and the cost compounds
through every construction built on top. On 2026-10-07 the test that builds
`O(E_6)`, a group of order 103680, took 72.8 s. Almost all of that time was preamble
overhead: each isometry was checked at construction, and each check rebuilt
the form at 60 ms a call.

*The tell:* a check, `assert`, `.inverse()`, `is_injective()` or generator
computation inside `__init__` or `_element_constructor_`; a `check=True`
default; a `for` loop over pairs of vectors, roots or basis elements; a
`sum(... for ...)` over pairings; a method that recomputes a datum on every
call.

# The preamble is a universe over Sage (always-on)

The live package is sage-extensions (`sage_extensions`), imported by the session preamble `src/dzack_research/preamble/`. This ownership contract governs
the live package; `archives/preamble/` is prior implementation material, not an
alternate API contract.

The preamble is a layer over Sage, not a collection of helpers.
Once a session loads it, the mathematician stops receiving raw Sage objects: everything reached from the preamble is an owned object, which may or may not use a Sage object underneath.
The stated purpose is *owned uniformization*.

What it exists to fix is Sage's non-uniformity, not Sage's algorithms.
Sage carries more than ten distinct notions of *group*, and an operation as elementary as $\operatorname{Aut}(G)$ is, depending on which one you hold: absent; present under a different name; known and simple but unwired (it is a call into GAP); or genuinely uncomputable.
A session cannot hold that variation, so the preamble presents one name for one mathematical operation, and either answers or asserts.

The preamble owns no mathematics. Each operation it names is one formalized in `lean-categories`, which alone decides what the operation is, where it lives and what it returns. An operation `lean-categories` does not have is a formalization request there ([below](#a-missing-foundation-parks-the-work-that-found-it-always-on)), never a name the preamble coins.

This governs the rules below:

- Sage objects are an implementation detail. The crossing happens inside owned code, at the point of computing, never in what a session receives.
- Where Sage spells one mathematical operation several ways, the preamble picks one spelling and the others do not exist in the session.
- Where Sage has no algorithm, the operation keeps its name. A missing capability is a stated gap on the interface, never a second spelling and never a silent absence.
- An engine defect is the preamble's to repair, now, in the owned route. When Sage's routine is wrong, partial or missing, the preamble computes the operation correctly itself: it repairs the result, uses the routine only where it is measured correct, or implements the cited mathematics with the engine's routine as a reference implementation. It never waits for an upstream fix, and no node, ruling or gap is ever "wait for Sage". Reporting the defect upstream is courtesy and is never a dependency. A consumer such as lattice-db never sees the engine and never routes around it; it calls the preamble operation, and that operation is correct. On 2026-10-09 a TODO node offered "wait on a repair of Sage's `siegel_product`" as an option for the Siegel product, and the owner ruled it out.
- A session is a Sage session with the preamble loaded on top: Sage's names stay in scope and the preamble's shadow them. A session's numbers never enter Sage's symbolic ring. The preamble binds `pi`, `e` and the elementary functions (`sqrt`, `exp`, `log`, the trigonometric and hyperbolic functions, `sgn`, `zeta`) to its own real-number implementation (ruled 2026-09-23); applied to anything that is not a real number, each is Sage's function of the same name.

# A missing foundation parks the work that found it (always-on)

Research work meets missing foundations constantly. The move is always the
same, and it is not a judgment call:

1. **Park** the node you are on. It is not abandoned and not deferred; it is
   waiting on something that was just discovered to be underneath it.
2. **Build the DAG of what it needs**, down to what already exists, and
   terminating at the node you were doing. Every missing piece of mathematics
   in it is a formalization request to `lean-categories`, never a research node
   that writes it (below).
3. **Add the edges**, so the parked node now `Needs:` the foundation.
4. **Take a ready node** from the bottom of what you just built, or any other
   ready node that does not wait on the request.

**Missing mathematics goes upstream to `lean-categories`.** A definition,
category, construction, operation or theorem that research needs and
`lean-categories` does not have is requested there, stating the mathematics
wanted and its sources. Its own formalization author writes it there, blind to
research and to every implementation. It is never hand-rolled in research or
in a leaf: not as a local definition, a substitute category, a temporary notion
to reconcile later, or a Lean file here. Until `lean-categories` formalizes and
releases it, research has no such notion.

**Independent implementation work can continue while a formalization request
is open.** That work does not introduce the missing notion into the public
language: declaring its category, operation, type or mathematical meaning waits
for the formal owner. A computation for an already declared operation can be
implemented through its existing contract without waiting for unrelated
formalization. Computations discharged entirely in Lean belong to the formal
side, as required by the evidence model above. Research implementations supply
answers through declared contracts and cannot supply the missing semantics.

You never proceed past an observed mathematical deficiency. Not with a note
attached, not with a substitute in place, not with a `TODO` at the site. The
work is genuinely blocked, and the blockage is a discovery about the shape of
the problem rather than an obstacle to route around.

**The failure this prevents has a specific shape: recording the gap and
continuing.** Filing the deficiency in an issue and leaving the work
queue untouched produces a document that describes the hole and a queue that
still schedules work over it. It feels like diligence -- the observation was
real, it was written down carefully, and the note is true. What makes it a
failure is that the DAG, which is the thing that actually selects work, was
never told. Nothing downstream changes, and the next worker inherits the same
queue and walks into the same hole.

So the test, applied before continuing past anything you have just called
missing:

> **Which issue's native blocked-by relation changed?**

If the answer is none, the foundation was observed and not acted on.

The issue records *why* the work is owed, with its dependency path and evidence,
under `DEV-59`. Native tree order and blocked-by relations schedule it.
Read that record through itree. Recording evidence alone does not establish
the prerequisite relation.

**Scope is a real question, and it is answered by the DAG, not by scoping the
mathematics down.** The prerequisite chain terminates at what exists, so a
foundation whose own prerequisites are already present is a short chain, and
one that is not is a long one. Discovering the chain is long is information
about the problem. It is never a reason to declare the original node ready,
nor to weaken it so that the foundation is no longer required.

# A misstep is a population, not a slice (always-on)

When a construction is found to contradict the architecture, repairing the object in
front of you is the smallest part of the work, because the hand that built it built its
siblings. Before the slice is repaired, four things are established and filed:

1. **How it entered.** The commits that introduced it and what they recorded. An empty
   body, or a checkpoint that adopted a working tree "as it stands", is itself a finding.
2. **The mental model that produced it**, written as the false belief so the next reader
   recognises it: "threading means re-running the lower constructor with extra data";
   "an existing object can never gain structure, so build a copy"; "the pattern for a
   datum is a `WithChosenX` subcategory". The false belief is mathematical before it is
   procedural, and the account names it as mathematics. The code's partition of a
   category is never a theorem about the objects: on 2026-09-17 the tree's split of
   `Algebras(R)` into a nonassociative root and a unital associative refinement holding
   the structure morphism was read as "a Lie algebra has no structure morphism", an
   impossibility manufactured from the code's shape and then "solved" by a generalization
   (the centroid) that the question never needed. A Lie algebra is an algebra: an
   $R$-module with an $R$-bilinear multiplication satisfying two more identities. Over
   commutative $R$ the datum $(M, m)$ already is the structure, $\rho$ is the scalar
   action of $M$, and the textbook case over a field carries over unchanged. Derive the
   mathematics independently of the tree first; the tree's shape is one of the things
   being judged.
3. **Where else it stands**, measured by an observable tell -- a grep a reader can rerun --
   per subtree, never by a judgment of intent, and named in the node by the mathematics
   it fails; an engine class appears only as the file it lives in. Each population becomes
   a DAG node with one loop body.
4. **Which rule would have prevented it.** If the rule exists and was violated, the node
   cites it. Check later owner rulings, the mathematical authority, and the applicable
   protected-test policy before calling two rules conflicting. An old expectation or
   migrated complaint does not reopen a choice already settled there. If two governing
   rules still conflict after that check, record their exact incompatible prescriptions
   for the owner to rule on; do not place an undecided implementation choice in the
   executable queue. If no rule exists, write it at its owner -- `CONTRIBUTING` for
   construction and naming, this file for always-on doctrine -- in the same commit
   that files the nodes.

A correction that reframes a finding never deletes it. When the owner corrects the
account of a misstep, the observation stays and is refiled in the corrected terms;
retracting it is the slice failure again. A deviation from the stated architecture is
debt and is filed the moment it is seen, however it was found.

A definition or theorem asserted while giving this account is opened from a source
first -- the formalization corpus, a text -- never recalled. The centre of a nonassociative
algebra was asserted from memory on 2026-09-17 where the definition is the centroid
(Mathlib `CentroidHom`), and the question built on it was wrong.

# A supercategory entry presents a formalized inclusion (always-on)

`super_categories()` states that **every object of this category is an object
of those**. It presents a theorem `lean-categories` states about the objects, not
a slot to fill so that construction proceeds, and it is read by inheritance: an
object receives the operations of everything its category declares. The
mathematics recalled in this section is `lean-categories`'; where the two
differ, the formalization governs, and an inclusion it does not state is not
declared.

So a declaration that is merely *available* is a false statement installed where
nobody looks for one. The recurring shape is `Sets()` written where the objects
are not sets:

- a **sheaf** on a space $X$ is a functor on $\mathrm{Open}(X)$, so it is an
  object of a functor category;
- a **ringed space** is a space together with a sheaf of rings;
- a **manifold** is a locally ringed space;
- a **log pair** is a scheme together with a divisor.

None of these has an underlying set that its category could be declaring, and
where one *does* exist the declaration still belongs to the forgetful functor,
never to the object. `Sets()` in such a row is the value category of some
functor in the construction, leaked upward into the slot where the object's own
category belongs.

**A false declaration is never an admissible state, and recording it elsewhere
does not make it one.** Filing the gap while the wrong supercategory stays in
the source leaves every reader and every object inheriting the false statement;
the issue text is read by nobody executing the code. There is no
ranking here in which the wrong claim is the better of two states.

When the honest supercategory is not presented in the tree, there are two
moves and nothing else:

- **Present the missing category, if `lean-categories` formalizes it.** This is
  usually the answer, and it is usually smaller than it looks, because the
  general construction is already presented. Presheaves needed no new theory:
  `[C, D]` is the functor category and `C^op` the opposite, both of which the
  tree presents. If `lean-categories` does not formalize it, request it there
  ([below](#a-missing-foundation-parks-the-work-that-found-it-always-on)) and
  make the second move until it is released.
- **Declare nothing.** `super_categories()` left abstract, so the category
  cannot be used until its placement is known, is honest and fails loudly.
  `OwnedCategoryOverBaseRing` already does this. A category that refuses to
  construct is a working signal; one that constructs into the wrong place is a
  silent wrong answer that propagates through everything it touches.

Record the gap in the native issue tree under `DEV-59`, with its dependency
path and the consumer it blocks. That is the record of *why* the node is
missing -- never a licence to keep a substitute in the source while it stands.

**Presheaves and sheaves are functor categories.** $\mathrm{Presh}(C) := [C,
\mathbf{Set}]$, a functor $\mathrm{Cat} \to \mathrm{Cat}$; more generally
$(C, D) \mapsto [C, D]$ is a bifunctor $\mathrm{Cat} \times \mathrm{Cat} \to
\mathrm{Cat}$, which is the same construction the tree already presents as its
functor category. Sheaves on $C$ are the full subcategory of $\mathrm{Presh}(C)$
cut out by descent for a coverage. Stating them this way is what makes the
passage to stacks and $\infty$-stacks a change of value category rather than a
new theory (`https://ncatlab.org/nlab/show/infinity-stack`). Any sheaf-like
category -- quasi-coherent sheaves, invertible sheaves, structure sheaves,
sheaves of modules or of algebras -- is placed under that construction as
`lean-categories` formalizes it, never under `Sets()`.

## Reading the declarations

The declared graph is read out of the source with `ast`, so it never imports
the preamble and answers while that tree is mid-refactor and does not load.
The graph theory is Sage's -- homology, minimum cycle basis, transitive
reduction -- so the recipes run under Sage's own interpreter:

```bash
just category-graph                     # every category, and what it declares
just category-graph by-supercategory    # each supercategory, and who claims it
just category-graph foreign             # owned categories declaring a Sage category
just category-graph shape               # breadth, depth, shortcut declarations
just category-graph cells               # homology, and the cycles owing a 2-cell
just category-graph-svg                 # the literal graph, rendered
just category-graph constructions       # each construction on objects, and where its result is placed
just category-graph routes              # where objects reach an operation's fallback assertion
```

The `by-supercategory` view is the audit surface: a large group under one
heading is one mathematical claim made many times over, and reading the members
together is how a member that does not belong becomes visible. Run it after any
change to a category's placement, and read the group the change lands in rather
than the single row it adds. `just category-graph audit` reports what needs no
reading of the objects: a name declared as a supercategory and defined nowhere,
a declaration computed from a local expression so the edge is not stated at
all, a category declaring its own name, and cycles.

`just category-graph constructions` is the audit surface for placement of
results. For each category it lists every operation on its objects that builds
an object, with the category the source places the result in and the property
of an input that changes that placement. Each line is a statement a
mathematician reads and rejects on sight when it is wrong: under `PowerSets`,
`X.from_predicate(predicate)` is an object of a slice category that places no
property of its base object, so a subset of a finite set is not placed finite.
The view does not decide which placement is correct; the reader does, and needs
no prior knowledge of a defect to see one. Run it with `--select CATEGORY` after
any change to a construction, and read every line of the categories the change
touches. `just category-graph routes --operation NAME` then shows which
categories' objects reach the fallback assertion of an operation such as
`cardinality`. `docs/architecture-inspection.md` gives the full list of views.

The live survey (`just preamble-megadoc`) answers a different question -- what a
session *does* -- and its `supers` field is empty for parameterized categories,
so it must never be read as evidence that a declaration is absent.

## Every declaration is the immediate one, and factoring is mandatory

Declaring `C -> D` asserts a forgetful functor $U : C \to D$. The rule is that
$U$ must be **atomic**: one step of structure, not a composite.

> **The factorization test.** Ask, from `lean-categories` alone: is there a
> category $A$ with $C \to A \to D$, where $A$ is a category that carries
> operations? If yes, the declaration `C -> D` is wrong and must be
> replaced by `C -> A`. **This holds when $A$ is not presented in the tree.**
> Then presenting $A$ is the work. If the literature has such an $A$ and
> `lean-categories` does not, it is requested there.

Run the test on the formalized mathematics, never on the code. Reading the category list
first and picking the nearest available node inverts the whole thing: it makes
the current contents of the tree decide what is true, so every gap becomes
permanent the moment something is declared across it. Name the categories the
objects actually pass through, and only then find out which of them exist.

The bar for $A$ is that `lean-categories` formalizes it, with a definition and
operations of its own -- convex bodies, topological spaces, labelled graphs, modules.
Inventing a node so that a rule is technically satisfied is the over-compliance
failure this repository bans everywhere else: a category with no mathematical
referent is worse than the unfactored edge, because the edge is at least
visibly wrong. If the intermediate has no name in `lean-categories` or the
literature, that is a signal to check the notion, not licence to coin one.

## The shape the graph is converging on

**A near-tree: high depth, low breadth.** Depth is what atomic declarations
produce -- a long chain from a leaf to `Sets()`, each step adding exactly one
structure, every operation inherited from the level that carries it. Breadth at a
node is how many categories declare it directly, and it is the diagnostic:

| Reading | What it means |
| --- | --- |
| High breadth at a node | The intermediate categories between it and its claimants are missing. Breadth counts unfactored edges. |
| High breadth at `Sets()` | The worst case: the claim that those objects share nothing but their points. |
| A short path from a leaf to `Sets()` | Structure is being restated at the leaf instead of inherited. Expect duplicated operations, and look for them. |
| A category declaring two or more levels up | A shortcut edge. It duplicates a path that already exists and adds a loop that carries no information. |

Breadth at `Sets()` is never zero: some objects are sets with structure and
belong there. The question is never the count, it is whether each member's own
definition puts it there.

## $\pi_1$, and what is actually being minimized

The declared graph is a 1-dimensional complex: a 0-cell per category, a 1-cell
per declaration, and no higher cells. So $H_1$ is the whole cycle space,
nothing bounds, and $\pi_1$ is free of rank $E - V + C$. A generator is a pair
of distinct paths $C \rightsquigarrow D$, hence two composites of forgetful
functors that the graph asserts are equal, and **the 2-cell that would fill it
is that assertion\'s proof**, which is `lean-categories`'. The complex has none. Nothing checks that assertion: Sage
computes a C3 linearization, so a diamond that does *not* commute never raises
-- it silently selects one route, and the object's inherited operations are
whichever the ordering picked. **Each generator is a coherence obligation and a
site where method resolution can quietly return the wrong answer.**

`just category-graph cells` computes the homology and a minimum cycle basis, so
each generator is a short readable square rather than a wandering path. An
axiom category is a vertex of its own, `Modules.FinitelyGenerated.Torsion`,
whether it is a nested class or only named in a declaration, and it declares
each vertex with one axiom fewer; that is Sage's join, so a generator lying
inside one base's axiom lattice is listed as a computed join, not as a cell
owed. Every
generator lies inside one 2-connected block, and the view lists the blocks
first: a near-tree has only small ones, so a block of a hundred categories is
the region where declarations mesh, and it is the finding, never something to
route around. The view then
separates the generators killed by deleting one declaration -- where one route
is a single edge and the other a path with the same endpoints, so the two
composites are the same functor -- from those owing a real cell. The first kind
are unearned: they add a cycle and no reachability, and removing them costs
nothing, which is why keeping the transitive reduction is minimizing $\pi_1$.

**The trap.** Taken raw, "minimize $\pi_1$" favours the graph this section
exists to prevent. A star is a tree, so thirty categories each declaring only
`Sets()` has rank zero; you can drive $\pi_1$ to zero by deleting every
intermediate category, and a single point is perfectly coherent. The criterion
is therefore **minimal $\pi_1$ among graphs that state every true forgetful
functor and only immediate ones**. Factoring an edge through a newly presented
category adds one vertex and one edge and leaves the rank unchanged, so
presenting a missing intermediate category is free by this measure. The rank
rises only where a genuine join appears, and that loop is wanted, because it is
a theorem `lean-categories` states.

Genuine multiple inheritance is real -- $\mathbf{Z}$ is a ring and a module and
a monoid. Those diamonds are **computed**, as joins and axioms, so that
commutativity follows from the join construction instead of being asserted
again at every site that happens to need it.

## Red flags

Each is observable in the declaration itself, with no judgment of intent:

- `Sets()` declared by a category whose own docstring describes a structured
  object -- a sheaf, a space, a pair, a complex, a matrix, a diagram.
- A declaration naming a category two or more levels above the one being
  declared.
- A supercategory chosen because it is what the tree has, rather than what the
  objects pass through. The tell is a declaration that nobody could derive from
  the category's own definition.
- A supercategory added so that construction proceeds, or so that one inherited
  method becomes reachable. Placement presents a `lean-categories` theorem about
  the objects; it is not a way to obtain a method.
- A declaration no `lean-categories` inclusion supports.
- A leaf implementing an operation that a category on its path already carries.
  That is evidence the path is missing, and the fix is the path, not the leaf.
- Any node whose breadth grew in the change you are about to commit.

A category declaring itself over a lower base, `Modules(R)` declaring
`Modules(S)` along `S -> R`, is a red flag of its own kind. Restriction of
scalars is a functor obtained from the category, never a declaration: Sage
applies every axiom of a category to every declared supercategory
(`CategoryWithAxiom.super_categories` joins `category._with_axiom_as_tuple(axiom)`
over the base's supercategories, category_with_axiom.py), so the declared
edge would make `Modules(QQ).FinitelyGenerated()` a subcategory of
`Modules(ZZ).FinitelyGenerated()`, a false statement for every property stated
relative to the base. Ruled 2026-09-16; `TRAPS.md` holds the engine fact.

# How the preamble presents the mathematics (always-on)

The rules below are the shapes that recur across unrelated categories. Each states
how the preamble presents what `lean-categories` says an object *is*; the *tell*
names the code shape or phrase that shows up while the drift is happening, when
the category involved is not the one a past record named. The mathematics these
rules recall is `lean-categories`'; they recall it to fix the presentation, and
where they differ from the formalization, the formalization governs. The vault
holds the episodes; this section is the contract.

**The preamble presents categories through its own classes; it never
monkey-patches Sage's.** When the preamble needs a category that
`lean-categories` formalizes, it presents it through its own class. Private
adapters lower the preamble object's data to Sage and raise results through the
same construction contracts. Sage parents and elements are never reclassified or
exposed as the owned objects. Installing
an axiom or a method onto one of Sage's own category classes (`setattr` on
`Groups`, `Modules`, `Category_module`, ...) is the legacy mechanism this project
is migrating away from: it makes Sage's spelling the public surface, splits
authority between two class hierarchies, and breaks silently when two copies of a
class exist in one process. The preamble's category is the single surface; Sage's
classes stay unmodified and are consumed, not extended. Tests assert against the
preamble surface, never against Sage's spelling of a notion the preamble presents.
*The tell:* `setattr` whose target is a class imported from `sage.*`; an axiom or
accessor that only exists because the preamble injected it into a Sage category; a
test asserting membership through `sage.categories.*` for behavior the preamble
presents; a stub declaration on a Sage class for a member Sage does not have.

**Enrichment is of two kinds, and which one applies is a fact about the mathematics, as `lean-categories` formalizes it.**
*Determined* enrichment adds structure the object itself determines — a free algebra *is*
the free module on $\mathrm{Mon}(S)$, a subobject is the object together with its own
inclusion, an axiom is a property of what is already there. The forgetful functor is
injective, so the enriched thing is the same object with more categories. *Chosen*
enrichment adds structure the same underlying object supports many of — many forms on
$\mathbb{Z}^2$, many $G$-actions on $\mathbb{Z}^n$ — so the forgetful functor is not
injective and the enriched thing **is its own object**; collapsing many structures onto one
parent would collapse distinct mathematics.

The construction chain makes the structured object an object of its weaker
categories. A lattice inherits module operations through that chain; it does not
implement another module and forward every operation to it. Distinct choices of
form or action on the same input remain distinct structured objects.

A received module is retained as defining data. `M.equip_bilinear_form(R, b)`,
`Modules(R[G])(M, rho)` and `Algebras(R)(M, m)` use the one constructor of their
category; the specified accessor returns that exact `M`. Keeping this datum is
required, not evidence of a wrapper. A second implementation of the weaker
operations, or an `equip_*`/`forget_*` identification pair connecting it back to
`M`, is the prohibited duplication. Elements pass through the owner-established
coercion. The category carries its forgetful functor; no object-level `forget_*`
forwarding API is introduced.

`CON-16` and `OWN-15`--`OWN-17` own this distinction. Actual mathematical maps
remain mandatory: inclusions, projections, selected resolutions and bases, scalar-change
units/counits and genuine chosen isomorphisms are not wrapper identifications.
A free algebra's generating module and its full underlying module are different
mathematical data and must not be merged merely to remove a source accessor.

**All of this holds uniformly across objects, elements and arrows.** The public owned
protocol is `ObjectType`, `ElementType`, `HomCatType`, `EndCatType`, `AutCatType`, with
`ArrowType`/`EndArrowType`/`AutArrowType` the corresponding Hom-category element types.
A morphism of $\mathbf{C}$ is an *element of* $\mathrm{Hom}_\mathbf{C}(A,B)$, and Hom/arrow
categories are ordinary objects of `Cat`; there is no third public "morphism methods"
mechanism. Sage's `ParentMethods`, `ElementMethods`, `MorphismMethods`, dynamic classes,
and related names are private runtime machinery while the owned type-protocol migration is
completed. Never use those Sage container names to decide placement or to
specify a new public preamble API.

**`MorphismMethods` is not the owned vehicle, and this was measured.** Sage never
instantiates `morphism_class`, and its `MorphismMethods` reaches a morphism only through
`Element.__getattr__` → `parent()._abstract_element_class`, never through the MRO — so
morphism *data* cannot be the basis of the owned architecture there. Taking
$\mathrm{Ar}(\mathbf{C})$ literally instead threads data and makes claims falsifiable on
real morphisms. A design that threads only object parents has not started.
`PLAN-threading-set-behaviour` records the runtime evidence; the later public type-protocol
decision supersedes its Sage method-container vocabulary.

**Added structure enriches an object; it never wraps one.** A formed module *is* a
module that additionally has a form. An abelian group *is* a $\mathbb{Z}$-module.
`ZZ` is at once a ring, a rank-one $\mathbb{Z}$-module, a rank-one
$\mathbb{Z}$-algebra, a group and a monoid — one object, several categories. A
subobject *is* the module $S$, an object of the ambient category like any other,
which additionally has an inclusion $f: S\hookrightarrow B$. Underlying-ness is what
a forgetful functor produces on demand, never data an object stores.
The construction says the same thing, in the same direction: a free module of rank
$n$ over $R$ is built **on** the underlying set $R^n$, and a lattice is that module
with a form. So every set-theoretic answer — cardinality, finiteness, countability,
the owned `Sets()` placement, membership, enumeration — is *inherited through the
construction*, never assigned to the enriched object. A lattice has no cardinality;
its underlying set has one. An element of the free module on $S$ is a finitely
supported $a: S\to R$, so for finite $S$ the underlying set is $R^{|S|}$ and the
count is $|R|^{|S|}$; for infinite $S$ finite support keeps it to
$\max(|R|,|S|)$, which is *not* $\prod_S R$; and over the zero ring, or for empty
$S$, it is $1$. If a construction reaches a lattice without passing through an
owned set that answers these, the construction is wrong, and stamping a placement
onto the lattice hides it.

**The category graph generates the implementation types.** The preamble's
architecture names `ObjectType`, `ElementType`, and the Hom-category types; it does not ask
contributors to maintain a parallel handwritten class hierarchy. Sage currently supplies
the dynamic-class/runtime mechanism underneath this: `parent_class`, `element_class`, and
related generated classes obtain bases from the category graph. The migration may map the
owned type protocol onto Sage method-container classes internally, but those containers are
not the mathematical vocabulary and must not leak into public design.

Above the root, a level declares its immediate category relations and only the data/behavior
introduced at that level. Only the root owns the host `Parent`/`Element` runtime bases and
non-cooperative Sage initialization. Construction threads cooperatively through the owned
graph: the set level establishes the underlying set, the module level adds the ring action,
the form level adds the form, and so on. A non-root level that imports/names an implementation
base from below, calls `Parent.__init__` directly, or restates lower-level state is patching a
second class graph by hand and has broken the construction chain.

**The leaf contract, which is what the mechanism exists to buy.** Defining a new leaf must
feel routine: the author should not search for an implementation class or know the transitive
construction chain. They declare the immediate mathematical supercategories/structure
functors, as `lean-categories` states them; extend only the appropriate `ObjectType`/`ElementType`/Hom-category types for
what this level adds; introduce only this level's datum; and construct through the immediate
supercategory. No implementation base is written. A leaf knows its own level and the one
above: it never names a category two levels up, never restates anything from below, and never
writes a forwarding method. Obligations compose by induction — if every level fulfils the one
above it, every object's obligations are met and no leaf carries the transitive burden.
**The author of a lattice category never writes the word cardinality**; they construct the
underlying module and stop. The decay signal is a leaf *reaching down*: importing a lower
implementation class to call it, restating a lower level's computation because the chain did
not deliver it, or calling `Parent.__init__`. The decision record, with the runtime evidence
and superseded method-container spelling, is `PLAN-threading-set-behaviour`.
*The tell:* a placement, cardinality, or enumeration installed on a module, lattice
or group directly; a set class imported into a module or lattice file, or hand-written in
its bases; a constructor that calls `Parent.__init__` instead of `super().__init__`;
the same count computed again at a second level of enrichment;
`_is_known_empty`-style code refusing an object "for want of a
placement" when the fix is that its underlying set was never built; the phrase "has
an underlying X"; a stored `self._underlying`; a
`forget_*()` call used to obtain the receiver of a method rather than to name a
functor; delegation chains for methods the object already has from its own category.
(Vault: `subobjects-are-a-subcategory-not-a-wrapper`.)

**An implementation obstacle is fixed where it occurs; the mathematics does not move
to accommodate it.** A recursion, a type error, a slow path, or a failing gate is a
fact about the implementation. Re-siting a construction onto a different object,
wrapping a type, or weakening an annotation to make one of them go away changes what
the code *says* in order to change how it *runs*, and the mathematical claim is then
false while the suite is green. Fix the recursion; make the type real; find out why
it is slow. An obstacle that survives that is a discussion, not a redesign made
alone.
*The tell:* a docstring or comment that justifies placement by what it avoids
("sited here, which keeps X from re-entering Y"); a wrapper type introduced during a
type-checking pass; `cast`; any edit whose stated benefit is that a checker or a test
stops complaining.
(Vault: `the-mathematics-never-moves-to-accommodate-an-implementation-obstacle`.)

**A predicate is computed from its definition, on the entity the definition is
about.** Nondegeneracy is $\ker c = 0$ for the correlation $c: L \to
\operatorname{Hom}(L,R)$ — form the kernel and ask it whether it is zero, or ask the
arrow whether it is injective. Primitivity of an embedding is that its cokernel is
torsion-free. Saturation and index are properties of a morphism, so they are asked of
the inclusion, never of a bare object. Determinants, gcds of matrix entries and rank
comparisons are recognition criteria that hold under hypotheses the definition does
not carry; using one asserts a theorem nobody proved, at a site where nobody will
look for it.
*The tell:* `det(...) == 0`; `gcd(...) == 1`; a predicate whose body mentions entries,
a basis, or coordinates; a predicate sited on an object whose mathematical statement
names an arrow.
(Vault: `numerics-quarantine-saturation-and-primitivity-are-subobject-definitions`,
`witness-consuming-methods-belong-on-morphisms-not-objects`,
`primitive-embedding-is-computed-from-cokernel-not-caller-flag`.)

**Present the general notion; recover the special case from it.** As formalized, a form is
$b: M\times M\to W$ for an arbitrary value module $W$, so its scale is a submodule of
$W$ — an ideal only when $W$ happens to be the ring. A group's generating set is a
set; finiteness and an ordering are the axioms `FinitelyGenerated` and `Finite`, not
part of the notion. A lattice is a *projective* module with a form; a form module is
any module with a form. Where a term already has an a priori meaning, that meaning
stands: any ring morphism $R\to S$ defines integrality, so integrality is never
re-parameterized by a submodule of the implementer's choosing.
*The tell:* a name that fixes the special case (`scale_ideal`, or `dual` for one of
several duals); a parameter added for something the definition already determines;
code that runs on $\mathbb{Q}/\mathbb{Z}$ where the statement was about $K/R$.
(Vault: `integrality-has-an-a-priori-meaning-never-parameterize-or-coin-it`.)

**When the vocabulary cannot express the general statement, that is the finding.**
Discovering that the repo can build $\mathbb{Q}/\mathbb{Z}$ but has no object for
$K/R$ stops the work. If `lean-categories` formalizes $K/R$, presenting it is the
work; if it does not, it is a request there and the work parks on it. Patching the
case that already worked leaves the general statement unsayable and the gap
unrecorded.
*The tell:* agreement with a general statement followed by an edit confined to the
one case that already worked.
(Vault: `agreeing-to-general-mathematics-the-dsl-has-no-vocabulary-to-express`.)

**Every name states the structure it belongs to.** `group_generators`,
`module_generators`, `algebra_generators`; `dual_module`, `dual_lattice`,
`dual_group`. A bare `generators` or `dual` is ill-defined the moment an object sits
in more than one category, which every object here does. Generators are a *set*,
possibly ordered, possibly finite: they have a cardinality, not a length, and
repeated elements are not an error. Use `lean-categories`' word, which is the
field's; where there is none, that absence is a signal to check the notion, not
licence to coin a name for it.
*The tell:* a bare structure noun; a plural returned as `tuple`, `list` or
`Sequence`; `len(...)` on generators; a coined compound adjective; `Any` or `object`
standing where a mathematical noun belongs.
(Vault: `generator-names-must-always-state-the-structure`,
`mathematical-apis-must-use-the-field-s-actual-lexicon`; proven repeat offenders are
in the banned-language index above.)

**A predicate is decided on the data that determines it, or it returns the
proposition.** Equivariance of $\rho$ is checked on generators when generators are
available; membership in $O(L)$ is $M^{t}G_{L}M = G_{L}$; a subgroup of $O(L)$ is
carved out by a predicate. Iterating a group, a homset or a module to establish a
property is correct only for the finite objects that happen to be in the suite, and
$\mathrm{GL}_n(R)$, $\mathrm{Gal}(\overline{\mathbb{Q}}/\mathbb{Q})$, $O(L)$ for
indefinite $L$, and $\mathbb{Z}^{\infty}$ are all ordinary inputs here. A predicate
returns a proposition, an element of `Propositions` (`preamble/logic.py`), and
`ask(P)` evaluates it, the way `sympy.ask` evaluates a sympy proposition. Where the
question is computable or decidable, the predicate computes or decides it and returns
`True` or `False`; where it is not decided, it returns the `Predicate` that states it,
whose own `_ask_` runs every procedure that applies and answers `Unknown` only when
none decides it. A predicate never returns a bare `Unknown`, never collapses an
undecided question to `False`, and never runs a loop that works only on small inputs.
`G_{\mathbb{Q}}` is not abelian because it surjects onto a finite quotient that is
not abelian, so `is_abelian()` decides it; injectivity of an arbitrary function on an
infinite set is undecided, so `is_injective()` returns the proposition. Sage is a computer
algebra system, not a proof assistant: a theorem is cited from `lean-categories`,
never re-established at runtime, and no computed answer is a proof.
*The tell:* `for g in G`; `for f in Hom(...)`; a bounded search with a cap;
`all(... for ... in <an object>)`; a docstring claiming a property is "verified" or
"proven" by the method body.
(Vault: `sage-is-a-cas-not-a-proof-assistant-runtime-verification-of-a-theorem-is-triple-slop`,
`undecidable-problem-pseudo-booleans`; the undecidability audit under *Work-selection
discipline* is the sibling rule.)

**The data a caller holds presents an object; it never selects the owner of an
operation.** A lattice-db card stores a presentation: a configuration matrix
of multidegrees in $\mathbb{P}^{n_1}\times\cdots\times\mathbb{P}^{n_m}$, a
decorated graph, a table of numbers. The false belief: "the operation belongs
to the category whose objects look like this data", so every function that
reads a configuration matrix goes to complete intersections, and every function
that reads a decorated graph goes to a "weighted graph" owner. The correct
sequence has four steps:
1. Name the object the data presents: a smooth complete intersection $X$, a
   root system, a real form of a semisimple Lie algebra, a hyperbolic
   reflection group.
2. Construct it through its category. The presenting category introduces only
   its own datum. For a complete intersection, that datum is the ambient
   product and the multidegrees.
3. Answer the asked value with the method of the category whose definition
   defines it, reached by inheritance. Examples: $\chi$ and $b_k$ of a space;
   $h^{p,q} = \dim H^q(X,\Omega^p)$ of a smooth proper variety; $\dim$ of a
   scheme; Calabi–Yau ($K_X$ trivial) as an axiom on the base that states it.
4. A formula in the presenting data is a realization on the subcategory,
   justified by a cited theorem. Examples: $\dim = \sum n_i - r$;
   $\sum_j d_{j,i} = n_i+1$ by adjunction; Hirzebruch's generating function.
   It is never the definition and never the placement.

A function that checks a stored value against a theorem (Hodge symmetry,
Serre duality, Vinberg's criterion on a stored Gram matrix) is not mathematics
to relocate. Either the object is constructed and the value is computed and
compared (certification), or the value is a transcription. Relocating the
functions of a leaf module one by one is the same false belief: the unit is
the notion asked, not the function that happened to compute it.
*The tell:* a class or module named for a data shape (`WeightedGraphInvariants`,
`HodgePoincareInvariants`, `catalogue_invariants`); a method whose arguments
are the presentation's raw numbers rather than the object; an owner chosen
because "that is where the formula can be evaluated".

**Morphisms are constructed by the caller, in the categories they live in.** A
$G$-action on $M$ is a group morphism $\rho: G\to\operatorname{Aut}(M)$ that the
caller builds; $M$ does not accept a group and a list of images and assemble one.
Passing from $R$-modules to $R[G]$-modules is a functor, and asking for an invariant
sublattice applies it. An $S$-module, for any ring $S$, is a set with a ring morphism
$S\to\operatorname{End}(M)$, so group modules, lattices with an action and modules
over a group ring all specialize one constructor and need no special case.
*The tell:* a constructor taking raw matrices or images where a morphism is the
datum; a method on an object returning a morphism between two *other* objects; a
`from_*` classmethod duplicating a homset's `_element_constructor_`.
(Vault: `a-group-action-is-a-morphism-the-caller-constructs`.)

**Shared infrastructure never carries a local exception.** The global QC in
`~/ai-review-ci` is machine-wide and already has sanctioned routes for shielding code
(the excluded directory names, the archived paths). A repo-specific rule, exclusion
or suppression written into it inverts ownership in either direction — a local ruling
promoted to a universal one, or a local exemption inlined into a universal gate.
Both are user decisions before they are edits.
*The tell:* a repo name, path or convention appearing in a shared config; an
exclusion added while fixing a failure in one repo.
(Vault:
`a-highly-specific-fix-is-not-a-general-rule-project-conventions-never-promote-to-global-qc`.)

**Reference implementations are absorbed by semantic reconciliation.** The archived
spikes are this project's own earlier versions, and their notions carry no
authority. Each notion they hold is first mapped onto the `lean-categories` notion:
where the preamble already presents it, the spike's version is superseded and call
sites are re-expressed in the preamble vocabulary; where the preamble does not yet
present it, it arrives rewritten to current standards and sited where
`lean-categories` places it; where `lean-categories` has no such notion, it is
requested there and the spike's version is not carried over. Neither a wholesale copy nor a minimal trim is
reconciliation.
*The tell:* a new file mirroring the source layout; a second definition of a notion
the preamble already presents; not-yet-absorbed code described as severed or contaminated
rather than as pending its round.
(Vault:
`spike-absorption-is-semantic-reconciliation-never-quarantine-or-copy-paste`.)

# Mathematical Sage API discipline (always-on)

These rules govern preamble, spike, and any Sage-facing API in this repo.
They are the generative constraints behind repeated corrections (override-refine, catalogue namespaces, Hom/Aut construction, session ergonomics).
A design that violates them is wrong even when it “works.”

**In one line:** write Sage so that the category and the catalogue present the theory directly — idiomatic constructions, one home per notion, no second layer between the mathematician and the object — and delete anything whose only job is to mediate, rename, wrap, or reassure. The theory itself is `lean-categories`'; the preamble presents it and owns none of it.

## 1. Public operations come from the formal catalogue

Public operation declarations and their category placement belong to
`lean-categories`; the `lean-cas-dsl` kernel consumes those declarations.
Research presents those operations and registers private computations through
their declared contracts. A missing declaration is requested at its formal owner.

The existing Python realization states method placement through `ObjectType`,
`ElementType`, and the object/element types of Hom/End/Aut category constructions. Sage's
`ParentMethods`, `ElementMethods`, `MorphismMethods`, dynamic MRO, and refinement hooks are
private runtime mechanisms used to realize that declaration on independently owned
objects; they never decide where mathematics belongs or admit foreign parents.
This protocol is transitional machinery to retire as its consumers move to the
formal catalogue and kernel, as specified in `CONTRIBUTING.md` under "Layers and
permitted dependencies".

If Sage's interface is wrong or incomplete, **present the formally declared
operation on its category and map it onto Sage privately**; if `lean-categories`
does not have it, it is requested there
([missing foundations](#a-missing-foundation-parks-the-work-that-found-it-always-on)).
Workarounds (`without_element_wrap`, ad-hoc `L.isometry(matrix)`, freestanding patch
modules) mean the operation was not placed at its category.

The private runtime mechanism remains one owned construction/dynamic-class path,
not a new installation strategy per capability. Host `Parent`/`Element` primitives
may implement that runtime; Sage's concrete mathematical parents and element types
do not become the public objects. Do not introduce an `ElementFacade`,
`MorphismFacade`, or generic attribute-forwarding layer to preserve a foreign API.

See [private runtime realization](#addendum-private-sage-runtime-realization-of-owned-category-types)
for the permitted host boundary and the architecture specification for the public
construction and private computation contracts.

## 2. API shape is dictated by the mathematics

Reject APIs that are software-coherent but mathematically incoherent.

- Named literature objects (e.g. a K3 involution) are **catalogue data**, not methods of every lattice of that type.
- Operations of an object under structure (e.g. invariant and coinvariant lattices under a group action) live on that object’s category methods — or as thin sugar on the morphism — not in a freestanding feature file.
- An isometry is a **Hom/Aut element**. Construct it the way morphisms are constructed (generator images `{g: image}`); the matrix is a derived view (`to_matrix`), not the definition.
- Algebraic operations use native protocols (`L + M`, `sum([...])`, `L ** n` for n-fold sum). Do not invent `_oplus` or force chains of `.direct_sum` when `+` is the monoidal operation.

If the call site would not be written at a Sage prompt while doing the math, the API is wrong.

## 3. Placement — one home

Every entity has exactly one kind of home:

| Kind | Home |
| --- | --- |
| Behavior of a class of objects | category methods on the refined category |
| Named specimens / literature tables | one catalogue namespace (e.g. `Lattices`) |
| Session defaults (implicit multiplication, traceback colour, …) | import-time effect of loading the init/ergonomics module |

Freestanding files, string registries, factory functions, module `__getattr__`, and dual module-level aliases of the same object are symptoms of placement by accident of authorship, not by what the entity is.

Named lookup is by attribute (`Lattices.U`).
Keys that are mathematics stay typed (`Lattices.TwoElementary[8, 8, 0]` for Nikulin $(r,a,\delta)$), never stringified tuples.
Put such tables on the namespace that owns the specimens.

Prefer **one clean export** for a catalogue surface: import `Lattices`, use `Lattices.…`. Do not re-export every attribute at module level.

**Functors, adjunctions and constructions are spelled on categories, never as standalone functions** (ruled 2026-09-05; the expectation files under `tests/constructions/` and `tests/user_simulations/` are written this way and are the spec). One rule per kind:

- A functor is a method of its domain category, named by the construction, taking only what fixes the codomain: `Modules(ZZ[H]).induction(G)`, `FiniteGSets(G).orbits_functor()`, `Groups().abelianization()`, `Algebras(R).Associative().Unital().Commutative().spectrum()`.
- An adjunction is a method of the left adjoint's domain category, named by the pair: `Modules(ZZ[H]).induction_restriction_adjunction(G)`, `FiniteSets().free_underlying_adjunction(G)`.
- A construction on objects is a method of the category that owns them, or of the object when one argument is distinguished: `M.tensor_product(N)`, `M.Mor(N)`, `M.ext(N, n)`, `C.cohomology(n)`.
- An object constructor is the category applied to the object's data: `FiniteGSets(G)(points, action)`, `Modules(ZZ[G])(M, action)`, `Subgroups(G)(predicate, description)`.

A standalone `XFunctor(...)`, `x_adjunction(...)`, `Ext(n, M, N)` or `finite_g_set(...)` in the session surface is a placement defect; the name belongs on the category or object above and the function is retired, not aliased.

**No standalone function constructs an object, and a shortcut is no exception.** A homomorphism is constructed by its homspace: `M.Mor(N)(data)`. A matrix is an element of the topological `R`-module `Mat_{n x m}(R)`. It is constructed by that module's constructor, by `GL_n(R)`'s, or by `tensor.matrix(R, rows)`. A matrix is not a linear map. The map `Mat_{n x m}(R) -> Hom_R(R^m, R^n)` is neither injective nor surjective in general, so reading a matrix as a map is a construction on the homspace, never an identification. A bare `matrix(...)`, or any other free session function that returns a new object, is the same placement defect as `finite_g_set(...)` (ruled 2026-10-08). Two kinds of free function are admitted. Basic mathematical primitives such as `factorial` and `binomial` may be free, but each should preferably read a method of the number it acts on. The owner's code-wrangling helpers (`lmap`, `lzip`, `zipsum`, `to_var_names`) stay; what they owe is precise types.

**Group modules are `Modules(R[G])`**, modules over the group ring, never a category of their own. Induction, coinduction and restriction along `H ≤ G` are scalar extension, coextension and restriction along `ZZ[H] → ZZ[G]`; the trivial action, coinvariants and invariants are restriction, extension and coextension along the augmentation `ZZ[G] → ZZ`. These functors are stated once over `ZZ`, the initial ring, and preserve the finer scalars an `R[G]`-module carries. Actions in categories that are not modules (sets, schemes) are `GObjects(G, C)`, with `GObjects(G, Modules(R)) ≃ Modules(R[G])` as an explicit equivalence when needed. Actions are left actions: `rho(g h) = rho(g) rho(h)`, the product of the matrices acting on an ordered basis, and the group law is composition.  These are presentations of `lean-categories`' definitions and conventions; where it states them differently, it governs.

**Object and category are not exclusive.** Every set is a discrete category, and every hom is a category, so a subset of a hom is a subcategory of that hom-category, and the same set is also an object of whatever category its structure places it in. The space of modular forms `M_k(Γ, χ)` is the standard case. It is the subset of the function space of holomorphic functions on the upper half-plane cut out by weight-`k` automorphy for `Γ` with character `χ` and the cusp condition. That function space is a hom, so `M_k(Γ, χ)` is a subcategory of it. The same set with its inclusion is a subobject of the function space in topological `C`-modules, here finite-dimensional with a rational structure, and `S_k(Γ, χ)` and the Eisenstein subspace are subobjects of it. Present such a space through the hom it is cut out of. Never write "X is an object, never a category". What does not exist is a category whose objects are the individual forms, with morphisms invented between them. *The tell:* "an object, not a category"; "a category of modular forms"; a new category class whose objects are the elements of one function space. Ruled 2026-10-09.

## 4. One source of truth, stated once, inline

Construction **is** where a catalogue value is defined.
Define values inline in the namespace class body (or a helper called from that body while dependencies are in scope).
Do not spread a definition across “empty container → later assignment → `globals().update` → string lookup → re-export.”
Do not construct after the class and patch attributes on afterward — that means the class body was not the definition.

An alias is object identity (`SEn is E10_2`), not a gram-matrix equality check in production code.
If identity matters, assert `is` in a test.

## 5. Hostility to non-semantic indirection

Delete anything that can be removed without changing what a mathematician can say or compute:

- wrap-then-call (`enable_X` → `install()` → `enable_X` → real call)
- catch-and-rethrow the same exception kind with a different message
- dict façades that reimplement `.items()` / `.keys()`
- re-exports of the same object under a second name
- import-time asserts that restate what construction already entails
- tests of “conflict scenarios” instead of tests of the intended dispatch or mathematical claim
- catalogue factories that re-verify primitives on every lookup (`is_involution` belongs on the morphism)

Ceremony is a bug: it creates a second, softer API that agents will use instead of the real one.
This is the same discipline as work-selection (above): an artifact that cannot fail carries no information.

## 6. Generality over local cleverness

When blocked, do not add a special case for this object.
Strengthen the general preamble interface (element construction, Aut construction,
`+` / `sum`, and structural refinement) so the special case disappears.
Ask “why does this freestanding file/function exist?” — if it has no mathematical referent, delete it and place the content in the category or catalogue.

## 7. Tests falsify the intended contract

Tests falsify the mathematical or dispatch claim: refined methods win over class methods; this alias is the same parent; this Aut is an involution; this table entry is that named lattice.
They do not exercise scaffolding, reassure about naming conflicts, or re-encode construction as gram-matrix comparisons.
These tests are research's own and certify nothing outside it. Correctness evidence about a computation exists only in the `lean-cas-dsl` acceptance suite, which never sees this code.

Predicates that are part of the theory (`is_involution`, invariant and coinvariant lattices, isotypic components, …) are methods on the preamble category interfaces, not side conditions in catalogue loaders.

**Adding to `tests/test_known_mathematics.sage`.** That file states mathematics the preamble must reproduce; it is research's own test and certifies nothing outside research. Agents do not extend it freely — but an addition is allowed whenever an independent source citation is attached to the new row: the Stacks Project, Kerodon, an item in the owner's Zotero library, a published paper, or an arXiv preprint. The citation is the admission ticket, and it names the source of the *asserted fact*, not of the implementation. Cite by the source's own identifier (Zotero `citationkey`, Stacks tag, arXiv id), verified against the source rather than recalled.

A row whose assertion would hold with the functionality removed certifies nothing. Assert the content: a maximal overlattice is reached by an inclusion, so the arrow's index is the assertion, not the codomain's existence.

## 8. Block Hom spelling, invariant and coinvariant lattices, and catalogue hygiene

Rules distilled from preamble work on direct-sum coordinates, embeddings, and coinvariant lattices (2026-07).

**Block Hom spelling.** A Hom/Aut between orthogonal direct sums is a block matrix: the $j$-th block column is the image of the $j$-th domain summand. Prefer block dicts via `L.summands()` — `{a1: b1, a2: b2 + b3}` — over flat generator-image lists when the mathematics is blockwise. Equal-rank block sums (`b2 + b3`) are gen-wise placement into multiple target blocks (the diagonal $N(2)\hookrightarrow N\oplus N$, not $N\to N\oplus N$). Name morphisms by their true domain; ergonomic sugar must not invent the wrong morphism type.

**Invariant and coinvariant lattices, and inclusions, are computed on the lattice.** There is no "eigenlattice": the notions are the invariant lattice, the coinvariant lattice, and the isotypic components. Invariant/coinvariant lattices and primitive inclusions (`invariant_lattice`, `coinvariant_lattice`, `coinvariant_inclusion`) are category methods on `IntegralLattices`; the coinvariant is $(L^G)^{\perp L}$. Catalogue must not ship helpers that take a named lattice plus an involution and assert kernel rank or Gram agreement — that certifies a guess, it does not construct. Named literature embeddings *use* the generic interface; they do not reimplement it.

**Catalogue is specimens plus nested namespaces, not ceremony.** Call `categories.install()` before building catalogue lattices; no manual `refine_one_lattice`. No `_with_names`, `_involutions`, `_embeddings`, or similar factories around one-liners or class bodies. Nested `Involutions` / `Embeddings` belong in the `Lattices` class body (populate empty nested classes in that body when Python scoping requires it); no post-hoc `__qualname__` patching or `Lattices.X = …` assignment after the class is built. Once the principled block or coinvariant API exists, catalogue entries use it everywhere — flat lists or kernel-basis shortcuts left “because they still work” are drift.

# Declaring a category: the questions answered before writing (always-on)

The tree this morning held thirty categories declaring `Sets()`, twenty-one
declaring `Objects()`, a block of 135 categories meshed by hand-written
property combinations, four notions each under two names, restriction of
scalars declared as a supercategory on three bases, and a diamond whose two
routes landed on different objects. None of it was a wrong object; all of it
was a wrong belief about what a declaration says. `CONTRIBUTING.md` codes
`CAT-15` to `CAT-27`, `DEV-64` and `DEV-65` state the rules with the artifact
each one came from, and *Presenting a category: the procedure* there is the
full order of work, from the `lean-categories` definition through the
survey of the tree to the delivery of every consumer. This section is the
short form asked before any declaration is written; no declaration is written
until each question has an answer in the commit body.

A declaration here presents a category that `lean-categories` formalizes; it
defines nothing. If `lean-categories` does not have the category, nothing is
declared and the need is requested there
([missing foundations](#a-missing-foundation-parks-the-work-that-found-it-always-on)).

1. **What are the objects?** Quote `lean-categories`' definition in one
   sentence, with its locator. If it names a chosen datum ("with a chosen basis", "with a
   differential"), this is a data subcategory. If it names only a property
   ("Noetherian", "finitely generated", "separated"), this is an axiom on its
   base and there is no class to write (`CAT-17`, `CAT-18`).
2. **Does it exist?** `just category-graph by-supercategory` for the parent it
   would declare; `rg` the nouns of the definition across `categories/`; the
   specification files for the name they use. If it exists, extend or retire
   into the owner; never a second class (`CAT-22`).
3. **What is the underlying object, over the same parameters?** An object of
   this category with the added structure forgotten, base and parameters
   untouched, is an object of exactly one category one step down. That is the
   declaration, and the only one (`CAT-15`, `CAT-16`). If the honest parent is
   not in the tree, declare nothing: a parent `lean-categories` has is presented
   first, and one it lacks is requested there. `Sets()` and `Objects()` are
   never placeholders.
4. **Is anything in the list a change of base or parameter?** Restriction of
   scalars, base change, an ideal to its fractional ideal, an `R[G]`-module to
   a `G`-object over `R`: each is a functor obtained from the category by a
   named method, never an entry in the list (`CAT-16`). Sage applies every
   axiom along a declared edge, so such an entry is a false statement for every
   relative property.
5. **Does the list create a second route to anything?** Write both composites
   and cite the `lean-categories` theorem relating them. Same category twice:
   delete the shortcut. Computed join: fine. Different objects: the entry is
   false (`CAT-21`).
6. **Is it a construction on a category?** Then it takes that category as a
   parameter and declares it; its instances do not declare the base again
   (`CAT-20`).
7. **Is every entry an expression a reader can resolve?** Names and
   parameters only; no locals, no `supers + [...]`, no method calls on `self`
   that compute a category (`CAT-24`).
8. **What does the graph say?** `just category-graph shape` and `cells`
   before and after; the delta goes in the commit body, and a grown block or a
   grown breadth is the finding (`CAT-25`).

Banned outright, each observed and removed on 2026-09-16: `Sets()` or
`Objects()` declared because the real parent is missing; a class named for a
combination of properties; a class for a property that Sage's axiom mechanism
states; a `super_categories` override on an axiom class; a category declaring
its own name over a lower base; `__contains__` deciding membership by a base
tower or an attribute probe; a declaration computed from a local variable; a
second class for a notion the tree already presents. Membership of a property
subcategory is the property's proposition, asked only when needed
(`CON-07`): `I in Ideals(R).Maximal()` asks whether `R/I` is a field. The
answer goes to the caller and never changes the object's category or its
operations; placement comes only from construction, including routing on a
`lean-categories` theorem, so no engine answer selects what an object can do.

Banned on 2026-09-17 (`CAT-28`): a category declared for the class of objects
an engine or a construction produces (a condition set is a class; the groups
\(\operatorname{Aut}(L/K)\) form a class), and an engine class deleted or
turned into a category.  Engines are threaded into the category their objects
already belong to.  An \(R\)-algebra is constructed from \((A, m)\), and its
structure morphism \(\rho\colon R\to Z(A)\) is produced from \(m\); for \(R\)
over itself \(\rho\) is the identity (`CON-16`).

# Categorical organization model (always-on)

How the preamble's category tree is organized, and where content presenting
`lean-categories`' mathematics goes. Every notion below is defined in
`~/gitclones/lean-categories` (FOUNDATIONS.md and `LeanCategories/`): framed
generators and bases are §13.5, chosen presentations as structure are §75,
partial resolutions and the $FP_n$ hierarchy are §76, resolution classifiers
are §77. The tree presents those definitions and defines none. When a preamble
docstring and `lean-categories` disagree, `lean-categories` is right and the
docstring is corrected; a notion `lean-categories` lacks is requested there,
not defined here.

## Property subcategories vs data subcategories

Two kinds of subcategory, and the distinction decides method placement.

- A *property* subcategory states a fact about its members: finitely
  generated, finitely presented, finite, abelian. Membership is the
  statement, so its methods are predicates answered by placement
  (`is_finite` returns `True` because membership states it) and theorems the
  property entails.
- A chosen datum states that members carry a choice: a chosen generating
  epimorphism $F(S)\twoheadrightarrow X$ from a free object, a chosen
  presentation (that epimorphism plus chosen free relations), a chosen basis.
  The first three are truncated resolutions and live in the category of
  resolutions over the base (`CAT-29`); its methods consume the datum.

An object together with an arrow is not "an object with data": it IS a slice or coslice object. Several arrows are remembered by slicing over pullbacks or coslicing under pushouts (products, coproducts). A pair \((X, x)\) with \(x\) an element of \(F(X)\) is an object of the Grothendieck construction \(\int F\) (category of elements) of \(F\colon \mathbf C\to\mathbf{Set}\), and a property of the element ("\(x\) primitive") cuts out a full subcategory of \(\int F\). When \(x\) is a point of \(X\), \(F\) is the covariant hom out of the point, \(F=\operatorname{Hom}_{\mathbf C}(*,-)\), and \(\int\operatorname{Hom}_{\mathbf C}(*,-)\cong {*}/\mathbf C\): a pointed object is a coslice object, the same statement as above. A family of elements is a set map \(v\colon I\to U(X)\), where \(I\) is a set carrying whatever structure the notion needs: a colouring is a map \(I\to C\) (so \(I\) is a set over \(C\)), and a coloured multiset is the family of pairs \((v_i, c_i)_{i\in I}\), a not necessarily injective map \(I\to U(X)\times C\). An \(I\)-indexed family of objects of a category \(\mathbf C\) (of sheaves, say) is a functor from the discrete category on \(I\), an object of \(\mathbf C^{I}\). Families are never encoded through a free functor (\(\mathbb Z^{I}\to L\)): that only exists where a free functor does, and it does not generalize (owner, 2026-10-14). Err on the side of the abstraction being actual mathematics; no class is declared for "an object with a chosen arrow" (owner ruling, 2026-10-14; `CAT-30`).

A property is the propositional truncation of the corresponding data
category: finitely generated = "some resolution finite in degree 0 exists";
finitely presented = "finite through truncation 1"; $FP_n$ continues through
chosen syzygies, and each extension of a resolution to the next degree is
itself a choice. So a method that consumes a choice lives on the data subcategory and
never on the property one. A group can be provably finitely presented
(arithmeticity) while no practical presentation algorithm exists; asking it
for a presenting free group must be an absence, not a computation.

Producing a choice is one explicit crossing: a single named method computes
the datum once, stores it, refines the object into the data subcategory, and
returns it. Downstream code then asks the data category's words. A property
category never silently computes presentation data on demand.

The basic form of such a datum is a collection of morphisms (the chosen
tower). Where the surrounding category supports it, prefer the principled
package — an augmented chain complex for additive data, a DGA only when the
resolution must carry multiplication — over loose tuples of maps.

Chosen generating sets, presentations and syzygy towers are truncations of
one datum, a resolution, and they live in a category of resolutions over `C`
(`CAT-29`), not in an axiom subcategory. Fix a projective class `P` in `C`,
usually the retracts of the free objects `G(X)` for the free/forgetful
comonad `G = FU`. `Res_{P,n}(C) -> C` has as fibre over `X` the augmented
simplicial objects `P_* -> X`, truncated at `n`, levelwise in `P`, acyclic
through `n`; `n = infinity` is a cofibrant replacement, and for modules
Dold-Kan returns augmented chain complexes. Levelwise conditions pull back
property classifiers along degree evaluation; acyclicity and length are
global. Truncation (how far the resolution is chosen) and length (above which
degree it vanishes) are different indices: a generating epimorphism
`F(S) ->> X` is truncation 0, a presentation truncation 1, `FP_n` finiteness
through truncation `n`. Every object is resolvable -- the counit
`F(UX) ->> X` starts the canonical comonadic resolution -- so resolvability is
never an axiom; frameability conditions (free, stably free, finitely
generated, finitely presented, `FP_n`, finite length) are the relative
properties.

A *framing* is a length-0 resolution by free objects, `0 -> F(S) -> X -> 0`
exact, i.e. a basis; free modules with a chosen basis are the framed
modules. *Framed* in the geometric sense is the manifold notion: a framed
manifold carries a length-0 resolution of its tangent bundle by trivial
bundles, a trivialization of `TX` (nLab *framed manifold*, the `G = {e}`
G-structure); a stable framing trivializes `TX + R^k`, a framing after
stabilization. Through Serre-Swan a trivialization of `TM` is a basis of
`Der(C^oo(M))`, and for an algebra the resolution computes the cotangent
complex whose trivialization is the algebraic framing.

A resolution travels along a forgetful functor, and what it becomes is
decided by the mathematics of that functor: `U : Alg_R -> Mod_R` carries the
algebra generating epimorphism `Free_Alg(S) ->> A` to the module one
`Free_Mod(Mon(S)) ->> U(A)`, the words in `S` spanning `A`. Finiteness is not
preserved: `R[x]` is generated as an algebra by one element, and `U(R[x])`
needs the infinitely many monomials.

## Axioms live as high up as possible

An axiomatic subcategory is declared once, at the highest category that can
state it, and reached by `with_axiom` (the axiom name registered in
`sage.categories.category_with_axiom.all_axioms`). An axiom is a property.
A chosen datum is never an axiom: Sage's joins close under axioms, so a
datum registered as one propagates across the branches of every join as
though each branch had it. The retired `Framed` axiom did exactly that
(`CAT-29`). What groups, modules and algebras share about chosen generators
is one contract on the category of resolutions, not one axiom.

Duplication is the diagnostic: if two parallel categories restate the same
contract or the same derived method, the axiom was attached too low. Never
re-declare in a subcategory what a supercategory already provides, and never
restate category methods on a concrete class.

## Abstract contracts are distinct from partial algorithms

A **genuine category implementation contract** uses Sage's `abstract_method` decorator on
the appropriate owned `ObjectType`, `ElementType`, or Hom-category type. It says that any
implementation participating at that category level must supply the operation. Never encode
such a slot as `assert False`, `raise NotImplementedError`, `pass`, or an empty ordinary
method body.

Do not confuse a genuine contract with either of these different situations:

- **Construction-supplied data.** If the category level's constructor itself introduces the
  datum, the constructed object should simply store/supply it. Do not create a redundant
  abstract accessor merely to ask later for data the construction necessarily established.
- **A mathematically general operation with incomplete current algorithms.** `cardinality()`
  on sets and `is_nondegenerate()` on formed modules are not abstract merely because some
  represented cases are not presently computable. Keep the method where `lean-categories`
  places it, route the cases currently implemented, and assertion-gate the unhandled
  computational remainder with an informative message. A specialized category may supply a
  stronger implementation without moving the mathematical notion.

An abstract predicate on an axiomatic/data-bearing subcategory is a requirement on
participants, not an inherited `return True`. If a refinement says that its objects must
supply a named operation/predicate, the participant supplies it by computing it, and that
answer is an untrusted computation like any other. Where `lean-categories` proves the
predicate for every object of a category, the preamble presents that inclusion and the
predicate answers by placement, as for a property subcategory above; an implementation
returning `True` on the strength of a theorem it asserts itself is a claim nothing
supports. The category declaration itself does not manufacture the answer, and runtime
proof/certificate/evidence objects are not introduced for this purpose.

Sage's `abstract_method` is the repository's explicit marker for the rare case where a
method is intentionally a category implementation contract. It is not a TODO mechanism and
not the default response to an algorithmic frontier.

## Every object we care about has an exercise file

`tests/objects/` holds one `test_<object>.sage` file per mathematical object the
preamble is expected to build: a named lattice, a group, a ring, a module, a
scheme, a discriminant form. Each file is a session. It builds the object in
every accepted way, each through the top-level category of its kind applied to
the object's data (`Sets()`, `Modules(R)`, `Lattices(R)`, `Groups()`,
`Algebras(R)`, ...). It asserts that the constructions agree. It asserts that the
object is in the categories it belongs to (`assert L in Lattices(ZZ)`). Then it
calls each operation expected of the object and asserts the result, one call
after another. Each expected value is cited from a source or proved,
independently of the implementation; a value of informal provenance is not an
expected value. These files are research's own and certify nothing outside it;
correctness evidence exists only in the `lean-cas-dsl` acceptance suite. A new
constructor or construction route adds its route to the file of the object it
builds; a new object adds its own file.

Nothing in these files inspects the implementation. There is no introspection,
no table of constructors and no check that a method is implemented: an
operation whose owner never supplied it fails when it is called, inside the
test that names it. `just test-lint` enforces the same standard here as for
every other test.

## Runtime classes only realize the presented constructions

Almost everything mathematical lives at the categorical level. The preamble's `ObjectType`,
`ElementType`, and Hom-category types are the implementation protocol generated by the
category graph presenting `lean-categories`; a separate handwritten concrete hierarchy is the exception, not the
rule. Host/runtime primitives remain where they implement the generated owned
types; concrete engine representations remain inside private adapters.
Historically this read the other way, and named classes such as `BasedFreeModule`
or old framed-algebra/group intake classes
are migration specimens, not patterns to copy.

Constructions are uniformized as high as their mathematics allows: one free functor for the
relevant category, one resolution contract, one universal construction. A new capability is new
category/type content presenting `lean-categories` plus only the representation machinery genuinely required by the
host; it is never a parallel class hierarchy.

# Python and Sage research code style (always-on)

These rules govern Python, Sage, spikes, the preamble, the installed package, tests, and notebooks.
Use the detailed mathematical and repository rules above when they give a narrower instruction.

## Mathematical model before representation

- Work in the order mathematical object → representation → implementation.
- Start with the mathematical object as `lean-categories` formalizes it: its data, its laws, and its hypotheses.
- Identify the relevant category, objects, morphisms, functors, and universal properties in `lean-categories` before choosing classes or methods.
- Map that representation into Sage only after its objects, morphisms, hypotheses, and constructions are specified.
- Implement only the operations that remain after native Sage structure is used.
- Do not derive an API from the methods, classes, or data layouts that happen to exist.
- Do not duplicate the data of a chosen morphism in fields on its domain or codomain.
- Represent a chosen representative of a subobject of $B$ by a monomorphism $f:A\hookrightarrow B$.
- Obtain its target from `f.codomain()` and use $f$ as the chosen monomorphism.
- Keep an element of $A$ distinct from its image in $B$.
- Do not use coercion to erase the distinction between an element and its image.
- Preserve distinctions between objects, presentations, morphisms, images, theorems, and decision procedures.
- A presentation is not the object that it presents, a registry label is not a category, and runtime validation is not a theorem.
- Never replace an undecidable equality problem with a new Boolean method.

## Goal substitution and agent hubris

Treat the user's technical discussion as a precise specification.
Do not read it as loose guidance because it arrives in prose.
Every mathematical noun, qualifier, example, caveat, and request to think can constrain the result.
If code and the stated model differ, surface the difference.
Never silently choose the code's weaker model.

This repository contains research code that is intentionally outside common software patterns.
The agent will tend to replace unusual mathematics with conventional code from its training distribution.
This default can change the object, hypotheses, codomain, or required construction.
Conventional code is not a useful default when the task is to implement new mathematics.

Assume that the user knows this repository, Sage, and the mathematical program better than the agent.
This is an operational limit on the agent's authority.
It does not make every user claim true.
It means that an apparent contradiction must become a discussion, not a silent correction.

Agent hubris occurs when the agent treats its current framing as the only possible framing.
An apparent implementation barrier proves only that the present approach has a barrier.
It does not prove that the mathematical requirement must be weakened.
The agent is often too close to its first design to see a better formulation.
User input can resolve the barrier by changing the representation, category, functor, or direction of construction.

Never make a theoretical compromise on the user's behalf.
This includes replacing a general object with a special case, a construction with a predicate, or a theorem with a runtime guess.
It also includes adding a fallback, an exception branch, or a weaker public operation to make the code run.

When the exact implementation appears impossible, stop before writing compromise code.
Report these facts:

- The exact requested object or statement.
- The precise obstruction in the current approach.
- The hypothesis or property that a proposed compromise would weaken.
- The mathematically distinct alternatives that remain visible.
- The smallest question that needs the user's judgment.

Recommend a compromise when useful, but do not select it without approval.
The user can often remove the obstruction without any compromise.
A short expert reframe can prevent generic code, false abstractions, and a later refactor.

For example, let $R$ be a commutative ring.
Let $M$ and $W$ be $R$-modules, and let $b:M\times M\to W$ be $R$-bilinear.
A user can request the submodule $\langle b(x,y)\mid x,y\in M\rangle_R\le W$.
Replacing it with a $\mathbb Z$-lattice's scale ideal changes the codomain and requested object.
The user already made that distinction.
The agent must preserve it, not teach it back or erase it.

Likewise, let $f:M\to N$ be an $R$-module homomorphism.
A request to construct $\ker(f)\le M$ is not a request to decide whether $\ker(f)=0$.
If current code decides only the latter in a special case, surface the mismatch before changing the construction.

A passing test can hide the substitution when the test encodes only the weaker claim.
The loop is self-confirming:

1. Replace the requested object with a familiar proxy.
2. Test the proxy.
3. Use the passing test as evidence for the original requirement.

Such evidence says nothing about the omitted requirement.
It makes later work inherit a mathematically false interface.

No instruction file can contain all of the user's mathematical knowledge.
Exact listening is therefore a required research method.
Implement what the user specified.
If that cannot be done exactly, surface the nuance and defer the mathematical decision.

## Native Sage model and direct code

- Use Sage's `Parent`, `Element`, `Category`, `Morphism`, and `Hom` structures.
- Model a functor as a functor and a morphism as a morphism.
- Let subcategory relations and Sage categories with axioms determine available methods, hypotheses, codomains, and algorithms.
- Put mathematical operations, constructions, and predicates in category methods, as specified above.
- Use a narrow subclass for one representation-specific defect that Sage categories cannot express.
- Override only the incorrect operation and retain the established implementation.
- Keep each method in the same order as the mathematical definition.
- A mathematician must be able to compare the method body directly with that definition.
- Do not hide the defining steps behind chains of non-mathematical helper functions.
- Return results in their correct parent and category.
- Make public operations and valid constructions explicit after every refactor.
- Compare valid constructions, methods, category membership, result parents, and notebook behavior.
- Compare semantics, not filenames, class counts, method counts, or structural similarity.

## Public interfaces and encapsulation

- Treat a leading underscore as a non-public interface marker.
- Call `self._f()` only inside the class that owns `_f` or inside a documented subclass contract.
- Treat every unrelated call to `x._f()` as a defect unless the declaration
  supplies the exact protected framework contract required by `OWN-05`.
- Treat `X._f(x)` as a defect when it bypasses instance dispatch.
- Do not read or write another object's `_state` directly.
- Ask another object through its public methods. Move missing behavior to the object that owns it.
- Do not expose internal state only to let callers reproduce the owner's behavior.
- Implement Python and framework hooks at the owning class boundary.
- Invoke those hooks through their public syntax or public dispatcher.
- Write `f(x)`, `parent(data)`, `iter(x)`, and `len(x)`. Do not call their protocol methods directly.
- In Sage code, callers use morphisms, parents, and elements through their public operations.
- A protected contract names its owner, permitted roles, types, invariants, and
  framework responsibility at the declaration. Invoke it through its designated
  dispatcher. Mathematical subsystems exchange owned values, not raw engine state.
- A call-site comment cannot authorize a private access or create an exception.
- Review every cross-object underscore access before committing Python or Sage code.

## Types

- Give each value the type that names its mathematical role.
- Use `Parent` for an object of a Sage category, not `Any` or `object`.
- Distinguish parents, elements, morphisms, coefficient rings, modules, matrices, domains, and codomains.
- Treat each mypy error as evidence about the model or import boundary.
- Fix the model, method owner, return contract, import path, or missing stub.
- Never weaken an annotation to silence the checker.
- Make stable `.sage` definitions importable when their real types cannot otherwise be named.

## `object` is never a type; `Any` has exactly one position

**`object` is never allowed as a type. There is no exception.** Not as a
parameter, not as a return, not inside a container, not under `TYPE_CHECKING`.
A value annotated `object` supports no arithmetic, no membership and no method,
so the annotation states nothing about the value and the checker admits
anything at all. It marks a place where a type was owed and not written.

`Any` is narrower. It has exactly one legitimate position: a **parameter of a
method whose job is to decide about an arbitrary argument**. So far as is
known those are `__eq__` and `__contains__`. `[1, 2] in MyModules` returning
`False` is a perfectly valid line of code — the argument really can be
anything, and answering is the method's whole purpose. If some other site
appears to take genuinely arbitrary input, that is a finding to raise, not a
licence to widen an annotation.

**`Any` is never valid as a return type.** A method knows what it produces.
Write the type:

- `Self`, when the method returns another object of the receiver's own kind;
- `None`, when it returns nothing;
- a preamble object whenever one exists. A natural number is
  the element type of `NN`, an integer the element type of `ZZ`, a real number
  the element type of `RR`. Reach for the preamble type before any Python
  built-in.

`float` is almost never right — it is a machine approximation standing where a
real number belongs. `list`, `tuple` and their relatives are never right: name
the notion you actually have, which is a set, an ordered set, a multiset, an
ordered multiset, or an indexed family. See *A list is not a mathematical
object* below for why that one choice cascades through every downstream caller.

**Inputs are held to the same standard.** A parameter is mathematically
structured and coherent, for the same reason a return value is: the signature
is where a reader learns what the operation is about. A method that accepts a
matrix where it means a morphism, or a tuple where it means a generating set,
has already lost the mathematics before its body runs.

**Private computation methods may use primitive and engine types internally.**
Those types remain inside the declared computation/transport owner. Its helpers
may exchange them as implementation data; mathematical consumers may not. A
protected mathematical contract still exchanges owned values. Naming a method
private or placing it in another module cannot expand this permission.
`OWN-05` and *Public interfaces and encapsulation* above own that boundary.

**Minting a type that names actual mathematics is welcome.** It is what the
preamble is for. A notion the work needs and the tree does not yet hold gets
its own object, its own place in the category graph, and its own name, and
that is a good day's work rather than a rule being bent. The test is never
novelty. It is whether the type has a mathematical referent a mathematician
would recognise, and it applies equally to a type that already exists.

**What is banned is a type invented to satisfy these rules.** A constructor
that took a list, a tuple and two integers does not become correct when those
become `MyCustomClassCreationDatum`. Nothing was fixed: the caller still
assembles the same unstructured data, the same mathematics is still missing,
and now there is a class with no referent to maintain as well. Ask what the
datum *is*. Usually it already has a name — a morphism, a generating set, a
presentation, an indexed family — and naming it makes the signature right with
no new type at all. When it genuinely has none and the notion is real, it is
`lean-categories`' to formalize: request it there, then present it; a real
addition to the category graph is never a wrapper to drop in.

Over-compliance is the failure from the other side. A class minted so a line
technically passes, a name coined because the rule said not to write `tuple`,
a type introduced to quiet a checker: each satisfies the letter and breaks the
statement, and each is worse than the original violation, which at least
stayed visible. These rules restate what the mathematics already requires. If
following one produces something a mathematician cannot name, the rule was not
the problem — stop and say so. The inventions this has already produced are
catalogued in `.agents/references/mathematical-auditor-priming.md`.

## Dynamic peeking is prohibited; the category is the type

`getattr`, `setattr`, `hasattr`, `isinstance`, `type(...)` comparisons, `cast`,
and instance-dictionary reads are explicitly prohibited in mathematical code in
the preamble.

- Never duck-type. Asking an object whether it happens to carry a name asks at
  runtime what the category graph already states.
- **Categorical containment is typing information.** Write `assert X in C`.
  Never write `isinstance(X, SomeClassRelatedToC)`. Membership is the
  mathematical statement; the class is an implementation accident, and one
  mathematical notion is realized by several unrelated classes.
- Assert the membership that *defines* an operation before using it. Every line
  below is then provably defined wherever it is reached.
- **Route by `case`/`match` on categorical containment.** `if`/`else` chains are
  almost never right here. A mathematical routing decision has one branch per
  category, and the reader must see the categories. Match a category with a
  guard, `case _ if x in FormModules(R):`, not a class pattern; a class pattern
  is `isinstance` written in different syntax.
- When an object lacks a capability, repair its placement. Do not probe. Refine
  it, construct it correctly, or state the gap on the owned interface.

| Peek | Write instead |
| --- | --- |
| `hasattr(x, "gram_matrix")` | `x in FormModules(R)` |
| `"_form" in x.__dict__` | `x in FormModules(R)` |
| `isinstance(x, SomeFormModuleClass)` | `x in FormModules(R)` |
| `isinstance(image, Vector)` | delete the branch; assert the parent |
| `getattr(g, "presented_group", None)` | `g in OwnedFinitelyPresentedGroups()`, then call it |
| `type(x) is X` | membership, or an owned element class |
| `cast(T, x)` | make the type real, or narrow by assertion |
| `x.__dict__.setdefault("_cache", {})` | `cached_method` |
| `setattr` on a class imported from `sage.*` | present the category through a preamble class; see *How the preamble presents the mathematics* above |

**Every use of `setattr` is suspect, not only on Sage's classes.** A reader of a
class must be able to see its fields by reading it. `setattr` puts state on an
object that the class never declares, so an auditor meets a field at runtime
that appears nowhere in the source, cannot tell which level introduced it, and
cannot tell whether it is always present. That is the same defect as
`__dict__` reads, arriving from the other direction.

There is no typing problem that forces it. The claim that a checker, a dynamic
class, or a mechanism made `setattr` necessary is a report that the
architecture is wrong at that point. Re-architect instead: declare the datum at
the category level that introduces it, establish it in that level's
constructor, and let it thread by cooperative `super().__init__`. If the field
cannot be declared where it belongs, the placement is wrong, and that is the
finding.

The exceptions are narrow, and each must be nameable at the site:

- `__contains__`, where the argument is genuinely arbitrary and deciding is the
  method's whole job.
- `_element_constructor_`, where the host invokes the owned element-construction
  contract for permitted literal or preamble data. This is not public
  admission for raw CAS parents or elements; private raising remains in adapters.
- A documented Sage runtime protocol inside its designated host boundary, or
  foreign representation dispatch inside the selected private adapter under
  `OWN-06`. Document the exact protocol and owner; a local comment alone grants
  no right to inspect a preamble object's state.
- Declarations under `if TYPE_CHECKING`, which have no runtime effect.

Nothing else qualifies. A probe outside these sites is a defect, and it is
where a non-mathematical shortcut hides.

**Exceptions are not control flow either.** `try`/`except` is banned in owned runtime
code, the same ban `test-guidelines` states for tests (`POLICY.NO_EXCEPTION_CONTROL_FLOW`).
A branch on placement is `case`/`match` on categorical containment; a computation the
engine cannot perform is an asserted frontier with its hypothesis named. A `try:` in
mathematical code is never weighed as "engine adaptation": an adapter that must catch an
engine exception is declared as such under `OWN-06`, and that declaration is the only
site. On 2026-09-17 the 500 `try:` blocks in the tree were reported as unmeasured
candidates; they are violations, and their node carries them as such.

## A list is not a mathematical object

`list` and `tuple` are programming constructs. They are not mathematical
primitives, and they do not belong in the preamble's public vocabulary.

Order is not the objection. Most objects here are ordered. The objection is
that `[1, 2, 1]` is Python, while $\{1, 2, 1\}$ regarded as an **ordered
multiset** is mathematics. Name the notion you actually have — a set, an
ordered set, a multiset, an ordered multiset, an indexed family — and each of
those is a real object that arrives carrying its own structure:

- a cardinality, and membership;
- unions, intersections, and the other set operations;
- an enumeration function where one exists;
- homs into other sets, so it composes with everything else;
- a place in a category, so its operations are inherited rather than written.

A `list` carries indexing, `len`, and `append`. None of those is a mathematical
operation. Concatenation is not union. A list has no homs and sits in no
category, so every operation on it must be hand-written.

**A list in one signature cascades.** The next caller writes
`range(len(xs))`, then `xs[0]`, then `zip`, then a comprehension building
another list — and the engineering idiom propagates from the type outward
through everything downstream. This is the mechanism by which mathematical code
turns into Python that happens to be about mathematics. The preamble must read
as a mathematical DSL, not as mathematics written in Python.

Consequences:

- `len` is almost never correct. Use `cardinality`. A length is an `int` and
  assumes finiteness; a cardinality is a cardinal and does not, so every `len`
  is a silent finiteness hypothesis at a site that never stated one. The order
  of a group and the order of an element are cardinalities, not integers.
- Do not loop to accumulate. **Sum over a set.** An index loop imposes an
  enumeration on an object that may have none, and hides the operation behind
  the iteration.
- Compare cardinalities, never lengths.

**Comparison itself is localized.** Do not compare coarse numerical invariants
in ordinary code at all. Every comparison belongs in `__eq__` or in
`is_isomorphic`, which are the two methods whose whole job is to decide
sameness. Everywhere else, ask the object.

Inside those two methods you `case`/`match` to route. One of the routes may
legitimately compare numerical invariants internally — but only in a case whose
hypotheses are stated in the match itself, so a reader sees the hypothesis
beside the comparison that needs it. A numerical comparison written outside
such a case is a criterion smuggled in without its theorem.

## Simplicity and prior art

- Choose the smallest implementation that satisfies the complete mathematical requirement.
- Add no unused parameter, speculative extension point, or interface with one caller.
- Add an abstraction only when a second real use requires it.
- Use the project's dependencies before adding code or packages.
- Use native Sage before adding a parallel implementation.
- Use a maintained package or mature reference implementation before new local code.
- Keep unavoidable local code small and cite its mature reference implementation.
- Remove obsolete constructors, aliases, fallbacks, bridges, and compatibility paths.
- Keep one current implementation for each operation or construction.

## Names and ownership

- Use established mathematical or Sage terminology.
- Name each entity by its mathematical role, not its storage or implementation.
- Treat a wrong name as possible evidence of a wrong abstraction.
- Check the definition, type, owner, operations, and category before a semantic rename.
- Give each mathematical entity one authoritative module and one public export.
- Place public exports at a clear package boundary.
- Keep category methods, catalogues of examples, session defaults, and computation code in their stated homes.
- Keep definitions, terminology, category declarations, exports, and decisions in one authoritative source.
- Do not create mirrored registries or synchronized copies.

## Repository placement

- Keep the installed package thin and stable.
- Move code from a spike into `src/` only after a high-level research notebook uses it.
- Do not promote code because it looks complete.
- Develop new mathematics in the active spikes by generalizing from verified examples.
- Use the frozen category specifications only as prior art.
- Install published dependencies normally.
- Put unpackaged external code in `computations/vendor/`.
- Code in `computations/vendor/` never graduates into the maintained package.
- Keep project-authored experimental code in a spike.
- Treat `computations/notebooks/` as the researcher's control surface.
- Do not reorganize, classify, or tidy that notebook tree unless the user asks.
- Use editable installs and repository symlinks instead of notebook path manipulation.
- Keep notebook setup cells minimal and make editable-install changes available without copying code.
- Use high-level notebooks for real mathematical work, not only API demonstrations.
- Keep the preamble small, cohesive, native to Sage, and usable without notebook setup.

## Tests

- Research's tests are its own and certify nothing outside it; correctness evidence exists only in the `lean-cas-dsl` acceptance suite.
- Test mathematical behavior and method resolution through Sage categories, not scaffolding or correction history.
- Assert the correct parent, category, domain, codomain, images of elements where defined, composition, or mathematical equality.
- Test high-level notebook operations when notebook usability is the claimed behavior.
- Use the smallest test case that distinguishes correct behavior from a plausible failure.
- Use a large named example only when the claim concerns that example.
- Verify the surface named by the requirement.
- Use a real Sage process for Sage behavior and a live kernel for notebook behavior.
- Inspect rendered output when the requirement concerns rendering.
- Treat a nearby green check as evidence only for the proposition it executes.

## Performance and search

- Measure wall time and its growth with input size.
- Use call counts only to locate repeated work.
- Remove repeated derivation, needless enumeration, repeated verification, and overly general algorithms.
- Preserve code that shows the correct mathematical sequence, even when a faster form is less clear.
- Start filesystem discovery at the requested path with a shallow query.
- Expand the search only when the evidence requires it.

## Completion and durability

- Complete the original mathematical operation or construction, not only a local type, test, registry, or plan task.
- Continue when the next in-scope step is clear and safe.
- Defer work only for a real dependency or a required user decision.
- Context limits and a successful local subtask do not justify deferral.
- End each substantive unit in a focused commit.
- Preserve unknown files until their ownership is known.
- After ownership is known, commit required files and use recoverable deletion for disposable files.
- Keep important work in version control, not only in a working tree or notebook session.

# Addendum: private Sage-runtime realization of preamble category types

The [architecture specification](CONTRIBUTING.md#preamble-architecture-specification)
governs this boundary. Host runtime reuse and engine computation are different
responsibilities. Neither permits a Sage mathematical parent or element to become
the public preamble object by reclassification, subclassing, or facade parenting.

The preamble's category graph supplies `ObjectType`, `ElementType`, and
Hom-category types. Its root runtime may use Sage `Parent`, `Element`,
dynamic-class machinery, and method containers to realize those generated types.
`ParentMethods`, `ElementMethods`, and `SubcategoryMethods` name private Sage
mechanisms, not public placement. Keep the mapping in the shared runtime; descendants
declare their immediate mathematical structure and do not assemble host bases.

The shared construction path establishes required data before public return.
Only the root owns non-cooperative host initialization. A host post-init or
element-construction hook implements that path and cannot bypass it. Refinement
acts on a preamble object whose supplied data place it in the added category;
it neither constructs missing data by a label, nor follows a computed answer,
nor adopts a foreign instance.

Method-resolution details remain private. The runtime must make the selected
preamble operation authoritative, preserve existing justified placements, and
propagate element and morphism behavior through the same graph. If private
Sage category joining or dynamic-class ordering is required, implement it once
at that owner under its declared protocol. Consumers do not call
`_refine_category_`, rebuild `__class__`, install methods, or intercept engine
constructors to change a result's public meaning.

Concrete Sage rings, modules, groups, matrices, and their elements remain private
computation representations. An adapter builds them from preamble data, invokes
established algorithms, then raises every result through the preamble constructors.
It does not reclass those Sage objects, patch their APIs, or teach Sage
constructors to accept preamble parents. Private computational workspace mutation
does not alter the defining data. Cache and lifetime choices respect `OWN-10`.

Historical mechanisms remain inspectable at
`archives/lattice-research/src/sage_patches/ring_base_category.py`,
`archives/lattice-research/src/sage_patches/ideal_submodule.py`,
`archives/lattice-research/src/sage_patches/fraction_quotients.py`, and
`archives/lattice-research/src/sage_patches/module_enrichment.py`, or in their
source history. These are references, not sanctioned public construction routes.
The live construction contract above is what future code must satisfy.

# Transcript-derived research directives (2026-08-21)

The governing model is:

- Mathematics determines the architecture.
- Categories own generic operations.
- Concrete classes store only necessary construction data.
- A leaf category handles only its immediate supercategory.
- Structure and methods must then propagate through the full category chain.
- The system must support parent, element, and subcategory methods.
- Category methods should precede class methods in the MRO.
- Concrete classes can then supply faster implementations when necessary.
- New leaf categories must need little repeated code.
- Generated methods are unacceptable because mathematicians cannot audit their source.

Specific mathematical directives include:

- A lattice is first a set and a module.
- Cardinality belongs to its underlying set.
- A formed module is constructed from its form morphism.
- Bilinear forms use the tensor square.
- Quadratic forms use the divided square.
- These form types require separate free-forgetful adjunctions.
- Forgetting a form is a functor, not an object method.
- Module morphisms require the same base ring.
- Every module-related category must require its base ring.
- `IntegralLattices` must also require an explicit ring.
- Membership predicates belong to refined subcategories.
- An object claiming membership must supply the required predicate.
- Other operations should remain category methods.
- Axiomatic subcategories need not have separate concrete realization classes.
- Special algorithms can make otherwise undecidable questions decidable on restricted categories.
- KBMAG is valuable for exactly this reason.
- Differences between full reflection groups and smaller reflection subgroups are substantive research results.

The migration philosophy is semantic preservation:

- A corpus selected for migration is presumed valuable.
- Every file must receive one semantic reading.
- Preserve mathematics, specifications, tests, examples, design work, and incomplete research.
- Incomplete research is not disposable.
- Foundational categories remain valuable without current callers.
- Tests and known values are mathematical products.
- Incorrect mathematics should produce a corrected statement.
- Deletion alone does not preserve the lesson.
- Remove a source only after its useful content has a durable destination.
- Byte equality, execution status, file names, maturity, and polish do not measure mathematical value.
- Do not split reading and implementation between agents when the reader’s mathematical context is essential.
- Prefer migration of existing prior art over a parallel implementation.

The epistemic directive is equally strong:

- A false architectural claim requires a review of foundational assumptions.
- Local counts and reduced error totals do not establish correctness.
- Inspect existing code, archived work, plans, and repository memory first.
- Use transcripts only when those sources do not resolve the question.
- Do not ask the user to make a technical decision that the assigned research should determine.
- Ask only when several materially different interpretations remain.

The recent verification rules were specific to the migration project:

- Perform the complete semantic migration before automated verification.
- Do not treat unverified work as deferred verification.
- Do not run Sage, tests, or hooks during that migration.
- Commit migration units without verification.
- Hold pushes until the later integrated verification pass.
- That later pass must use global `ai-review-ci` ownership.
- Sage source must be lowered before Python type analysis.
- QC must preserve detailed logs and wall-time reports.
- Local projects should follow current upstream `main`, not fixed revision pins.

Communication must report mathematical effects. It must not report token use, agent waves, repeated checks, or administrative state.

# Mathematical judgment and repository practice from transcript corrections (2026-08-21)

The preceding section records a first synthesis. This section adds the mathematical
reasoning, cognitive corrections, repository rules, and style requirements that the
short synthesis did not capture.

## Standard of mathematical thought

- Treat each mathematical correction as compressed research guidance.
- Derive the structure that makes the correction true.
- Do not translate one mathematical correction into one local method request.
- Identify the objects, morphisms, hypotheses, codomains, and universal properties first, in `lean-categories`.
- Determine where `lean-categories` places each construction before writing its representation.
- A named category must exist as a category, not as a class with similarly named methods.
- A named functor must act on objects and morphisms.
- A named adjunction must include the hom-set bijection, unit, counit, and naturality.
- Do not use category theory as a metaphor for a collection of constructors.
- Do not replace a mathematical object with the data returned by an external engine.
- External engines compute data used to construct preamble objects; their answers are untrusted.
- Local computational data never replaces the structure that explains its functorial behavior.
- Prefer a general mathematical construction when it removes many apparent local tasks.
- A short advisor question can expose a missing theory rather than a missing method.
- Unfold that theory before estimating or implementing the apparent method backlog.
- Do not hedge after the user has supplied enough structure to derive the answer.
- Perform the mathematics needed to resolve the stated universal property.
- If a conclusion contradicts standard structure, rederive it before changing code.
- One false foundational assertion invalidates every downstream inference that used it.
- Review foundational assumptions after such a contradiction.
- Do not review counts, file totals, or gate output as substitutes for those assumptions.
- Ask whether the current construction is the requested mathematical object at all.
- Ask whether the code models the user's stated object, morphism, or functor exactly.
- A locally working representation does not answer either question.

## Object, structure, and representation

- Start from mathematical objects and their relations.
- Choose representations only after `lean-categories`' placement is clear.
- A lattice is a set with module structure and a form.
- It does not merely hold unrelated objects representing those structures.
- A formed module is a module with a form.
- It does not wrap a second module that remains the real mathematical object.
- Category membership must correspond to actual supplied structure.
- An object in a structured category must carry the data required by that category.
- Do not refine an existing object into a data-bearing category without constructing the required data.
- Construct preamble objects through the preamble category hierarchy.
- Refine preamble objects only when their supplied defining data place them in the
  added structure, never on a computed answer; keep Sage representations private
  to computation adapters.
- Provide a `preamble.all` construction surface analogous to `sage.all`.
- That surface constructs preamble objects and populates the research namespace.
- Never build a parallel toy hierarchy when the task concerns the live preamble hierarchy.
- A toy that proves itself against itself does not prove the real architecture.
- Convert one real category before claiming that a category mechanism reduces author effort.
- User-facing notebook objects are evidence about the live surface.
- Do not describe a new experimental path as the state of that surface.

## Category and class architecture

- Defining a new leaf category must feel routine.
- The leaf author handles the leaf and its immediate supercategory only.
- The leaf author never implements the transitive chain manually.
- `super_categories()` is the sole declaration of categorical inheritance, presenting `lean-categories`' inclusions.
- Do not add a second registry, binding declaration, or `forgets_to` relation.
- The declared category graph already contains that information.
- Sage already derives parent, element, and morphism method hierarchies from that graph.
- The owned mechanism must propagate constructors and fields through the same graph.
- The category and its implementation class should become one readable source unit.
- The owned `ObjectType`/`ElementType`/Hom-category types are the public implementation protocol.
- Sage method-container/dynamic classes may realize those types privately during migration.
- Each generated implementation type stores only the minimal data introduced at that level.
- Its construction consumes that data and delegates the remaining construction upward.
- A category level supplies the structure it introduces.
- It must not merely declare an obligation that its own construction could discharge.
- Abstract obligations remain valid for genuinely axiomatic categories.
- An axiomatic subcategory need not have a separate concrete implementation class.
- Generic mathematical operations belong on the category types where `lean-categories` places them.
- Object operations belong on `ObjectType`; element operations on `ElementType`; arrow operations on the corresponding Hom-category element type.
- Concrete/runtime classes remain minimal data containers when Sage ownership requires them.
- Category methods precede concrete class methods in the owned MRO.
- A concrete class can then provide a more efficient implementation when required.
- Generated forwarding methods are forbidden.
- A mathematician must be able to open the source and inspect each method body.
- Do not replace readable mathematics with generated indirection.
- Delete hand-written forwarding after the category graph supplies the operation directly.
- Do not delete forwarding before the correct category surface exists.
- The mechanism must compose through parents, elements, and morphisms.
- The mechanism must also propagate fields and construction data.
- Method propagation without data propagation does not solve the architecture.
- Data propagation without the three method surfaces does not solve it either.

## Immediate-supercategory construction

- In a chain `Sets -> Modules -> Lattices`, each level owns one construction step.
- A lattice constructor supplies the module required by the module level.
- It never reimplements set cardinality or product behavior.
- A module constructor supplies its underlying set construction.
- A free module of rank `n` supplies the product of `n` copies of its base ring.
- The set level carries cardinality, finiteness, countability, products, and coproducts.
- The ring level supplies the set data for the ring.
- Higher levels inherit the set operations through the category chain.
- `L.cardinality()` must work without `Lattices` naming cardinality.
- The implementation must preserve actual element parents and element operations.
- Do not identify a module's elements with bare tuples merely because their sets are bijective.
- Use the correct categorical relation when only a bijection is available.
- Cardinality and finiteness are invariant under bijection.
- Element representation and parenthood are not invariant under an arbitrary implementation shortcut.
- The architecture must preserve both facts.

## Subcategories, predicates, and operations

- Distinguish membership predicates from ordinary categorical operations.
- A predicate-defined subcategory states the contract for membership.
- An object refined into that subcategory supplies the predicate computation, which is untrusted.
- The category does not return `True` merely because its name asserts a property; it answers by placement only where `lean-categories` proves the predicate for every object.
- Other operations should remain category methods whenever their hypotheses are categorical.
- Place axioms as high as their hypotheses permit.
- Presentations of foundational categories remain essential without current callers.
- Presenting the category of magmas is foundational work, not disposable empty code.
- Empty method bodies, low call counts, and unfinished descendants do not reduce its value.

## Forms and formed modules

These recall `lean-categories`' definitions to fix the presentation; where they differ, the formalization governs.

- A form is not synonymous with a bilinear form.
- Bilinear and quadratic forms have different classifying constructions.
- A bilinear form on `M` is a morphism from `M tensor M` to its value module.
- A quadratic form uses the divided square appropriate to quadratic maps.
- Construct a formed module from that defining form morphism.
- Recover the underlying module from the source construction of the form.
- Do not pass the same module twice through independent constructor arguments.
- Independent copies can disagree and make invalid states representable.
- A Gram matrix constructor first constructs the implied free module.
- It then constructs the required homset and form morphism.
- It finally calls the main formed-module constructor.
- Forgetting the form is a functor between categories.
- It is not a method on a formed module.
- Each form flavor has its own free-forgetful adjunction.
- The free bilinear form is the identity on the tensor-square classifier.
- The free quadratic form is the identity on the quadratic classifier.
- Present each adjunction through its hom-set bijection, as `lean-categories` formalizes it.
- Do not name an adjunction and then deny the existence of its adjoint.

## Base rings and morphisms

- A module category always requires its base ring.
- No module constructor may silently substitute the integers.
- `IntegralLattices` also requires an explicit ring.
- Remove optional-ring signatures and their fallback branches.
- A module morphism has a source and target over the same base ring.
- `Hom` between an `R`-module and an unrelated `S`-module is not a module homset.
- Scalar extension and restriction require named functors and changed categorical data.
- Do not conceal such changes inside a permissive homset constructor.
- Make invalid base-ring combinations impossible at construction.
- Fix the architecture that permits ringless modules.
- Do not patch individual ringless instances.

## Decidability and specialized algorithms

- State the exact decidability boundary for each equality or isomorphism question.
- Do not invent Boolean procedures for general undecidable problems.
- Do not use general undecidability to reject a specialized decision procedure.
- KBMAG can make equality decidable for groups with suitable automatic structures.
- Such machinery is significant research, not a conflict with the undecidability rule.
- Return the proposition, a `Predicate` that `ask()` evaluates, where the available hypotheses and algorithms do not decide the question; never a bare `Unknown`.
- A specialized algorithm should return a definite result on its valid domain.
- Record its hypotheses, citing the `lean-categories` theorem that justifies it, in the category that supplies it.
- Let category placement select the specialized algorithm.
- Do not special-case it inside a general method without a placement stating its hypotheses.

## Mathematical discrepancies and research findings

- Preserve discrepancies that expose distinct mathematical group actions or conventions.
- A Sterk root-count difference is not debris.
- It can distinguish full reflection-group orbits from smaller subgroup orbits.
- Preserve the groups, actions, and orbit relation needed to state that difference.
- Do not reduce such a finding to a note that two numbers disagree.
- A false source statement is recorded with its evidence, and the corrected statement is requested from `lean-categories`; research does not write the correction.
- Land the cited specimen that exposes the discrepancy in the repository.
- Do not retain tests whose only purpose is to forbid a past mistake.
- Test the intended positive mathematics instead.
- Cited published tables and literature examples can be proper oracles.
- Their value does not depend on whether an agent considers the source prestigious.
- An expected value needs a verifiable source independent of the implementation: a proof, a cited result, or an independent oracle.
- Verify provenance when adding a new citation-gated specimen.
- An existing fixture value with informal provenance is not an oracle. Keep it during migration as a value awaiting its source, never as evidence.

## Semantic migration

- The preamble centrally holds research's locally-authored Sage code. The mathematics it presents is `lean-categories`'.
- A migration request establishes the value of the selected corpus.
- The executor decides destination and synthesis, not whether the corpus deserved preservation.
- The unit of migration is a mathematical notion, not a file.
- Read each notion once for semantics.
- The reader should migrate or synthesize it while that context is live.
- Do not separate deep analysis from implementation when implementation needs that mathematical context.
- Do not make one agent produce a report for an unrelated new agent to interpret.
- A summary is not the migrated mathematics.
- Move prior art into the live preamble before reconciling it with current code.
- Prefer a real move over a parallel rewrite.
- After a mistaken edit yields the correct state, repair forward.
- Do not undo the correct state merely to reproduce it by a preferred method.
- Reconcile source and destination until the result is semantically a move plus required updates.
- Delete the original only after every useful notion has a destination: a preamble presentation, or a `lean-categories` request for mathematics it lacks.
- Deletion is a receipt for completed relocation.
- It is never a value judgment on the source.
- Preserve code, tests, specifications, examples, design corpora, and incomplete research.
- Incomplete research remains research.
- Planning corpora can contain mathematical structure and future categorical homes; the mathematics in them is carried to `lean-categories` as requests, never adopted here.
- Stub declarations can present structure `lean-categories` formalizes before algorithms exist.
- Existing TDD suites are forward requirements and must migrate to the preamble surface.
- Existing parity tests can document delegation boundaries.
- False source mathematics creates an obligation: record it with its evidence and request the corrected mathematics from `lean-categories`.
- Do not delete the false statement and preserve only an error ledger.
- Non-code logs, telemetry, caches, and tool output are outside a mathematical code migration.
- Do not create dispositions or rulings for irrelevant material.

## Value and evidence during migration

- Byte equality has no positive or negative mathematical meaning.
- A checksum can locate possible duplicates but cannot decide semantic equivalence.
- Execution status does not determine research value.
- Maturity, polish, file name, directory, and current scope do not determine research value.
- The absence of callers does not determine research value.
- The absence of complete algorithms does not determine research value.
- A source outside the current preamble scope is a reason to enrich the preamble.
- It is not a deletion reason.
- Compare source and destination definitions, hypotheses, codomains, conventions, and behavior.
- Verify that the destination presents every useful mathematical distinction.
- If the destination cannot express a notion because `lean-categories` lacks it, request it there; research does not define it.
- Do not discard the notion because the destination is incomplete.

## Execution shape for large migrations

- Inventory files once.
- Partition them into disjoint semantic batches.
- Assign one reader to each artifact or notion.
- Read, decide, migrate or synthesize, and retire the source in one context.
- Do not analyze the same material in repeated waves.
- Do not create an analysis fleet followed by a context-free implementation fleet.
- Preserve an agent's mathematical context when revising its instructions.
- Ask it to checkpoint before stopping it.
- Stop only when its frame is unusable, not when one instruction changes.
- Use agent reasoning effort that matches the mathematics.
- Do not spend a large research context on a file move or import update.
- Perform simple moves and direct edits directly.
- Do not write edit scripts for a bounded hand edit.
- Do not replace a direct migration with scripts that match and rewrite source text.
- A sweeping architectural refactor need not pass tests at each intermediate state.
- Determine the correct final migration and execute the coherent sweep.
- Do not invent an incremental-green requirement that the user did not give.
- During a declared semantic-only migration, do not run tests, hooks, or Sage.
- Commit those migration units with the user's declared hook posture.
- Run the separate integrated verification pass only after the semantic migration finishes.

## Architecture before local repair

- A repeated local defect often indicates one missing mathematical foundation.
- Fix that foundation before patching its instances.
- If a module can exist without a ring, forbid ringless construction.
- Do not hunt only for the current ringless object.
- If a formed module delegates through `forget_form`, fix its construction chain.
- Do not add another forwarding method.
- If many leaves restate set behavior, fix the category construction chain.
- Do not optimize the forwarding calls.
- If prior art already solved the problem, migrate it before deriving a new mechanism.
- Read the archived implementation and its reasons.
- A row marked superseded is a claim requiring semantic comparison.
- It is not evidence that the older implementation adds nothing.
- Preserve small load-bearing details from the older implementation.
- Do not infer their irrelevance from file size.

## Fundamental-assumption reset

The conditions below require a frame reset rather than a local correction.

- A user states that a claimed mathematical object already works in live notebooks.
- A user identifies a category, functor, or adjunction that the implementation does not model.
- A user shows that the current code permits a mathematically invalid object.
- A user shows that the work built a parallel hierarchy instead of changing the live hierarchy.
- Two corrections remove mechanisms introduced by the same design frame.
- A local patch produces another defect at the same ownership boundary.
- An acceptance check measures a toy, count, or checker rather than the requested object.

When one condition occurs:

- Stop the local edit.
- Restate the requested mathematical object in standard terms.
- Identify the live repository object that must model it.
- List the foundational assumptions used by the current approach.
- Check those assumptions against source, runtime objects, and prior art.
- Remove every inference whose premise failed.
- Resume only from the corrected mathematical model.
- Do not ask the user to select the next probe when the repository can answer it.
- Do not manufacture ambiguity after the user has already decided the architecture.

## Work selection and checking

- A count of type errors does not measure architectural correctness.
- A count of passing tests does not measure mathematical correctness.
- A count of migrated files does not measure semantic completion.
- A green toy specimen does not prove migration of the live surface.
- State the mathematical claim the current artifact is meant to make true.
- Exercise that claim on a concrete repository object; the exercise is research's own check, not evidence of correctness.
- Choose specimens that exercise the real category, constructor, element, and morphism paths.
- Use notebook research objects when the requirement concerns notebook research.
- Do not substitute a nearby proxy object.
- By-eye review during a semantic migration concerns definitions, organization, and types.
- Automated verification belongs to its separately declared pass.
- Do not report unverified work as deferred verification.
- It is simply unverified until that pass occurs.

## Repository organization

- Organize the preamble by `lean-categories`' placement.
- The tree should expose the category hierarchy to a mathematician.
- Place generic constructions at the highest valid categorical level.
- Keep value-level form morphisms distinct from categories of formed modules.
- Keep research-specific computations below the general structures they use.
- Preserve a clear root for categories, functors, homsets, subobjects, and named specimens.
- A new leaf should have one obvious filing location.
- Adding that leaf should require only its new data and immediate-supercategory construction.
- Do not keep the same mathematical notion in an archive and the live preamble after migration.
- Do not create parallel sources of truth.

## QC and tooling house rules

- Global QC belongs in `ai-review-ci`.
- Local repositories delegate to that global owner.
- Sage source must be lowered to Python before Python type analysis.
- Type checkers inspect the lowered Python, not raw `.sage` syntax.
- The custom Sage parser must be globally available to the lowering path.
- `sage-stubs` supplies the global Sage type surface.
- Owned tools track the latest upstream default branch.
- Do not create fixed revision policy for fast-moving local projects.
- Diagnostic recipes must preserve detailed errors, warnings, and issues in logs.
- Their final output must name the detailed log paths.
- Test execution must produce wall-time and profiling artifacts.
- Agents should inspect those artifacts instead of rerunning long commands for omitted output.
- These rules govern the later verification pass.
- They do not authorize running verification during a semantic-only migration.

## Communication and research style

- Lead with the mathematical result or unresolved mathematical point.
- Explain repository objects in plain technical English before using local shorthand.
- Do not report internal batch labels without their mathematical referents.
- Do not report agent waves, token use, idle notices, or administrative counts.
- Do not describe an analysis report as if its mathematics landed in the repository.
- State what was migrated, synthesized, corrected, or left unresolved.
- Explain the mathematical meaning of a discrepancy.
- Do not substitute tourist commentary for a construction, theorem, definition, or source edit.
- Do not use vague phrases such as `missing machinery` without naming the missing objects and morphisms.
- Do not call work deferred when the assigned task requires its completion.
- Do not ask the user to decide questions that mathematical analysis should decide.
- Ask only when the remaining alternatives encode different research choices.
- Preserve long-lived decisions in their owning plan during a long migration.
- Do not let important architecture exist only in chat.
- A plan records settled mathematical direction.
- It does not replace the code, proof, or migrated research.

# Categorical constructions carry structural relations

The preamble has categories, method classes, and the category graph. It has no
independent behavior-composition layer.

- Do not call a preamble component a `mixin`.
- Do not insert a hand-written Python base to state a mathematical relation.
- State the relation, as `lean-categories` formalizes it, in the category graph.
- Class inheritance can implement the graph after category placement.
- Class inheritance must never replace categorical placement.
- `ObjectType`, `ElementType`, and Hom-category element types expose operations placed
  on a category in the public preamble architecture.
- Sage `ParentMethods`, `ElementMethods`, and `MorphismMethods` are private runtime
  implementation vocabulary during migration, not a second public class graph.

The set of core categorical constructions is small. Inspect all existing owners
before creating another construction.

- Start with `Cat.Object`, `SliceOver`, `CosliceUnder`, `Product`, `Coproduct`,
  `Biproduct`, `TensorProduct`, `Kernel`, and `Cokernel`.
- Inspect the preamble's module-level `Subobjects` construction as part of the same
  analysis.
- Use this subtree as the canonical construction vocabulary.
- Do not create a local helper for a relation already represented there.
- Do not let a preamble category silently use Sage's parallel construction.
- Resolve the construction owner instead of patching each call site.
- Do not keep two construction paths for the same mathematical construction.

Modules with varying base rings project to the category of rings. Modules over a
fixed ring form one fiber of that projection.

- A construction that requires one base ring belongs inside that fiber.
- Scalar extension and scalar restriction connect different fibers.
- Do not encode the same-base condition through Python inheritance or method
  resolution.
- Products, coproducts, tensor products, kernels, and cokernels must preserve the
  selected base ring when their definitions require it.
- A category join that returns `None` from `base_ring()` exposes an incorrect
  categorical relation.
- Fix the join or construction that lost the base ring.
- Do not add a local `base_ring()` override before that relation is correct.

A formed module is a module equipped with a form morphism. It is not a wrapper
around another module.

- Never inspect `__dict__` to discover mathematical structure.
- Never recover a deleted wrapper field through direct storage access.
- Ask the category-owned interface for the form and its defining module.
- A construction must define its action on objects and morphisms.
- A parent-only result does not establish a categorical construction.

Let `i: A -> M` be a subobject inclusion. For a bilinear form
`b: M tensor M -> R`, the induced form is `b compose (i tensor i)`.

- Implement formed subobjects through this functorial pullback.
- For another form classifier, apply its source functor to `i` before composition.
- Do not infer formed-subobject behavior from `_form` or `_module` storage fields.
- The subobject construction owns this transport.

When a correction identifies an existing construction subtree, return to that
owner immediately.

- Do not reduce the correction to a naming change.
- Do not continue a local field repair after the ownership error is known.
- Trace the canonical constructor, category join, parent construction, morphism
  action, and inherited methods as one path.
- A local patch is incomplete while that path remains incoherent.
- If local edits stop producing mathematical progress, return to the categorical
  construction. Do not stop the assigned work.

