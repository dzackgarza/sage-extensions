# Contribution policies

These policies govern the mathematical library. Each policy has a unique
identifier, grouped by family:

| Family | Governs |
| --- | --- |
| `OWN-*` | [normative architecture](#preamble-architecture-specification): sanctioned construction paths, the recursive public boundary, encapsulation, and reuse |
| `ARC-*` | architecture of the preamble's presentation of `lean-categories`' mathematics |
| `API-*` | the public surface of preamble objects |
| `CON-*` | constructors, witnesses, actions, and structural transport |
| `CAT-*` | category placement, chosen data, and computational capability |
| `DEF-*` | definitions, predicates, structural results, and special cases |
| `LEX-*` | mathematical vocabulary and public type names |
| `SET-*` | mathematical collections, underlying sets, and cardinality |
| `ENG-*` | delegation of heavy computation to exact engines |
| `BND-*` | private engine crossings and representation boundaries |
| `BRG-*` | external-system interoperability and bridge transport |
| `ENV-*` | repository execution and environment conventions |
| `STY-*` | corrective implementation style and declarative Python patterns |
| `FSA-*` | search of `lean-categories` and its libraries, absence claims, and the sourcing of a formalization request |

## Preamble design philosophy

**The preamble presents, behind one uniform interface, operations that
`lean-categories` formalizes, and wires them to existing implementations. It
owns no mathematics and is not a mandate to build another computer algebra
system.** `lean-categories` is the single mathematical authority: it alone
defines what an object, category, operation or theorem is, where it lives and
what it returns, formalizing from the literature and blind to every
implementation. A feature request ordinarily asks the contributor to present a
construction `lean-categories` already formalizes, with the objects, maps and
hypotheses it states, and to route it to a computation. It does not ask the
contributor to define mathematics or to invent the algorithm that computes it.
Mathematics `lean-categories` does not have is requested there
([AGENTS.md](AGENTS.md#a-missing-foundation-parks-the-work-that-found-it-always-on)),
never written here.

Every public value is a preamble object. Sage, GAP, Julia, OSCAR, Singular,
Macaulay2, PARI/GP, and other suitable maintained systems provide private
computation. The preamble supplies the uniform presentation and the integration
between their results and its own objects. A uniform interface must make these
capabilities compose without requiring the researcher to know which engine was
called, speak its vocabulary, or handle its objects. Every computation behind
the interface, a Sage call or research code alike, is untrusted: nothing it
reports about its own correctness is believed. Correctness evidence exists only
in the `lean-cas-dsl` acceptance suite, whose expected values are independently
cited or proved.

This is the integration philosophy of `sage-categories`, applied to the
preamble's stricter public boundary. Its
[README](https://github.com/dzackgarza/sage-categories/blob/main/README.md)
names categories, functors, and universal constructions as the reuse model;
its [repository-role instructions](https://github.com/dzackgarza/sage-categories/blob/main/AGENTS.md#repository-role-integration-framework-and-engine-delegation)
make stitching and engine delegation the engineering purpose. The
[architecture specification](#preamble-architecture-specification) below turns
that purpose into construction, dependency, and encapsulation contracts.

### Mathematical dependency tracing

**First locate the addition in `lean-categories`' formalization, independently
of the current implementation. Then unfold the formalized mathematics it needs.
Only afterwards select its implementation.** This applies to a new operation, category, object,
morphism, specialization, research example, or repair that introduces new
mathematical behavior. It is not a preliminary search for a convenient class
whose existing methods can be made to resemble the requested answer.

Start with the mathematical question a researcher is asking. State the input
objects and their categories, the desired object or morphism, its defining
datum or universal property, and the hypotheses under which it exists. Include
the maps that make the result useful in subsequent mathematics. Establish these
facts from `lean-categories`' formalization, not from recalled definitions, this
repository's code or the current backend's capabilities. What `lean-categories`
does not formalize is a request there, stating the mathematics wanted and its
sources.

Express the request in the vocabulary an ideal mathematical API should support:
sets, indexed families, maps, categories, functors, groups, actions, rings,
modules, subobjects, quotients, tensor products, schemes, sheaves, complexes,
and the other standard notions the question actually uses. Pseudocode may
express this account, but it is mathematical notation, not a claim that the
displayed Python names exist. Name the mathematical operation before discussing
classes, storage, registration, adapters, callbacks, or dispatch.

For each notion in that account, recursively ask what makes it meaningful:

- What are its defining objects, operations and laws? What additional datum is
  supplied, rather than inferred from a property or chosen silently?
- In which category do its morphisms live? What are their source and target,
  their composition, and the maps retained by the construction?
- Which subobjects, quotients, limits, colimits, or other standard constructions
  does it use? What diagram, indexing object, or equivalence relation defines
  them, and which existence or preservation hypotheses are needed?
- Which structure is forgotten, transported, or added? If a construction on
  underlying objects is used, what theorem supplies the desired structured
  object and its maps? Faithfulness alone does not supply that theorem.
- Which properties refer to which mathematical object? Specify, for example,
  the notion of integrality or reflexivity in use rather than transferring a
  familiar property name between unrelated theories.
- What do these prerequisites themselves require, down to the chosen
  set-theoretic and categorical foundations: sets and families, functions,
  relations, objects and morphisms, identities and composition, and the
  relevant universal constructions? Retain size and finiteness hypotheses;
  a category is not assumed to have a finite enumerable set of objects.

The result is a mathematical dependency account, not a flat list of associated
subjects or a list of files to create. Each dependency must explain what datum,
map, theorem, or construction it supplies to its dependent notion. A phrase
such as "needs category theory" does not explain the dependency. Neither does
adding a class named after the missing notion.

#### Unfold through established foundations, not repeated reconstruction

The trace must reach the foundations, but it need not restate their definitions
for every leaf. Follow and cite the `lean-categories` formalization that unfolds
a prerequisite. Make the path to it explicit; do not stop at an unexplained term
such as module, action, or sheaf because a similarly named class exists. A
prerequisite `lean-categories` does not formalize is a formalization request
there, never a definition supplied here. No separate trace registry is
required.

Distinguish three sorts of dependency without weakening any of them:

- **Defining mathematics:** what the requested object and maps mean, and the
  general theory needed to express them. These requirements do not shrink to
  match the current implementation.
- **A computational realization:** the additional hypotheses, presentation,
  coordinates, resolution, cover, or finiteness that a selected algorithm uses.
  Its comparison with the defined object is part of the obligation.
- **A related extension:** a broader theory or further research question not
  required by this request. Record a concrete discovered need when appropriate,
  but do not make every mathematically related generalization a prerequisite.

Different presentations of the same mathematics may yield different computation
routes. Establish their comparison rather than treating the easiest one as the
definition. Conversely, do not demand every possible computational route before
using one justified route. For example, a particular sheaf-cohomology computation
may use an acyclic cover while another uses a resolution. The underlying sheaf
and complex categories and the comparison remain mathematical requirements;
this does not force every calculation to construct a spectral sequence. An
unpresented general interface that `lean-categories` formalizes remains owed
even when one computation can already be performed.

#### An example of the reasoning, not a prescribed workstream

Consider a request involving an equivariant morphism of modules, with actions
formalized as functors and forgetting the action as evaluation. A mathematical
trace can begin as follows:

```text
Requested: a morphism between two R-modules with G-actions.
Needed: the two R-modules, their G-actions, and an equivariant linear map.
Actions: functors from the one-object category BG to R-modules.
Maps: natural transformations between those functors.
Unfold BG: the group, its elements, multiplication, identity, and inverses.
Unfold R-modules: the ring, underlying additive groups, and scalar actions.
Unfold both: underlying sets, functions, products, and their defining laws.
Unfold the categorical language: objects, Homs, identities, composition,
functors, and naturality, with the actual source and target of each map.
```

If the request also asks for a kernel, scalar change, or invariant submodule,
continue the trace through that construction and its hypotheses. Do not append
an unrelated collection of matrix routines. The point is to identify which
formalized general mathematics supplies the requested result, so that a module
action, a geometric action, and another structured action are presented through
the same theory without pretending their computations are identical.

The same reasoning applies in geometry, homological algebra, arithmetic,
polyhedral geometry, and every other preamble domain. A sheaf operation unfolds
through its site or space, covering and restriction data, category of values,
and relevant functors. A metric or convex construction must specify its space
and geometric hypotheses before importing a Euclidean computation into another
geometry. These are examples of how to ask the questions, not a fixed list of
foundations to implement on every task, and not a toric-cohomology checklist.

#### Compare the mathematical account with the available language

After the mathematical trace, check each required notion against
`lean-categories`, then inspect the preamble's presentation of it (generated
reference, live source and consumers), and then the relevant maintained
packages. For each required notion, establish whether `lean-categories`
formalizes it, whether the preamble presents it with its data, maps, hypotheses
and inherited structure, and whether a computation is wired for the case at
hand. Only `lean-categories` establishes that a mathematical prerequisite exists;
the name of a method, a numerical answer, a category label, or a foreign engine
object does not.

Distinguish mathematics `lean-categories` lacks from a formalized operation the
preamble does not yet present, a missing comparison or inherited datum in the
presentation, a specialization that bypasses its foundation, and an unavailable
computational case. These require different responses. Missing mathematics is a
formalization request to `lean-categories` and parks the work
([AGENTS.md](AGENTS.md#a-missing-foundation-parks-the-work-that-found-it-always-on));
it is never written here. A formalized operation that exists in Sage while
absent from the preamble calls for integration, not reinvention. An API may also
present the correct object while a requested decision procedure is unavailable
or undecidable. Do not confuse that with nonexistence of the object.

When this comparison exposes an actual gap, record it in the
[native issue tree](https://github.com/dzackgarza/research/issues/46) under `DEV-59`. Explain the missing mathematics
and the dependency path that exposed it, not only the failing method. Search
broadly enough to distinguish absent machinery from undiscovered machinery;
record the inspected boundary and unresolved questions honestly. For missing
mathematics, the complaint links the `lean-categories` request.

Then select the remaining implementation delta under `OWN-01` and `DEV-56`.
Repair a missing presentation or wiring at its owner and connect the real
consumer.
Record newly discovered independent needs without silently expanding the active
task. Do not turn the trace or complaint into a substitute for a repair already
required by that task. Equally, do not suppress a foundational finding merely
because it is outside the file, workstream, or session currently being edited.

### What the preamble contributes

The distinctive work is making separate capabilities form one usable interface
to the mathematics `lean-categories` formalizes. That includes placing an
operation where `lean-categories` places it, retaining the data its definition
names, carrying the structure and maps its constructions state, and reconciling
engine representations with those requirements. The mathematics is
`lean-categories`'; the contribution here is its presentation and wiring, even
when the final implementation consists mostly of declarations and short
compositions.

For a typical feature, the intended contribution consists of:

- A presentation of the `lean-categories` definition, with the defining data and
  hypotheses it states.
- Construction through existing preamble categories and sanctioned constructors.
- Reuse of inherited operations, structural functors, and universal maps.
- A private integration of a suitable maintained computational operation.
- Complete raising of results, including elements and constituent maps.
- Examples that exercise the presentation, executed only in the authorized
  verification phase. They are research's own and certify nothing; correctness
  evidence exists only in the `lean-cas-dsl` acceptance suite.

These responsibilities do not imply a new file, class, or adapter for every
feature. An existing owner may already supply several of them, and an existing
adapter may already contain the needed computation. The contribution is the
actual missing integration, not a restatement of everything the dependencies do.

### Two kinds of reuse are required together

**Mathematical reuse** means deriving behavior from structure `lean-categories`
formalizes and the category framework already presents. A differential graded algebra uses the common graded
algebra and complex structures. A special localization uses the general
localization construction. A newly presented structured category uses the
existing object, element, morphism, and functor machinery rather than
reimplementing them under new names. The hypotheses that justify inheritance or
transport are `lean-categories`' theorems; a forgetful functor does not preserve
every construction merely because it forgets structure.

**Computational reuse** means leaving established algorithms with systems that
already maintain them. A generic cohomology interface does not justify a new
local homology algorithm. A common preamble category does not justify rebuilding
finite-diagram or path-reduction computations. The same prior-art requirement
applies at the framework level as at a specialized mathematical level.

Neither kind substitutes for the other. Calling Sage directly from a specialized
constructor can reuse an algorithm while bypassing the preamble's presentation
of the construction. Conversely, presenting the right construction in a generic
module can still duplicate an entire maintained computational system.
The intended architecture combines a shared semantic construction with suitable
maintained computations behind its private boundaries.

**Presenting an operation does not mean implementing its algorithm; delegating
the algorithm does not mean surrendering the interface.** All publicly reachable
constituents remain preamble objects. A private engine can compute a
presentation or representative, but its result must become the preamble object
with the structural maps the formalized operation requires. Neither a thin facade over foreign objects nor a fresh
implementation of all their arithmetic satisfies this division of responsibility.

### Shared foundations should make later work smaller

The framework exists so that a new mathematical specialization supplies its new
data and immediate structural relationships, then receives the consequences from
the existing construction machinery. The author of a formed module should not
also implement general set behavior. A geometric cohomology consumer should not
also implement general module kernels. A new action should not bring another
implementation of identity, composition, or scalar change.

When several apparent methods require the same missing foundation, treat that
foundation as the common dependency. Supply it at its owner, connect the first
real consumer, and let other consumers use it. Do not preserve a method-by-method
backlog that assumes every consequence needs an independent implementation.
Equally, do not use the word foundation to justify constructing an entire new
framework before the selected mathematical operation can begin. Reuse the
available framework and repair the exact prerequisite that the consumer needs.

A claim of reusable foundations must be visible in a real consumer. The new
construction should obtain its data, maps, and inherited operations through the
shared route. Merely placing duplicate algorithms in one file, adding an abstract
base, or adding a category class does not establish that later work has become
simpler. If each new specialization still needs to understand transitive runtime
initialization or reconstruct structural maps, repair the framework contract.

### Select dependencies by the responsibility they can discharge

A computation package need not implement the preamble's class compiler, public
interface, or whole research workflow to be useful. Ask whether it supplies the
specific computation with the required inputs, hypotheses, and outputs. A
different object model or method spelling normally calls for an adapter, not
rejection of the computation. A result missing necessary maps calls for further
capability research or a precise integration decision, not an unsupported claim
that an invariant is the full construction.

The [sage-categories complaints](https://github.com/dzackgarza/sage-categories/blob/main/COMPLAINTS.md)
illustrate why this separation matters: inability to use CAP as an abstract
Python class compiler was treated as a reason to discard its concrete category
computations too. The relevant principle is responsibility-specific evaluation.
Inspect the shared framework, Sage, and the appropriate specialized packages for
their respective jobs; no single dependency has to replace the whole project.

The preamble can coordinate more than one engine through the existing private
bridges. Requiring an unnecessary direct connection between every pair of
engines creates work that the mathematical task did not require. Conversely,
inventing a new bridge when a suitable one exists transfers another maintained
responsibility into this repository. Integration follows the established
transport owners and raises owned values before returning to mathematical code.

Search for the full semantic operation, not just its easiest primitive. A
homology package can discharge more responsibility than a matrix routine used
inside a home-written homology implementation. A module-presentation operation
can discharge more than a long local sequence of intermediate syzygy operations.
Use the highest suitable maintained operation that supplies the actual contract;
compose established operations when no single call does. The
[computation references](#existing-computation-references) are starting points,
not a reason to restrict discovery to the first familiar engine.

### Integration code has a specific job

Local code is justified by the semantic difference between an existing capability
and the presented operation. Typical differences include expressing the source and
target as preamble objects, reconciling grading or variance conventions, preserving
chosen presentation data, constructing the required comparison maps, and
converting complete results into their preamble parents. State that difference at
the construction or adapter that owns it.

An adapter is not a place where arbitrary new algorithms become acceptable by
being hidden. Renaming a computation, moving it to a private helper, translating
it into Julia, or putting it inside the generic category layer does not transfer
its maintenance to an upstream project. A dependency import also proves no such
transfer if the repository still implements most of the dependency's job itself.
Review which system actually performs the semantic operation.

Some integration is necessarily substantial. Engine presentations can differ,
maps may need transport, and exactness or coefficient hypotheses may differ.
Investigate that difficulty rather than assuming every operation is a one-line
call. But the difficulty must be an identified semantic or integration gap, not
an unexamined presumption that locally implementing familiar mathematics is the
normal route. Fix defective packaging or bridges at their established owner;
they are not mathematical evidence that a replacement algorithm is necessary.

### New mathematics goes upstream; a new algorithm is an engineering decision

New definitions, categories, constructions and theorems are formalized in
`lean-categories` by its own formalization author, never here. A request to
present an existing construction does not authorize new mathematics, and
research never supplies a missing notion locally, not even temporarily.

When the relevant mature systems and standard compositions do not supply the
required computation, state the precise remaining gap. Preserve the formalized
domain of the operation while distinguishing the representations and cases for
which an algorithm exists. General undecidability does not invalidate an
available specialized algorithm, and a useful special case does not justify
claiming a general decision procedure.

Writing a new nontrivial algorithm here requires the deliberate engineering
decision in `ENG-06`, because it adds a maintenance obligation. The algorithm is
an untrusted computation like any other: any correctness argument attached to it
is not evidence, and only the `lean-cas-dsl` acceptance suite judges its
answers. The decision concerns that algorithm, not permission to rebuild
adjacent infrastructure. Discovery can establish that the operation needs further
research; it cannot turn an unmet interface into a guessed answer, a weaker
substitute, or an assertion that the requested mathematics does not exist.

### Progress means useful composition with controlled maintenance

Assess a feature by what mathematical work a researcher can perform through the
preamble's interface, whether the result retains the structure its formalized
operation requires, and which
system maintains each necessary computation. This includes the cost imposed on
future changes: a shared correction should reach its consumers through their
existing contracts rather than require the same repair in every theory.

More locally implemented mathematics is not inherently more progress. A feature
that duplicates a mature algorithm adds a correctness and maintenance burden
even when its examples give the right answers. Fewer lines are not inherently
better either: deleting structural maps or exposing raw engine results makes
the implementation shorter by abandoning the contract. The objective is full
mathematical capability through principled composition, not a source-line quota,
dependency count, passing-test count, or administrative completion signal.

Evaluate work over time against that objective. Identify the new usable
construction, the existing capability reused, the necessary local integration,
and whether later work preserves those boundaries. An unexpectedly prolonged
implementation warrants revisiting missing reuse and structural dependencies;
elapsed time alone does not prove reinvention. Returning repeatedly to local
repairs while retaining the same bypass is not a forward trajectory merely
because each repair is individually substantive.

### The artifacts are instruments; the product is a map of Sage

Every task in this repository is a means. A tool that prints its view, a
category that constructs, a notebook cell that reproduces a table: each is an
instrument, and the result it produces is worth very little next to what
producing it teaches about the engine underneath. The product of the work is a
durable map of Sage's ecosystem: which spelling of an operation to route
through, what it demands of its input, what it returns, where it is absent,
where it is present and wrong, and where it is present, correct, and
unaffordable at the size the research runs at. The preamble encodes that map as
one name per operation that `lean-categories` formalizes, and every such name is
a place where somebody found out what Sage does there. Without that finding a
preamble name is a rename.

This inverts the ordinary cost model. The route that feels cheap, which is to
close the task in front of you by whatever works, yields nothing: the task
closes and the map gains no entry. The route that feels expensive, which is to
stay inside Sage when it resists, find out why, find the keyword, the backend
or the constructor that answers, and write down what was found, is the one that
pays, and it pays long after the task is forgotten. Friction with the engine is
therefore the most informative event a task can produce. A slow call, a rejected
input, a wrong-shaped result: each is a fact about Sage that the map does not
yet hold. Going around it costs nothing visible and destroys the only thing the
task was for.

Two moves throw the knowledge away, and both feel like progress from the
inside. Hand-rolling the algorithm closes the task while leaving the engine's
own routine unexamined: nothing is learned about its speed, its output
convention, its input demands, or its failure modes. Pivoting to a second
library at the first bump leaves the ecosystem the project is mapping, so the
search for the Sage-internal answer is abandoned exactly where it would have
paid, and the dependency surface fragments. The escalation ladder, Sage native,
then the backends Sage ships, then a local implementation under an audit trail, is not a
convenience ordering. It is the research protocol, and a rung teaches only if
you stand on it. `ENG-07` and `ENG-08` make this reviewable; `DEV-62` says what
counts as a finding and `DEV-63` says where a finding lands.

### Interactive discovery is the user-facing consequence

The preamble is an **interactive discovery language for mathematics**, not a flat library of globally named functions.  A user should be able to start from the mathematical object already in hand and discover the language locally with tab completion.  If `C` is a category, `C.<TAB>` should expose the constructions and structure that `C` knows; if `M` is a module, `M.<TAB>` should expose module-level operations; if `x` is an element, `x.<TAB>` should expose element operations; if `f` is a morphism, `f.<TAB>` should expose morphism operations; and Homsets, functors, subobjects, and other mathematical objects should likewise expose the operations `lean-categories` places on them.  The receiver is part of the mathematical documentation: it tells the user what kind of thing an operation acts on and sharply narrows the admissible language before any manual or source file is opened.

This is a deliberate contrast with a GAP/Julia-style global operation catalogue.  A global name such as `Product`, `Kernel`, or `Orbit` gives almost no local information about its domain: the user must already know whether it acts on categories, parents, morphisms, elements, families, or some combination.  As the system grows, that design requires memorizing an ever larger language or repeatedly consulting documentation.  The preamble instead scales by **navigating from mathematical objects to their methods**.  The public global namespace therefore exists primarily for canonical mathematical objects, category/object constructors, notation entry points, and genuinely language-level forms—not as a convenience catalogue of operations on objects that already exist.

**The formalized placement determines API placement.**  An operation lives where `lean-categories` places it: on the mathematical object whose structure makes the operation meaningful.  Products of a category with products are constructed on that category.  Operations whose hypotheses are properties of a Hom live on that Homset.  Morphism-level constructions live on morphisms, parent-level constructions on parents, element-level operations on elements, functorial operations on functors.  The code implementing the operation belongs with that receiver or in its subtree.  Free-standing helpers may support notation internally, but they must not become a second public language.

The same placement determines implementation dataflow.  Code wires a computation **where `lean-categories` places the operation**, and downstream behavior follows from the presented object/category graph.  If `C` has products, wire their construction on `C`; do not teach a global `Product(...)` dispatcher every category for which products happen to exist.  If equality of arrows is determined by structure of a Homset, teach that Homset; do not make a root equality helper enumerate concrete theories.  This is mathematical organization used as implementation compression: the general structure is stated once at its owner and inherited or delegated through the ordinary category machinery.

**Mathematical domain and computational domain are different.** Method placement follows the first category/object/element on which `lean-categories` defines the notion, not the currently decidable or implemented cases. Every set has a cardinality, so `cardinality()` belongs to sets even though no CAS can compute the cardinality of an arbitrary represented set such as `X = {n in NN | n.is_twin_prime()}`. Every formed module has a well-defined degeneracy predicate, so `is_nondegenerate()` belongs with formed modules even when the current implementation only decides finite-rank represented forms. The implementation may therefore route across the cases currently understood and assert-gate the remainder with an informative statement of the missing computational hypothesis. This is not a stub: supported cases must actually compute. Over time the routing table grows so that the computational domain converges toward the mathematical domain.

This is one of the few places where an explicit `case`/`match` or other routing table is positively desirable. It reads like mathematics: identify which represented situation the object lies in, invoke the theorem/algorithm appropriate to that case, and use an exhaustive final assertion for cases not yet computationally covered. The banned shape is a method whose entire body is failure (`assert False`, `NotImplementedError`, or equivalent) and which therefore advertises functionality without implementing any case at all.

**Infinite-compatible semantics come before finite-coordinate algorithms.**  The mathematical layer should be written so that replacing a finite indexing set by an infinite one, a finite basis by a lazy framing, or a matrix realization by an abstract Hom does not force a redesign of unrelated consumers.  Finite coordinates, rows, columns, exhaustive enumeration, and concrete arrays are computational specializations.  They belong behind semantic objects that remain meaningful in infinite settings: preamble sets/families, finite-support elements, subobjects, Homs, kernels/images, products/coproducts, tensor/block constructions, actions, and universal properties.  A large blast radius when moving from finite to infinite data is strong evidence that coordinates or enumeration leaked above their proper layer.

**The public API is an adversarial semantic gate.**  It is judged not only by whether correct code can be written through it, but by which mathematically invalid shortcuts it makes easy to write.  If a caller holding a morphism can casually unwrap a matrix, compute a nullspace, and rebuild a pretend kernel, the interface is too permissive even when `f.kernel()` also exists.  If an element constructor accepts a bare coordinate tuple, the API invites callers to forget the parent and framing that make those coordinates meaningful.  Close these hatches structurally: force construction through mathematical data, keep numerical representations private or one-way, and use assertions that reject a predicted shortcut while naming the correct construction.  The goal is not to trust every future consumer to remember the doctrine; the interface should make the semantic route the path of least resistance and the numerical bypass visibly abnormal.

**Repository prescriptions are part of the executable architecture.**  Issue bodies, plan cards, comments, docstrings, examples, tests, and migration notes train later contributors and agents just as neighboring source code does.  Once a mathematical or architectural ruling falsifies a prescription, correct or delete that prescription before implementation continues.  A stale comment that says “shared ambient,” a test that still unwraps coordinates, or an issue body that asks for a deprecated signature can faithfully regenerate the exact defect that the code was meant to remove.

**Diagnose recurring slop by generator, not by instance.**  A new occurrence of a known pattern is repaired by the existing rule; it does not earn another bespoke exception or workaround.  Add a catalogue entry only when review discovers a genuinely new code-shape generator.  The principal generators include presentation/object confusion, theorem proxies replacing definitions, stored or witness-free structure, signature-porting from a foreign engine's object model, contaminated prescriptions, and laundering mathematically correct failures instead of repairing what they expose.

**Construct the defining data where the definition places them.** Start a category contribution by reading the `lean-categories` definition, then the preamble's immediate structure owners and constructors.
Cite the formalized datum, its domain and codomain, and the equations its morphisms preserve in that category's documentation; the documentation cites them and defines nothing.
Pass the datum through the owning constructor so its concrete accessors are fulfilled there.
Alternative constructors must establish the same datum, including the maps that transport it between presentations.
An inherited method name alone does not establish its required state.

Distinguish properties from additional choices, as the formalization does.
A property refinement retains the existing structure; a selected action, multiplication, framing, or presentation requires construction data.
Present morphisms as well as objects when presenting structure.
Reuse a universal construction through a structural functor only where `lean-categories` states the corresponding preservation or creation result and canonical maps.

**Keep specialization at its own owner.** A specialized constructor calls its general mathematical construction.
Adding a leaf should ordinarily require changes to that leaf and its immediate mathematical dependencies.
A generic owner importing the new descendant indicates a missing construction interface.
Read the [construction and inheritance proposal](https://github.com/dzackgarza/research/blob/main/references/preamble-architecture.md) for current examples and the proposed repair.
The [architecture prerequisite](https://github.com/dzackgarza/research/blob/main/TODO.md#constructor-and-admission-foundations) sets their implementation order.

For review, follow one public constructor through its defining datum, one nonidentity structural-functor image, and one inherited operation.
Include the resulting objects, morphism endpoints, and defining equations in the example.
Inspect required operations on the actual generated classes through Sage's abstract-method discovery.
Write the example at the existing owning test surface, subject to the expectation-subtree rules and the current verification policy.
Keep the category declaration, constructor signature, and executable contract as the discoverable source; derive reports from them.

These principles are more important than any current list of prohibited code shapes.  The policy codes below record concrete consequences and reviewable failure modes, but contributors should apply the discovery, placement, locality, and dependency-direction model to new code even when no existing example names the exact violation.

### Collaborative, agent-driven research with visible evidence

This repository is built for collaborative research between humans and AI agents. A result
typically passes through three stages. A human states the mathematics informally, in natural
language. An agent pseudo-formalizes that draft in Sage, inside a relatively rigid ecosystem of
owned categories, constructions and contracts that gives the translation a definite place to land.
Humans and agents then edit, review and audit that Sage until the result carries evidence strong
enough to be used in a paper.

Sage is not a proof checker, and this process does not make it one. Confidence in a computed
result is fundamentally probabilistic and subjective. The aim is to build as many objective
mechanisms as possible, so that confidence rises and so that everyone can see what the evidence
is and how strong it is.

The code should therefore be easy for agents to use correctly and hard for them to get wrong,
whether by accident or on purpose, without a clear signal. For example, an agent needs subgroups
of `O(L)`. The general interface for subgroups of groups carries guarantees, but it is harder to
satisfy, so the agent adds a special-purpose construction that bypasses it. This will happen, so
the first defence is to make such a bypass visible quickly. The ideal is a structure in which the
bypass cannot be written at all.

Concretely:

- **Separate what exists from how well it is known.** The dashboard keeps three questions apart:
  whether a capability exists, how broad it is, and how strongly its behavior has been certified.
- **Independent oracles.** Results are checked against independent systems such as PARI/GP, Magma
  and OSCAR, not against a single reference implementation, so that agreement is evidence rather
  than circularity.
- **Structure that shows its gaps.** Algorithms, interfaces and documentation are organized so
  that humans and agents can find gaps, see the contract a general owner guarantees, and notice
  when new code steps around it.

## Preamble architecture specification

This section is the authoritative specification of construction, entrypoints,
encapsulation, and computational delegation in the preamble. It is an engineering
specification: the mathematics each construction presents is `lean-categories`',
and nothing here defines it.
It applies to new features, repairs, internal consumers, engine adapters,
catalogues, and session integration. An importable implementation is not thereby
a sanctioned entrypoint. A policy permitting private implementation machinery
does not permit a second mathematical API.

`AGENTS.md` routes contributors here. `lean-categories` gives each operation's
mathematical contract; the category declaration, constructor, and their
docstrings cite it and state how the preamble presents it; this specification
gives the architecture those declarations must realize. TODOs contain only the
unfinished delta to that architecture. They do not own architectural decisions
that would disappear when an item is completed. Historical proposals and examples
are reference material, not exceptions to this contract.

### Layers and permitted dependencies

`lean-categories` is outside this table: it alone defines the objects, maps,
hypotheses, categories and theorems every layer below presents or computes.

| Layer | Responsible for | Permitted dependency | Forbidden responsibility |
| --- | --- | --- | --- |
| Session and notation | The selected preamble spellings | Preamble entrypoints | Backend exports, adoption helpers, alternative constructor languages |
| Research presentation | Research notebooks and experiments expressed in the catalogue's language | `lean-cas-dsl` and its public semantic operations | Defining mathematics, a parallel category runtime, or implementation-controlled operation availability |
| Semantic kernel | Typed elaboration, structural route resolution and result reconstruction | `lean-categories`' catalogue and declared leaf contracts | Subject-specific mathematics or trusting a leaf's claims |
| Computation leaves | Opaque implementation of a registered operation on its declared input form | Leaf contract and selected engines' supported interfaces | Public taxonomy or semantic authority |
| External engines | Their maintained computational algorithms and internal representations | Their own dependencies and supported bridges | Defining the preamble's public API or accepting preamble objects as foreign parents |

Every computation supplied by a leaf or external engine, including research's
own code, is untrusted: its answers are run, never believed, and only the
`lean-cas-dsl` acceptance suite judges them.

The final semantic runtime is the `lean-cas-dsl` kernel, which consumes
`lean-categories`' catalogue and replaces `sage-categories`' dynamic-inheritance
core. `sage-categories` remains a source of requirements and, where suitable,
private computational implementations; it is not a second public category
runtime. Retire the transitional Python construction and inheritance machinery
as its consumers move to the formal catalogue and kernel. A computational
implementation registers through the leaf contract and cannot determine the
mathematical meaning or availability of an operation.

### `OWN-01`: Locate the formalized operation before selecting an implementation

- **Rule:** First perform the
  [mathematical dependency trace](#mathematical-dependency-tracing), independent
  of the implementation's current shape, against `lean-categories`. Then read the
  preamble category presenting it, its immediate structure owners, current
  entrypoints, and consumers. Identify the input, output, structural maps, and
  exact operation the formalization states. Search the megadoc and live
  source beyond the selected subtree for that operation, then inspect relevant
  upstream implementations. Reuse both the preamble's presentation of the
  construction and the maintained computation; satisfying only one half is
  insufficient. Missing mathematics is a formalization request to
  `lean-categories`. Record it, missing presentations, and observed workflow
  friction in the native issue tree under `DEV-59`, even when found outside the selected
  implementation task. The complaint states the need; it does not authorize a
  bespoke replacement or a change of scope.
- **Rationale:** A private Sage call can bypass the presented localization just as
  a correctly named kernel can conceal a redundant local elimination algorithm.
- **Violation Example:** Start a geometry-specific matrix kernel because the
  selected geometry file does not implement kernels; reject CAP's computational
  categories because CAP does not generate Python classes.
- **Correct Example:** Geometry asks the complex for cohomology; the complex
  and module categories present the structure, and their private adapters reuse an
  applicable established homology or module algorithm.

### `OWN-02`: Every construction route converges on one semantic constructor

- **Rule:** Each construction `lean-categories` formalizes has one construction
  contract at the preamble category or object that presents it. Operator notation, literal ingress,
  catalogue specimens, functor images, direct morphism construction, and raised
  engine results establish that same contract. Specialized routes supply the
  general constructor's defining datum; they do not allocate an alternative
  parent and attach enough methods to resemble its output.

  The public spelling follows `ARC-07` and `ARC-12`: morphisms are asked through
  `Mor`; operations are asked of their owners. A private implementation function
  is not a second public constructor. There are no shorthand, abbreviated or
  "convenience" constructors: agents write the code and spell out the full
  construction every time (owner ruling, 2026-10-14: "there is no reason to allow
  shorthands and coinages and 'convenience' constructors. Agents write the code,
  they can spell it out each and every single time"). No `from_engine`,
  `from_raw`, `unchecked`, or validation-disabling route admits weaker data. Host allocation and `_element_constructor_` implement this contract;
  they do not exempt a caller from it.
- **Rationale:** One semantic funnel makes an invariant apply to every way an
  object is obtained, instead of making correctness depend on caller diligence.
- **Violation Example:** The direct module constructor establishes a scalar
  action, but the backend-result constructor returns a parent without it.
- **Correct Example:** The owner establishes the defining action once; each
  supported representation supplies that action through the same construction.
  Backend specialization changes computation, not the constructor obligations.

### `OWN-03`: Construction establishes all inherited data before exposure

- **Rule:** Each category level introduces only its own mathematical datum and
  constructs through its immediate structure owners. The returned object has
  every datum required by its actual placement, including its element and
  morphism structures. Accessors recover that established datum; they do not
  reconstruct it from descendants, probe for hidden state, or repair placement
  when first called. Lazy realization is allowed only from complete defining
  data with a fixed owned codomain, not as delayed provision of missing structure.

  A property refinement retains the existing data. Adding a choice, action,
  multiplication, framing, or presentation supplies that structure through its
  constructor. Category membership alone never supplies missing data. The same
  rules apply to zero objects, empty families, identity maps, and boundary degrees.
  A specialization threads that construction by honest inheritance or composition
  with its actual owned instance, as required by `OWN-14`; equivalent independent
  implementations do not satisfy this rule.
- **Rationale:** Inherited method names without inherited construction data make
  invalid objects available for subsequent features to build upon.
- **Violation Example:** A DGA gets a cochain-complex category label but its
  differential interface cannot supply the zero components its grading
  requires; a formed object implements its own set operations.
- **Correct Example:** The DGA construction supplies the graded module and
  differential contract, then adds multiplication; generic complex operations
  consume that same differential. Each lower level holds its own inherited data.

### `OWN-04`: The public boundary is recursive and includes implicit operations

- **Rule:** Every mathematical value reachable through a public preamble operation
  is a preamble object, never a raw engine value. This includes coefficients, base rings, indexing sets, family values,
  iterated elements, morphism endpoints, structural maps, cycles, boundaries,
  quotients, chosen representatives, and results of arithmetic and coercion.
  A lazy family or callable must return preamble values when evaluated; wrapping
  its outer container is not enough. Public coordinate objects are themselves
  preamble objects tied to their chosen framing, never foreign arrays.

  Public signatures, inherited methods, parser bindings, introspection-visible
  conveniences, and serialization/reconstruction routes obey the same closure.
  Python syntax/support values expressly allowed by the session contract are
  not permission to return foreign mathematical values. There is no exception
  for small integers, singleton rings, fast arithmetic, or a backend's
  particularly convenient element type.

  Encapsulation hides representation, not the mathematics: the defining action,
  form, framing, inclusion, projection, and other required structure remain
  available through their preamble APIs. Returning opaque handles in place of
  these objects is not stronger encapsulation.
- **Rationale:** One reachable foreign constituent gives every downstream consumer
  a second API even when the outer parent is a preamble object.
- **Violation Example:** A preamble cohomology module returns Sage cycle vectors;
  a preamble family yields GAP elements; inherited arithmetic returns Sage scalars.
- **Correct Example:** A cycle representative is an element of the preamble cycle
  module, its inclusion lands in the preamble complex component, and its quotient
  image has the preamble cohomology module as parent.

### `OWN-05`: Private means confined to a named owner, not merely underscored

- **Rule:** Store private representation fields only at their owning runtime or
  adapter boundary. Mathematical consumers use public preamble operations, including
  when the consumer lives in the same repository or file. An underscore, a helper
  module, a friend-like import, or omission from `preamble.all` is not permission
  to access another owner's storage. Do not expose raw state through a newly
  public accessor, a neutral name such as `data`, an iterator, or a closure.

  A protected framework contract must be declared at its owner with its exact
  purpose, permitted implementing/calling roles, input/output types, maintained
  invariants, and reason ordinary public operations cannot implement that
  framework responsibility. It is invoked through the designated dispatcher.
  A comment at a consuming call site cannot create that authority. Protected
  mathematical contracts exchange owned values. Raw handles may move only among
  helpers of the same declared private computation/transport boundary; they do
  not cross into another subsystem.
- **Rationale:** Broad permission for a documented private call makes every
  inconvenient public contract optional.
- **Violation Example:** A lattice module imports a ring's private engine accessor
  and documents the import as a protected extension so it can run its own algebra.
- **Correct Example:** The ring or module category presents the missing formalized
  operation. Its private adapter may share transport helpers internally while
  mathematical callers receive only the preamble result.

### `OWN-06`: Engine inspection is local to an already selected computation

- **Rule:** Mathematical dispatch follows the presented structure and hypotheses.
  Only the designated adapter may inspect foreign representation types or invoke
  engine-specific APIs after the operation is selected. Prefer supported
  upstream APIs. If an upstream private function is genuinely required, first
  check the public alternatives; document the exact upstream symbol, source,
  assumptions, and consuming adapter at that adapter's declaration. This grants
  no permission to inspect unrelated preamble internals or to export that function.

  No dynamic attribute forwarding, blanket delegation of unknown methods,
  runtime class mutation, public engine selector, backend option bag, or raw
  adoption constructor belongs on a preamble object. Private host initialization
  and dispatch hooks are runtime implementation contracts, not escape routes.
- **Rationale:** Foreign implementation details need one repair site when upstream
  changes, and must not become the language used by mathematical consumers.
- **Violation Example:** Ordinary toric code spreads calls to private Sage sheaf
  helpers through several consumers; `__getattr__` forwards missing owned methods
  to a Sage parent.
- **Correct Example:** One toric adapter calls the source-grounded Sage helper
  when no suitable public operation supplies the needed data; it raises the
  result through the preamble complex construction before returning.

### `OWN-07`: Raise results through the same construction without losing maps

- **Rule:** A private adapter lowers the preamble object's defining data, performs
  the engine computation, and raises the result through the relevant preamble
  construction. Preserve the selected base ring, grading, action, presentation,
  and structural arrows. Record actual comparison morphisms whenever a change
  of representation requires them. An engine normal form cannot replace a
  chosen presentation silently. Matching an invariant such as dimension does
  not supply the required chosen isomorphism or presentation-comparison map.

  The computation and construction steps must not recurse: raising computed
  defining data enters the same semantic constructor without requesting the same
  engine computation again. Make that dependency explicit at the owning methods;
  do not solve recursion with a second unchecked constructor. If an engine
  supplies only dimensions, it supplies a dimension computation, not class
  representatives or induced maps. Obtain the missing data through an existing
  suitable operation before claiming the richer construction.
- **Rationale:** Correct numerical answers do not reconstruct the relationships
  that subsequent mathematics needs.
- **Violation Example:** Wrap the dimension of cohomology in a fresh vector space
  and expose it as the cycle quotient; discard basis-change maps during lowering.
- **Correct Example:** Raise the computed cycle and boundary data into the preamble
  modules and maps, retain their quotient map, and derive the induced map from
  the supplied chain map through those structures.

### `OWN-08`: Reuse the highest suitable maintained operation

- **Rule:** Search by mathematical operation, equivalent standard formulations,
  required maps, and coefficient hypotheses, not only by the desired Python
  method name. Inspect existing dependencies first, then appropriate maintained
  systems. Compare the full result contract: exactness, characteristic, torsion,
  grading, presentations, representatives, and morphism action where required.
  Compose established operations when that supplies the contract. Calling one
  matrix routine inside a new local homology engine does not establish that
  the existing homology implementations were considered.

  Record the selected upstream operation and its actual uncovered semantic delta
  at the private adapter or owning construction. For a planned task, record the
  selection in the unfinished item and retain the durable contract at delivery.
  A new nontrivial algorithm needs the demonstrated gap and explicit engineering
  decision required by `ENG-06`. Moving a local algorithm to Julia, Singular,
  or a generic helper does not make it upstream-maintained.
- **Rationale:** Mature dependencies reduce the project's algorithmic maintenance
  burden only when they actually perform the corresponding computation.
- **Violation Example:** Rebuild syzygy or chain-reduction logic because a package
  has an inconvenient return type, a different class model, or missing packaging.
- **Correct Example:** Adapt an existing module-presentation or homology operation,
  adding only the preamble construction and map conversion that the engine does not
  supply. Repair a bridge or packaging defect at its existing owner.

### Existing computation references

These are discovery starting points, not claims that one package computes every
instance. Check the relevant current documentation and local adapter contract.

| Required computation | Existing implementations to inspect |
| --- | --- |
| Chain-complex homology and cycle representatives | [Sage chain complexes](https://doc.sagemath.org/html/en/reference/homology/sage/homology/chain_complex.html); its documented implemented homology cases include integer coefficients and fields |
| Commutative DGA cohomology and products | [Sage commutative DGAs](https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/commutative_dga.html); inspect the grading and degree range of each operation |
| Toric sheaf cohomology | [Sage toric divisors](https://doc.sagemath.org/html/en/reference/schemes/sage/schemes/toric/divisor.html) and [equivariant bundle complexes](https://doc.sagemath.org/html/en/reference/schemes/sage/schemes/toric/sheaf/klyachko.html) |
| Linear categories, presented modules, complexes | [CAP constructors](https://homalg-project.github.io/docs/CAP_project-based/constructors): LinearAlgebraForCAP, ModulePresentationsForCAP, FreydCategoriesForCAP, ComplexesAndFilteredObjectsForCAP |
| Polynomial and module algorithms | Sage, Singular, Macaulay2, and OSCAR through the existing private bridges; inspect the needed presentation and map outputs, not only an invariant |
| Standard polynomial-ring completions | [Sage multivariable polynomial completion](https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/multi_polynomial_ring_base.html) and [lazy series](https://doc.sagemath.org/html/en/reference/power_series/sage/rings/lazy_series_ring.html) |

The [sage-categories README](https://github.com/dzackgarza/sage-categories/blob/main/README.md),
[complaints and reuse catalogue](https://github.com/dzackgarza/sage-categories/blob/main/COMPLAINTS.md),
and [engine-boundary specification](https://github.com/dzackgarza/sage-categories/blob/main/specs/leaves.md#computation-engine-boundary)
provide additional discovery context. Their historical findings are not a current
capability audit, and their framework-specific exceptions do not relax the
preamble's recursive public boundary (`OWN-04`).

### `OWN-09`: Transport through structure, with the actual preservation theorem

- **Rule:** Present functors on objects and morphisms, with the domain, codomain,
  variance, and comparison maps `lean-categories` states. Inherited operations
  follow those structural functors only where `lean-categories` proves the
  relevant preservation or creation result. Reuse the framework's composition, identities, and
  universal-construction interfaces; a leaf adds its new datum and genuinely
  specialized computation, not another implementation of general map calculus.

  Neither forgetfulness nor faithfulness implies preservation of every limit,
  colimit, quotient, or cohomology operation. Cite the `lean-categories` theorem
  and its hypotheses at the preamble construction; do not generate runtime boolean
  proofs of general categorical identities or undecidable equality. A theorem
  `lean-categories` lacks is requested there; the transport waits for it. Distinct mathematical choices remain
  distinct even when an engine represents them by the same data.
- **Rationale:** Generic reuse without its hypotheses can propagate incorrect
  mathematics just as efficiently as correct mathematics.
- **Violation Example:** Treat every algebraic cokernel as the cokernel of the
  underlying linear map; implement scalar extension by changing stored ring
  fields without transporting the module and its structure maps.
- **Correct Example:** The relevant quotient construction builds the required ideal
  closure before the quotient; scalar extension acts on the module and the
  defining action or multiplication through the same functorial construction.

### Required construction factorizations

These are presentation obligations, not additional global function names or a
runtime registry. The constructions and their hypotheses are `lean-categories`';
each row names the general preamble construction through which its special cases
pass. A row whose mathematics `lean-categories` does not yet formalize is a
formalization request there.

| Family | Required construction and retained data | Specialization boundary |
| --- | --- | --- |
| Limits and colimits | The indexing category, diagram, universal cone/cocone, and induced maps under the [general contract](#limits-colimits-and-structured-specialization) | Product/equalizer and coproduct/coequalizer constructions, directed systems, and category-specific realizations implement the same construction through inheritance or composition |
| Ring localization | The commutative ring's localization at a multiplicative submonoid, with its structure map and universal factorization | Element inversion uses the generated submonoid; prime localization uses the prime complement; a domain's fraction field uses its nonzero elements |
| Scalar change | The existing scalar-change construction along a ring morphism, acting on objects and morphisms | Module localization uses the localization ring map; extra algebra/action/form structure is transported under the applicable hypotheses |
| Completion | The inverse system of ideal-power quotients, its transition maps, limit, source map, and projections | Series and adic engines realize supported instances privately; no finite stage becomes the completed object |
| Complexes and cohomology | The graded components and differentials; cycle inclusion, boundary inclusion, quotient, and induced maps | Chain/cochain conventions, coefficient hypotheses, and boundedness belong to the stated construction or computational case, never an implicit matrix convention |
| Differential graded algebras | The common complex and graded algebra structures, with the differential and multiplication compatibility | Cohomology multiplication is induced through those structures; a commutative-DGA engine does not cover arbitrary DGAs by renaming |
| Subobjects, quotients, and Homs | The existing inclusion/projection and fixed-endpoint `Mor` constructions | Coordinates enter only through the appropriate chosen framing/presentation and the same morphism constructor |

The citations below orient the reader to the sources `lean-categories`
formalizes from; the formalization, not this text, is the authority. For
localization, see [Stacks 02C5](https://stacks.math.columbia.edu/tag/02C5).
Locality is a consequence with hypotheses, not a property of every localization:
prime localization is local, whereas `ZZ[1/2]` retains distinct maximal ideals
generated by 3 and by 5. For completion use
[Stacks 00M9](https://stacks.math.columbia.edu/tag/00M9): the objects are the inverse
limits of `R/I^n` and `M/I^n M`. General completion is not assumed exact; comparison
with scalar extension requires its stated hypotheses. The limit contract does
not claim a general algorithm for computing arbitrary inverse limits. This is
not permission to restrict the general mathematical interface to finite diagrams:
apply the general contract below and specialize its realization.

### Limits, colimits, and structured specialization

**Present the theory at the most general category where `lean-categories`
places it, then specialize by threading that construction through every
refinement.** A completion, a directed union, or a geometric construction does
not carry a separate theory of diagrams. The mathematics recalled below is
`lean-categories`', cited here from its sources; this section specifies how the
preamble presents it; `OWN-14` makes the same threading
requirement binding on all specialized constructions, not just limits.

#### Diagrams and universal constructions

For an ordinary category `C`, a diagram is a functor `D: J -> C`; maps of
diagrams of fixed shape are natural transformations. A limit is a terminal
cone over `D`; a colimit is an initial cocone under `D`. Their structural maps
and universal factorizations are part of the construction, not optional output.
Use the definitions in [Stacks, Limits and colimits](https://stacks.math.columbia.edu/tag/002D).

The preamble must express the index category, object and arrow families,
their source/target and composition, the functor, cone/cocone legs, and maps
between these objects. All constituents, including lazily returned values, use
the existing preamble categories, Homs, functors and indexed families. A Python
iterator of engine values is not a diagram. A finite list of arrows does not
define an arbitrary category without its identities, composites and relations.

Smallness is relative to the declared foundations. Do not confuse small,
finite, countable, enumerable, and computationally presented. Support arbitrary
represented small shapes at this level, including parallel arrows and infinite
indexing; do not define the general interface using integer degrees, a maximum
stage, a matrix size, or finite traversal. Size hypotheses belong to the
mathematical contract; representation limitations belong to specific operations.

Functoriality, compatibility and universality are `lean-categories`' theorems,
used through the sanctioned constructions and their hypotheses. Do not try to
validate an infinite diagram by traversing every arrow, or treat a finite sample
as proof of its laws. Represented input must meet its declared construction contract;
an arbitrary callable plus a boolean claiming compatibility is not a substitute.
This is not permission to add an unchecked ingress or a runtime theorem registry.

A chosen universal construction retains its actual diagram and universal
cone/cocone, with access to their constituents through preamble objects. Its
underlying result object alone need not determine its presentation. Distinct
diagrams may have isomorphic results, or share one canonical result object.
Keep each construction's data at that construction; never overwrite shared
object state with the latest caller's diagram. Nor should equality of result
objects be defined by equality of their chosen presentations.

#### Construction theorems supply general realizations

For a small diagram `D: J -> C`, the following formula constructs its limit
when the displayed products and equalizer exist:

```text
P = product over objects j of D(j)
Q = product over arrows a: i -> j of D(j)
u, v: P -> Q
component_a(u) = projection_j
component_a(v) = D(a) composed with projection_i
limit(D) = equalizer(u, v), with its induced projections
```

Thus the appropriate small products and equalizers suffice for small limits.
Empty products include the terminal-object case. The formula is categorical,
not an instruction to enumerate all factors or compute all compatible tuples.
See [Stacks 002N](https://stacks.math.columbia.edu/tag/002N).

The corresponding colimit construction is:

```text
A = coproduct over arrows a: i -> j of D(i)
B = coproduct over objects j of D(j)
u, v: A -> B
restriction_to_a(u) = coprojection_i
restriction_to_a(v) = coprojection_j composed with D(a)
colimit(D) = coequalizer(u, v), with its induced coprojections
```

The appropriate small coproducts and coequalizers suffice; the empty coproduct
supplies the initial object. Products alone do not impose compatibility, and
coproducts alone do not impose identifications. See
[Stacks 002P](https://stacks.math.columbia.edu/tag/002P).
These displays are mathematical pseudocode, not new public factory names.

Wire these realizations, which `lean-categories`' theorems justify, through the
common construction's sanctioned specialization boundary. Do not introduce a competing public
product-based limit API. Products and equalizers are themselves limits, so an
implementation must distinguish their defining diagram from a request to solve
that diagram again. The primitive category-specific realization supplies its
universal data to the common constructor without recursively requesting itself.
The same rule applies to coproducts and coequalizers. A general reduction is
not an excuse for constructor recursion or an unchecked allocation path.

For every specialized realization, cite the `lean-categories` applicability
theorem and identify the actual computational operations it delegates to. An optimized realization
overrides the realization step of the inherited general construction, or
operates through the composed general instance under its declared contract.
It does not maintain a parallel limit implementation. Both the generic reduction
and its specialization use the same diagram, map, restriction, and
universal-factorization machinery. Select the applicable realization
by the established category/representation mechanism, not by catching an error
and silently trying a mathematically different construction.

#### Directed systems and finite restrictions

Use the common diagram language for directed and inverse systems. For a directed
poset `I`, direct systems use arrows `i -> j` for `i <= j`; inverse systems
use the opposite direction. Filtered categories generalize directed posets and
need not have at most one arrow between two objects. Their hypotheses must not
be replaced by a sequence convention. See
[Stacks, Filtered categories](https://stacks.math.columbia.edu/tag/002V).

Restriction is precomposition: an indexing functor `u: K -> J` gives `D o u`.
Retain `u` and the restricted diagram. In particular, expose requested finite
restrictions of represented systems without evaluating the whole infinite
diagram. A sequential system admits finite prefixes; a general directed system
requires explicit selected indexing data, not an invented canonical prefix.
A finite selection of objects is not necessarily a finite full subcategory:
its arrow sets can still be infinite. State what was selected.

When the relevant constructions exist, restriction induces

```text
limit_J(D) -> limit_K(D o u)
colimit_K(D o u) -> colimit_J(D)
```

These directions follow the universal maps, not a common untyped projection
operation. Diagram transformations induce maps between limits and between
colimits, preserving identity and composition. Reindexing comparisons follow
the appropriate initial/cofinal theorem when an isomorphism is claimed; neither
a finite sample nor a convenient subsequence is automatically sufficient.
See [Stacks, induced maps](https://stacks.math.columbia.edu/tag/002D).

Separate the full system, a restricted system, a stage object, the (co)limit of
a restriction, and finite information about an element. A stage can itself be
infinite. Finite restriction never turns the full object into a finite stage.
In inverse systems, compatible finite data need not extend to a compatible
global family. In direct systems, later arrows may identify elements distinct
at earlier stages; coprojections are not automatically injections.

For completion, the maps to `R/I^n` come from the retained quotient diagram;
the ideal and its powers supply the interpretation of a stage as precision.
That interpretation is completion-specific, while restriction and comparison
are general. Increasing precision cannot invent a lift from a bare residue or
certify equality from finitely many agreeing components (`OWN-10`).

#### Structured categories specialize the same mathematics

In `R`-modules, equalizers are kernels of differences and coequalizers are
cokernels of differences. Consequently the displayed reductions become a
submodule of a product and a quotient of a direct sum. Preserve the inclusion,
projection and universal maps, not just a module with matching invariants. The
direct-system quotient and its maps are described in
[Stacks 00D5](https://stacks.math.columbia.edu/tag/00D5).

Use the actual categorical products and coproducts. In commutative rings,
products are ring products, while binary coproducts are tensor products over
`ZZ`; the pushout of commutative ring maps `R -> A` and `R -> B` is
`A tensor_R B`. They are not coproducts of underlying modules. See the explicit
cones and universal maps in
[Mathlib's commutative-ring constructions](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Category/Ring/Constructions.html).
Do not transfer this commutative formula to arbitrary associative algebras.

Limits computed on underlying objects and colimits requiring further algebraic
or sheaf constructions must follow their own creation/preservation theorems
(`OWN-09`). An infinite product of finite-rank modules need not have finite
rank; a subcategory restriction must not silently change the target category.
Use maintained algebra, module, series, and geometric computations privately.
The general constructor presents the mathematical relationships; it is not a
second CAS implementation of every product or quotient.

#### Representation, existence, and homotopical structure

Keep distinct the ability to represent a diagram, the existence of its universal
object in the category, a chosen representation of that object, and the
computability of a requested operation. A construction may represent an
infinite universal object exactly without an eager enumeration or
general equality algorithm. Conversely, retaining a diagram alone is not a
proof of existence in a category lacking that limit. A formal system must stay
identified as a system; it cannot be relabeled an existing object of that
category. Any use of a different completion of the category requires its actual
construction, formalized in `lean-categories`, and its target.

Ordinary strict limits and homotopy limits are different mathematical requests.
Name the relevant category, equivalences and coherence before selecting their
realization; the ordinary equalizer formula is not a homotopy-invariant recipe
merely because its factors are spaces. Reuse established homotopical machinery
with its hypotheses. See
[Shulman, Homotopy limits and colimits and enriched homotopy theory](https://arxiv.org/abs/math/0610194).

For example, sequential spectra have pointed spaces and bonding maps
`Sigma X_n -> X_(n+1)`, with morphisms compatible with those maps; they are not
ordinary sequences `X_n -> X_(n+1)` obtained by forgetting suspension. Retain
the suspension/loop relationship and the chosen spectral and homotopical
structure when expressing finite portions or universal constructions. See
[Malkiewich, Definition 2.1.1](https://people.math.binghamton.edu/malkiewich/spectra_book_2026Jan09.pdf#page=84).
This example sets a generality boundary, not a prerequisite to implement stable
homotopy theory before repairing ring completion.

#### Reviewing that a specialization remains threaded

For a selected realization, follow its inherited or composed general object
from construction through stage access, restrictions, universal factorization,
and a nonidentity induced morphism. All use the same diagram and structural
maps. A comparison with another realization respects those maps; agreement of
dimensions, printed expressions, or finite residues is insufficient. This is an
engineering review of the wiring; it is not correctness evidence, which exists
only in the `lean-cas-dsl` acceptance suite.

Distinguishing specimens include a diagram with parallel arrows, both an empty
limit and empty colimit, a directed index with incomparable elements, an inverse
system with non-surjective transitions, and a direct system with non-injective
transitions. Select specimens for the contract being delivered, preserve broader
unfinished cases in TODO, and follow terminal T for execution (`DEV-58`). Record
observed missing foundations in the native issue tree, with the `lean-categories` request
for missing mathematics, not invented failures inferred merely from the breadth
of this specification.

### `OWN-10`: Representation state cannot alter mathematical meaning

- **Rule:** The defining data a preamble object was constructed from are
  authoritative over its representation. Backend workspaces, caches, finite
  precision, normalization state, and transport handles are private realizations
  of those data. Reuse existing cache/lifetime mechanisms with keys respecting the
  construction's actual choices. Replacing an engine, increasing precision, or
  populating a cache does not change what the object is, its defining maps, or
  its category. Engine identity never justifies refinement.

  Exact equality, zero, membership, and hashing cannot be inferred from a lossy
  projection or an engine's inconclusive boolean. Apply `DEV-51` and `DEV-52`.
  Unsupported computation fails at its documented boundary; it never returns
  a foreign object, an approximation under an exact name, or an invented answer.
- **Rationale:** Private storage otherwise becomes a second source of meaning and
  can contradict the structure the constructor received.
- **Violation Example:** Treat one truncated series residue as the exact element,
  or cache two differently framed objects under the same engine normal form.
- **Correct Example:** Retain the exact defining object and its projection maps;
  precision describes available computational information about its elements.
  A new presentation comes with its change-of-presentation map.

### `OWN-11`: A missing shared operation is repaired at its owner

- **Rule:** If the sanctioned path is absent, recursive, awkward, slow, or
  insufficient, identify the exact missing datum or operation at its owner.
  Repair that prerequisite and route the selected consumer through it. When the
  missing piece is mathematics rather than presentation or wiring, it is a
  formalization request to `lean-categories` and the consumer waits for it. Source
  locality, elapsed effort, a passing example, or a smaller diff cannot justify
  a second constructor, a private-field read, or a copied algorithm. Existing
  violations are repair sites, not precedents for new code.

  Keep the repair bounded to the actual dependency and its affected consumers.
  Do not prebuild all of category theory, add a new registry, or start a framework
  rewrite to avoid the concrete construction. If the required owner cannot be
  changed within the granted scope, report that owner and obstruction; continue
  independent work, but leave the dependent capability unfinished. An exception
  requires an explicit user architectural decision, recorded here and at the
  affected contract, not a worker-authored justification for convenience.
- **Rationale:** Otherwise the easiest local route becomes the rewarded route,
  while each apparent feature increases future repair and maintenance work.
- **Violation Example:** Add another direct fraction-field allocation because
  routing through localization would require repairing localization.
- **Correct Example:** Complete that localization case and its map, then obtain
  the fraction field through it; other localization consumers share the repair.

### `OWN-12`: Acceptance includes the path, not just the final invariant

- **Rule:** Review the actual public entrypoint, defining-data construction,
  inherited operation, private lowering/computation/raising boundary, and a
  nonidentity induced map where the feature has one. Compare every alternative
  route touched by the work against the same semantic contract. Reject a correct
  invariant obtained through an unsanctioned path. A conforming specimen must
  expose the preamble constituents and their mathematical relationships, not
  merely an outer type, engine call count, or dimension.

  This is engineering acceptance of the wiring. It is not evidence that any
  answer is correct; that exists only in the `lean-cas-dsl` acceptance suite.
  Establish architectural reuse by reading the implementation and upstream
  contract. Research's specimens exercise observable behavior; do not turn
  them into source scanners or mock expectations that a particular helper was
  called. Respect the protected expectation subtrees and `DEV-58`: written
  specimens remain unverified until the authorized execution phase. A policy
  edit specifies the architecture; it does not establish code conformance.
- **Rationale:** Numerical agreement alone rewards a shortcut that leaves the
  construction and its future consumers structurally wrong.
- **Violation Example:** Close a cohomology task after matching Betti numbers
  while representatives or induced maps still escape to Sage; call a moved
  private algorithm delegated because its Python caller became shorter.
- **Correct Example:** Source review follows the shared construction and real
  maintained algorithm. The specimen composes the preamble inclusion,
  quotient map, and induced morphism and distinguishes the promised behavior
  from a dimension-only substitute.

### `OWN-13`: Declarations identify sanctioned entrypoints and private boundaries

- **Rule:** At each construction's existing declaration, cite the
  `lean-categories` definition it presents and document its preamble
  category/object, canonical signature, defining datum and maps, admissible input
  forms, required output structure, and how each specialization factors through
  it. At each adapter declaration, document the semantic operation it implements,
  its owning caller, the upstream operation, representation hypotheses, and
  lowering/raising correspondence. Keep these contracts beside their source,
  not in a second constructor registry or manually synchronized status table.

  Public mathematical names describe mathematics. Private implementation classes,
  allocation helpers, conversions, and adapter-only imported engine symbols use
  leading underscores and are excluded from public exports. Engine names belong
  in private adapter names where that makes their boundary clearer, never in
  public operation names. Internal consumers import the defining owner rather
  than a session aggregator, and invoke its sanctioned operation rather than an
  implementation class. Access scope follows the declared role, not the physical
  file: putting consumer and adapter code together does not authorize raw access.
- **Rationale:** A constructor or helper whose allowed callers are unspecified
  becomes an alternate API through ordinary imports and copied examples.
- **Violation Example:** Export a concrete module implementation because one
  sibling needs its unchecked initializer; call a raw conversion `normalize`
  and omit its backend-specific input/output contract.
- **Correct Example:** The module category documents its presentation constructor;
  a private adapter documents its one computational responsibility. Their source
  declarations and exports make the mathematical entrypoint distinguishable from
  the backend conversion without requiring another policy registry.

### `OWN-14`: Specializations inherit or compose their general construction

- **Rule:** A specialized construction is implemented by honest inheritance from
  the general preamble construction, or by composition with an actual instance of
  it. Declare which relationship is used at the existing owner (`OWN-13`). This
  applies to every mathematical refinement, not only the
  [limit and colimit contract](#limits-colimits-and-structured-specialization).

  Inheritance initializes the general defining datum and retains its operational
  contract. Overrides supply only the specialized datum or a realization a
  `lean-categories` theorem justifies. A category label, class ancestry, or copied method body is not
  enough when inherited operations have missing state or disagree with the leaf.

  Composition stores the actual general construction and delegates its
  general operations to that instance. The specialized object adds its own
  mathematical structure and the maps relating the two. A diagram accessor or
  metadata-only object attached to an independent implementation is not this
  relationship. Neither is a second general object reconstructed for each call.

  Keep a single authority for defining data, universal maps, restrictions and
  induced morphisms. Do not keep parallel mutable copies in the specialized and
  general objects. A mathematical comparison between distinct presentations is
  allowed and must be an explicit map, but an isomorphism does not excuse duplicating the
  general implementation. Thread specialized computation through the shared
  constructor without eagerly computing a second, generic realization merely
  to prove that the architecture was followed.

  Change the shared contract and its dependent consumers together. A leaf may
  not hide an inherited operation, weaken its inputs, discard its maps, or add
  a second implementation because the general owner is awkward to use. Repair
  that owner under `OWN-11`. Runtime optimization changes a realization, not
  which construction defines the object.
- **Rationale:** Parallel implementations can agree on one answer while drifting
  on inherited operations, maps, precision, and subsequent refinements.
- **Violation Example:** construct a series ring independently, attach an inverse
  system for display, and separately implement truncation and induced maps; claim
  that matching a generic limit on examples establishes architectural reuse.
- **Correct Example:** a completion inherits the chosen inverse-limit
  construction or contains that construction and delegates to it. A maintained
  series engine realizes its supported ring operations privately. Diagram
  restriction and universal maps still come from that same general construction.

### `OWN-15`: The underlying object is defining construction data, never a post-hoc view

- **Rule:** When a mathematical object is obtained by adding structure to an
  existing preamble object, construct the weaker object first and retain that exact
  object as part of the stronger object's defining data.  The stronger object
  is then the weaker object together with additional selected datum and the
  structural maps required by the mathematics. An accessor such as `underlying_set()`,
  `unformed_module()`, `base_scheme()`, or `source_object()` exposes
  that already-constructed object/map; it does not synthesize a fresh isomorphic
  object from dimensions, labels, coordinates, category membership, or other
  metadata.

  This applies whenever the mathematics has a canonical construction chain:
  `S -> Free_R(S)`, a module plus a form, a module plus a group action, an algebra
  over its underlying module, a graded object over its underlying object, a
  subobject with its inclusion, a quotient with its projection, a scalar change
  with its unit/counit/comparison map, a scheme over its coordinate algebra, or
  a functor image with its source provenance.  The chain is construction data,
  not documentation about a separately implemented object.

  Lazy realization is permitted only for computation *inside* an already fixed
  underlying object.  It is not permission to postpone deciding what the
  underlying mathematical object is until a method is first called.
- **Rationale:** Reconstructing the weaker object later creates a second
  authority for the object and lets generic operations drift from the object whose structure
  they are supposed to inherit.
- **Observed defect:** lattice construction already created a concrete
  `FreeModuleOn(R,S)` and stored it as `_module`, but lattice-level accessors then
  maintained parallel generator/index state and `unformed_module()` returned the
  lattice itself rather than that stored module.  The correct underlying module
  existed but was bypassed by the public surface.
- **Correct Example:** construct `M = FreeModuleOn(R,S)` once; construct the
  lattice from `(M,b)`; `unformed_module()` returns `M`; every generic module
  operation uses the module structure established from that same `M` by the
  category construction chain. `CON-16` forbids a second module implementation
  connected back to `M` by invented identification maps.

### `OWN-16`: Thread added structure through the retained datum

- **Rule:** `CON-16` governs every structure-adding constructor. Construct
  `X=(M,d)` through the immediate category owner on the data of the exact
  `M` received. Inherited module operations act on `X` through that construction chain;
  they do not forward to a separately implemented module. An accessor explicitly
  required by the mathematical contract, such as `unformed_module()`, returns
  the received `M`. Distinct choices of `d` remain distinct structured objects.

  Element coercion is established by the same owner and respects addition,
  scalar action and the selected structure. Do not create a public
  `equip_*`/`forget_*` or `from_*`/`to_*` identification pair to connect a
  duplicated realization to the input. Renaming that pair or hiding it behind
  a construction record does not repair the duplication.

  This rule does not remove actual mathematical arrows: kernel inclusions,
  quotient projections, free-cover epimorphisms, localization maps, scalar-change
  units/counits and a genuinely selected isomorphism remain preamble morphisms with
  their exact endpoints. A forgetful functor is supplied by its category; the
  retained-input accessor is not a second implementation of that functor.
- **Rationale:** The input datum and inherited structure have one authority.
  Wrapper-identification machinery introduces another authority without adding
  mathematics; erasing genuine universal maps loses mathematics instead.
- **Violation Example:** build a copy of `M`, give it a form, and recover `M`
  through `equip_form_morphism` and `forget_form_morphism`; or replace a kernel
  inclusion by element coercion because both objects admit the same coordinates.
- **Correct Example:** construct two formed modules `(M,b)` and `(M,c)` through
  `FormedModules`; both retain `M`, each inherits its module operations, and
  each evaluates its own form. For a submodule `i:N -> M`, the induced form is
  `b` composed with `i` tensor `i`; the actual inclusion `i` is retained.

### `OWN-17`: Accessors expose established structure; they never complete construction retroactively

- **Rule:** A public accessor is observational.  It may return stored defining
  data, a canonical map from those data, or a lazy mathematical view whose
  identity was fixed at construction.  It may not create the missing underlying
  object, selected generating set, framing, presentation, category placement,
  or structural map merely because the user asked for it.

  In particular, a method inherited from a category presumes that the
  constructor already supplied the datum that method names.  If calling
  `module_generators()` causes the object to manufacture a new generator-family
  wrapper because no canonical generator object was retained, or if calling
  `presentation()` first allocates the presentation that should define the
  object, construction is backwards.  Repair the constructor/owner; do not make
  the accessor a hidden second constructor.

  Caching an accessor result does not cure this violation.  “Construct once on
  first query” is still post-hoc construction unless the result is merely a
  realization of defining data that were already fixed at construction.
- **Rationale:** Retroactive construction makes object validity depend on which
  methods happened to be called and rewards synthetic compatibility layers over
  honest reuse of general constructors.
- **Observed defect:** lattice `module_generators()` constructed a new
  `IndexedFamily` every time its cache was empty, despite the lattice constructor
  already having built the free module and its canonical generating data.
  Similar labels such as `Free-module generator family` and `Presented-module
  generator family` show the same tendency to manufacture an interface object
  instead of exposing the construction that already holds the generators.
- **Correct Example:** `Free_R(S)` holds the canonical basis map from construction;
  `module_generating_set()` exposes `S`, `module_generator(s)` evaluates the
  stored unit/basis map, and `module_generators()` exposes its represented image
  when that image is mathematically a set.

### `OWN-18`: Generic operations live on the weakest sufficient structure

- **Rule:** The public meaning and codomain of an operation are those of the
  weakest structure on which `lean-categories` defines it.  A refinement may
  provide a faster implementation or additional specialized operations, but it
  does not silently specialize the generic operation's result type or display
  vocabulary.

  If `module_generators()` is defined for framed/free modules, a lattice that is
  a formed free module uses that same module-theoretic operation.  The result is
  not a “lattice generator family” merely because the receiver is internally
  refined as a lattice.  A lattice-specific generating object is justified only
  when extra lattice structure is genuinely selected — for example a simple
  root basis carrying root-system structure — and then it belongs to a distinct
  lattice/root operation whose stronger codomain is part of its contract.

  Apply this rule through all forgetful towers: groups versus sets, algebras
  versus modules, formed versus unformed modules, graded versus ungraded objects,
  schemes versus underlying spaces/rings where appropriate, and specialized
  morphism categories versus their underlying Homs.
- **Rationale:** Otherwise every refinement forks generic concepts into a swarm
  of cosmetically specialized wrappers, leaking implementation taxonomy and
  destroying compositional reuse.
- **Observed defect:** `L.module_generators()` returned an `IndexedFamily` named
  `Lattice-generator family`; free modules independently used `Free-module
  generator family`.  Neither name described additional mathematics of the
  returned generators.  The refinement leaked into a generic module operation.
- **Correct Example:** both the free module and a lattice built from it expose
  the same canonical generator set/image at the module level.  A separate
  `simple_roots()` or similarly standard refined operation may return a richer
  root object when that structure actually exists.

### `OWN-19`: One defining datum has one authority throughout a construction chain

- **Rule:** Do not maintain parallel copies or parallel holders of the same
  defining datum.  An indexing set `S`, selected generating map, relation
  family, grading, action, form, presentation, or universal arrow is received
  once at its constructor and referenced by stronger constructions.  A descendant may
  retain a direct reference or canonical map to it; it may not copy it into a
  second `_indices`, `_generators`, `_presentation`, or equivalent field and then
  implement generic operations against the copy.

  A second datum is legitimate only when it is mathematically distinct: another
  presentation, another basis, another form, another grading, etc.  Then the
  distinction is explicit and the comparison map is first-class.  Equality of
  values or current synchronization is not enough to identify two authorities.

  Review constructors by following defining data forward: each datum should have
  one creation point and thereafter flow by reference, functorial image, or
  canonical morphism.  If two fields can disagree without violating Python type
  invariants, the architecture already permits an impossible mathematical state.
- **Rationale:** Parallel state is the source of drift, duplicated validation,
  accidental recomputation, and contradictory displays.
- **Observed defect:** the lattice stored an actual free module whose
  `module_generating_set()` was authoritative, while `IndexedGenerators` also
  installed a lattice-level `_indices`; lattice module methods then read the
  latter rather than delegating to the former.
- **Correct Example:** `S` belongs to `M = Free_R(S)`; the lattice stores `M` and
  the form.  Any indexing needed for printing or coordinate realization is
  derived from `M.module_generating_set()` rather than stored as an independent
  mathematical authority.

### `OWN-20`: Essential-image claims require using the functorial construction, not imitating it

- **Rule:** When an object is claimed to lie in the image or essential image of
  a standard functor/construction, build it through the preamble's presentation
  of that construction (or
  retain an actual object and specified isomorphism from that construction).
  Do not independently implement an object with equivalent-looking methods and
  then infer after the fact that it “is” a free module, quotient, localization,
  scalar extension, product, completion, or other standard construction.

  For a free object this means the source object and unit are defining data.  If
  the theory says `M = Free_R(S)`, then `S -> U(M)` is not metadata reconstructed
  from a basis after allocation; it is the unit/generating map used to construct
  `M`.  For an object only *isomorphic* to a free object, retain the chosen
  isomorphism rather than silently replacing its presentation by `Free_R(S)`.

  The same distinction applies to equivalence versus equality throughout the
  project.  Being abstractly isomorphic to the output of a construction does not
  license bypassing the construction when its selected source and structural
  maps matter to subsequent mathematics.
- **Rationale:** Method-level imitation loses the universal maps and chosen data
  that make a standard construction reusable and makes later code rediscover
  them from coordinates.
- **Observed defect:** the lattice implementation did create `Free_R(S)` but then
  behaved publicly as though lattice-level generator/index machinery were the
  source of its module structure.  That pattern is the same failure one would
  get from never constructing `Free_R(S)` at all: the functorial construction is
  no longer the authority for its own consequences.
- **Correct Example:** construct `Free_R(S)` with its unit, use that exact module
  as the unformed object of the lattice, and let every generic free-module
  consequence flow from it.  The lattice contributes only the additional form
  and form-specific mathematics.

### `OWN-21`: Interactive display is a semantic projection, not implementation introspection

- **Rule:** `repr`, LaTeX/`show`, rich display, and displays of returned
  collections must present the mathematical object/result at the abstraction
  level of the public operation that produced it.  They may use cheap canonical
  defining data, category placement, invariants, finite members, or a bounded
  lazy window, but they must not expose private class names, storage notation,
  backend coordinates, refinement/classifier names, or implementation-family
  labels unless those are themselves part of the mathematics requested.

  Every default display must provide positive information about the particular
  object.  Repeating the noun phrase of its type is not information.  Removing
  the implementation/type name from the user's memory should still leave the
  display useful.  Conversely, adding more internal words does not make a display
  informative if those words describe routing rather than mathematics.

  A public preamble object must never fall back to Python's object-address
  representation (`<... object at 0x...>`), and a public `_repr_`/`_latex_` must
  never delegate wholesale to a private backend/engine object's display.  Even
  when that backend currently prints familiar mathematics, its notation and
  future changes are implementation details.  Cross the represented data back
  into preamble mathematical syntax and render that syntax here.

  Display must not perform expensive classification, enumerate an unknown or
  infinite object, mutate caches in a mathematically significant way, or create
  missing structure.  It observes the defining data fixed under `OWN-15` through
  `OWN-20`.
- **Rationale:** Interactive display is part of the mathematical API.  A user
  inspects an object to learn what was constructed, not to discover which
  internal refinement or sparse representation happened to implement it.
- **Observed defects:** `Lattice-generator family` and `Natural numbers` merely
  renamed types; `1*B['alpha']` exposed sparse free-module storage; `placed map`
  hid even the map's domain/codomain.  Each output discarded mathematical data
  already available at negligible cost.
- **Correct Examples:** `{e_0, e_1}` for the canonical finite generator image;
  `NN = {0,1,2,...}` for the natural numbers; a pointwise-defined map displays
  its source and target when no closed formula is represented; a free object may
  display `Free_R(S)` together with a useful view of `S`.

### `OWN-22`: Structure is constructed, and checking it is asked for

- **Rule:** An object or morphism is built by the construction that places it
  in its category, and construction does not check it: nothing re-derives at
  construction what the construction states.  Construction is not evidence that
  the result satisfies its laws, and nothing treats it as such; whether an
  implementation's answers are correct is judged only by the `lean-cas-dsl`
  acceptance suite.  Checking that a map preserves structure, is equivariant, is
  bilinear, or satisfies an algebra's relations is never eager.  It is a flag the
  caller sets when they want their input checked, or a method they call; the
  default constructs without checking.  Such a check is itself an untrusted
  computation, a diagnostic for the caller and never evidence.

  Structure is the morphism that defines it, held as a callable, not a
  computed table.  An algebra's multiplication is its ring structure, and
  the multiplication of `RR` as an `RR`-algebra is the multiplication of
  `RR`.  An `R`-module is the action morphism `rho: R -> End(M)`, and
  `End_R(M)`'s algebra structure is composition.  Most algebra and module
  constructions go through the action-morphism construction; the
  construction of an algebra from a multiplication map uses that map only to
  define the action.  A multiplication tensor, a structure-constant array or
  a presentation of a Mor module is computed only when it is asked for, and
  then as a morphism, with a matrix-like array extracted only by an explicit
  matrix-like request.

  `Mor_C(X, Y)` is always a category (a set when 0-truncated), and one
  category: constructing it fixes its endpoints and composition, and never
  computes a presentation of it as a module or of its composition as a map
  out of a tensor product.

  Construction is therefore almost instant: it stores the defining datum and
  fixes the category.  Every other datum of the object (an inverse, a group's
  generators, a sublattice's Gram matrix, a genus symbol) is computed on its
  first request, cached on the object, and reused by every method that needs
  it.

  A well-definedness condition is a validator method of the object.
  Construction calls the object's validators once, after the object exists,
  in the manner of a pydantic post-init validator, and each validator returns
  at once unless the global strict-checking flag is on.  The flag is one
  session-wide setting, off by default, for exploratory work; no construction
  turns it on for itself.  A caller may call any validator by hand.  A
  constructor's `check=True` runs that constructor's validators for that one
  call.  No check is written into `__init__`, an element constructor or a
  computation, because some laws cannot be checked at all: no finite
  computation shows that the Fourier transform is an isometry of `L^2(RR)`.

  The flag and the protocol have one owner, `sage_extensions.validation`.
  `strict_checking()` reads the flag and `strict_checking(True)` sets it, in the
  spelling of Sage's `proof.arithmetic()`; the session import exports it.  A
  validator is a method decorated with `@validator`, named `validate_<law>`
  (`validate_linearity`, `validate_injectivity`, `validate_surjectivity`,
  `validate_form_preservation`, `validate_lift`), that raises `ValueError` when the
  object fails the law.  It takes `check=True` by default, so a call by hand
  runs; an element constructor calls each validator of its category with its
  own `check` argument, which defaults to `False`.  A membership that states a
  property answers the predicate by placement: an element of `Mono(M, N)`
  answers `is_injective()` with `True`, and `validate_injectivity` is how that
  claim is checked.
- **Rationale:** An eager check or an eager structure table costs what the
  construction never needed, and it compounds: building `End_R(C)` for a
  presented `C` built its multiplication `End ⊗ End -> End` through another
  presented Mor module, so `End(Z/2 + Z^(n-1))` took 0.42 s, 2.76 s and 329 s
  for n = 1, 2, 3 (measured 2026-09-25).  On 2026-10-07 the test that builds
  `O(E_6)` took 72.8 s, almost all of it preamble overhead: each isometry
  checked its form and inverted its matrix at construction.
- **Violation Example:** a Mor constructor that computes the presented
  internal-Hom model of its endpoints; an `End` constructor that builds its
  multiplication as a morphism out of `End ⊗ End`; a constructor that checks
  linearity or equivariance unless the caller asked it to; an isometry
  constructor that inverts its matrix; an orthogonal group whose constructor
  computes its group generators.
- **Correct Example:** `End_R(M)` multiplies by composing its elements;
  `f.is_equivariant()` checks equivariance when called; a constructor's
  `check=True` checks the caller's data; `A.multiplication()` returns the
  multiplication as a morphism when asked, and its matrix only through an
  explicit matrix extraction; `O(L).group_generators()` is computed on the
  first call and cached.

### `OWN-23`: Lazy realization fixes all defining choices before exposure

- **Rule:** Distinguish a mathematical datum from its evaluated representation.
  Construction must fix the selected objects, endpoints, base morphisms,
  equations and law hypotheses. A lazy realization may evaluate exactly that
  datum later, with its codomain already fixed. Access order cannot select a
  new framing, a new presentation, a different source, or different placement.

  A selected **free cover** (historically called `framing_morphism` in the
  preamble) is an epimorphism `Free_R(S) -> M`, including its specified source,
  generator images, and spanning obligation. A categorical **framing** has an
  *invertible* augmentation `Free_C(S) -> X` for a specified free--forgetful
  adjunction (`CAT-29`); a surjection is not a framing. A stored callable
  without the relevant source and morphism contracts is neither. A delayed
  realization of those fixed data is allowed when constructing its enriched
  morphism eagerly would recursively demand another resolution-dependent Mor. Admission
  of the module's datum and realization of that morphism must be stratified at
  their common owner; `_install_*` helpers and post-allocation refinement are
  not alternative public constructors.

  Settle mutually recursive constructor obligations together before their
  consumers rely on either one. Follow actual initialization and accessor calls
  and identify the already-fixed datum on which each step depends. The chain
  must terminate without demanding its own enriched framing or proving a law
  from the very placement that law is needed to admit. Preserve this argument
  when adding a new realization; a cache or delayed callback alone does not
  establish well-founded construction.
- **Rationale:** Requiring eager evaluation of every enriched map produces a
  constructor cycle; accepting arbitrary delayed choices produces invalid
  objects. Neither follows from the mathematical definition.
- **Correct Example:** a framed module and a morphism space retain their selected
  framing sources; requesting generators, the framing arrow and a nested morphism
  space in different orders yields the same sources, maps and operations.
  A nonsurjective map is not a framing merely because it supplies some elements.

### `OWN-24`: Computations over families are tensor operations, and coordinate conventions live only in the tensor package

- **Rule:** Mathematical code states a computation over a family as the tensor
  operation it is. It never states it as a loop and never as a matrix
  product.  The pairings `b(v_i, w_j)` of two families are one contraction.
  `f` preserves forms when `f^* b_W = b_V`, written
  `codomain.gram_tensor().pullback(f)` compared with `domain.gram_tensor()`.
  A change of basis of a form is its pullback along the change of basis.
  Composition is `f * g`, inverse is `~f`, and application is `f(v)`.

  Which side a matrix acts on, and where a transpose falls, is a coordinate
  convention.  It is fixed once, inside `preamble/tensors/`, where
  `Tensor.pullback` holds the only `A^t G A`.  The engine's own convention
  (Sage matrix groups act on rows) is converted once, at the tensor package's
  lowering and raising of a morphism.  Outside that package no code transposes
  **coordinate matrices** with `.transpose()` or `.T`, calls `matrix_action_*`,
  or multiplies coordinate matrices to state a mathematical equation.
  Transpose on an owned framed module morphism is itself a typed morphism
  operation with reversed endpoints; it is not a choice of engine convention
  and is not banned.  Thus `M^t G M` and `M G M^t` cannot be written as raw
  matrix equations at their consumers, and no caller chooses between them.

  **The semantic operation is the requirement, not a permitted spelling.**
  Before changing an offending site, identify its mathematical domain,
  codomain, selected morphism or family, the tensor/form it acts on, and the
  actual categorical construction (pullback, evaluation, contraction or
  composition). Route the operation through that owner; only its private
  numerical realization may choose matrices, NumPy operations or einsum
  subscripts. Replacing `@` with `einsum`, `.transpose()` with a helper that
  still chooses a side, or a pairing loop with another hand-written
  contraction at the consumer **does not** repair a boundary violation.
  Quotient-valued bilinear and quadratic forms retain their actual target
  modules (for example `K/R` and `K/2R`); an integer matrix of
  representatives is only a private realization, never a replacement for
  the form morphism or its chosen generator map.
  For a finite form module with selected generators, construct the
  surjection from the free module on those generators, and pull back
  the bilinear and quadratic forms along that actual morphism. Numerical
  family contraction takes the pulled-back forms as inputs, not a
  manually assembled Gram array at the consumer. The value modules of
  the bilinear pairing and its quadratic refinement remain distinct.

  **Mathematical transposition and coordinate transposition are different
  operations.** Determine the receiver's actual owning Mor and the source and
  target of the transposed arrow before classifying a `.transpose()` call.
  A checker match is not evidence that a Sage matrix was transposed. Conversely
  a checker miss, or a different spelling such as `@`, `dot`, `matmul` or
  `einsum`, is not evidence that the computation crosses the right boundary.
  Do not move a public morphism operation to an engine package, change its
  API, or weaken a rule merely to satisfy a textual checker.

  One equation has one owner.  A second statement of the same invariant, such
  as a loop of form evaluations beside a pullback, is deleted.
- **Rationale:** An imperative loop over elements re-enters the preamble's
  element and form machinery once per pair. Its cost is that overhead times
  the square of the family.  A side convention written at each call site
  is a choice made again at each site, and a wrong choice there is a wrong
  answer that no check sees on symmetric specimens.  On 2026-10-07 the
  isometry check was stated three times in `lattice_morphisms.py`: as the
  pullback, as `transformation.transpose() * codomain_gram * transformation`,
  and as 64 `b(., .)` evaluations in `_form_square_commutes`. The last one cost
  18 s of the `O(E_6)` test.
- **Violation Example:** `for` loops over pairs of roots, basis vectors or
  generators; `all(b(x, y) == ... for x ... for y ...)`; `P * G * P.transpose()`
  in a reduction; `form.matrix_action_right(step)`; a helper whose docstring
  says "Sage acts on rows, hence one transpose" outside the tensor package.
- **Correct Example:** the isometry validator compares
  `codomain.gram_tensor().pullback(f)` with `domain.gram_tensor()`; the form
  in a reduced basis is the pullback along the reducing automorphism; the
  Gram tensor of a family of roots is the pullback along the map that
  sends the standard basis to the roots.
- **Enforcement:** `just tensor-boundary` detects several *syntactic*
  manifestations of coordinate operations outside `preamble/tensors/`.
  Its retained exceptions must be justified by the mathematical receiver
  and construction, never by an identical line of text. It is a necessary
  regression check, not a complete checker for semantic ownership. At every
  affected site the reviewer separately traces the mathematical operation,
  its categorical owner, the lowering/raising boundary and its consumers;
  this source review is required even when the recipe reports zero matches.
  A failure of an existing whole-tree gate on unchanged source does not create
  a dependency of an unrelated worktree integration: apply the repository's
  stage-scoped commit/verification rules, and repair the violation at its own
  mathematical owner under the appropriate task.

### Construction-chain review protocol

For any constructor that adds structure, review the construction chain before
reviewing leaf methods.  This is a source-review discipline, not a request for a
new static checker, certificate, registry, or generated compliance report.

1. **Read the mathematics first.** From `lean-categories`, take the weaker object
   `Y`, the added datum `d`, the stronger object `X=(Y,d)`, and every canonical
   map relating them. If the construction is functorial, name the
   functor/unit/counit or structural arrow that supplies the relationship.
2. **Find the unique construction of `Y`.** There must be one construction of it
   in the preamble.  If no actual `Y` is constructed, determine whether honest inheritance
   supplies it; otherwise the stronger constructor is imitating a weaker theory.
3. **Follow identity, not equality.** Confirm that `X` retains that exact
   `Y` or an explicit chosen isomorphism when only equivalence is intended.
   Reconstructing an equal/isomorphic object later is not reuse.
4. **Follow every defining datum forward.** Index set, framing, presentation,
   grading, form, action, inclusion/projection, and source/codomain data should
   be created once and thereafter referenced or transported.  Search for parallel
   fields and parallel constructor calls that can drift.
5. **Inspect the forgetful direction.** `underlying_*`, `unformed_*`, category-owned forgetful functors,
   restrictions, and generic inherited operations must land in/use the actual
   weaker object.  Returning `self` requires a mathematical reason, not shared
   coordinates or class ancestry.
6. **Inspect the structure-adding direction.** Each required unit, inclusion, projection or comparison
   map must have the endpoints specified by its universal property. Do not
   invent an identification pair for structure added through `CON-16`.  Test a
   nontrivial element/map, not only identities or dimensions.
7. **Inspect generic methods at the weakest owner.** A descendant should normally
   inherit/delegate module/set/group/etc. operations.  An override needs genuinely
   stronger mathematics, not access to more internal state.
8. **Inspect accessors for hidden construction.** A getter may realize a lazy
   computation but may not create the first canonical underlying object, family,
   presentation, or structural map.  `@cached_method` does not make such creation
   legitimate.
9. **Inspect the displayed result.** The display should reveal the mathematical
   result of the public operation and cheap defining data, not the internal leaf
   category, implementation class, backend notation, or a noun phrase naming its
   type.
10. **Inspect downstream consumers.** They should compose the retained objects
    and maps rather than reopening coordinates or reconstructing the same
    construction independently.

Immediate red flags discovered in prior repository work include:

| Red flag | Architectural diagnosis | Required direction |
| --- | --- | --- |
| A structured object stores `_module`, `_underlying`, `_source`, etc., but its `underlying_*()` accessor returns `self` | the real weaker object exists but the public construction bypasses it | return/reuse the stored object and build the actual structural maps |
| A constructor builds `Free_R(S)` while the descendant also stores `_indices` or another copy of `S` | two authorities for one defining datum | make `Free_R(S).module_generating_set()` authoritative |
| `module_generators()` / `relations()` / `presentation()` first allocates a wrapper describing data that should already define the object | accessor is acting as a hidden constructor | construct/retain the mathematical datum at the owning constructor |
| Generic operation results are named `Lattice-*`, `Group-*`, `Scheme-*`, etc. only because the receiver is refined | internal category refinement leaked into a weaker public operation | return the result type/display of the weakest sufficient structure |
| A free-module generator prints as `1*B['alpha']` | storage coordinates escaped as mathematical syntax | render the selected formal generator/linear combination |
| A display says only `Lattice-generator family`, `Natural numbers`, `placed map`, or another type paraphrase | zero mathematical information gain | show defining data, endpoints, members/window, invariants, or canonical notation |
| An isomorphic replacement is reconstructed from rank/dimension/labels while the original object is available | equality/isomorphism substituted for construction provenance | retain the original object or explicit chosen comparison map |
| Category membership is taken to mean that framing/action/form/presentation data must exist | property/type label substituted for selected structure | require the constructor to supply the actual datum |

These are examples of the general policies `OWN-15` through `OWN-21`, not an
exhaustive blacklist.  When a new instance has the same generator, repair the
construction owner; do not mint a narrower exception or a detector for the one
spelling that happened to expose it.

### Presenting a category: the procedure

This is the order of work for adding, moving, splitting or retiring the
preamble's presentation of a category. The preamble has no categories of its
own: every category class presents a category `lean-categories` formalizes, and
every supercategory entry presents an inclusion `lean-categories` states. A
category `lean-categories` lacks is requested there and is not presented until it
is released. This procedure exists because the declared graph read on 2026-09-16 was the sum of locally
defensible edits: thirty categories under `Sets()`, a hand-meshed block of 135,
four notions each under two names, restriction of scalars declared on three
bases, a diamond through two different objects.  None of those was wrong at the
moment it was written, from where its author stood.  The procedure moves the
author to where the errors are visible, which is the formalization first and the
whole graph second, and it makes each step leave a record in the commit body.

**How the graph drifts, so that the steps below read as remedies.**  A
category is minted where a consumer needs it and named from that vantage,
which is research authoring mathematics, and one notion acquires a second name (`FormedModules` beside `FormModules`).  A
property is written as a class because a class is what the language offers,
and then a class per combination follows, so a product of independent axes
becomes a mesh of hand-declared diamonds (`FinitelyPresentedQuadraticFormModules`).
A supercategory is chosen because it makes construction succeed or a method
resolve, so `Sets()` and `Objects()` become placeholders and `Schemes` is
declared beside `QuasiAffineSchemes` for safety.  A functor across a base is
declared as an inclusion because both are true sentences (`Modules(R) ->
Modules(S)`).  A consumer is left behind by a rename, and a lazy export table is
added so the package still imports, which hides the dangling import for a year.
Each step is local, each is defensible, and the disorder is only visible in
aggregate, which is why the instrument runs on every declaration change.

1. **Read the notion in `lean-categories`, with no implementation names.**
   Its objects, morphisms, defining datum, hypotheses and inclusions, as
   formalized there.  Apply
   [mathematical dependency tracing](#mathematical-dependency-tracing): the
   categories the definition passes through, each formalized in
   `lean-categories`.  If any is not, stop: it is a formalization request there
   ([AGENTS.md](AGENTS.md#a-missing-foundation-parks-the-work-that-found-it-always-on)),
   and nothing is presented until it is released.  Do not open the tree yet;
   reading the tree first makes its current contents decide what is true.
2. **Classify every level of that chain as the formalization does.**  A
   property of the objects with no chosen datum is presented as an axiom on the
   base that first states it (`CAT-17`).  A chosen datum is presented as a data
   subcategory, a class that declares the axiom it truncates to; a chosen
   generating set, presentation or syzygy tower is a truncated resolution in the
   category of resolutions over the base (`CAT-29`).  A construction on a
   category (G-objects, direct-sum decompositions, arrows, presheaves) is
   parameterized by that category and declares it (`CAT-20`).  An object
   constructor is the category applied to the object's data and is not a
   category at all.  A combination of properties is a join and gets no class
   (`CAT-18`).
3. **Survey the tree, level by level.**  `just category-graph by-supercategory`
   for the parent each level would declare; `just category-graph json` with
   `jq` for who owns an operation; `rg` on the nouns of each definition across
   `categories/`; the expectation files under `tests/constructions/`,
   `tests/user_simulations/` and `tests/conftest.py` for the names they use.
   Record each level as: presented; presented under another name, which is
   retired into the owner (`CAT-22`); or not yet presented.
4. **Reuse axioms before naming any.**  `sage.categories.category_with_axiom.all_axioms`
   and the base's nested axiom classes first.  A new axiom name is
   `lean-categories`' name for the property, registered once; a property relative
   to a different structure is qualified in Sage's idiom
   (`FinitelyPresentedAsAlgebra`) so that it does not collide with the module
   meaning (`CAT-19`).
5. **Present what is missing from the top down.**  The deepest intermediate
   category `lean-categories` formalizes and the preamble does not yet present
   first, declaring its one immediate parent, then the next, then the leaf.  A leaf written before its intermediates is a leaf that
   declares two levels up, and that edge is never removed later.
6. **Wire the leaf onto the deepest existing node.**  Its declaration is the
   most specific category the tree can spell, as a join where it is one:
   `Schemes(R).Affine().FiniteType().Smooth()`, not `AffineSchemes(R)` beside a
   list of properties the join already composes.  One entry, unless the object
   is genuinely two structures at once (a ring and a module), in which case
   write both and cite in the commit body the `lean-categories` theorem that the
   two routes are the same functor (`CAT-21`).
7. **Keep every change of base or parameter out of the list.**  Restriction of
   scalars, base change, the passage from an ideal to a fractional ideal or from
   an `R[G]`-module to a `G`-object over `R`: each is a functor obtained from
   the category by a method named for the construction (`CAT-16`).  Sage
   applies every axiom along a declared edge, so such an entry is a false
   statement for every relative property.
8. **Write the declaration as expressions a reader can resolve** (`CAT-24`):
   names and parameters, no locals, no method calls on `self` that compute a
   category.  `extra_super_categories` on an axiom class states a genuine
   implication over the same base and nothing Sage's join already supplies.
9. **Read the graph before and after** (`CAT-25`): `shape`, `cells`, `audit`,
   and `just preamble-imports`.  The breadth of the target does not grow, no
   shortcut appears, no piece splits off, and any new generator owing a cell is
   named in the commit body with the `lean-categories` theorem that fills it; a
   cell with no such theorem is a request there, and the generator waits.
10. **Deliver the consequences in the same commit.**  Consumers of a retired or
    renamed name are rewritten (`CAT-26`); a name an interface requires
    survives as a thin function returning the category (`CAT-27`); the TODO
    node the change delivers is removed with its edges; the delta from step 9
    is in the body.
11. **When the honest parent is not in the tree, stop and say so.**  Present it
    if `lean-categories` formalizes it; otherwise request it there, leave
    `super_categories` abstract so the category refuses to construct, and record
    the missing category in the native issue tree, with its
    dependency path and the consumer's native blocked-by relation. Never a
    placeholder, never a local definition, never a mechanism that makes the
    construction proceed (`DEV-65`).

The procedure in one line: read the formalization, classify as it does, survey,
reuse, present top-down, wire to the deepest node, keep functors out of the
list, write resolvable expressions, read the graph, deliver the consequences,
and stop where `lean-categories` has no mathematics yet.

## Corrective implementation style guide (`STY-*`)

This is a **living catalogue of concrete code shapes**.  Add a new entry whenever review identifies a recurring implementation pattern whose replacement is known.  Do not wait for the same mistake to recur in several files.  The point is to teach the repository's preferred constructions—not merely to ban today's instances.

The default order of preference is:

1. the preamble operation on the category/parent/element/morphism/Homset/functor where `lean-categories` places the notion;
2. a mature library abstraction (`itertools`, `collections`, `functools`, graph/group/CAS APIs, etc.);
3. a declarative Python expression (comprehension, generator expression, `any`, `all`, `sum`, `min`, `max`, `next`, dictionary union, etc.);
4. an explicit stateful loop only when state evolution is actually the algorithm.

An explicit loop is not intrinsically bad.  Search, fixed-point iteration, backtracking, dynamic programming, state-machine protocols, and backend algorithms may be clearest as loops.  The smell is an imperative loop whose only job is to spell a standard map/filter/fold/group/traversal operation manually.

### One-shot red-flag lookup

Use this table during review before reading the longer entries below.  Each left-hand shape should immediately suggest the right-hand replacement; if the replacement is mathematical data rather than private Python data, use the owned mathematical construction first.

| Red flag | First replacement to consider |
| --- | --- |
| `result = []; for x in xs: result.append(f(x))` | `[f(x) for x in xs]`, `map(f, xs)`, generator, or owned image/family |
| `result = []; ... if p(x): result.append(x)` | `[x for x in xs if p(x)]` / `filter(p, xs)` |
| `result = []; for block in blocks: result.extend(block)` | `itertools.chain.from_iterable(blocks)` |
| `sum(rows, [])` | `itertools.chain.from_iterable(rows)` |
| `result = set(); ... result.add(f(x))` | `{f(x) for x in xs}` / `set(map(...))` / owned set |
| `result = {}; ... result[key] = f(x)` | dict comprehension |
| `d.setdefault(key, []).append(value)` | `collections.defaultdict(list)` or `itertools.groupby` for sorted streaming input |
| `d[key] = d.get(key, 0) + 1` | `collections.Counter` |
| `d[key] = d.get(key, zero) + value` | finite-support abstraction / `defaultdict` |
| `total = zero; ... total += term` | owned finite sum/`linear_combination`; otherwise `sum(..., start=zero)` |
| `product = one; ... product *= factor` | owned `product`; numeric `math.prod(..., start=one)`; otherwise `reduce(mul, ..., one)` |
| nested `for a in A: for b in B:` producing all pairs | `itertools.product(A, B)` or owned Cartesian product |
| hand-built subsets/tuples of fixed size | `itertools.combinations` / `combinations_with_replacement` / `permutations` |
| manual first `n` values | `itertools.islice` |
| manual running partial sums/products | `itertools.accumulate` |
| `for x in xs: if not p(x): return False` | `all(p(x) for x in xs)` |
| `for x in xs: if p(x): return True` | `any(p(x) for x in xs)` |
| `for x in xs: if p(x): return x` | `next((x for x in xs if p(x)), default)` |
| manual count with `count += 1` | `sum(p(x) for x in xs)` / `Counter` |
| manual min/max tracking | `min` / `max(..., key=...)` |
| `for x in xs: yield x` | `yield from xs` |
| `for x in xs: yield f(x)` | generator expression / `map(f, xs)` |
| `for i in range(len(xs))` only to pair position/value | `enumerate(xs)` |
| indexing two equal-length collections in parallel | `zip(left, right, strict=True)` |
| repeated `labels.index(x)` inside a loop | owned `rank(x)` or one precomputed rank map |
| list used as FIFO frontier | `collections.deque` |
| hand-built orbit closure | owned action/G-set `.orbit(...)` or GAP/Sage backend |
| hand-built connected components/reachability | Sage/networkx graph API |
| hand-built multiplicity map | `Counter` / owned multiset |
| hand-built ordered deduplication | owned ordered set; private `dict.fromkeys` when appropriate |
| `try/except` in mathematical code | remove exception-driven control flow; assert the mathematical hypotheses and call code that is total under them; catch/translate failures only in engineering adapters |
| `x = f(...); return x` | `return f(...)` unless `x` names a mathematical intermediate |
| `if p: return True; return False` | `return p` |
| whole method is `assert False` / immediate failure | Sage `@abstract_method` for a genuine abstract contract, or correct mathematical placement; an assertion fallback is valid only after real implemented computational cases |
| `assert mathematical_hypothesis` | normally **keep or add it**: assertions loudly state the proof context; move the method only when the operation itself belongs to a narrower mathematical category |
| `hasattr/getattr/isinstance` to discover owned structure | category/method placement; private engine dispatch only at backend boundary |
| module-global `*_CACHE = {}` for canonical objects | shared memoization / `UniqueRepresentation` / `cached_function` |
| repeated `foo = OtherClass.foo` | common superclass/category implementation/delegation |
| repeated cross-engine convert→compute→convert stages | one adapter crossing around the complete engine computation |
| `f.matrix()` followed by nullspace/kernel rows and reconstructed submodule | `f.kernel()`; improve the Hom kernel implementation if necessary |
| structural predicate implemented by determinant/rank/gcd/minors | spell the categorical/module-theoretic definition; hide the numerical criterion underneath it |
| downstream code branches finite/infinite then performs coordinates | semantic owner routes representation cases; caller stays representation-oblivious |
| local `_..._from_matrix/_rows/_coordinates` helper recreates a standard construction | add/fix the kernel/image/pullback/cokernel/quotient/block-Hom/etc. API |
| same numerical workaround appears in a second consumer | treat it as missing semantic API and factor it immediately |
| subobject equality ignores its inclusion morphism | equality in the owned subobject/slice construction; the mono is part of the data |
| quotient equality ignores its projection | equality in the owned quotient/coslice construction; the epi is part of the data |
| normal form mutates/replaces chosen presentation | return a new represented object together with the isomorphism from the source |
| kernel/cokernel/product/etc. returned without canonical arrows | return/attach inclusion, projection, injections/projections, or other universal structure maps |
| test of isomorphism/isometry/genus uses equal objects | use distinct objects/presentations related by the weaker relation |
| `provider`/`manager`/`evidence`/`context` object in math layer | identify the actual morphism/functor/family/choice/standard mathematical datum |
| review finding is patched by moving code to a helper/registry | identify and repair the architectural generator/owner; migrate consumers |
| functor accepts `C` but rejects every non-isomorphism | declare the domain `C.core()` (or the actual slice/coslice/subcategory) |
| parameter redefines a canonical mathematical notion | derive it from existing structural data; use a new name only for genuinely different mathematics |
| deep specialized file computes generic set/Hom/quotient/product semantics | stop local patching and audit the general owner |
| universal construction gains arrows by product/matrix analogy | write the universal diagram and expose only the canonical maps it actually supplies |
| public `*args` / `**kwargs` forwards backend options | replace by closed named mathematical signatures; keep option forwarding private to adapters |
| `None` sentinel changes object/witness/return shape | split operations or accept the actual mathematical datum; only canonical defaults may be omitted |
| boolean mode flag changes mathematical result | named operations/constructors or precise literal overload at a compatibility boundary |
| `not is_X()` where the complementary mathematical property has a standard name | expose the positive predicate; preserve three-valued semantics where relevant |
| one-line `same_*` / per-element action wrapper hides value/morphism object | expose the composable value/morphism/Hom identity directly |
| supplied generators are returned as `O(L)` / `Aut(X)` | canonical group object plus `.subgroup(gens)`; completeness is a separate theorem |
| `Random*` / `Example*` / `Test*` type/category | process generates defining data for the ordinary constructor; named specimens go in catalogues |
| negative/absence test passes if object/result is empty/dead | prove a positive live surface/completeness witness first; prefer the positive universal property |
| easy determinant/count/fingerprint used to prove stronger claim | definition, cited complete invariant, or explicit witness |
| algorithm must exhaust `G`, `M`, `L`, etc. | structural/generator/presentation check justified by a `lean-categories` theorem; explicit lazy enumeration only when enumeration is the operation |
| public name contains `partial`/`fast`/`cached`/engine name | use the stable mathematical noun/verb; put algorithm routing in implementation |
| “tensor product of matrices” | Kronecker product of matrices; tensor product belongs to represented maps/modules |
| `dot_product`/Euclidean norm/projection on arbitrary formed object | use the object's declared form/correlation; Euclidean algorithms only under the correct refinement |
| definite/nondegenerate restriction comes only from backend routine | keep general semantic domain; localize current algorithm case beneath it |
| owned upstream defect gets local Protocol/wrapper workaround | repair the authoritative source as part of the dependent task |
| long-lived stored backend twin drives ordinary math | prefer ephemeral construct-compute-convert-discard; durable backend state has one private owner |
| Sage `super_categories()` edge copied as “is-a” | classify actual structural functor first; Sage graph is runtime evidence only |
| Sage category equality/identical parents treated as mathematical equivalence | compare owned normalized constructions/functors |
| runtime bundled type/presentation called the category | separate category, object, runtime type, chosen presentation, property refinement |
| exact upstream class/name not found | compose standard mathematics from existing constructions before declaring a gap |
| mature dependency rejected mainly for package/build weight | compare owned LOC/reasoning, future blast radius, and reuse instead |
| local helper appears before checking Sage/stdlib/upstream idiom | inspect/probe the host first; use native capability behind owned semantics |
| scanner finding “fixed” only by syntax/suppression | diagnose against policy and repair the structural generator |
| generated certificate/status ledger mirrors live category/code facts | encode invariant structurally; live tests/on-demand report; no stored second ledger |
| category constructibility proved by graph BFS/name presence | derive the required canonical structural maps/category expression |
| repeated compliance checks grow around same violation | strengthen type/category/constructor/API so violation is structurally exposed |
| upstream tether shows duplicate general operation but local alias is preserved | delete/resite the local declaration; alignment can expose a defect |
| `pass` in mathematical implementation | implement/delete; genuine contract uses Sage `@abstract_method` + `...` |
| exact predicate returns `False`/bare `Unknown` because algorithm is missing | decide what the data decides and return the proposition (`Predicate`) otherwise (`DEF-06`); `Unknown` stays only for explicitly soft knowledge predicates and `ask` |
| `list(...)` / `tuple(...)` only to iterate | keep owned collection/generator lazy |
| multiple eager map/filter stages | generator/`map`/`filter` pipeline |
| raw `while` used only for ordinary iteration | `for`/iterator construct; retain `while` only for genuine evolving state |

### API and ownership patterns

#### `STY-01`: Global operation function -> method on the mathematical owner

**Bad:**

```python
Product(X, Y)
Kernel(f)
Orbit(G, x)
BaseChange(M, S)
```

**Preferred:**

```python
C.product([X, Y])
f.kernel()
G.orbit(x)
M.base_change(S)
```

The receiver supplies domain information and makes the operation discoverable by `<TAB>`.  A public global helper is not justified merely because it can dispatch correctly.

#### `STY-02`: Global dispatcher -> category/Hom/parent method dispatch

**Bad:**

```python
def Product(X, Y):
    if X in Modules(R) and Y in Modules(R):
        return module_product(X, Y)
    if X in Sets() and Y in Sets():
        return set_product(X, Y)
    if X in Schemes(S) and Y in Schemes(S):
        return scheme_product(X, Y)
```

**Preferred:**

```python
C = X.ambient_category()
return C.product([X, Y])
```

and each category subtree defines its own `product` implementation.  The global switchboard is usually a consequence of putting the operation on no mathematical owner.

#### `STY-03`: Ancestor imports descendant -> descendant imports/refines ancestor

**Bad:**

```python
# Cat/products.py
from ...lattices.my_special_lattices import MySpecialLattices
```

**Preferred:**

```python
# lattices/my_special_lattices.py
from ...abstract_categories.products import ProductsOfCategory

class MySpecialLattices(...):
    ...
```

A new specialized subtree should normally be addable without semantic edits to its ancestors or unrelated siblings.  Upward knowledge is a code smell even when not categorically forbidden.

#### `STY-04`: Export convenience operation -> keep global namespace sparse

**Bad:**

```python
# preamble/all.py
from .foo import Product, Kernel, Cokernel, Orbit, Stabilizer, BaseChange
```

**Preferred:** expose constructors/objects/categories globally and discover operations from the object already in hand:

```python
C = Modules(R)
C.<TAB>
f.<TAB>
G.<TAB>
```

A session namespace should not become a catalogue of every verb in the system.

#### `STY-05`: Runtime capability probing -> category-owned operation

**Bad:**

```python
if hasattr(M, "presentation_matrix"):
    return algorithm(M)
```

or:

```python
try:
    presentation = M.presentation_matrix()
except AttributeError:
    ...
```

**Preferred:** put the operation on the category that supplies the hypothesis:

```python
class ModulesWithChosenFinitePresentation(...):
    class ObjectType:
        def operation(self):
            ...
```

If a caller genuinely must branch, branch on owned mathematical category membership, not Python method presence.

#### `STY-06`: Manual sibling-method grafting -> common implementation/inheritance/category mixin

**Bad:**

```python
class GroupModuleHomset(...):
    base_ring = ModuleHomset.base_ring
    scalar_multiple = ModuleHomset.scalar_multiple
    elementwise = ModuleHomset.elementwise
    zero = ModuleHomset.zero
```

**Preferred:**

```python
class GroupModuleHomset(ModuleHomset, ...):
    ...
```

or move the shared API to the common Hom/category abstraction.  Assigning methods one-by-one is manual inheritance.

#### `STY-07`: Hidden source/provenance attributes -> explicit chosen-image/witness object

**Bad:**

```python
image._preamble_scalar_extension_source_module = M
...
M = image._preamble_scalar_extension_source_module
```

**Preferred:**

```python
selected_image = F.Image(M)
M = selected_image.preimage()
image = selected_image.image_object()
```

If later mathematics requires a chosen source, presentation, decomposition, or witness, that datum is part of the mathematical object model.

#### `STY-08`: Import-order-dependent refinement -> stable dependency DAG

**Bad:**

```python
try:
    from .modules import Modules
except ImportError:
    return R   # try again on a later lookup
```

**Preferred:** reorganize dependencies so the canonical structure is available deterministically from the defining object/category.  Function-local imports are for optional/heavy implementation dependencies, not a general cycle-breaking architecture.

### Collection construction patterns

#### `STY-09`: `append(f(x))` loop -> list comprehension or lazy image

**Bad:**

```python
images = []
for x in xs:
    images.append(f(x))
```

**Preferred:**

```python
images = [f(x) for x in xs]
```

or, when materialization is unnecessary:

```python
images = (f(x) for x in xs)
```

If this is a mathematical image/family, use the owned image/indexed-family construction instead of a Python list.

#### `STY-10`: Conditional `append` loop -> filtered comprehension/generator

**Bad:**

```python
compatible = []
for candidate in candidates:
    if agrees(candidate):
        compatible.append(candidate)
```

**Preferred:**

```python
compatible = [candidate for candidate in candidates if agrees(candidate)]
```

or lazily:

```python
compatible = (candidate for candidate in candidates if agrees(candidate))
```

#### `STY-11`: Dict assignment loop -> dictionary comprehension

**Bad:**

```python
images = {}
for label in labels:
    images[label] = f(label)
```

**Preferred:**

```python
images = {label: f(label) for label in labels}
```

This applies only when the loop is a direct map.  Multi-step coefficient accumulation may instead belong to a finite-support or linear-combination abstraction.

#### `STY-12`: Set `add` loop -> set comprehension/constructor

**Bad:**

```python
category_types = set()
for category in categories:
    category_types.add(type(category))
```

**Preferred:**

```python
category_types = {type(category) for category in categories}
```

or simply `set(values)` when no transformation occurs.

#### `STY-13`: Two disjoint dict-building loops -> dict union/comprehensions

**Bad:**

```python
images = {}
for label in left_labels:
    images[("left", label)] = left_map(label)
for label in right_labels:
    images[("right", label)] = right_map(label)
```

**Preferred:**

```python
images = {
    **{("left", label): left_map(label) for label in left_labels},
    **{("right", label): right_map(label) for label in right_labels},
}
```

or Python 3.9+ dictionary union:

```python
images = left_images | right_images
```

If the keys are mathematically tagged coproduct labels, prefer the owned coproduct/family construction.

#### `STY-14`: `extend` flattening loop -> `itertools.chain.from_iterable`

**Bad:**

```python
flat = []
for block in blocks:
    flat.extend(block)
```

**Preferred:**

```python
from itertools import chain
flat = chain.from_iterable(blocks)
```

Materialize with `list(...)` only at an explicitly finite private boundary that requires a Python sequence.

#### `STY-15`: `sum(rows, [])` flattening -> `chain.from_iterable`

**Bad:**

```python
entries = sum(rows, [])
```

This is quadratic for lists and hides flattening as addition.

**Preferred:**

```python
entries = chain.from_iterable(rows)
```

or a nested comprehension when a concrete private array is actually needed:

```python
entries = [entry for row in rows for entry in row]
```

#### `STY-16`: Nested Cartesian loops -> `itertools.product`

**Bad:**

```python
for a in A:
    for b in B:
        use(a, b)
```

**Preferred:**

```python
from itertools import product
for a, b in product(A, B):
    use(a, b)
```

If `A × B` is itself mathematical data used downstream, use the owned Cartesian-product object rather than `itertools.product`.

#### `STY-17`: Hand-built combinations/permutations -> `itertools`

**Bad:** recursive/index code whose only purpose is to enumerate subsets, fixed-size subsets, tuples, or permutations.

**Preferred:**

```python
from itertools import combinations, combinations_with_replacement, permutations
```

For mathematical finite/infinite combinatorial families, wrap or implement the corresponding owned enumerated set rather than leaking raw tuples as the public object.

#### `STY-18`: Slice-by-loop -> `itertools.islice`

**Bad:**

```python
result = []
for i, x in enumerate(xs):
    if i == n:
        break
    result.append(x)
```

**Preferred:**

```python
from itertools import islice
result = islice(xs, n)
```

Again, materialize only if the consumer actually needs a concrete finite sequence.

#### `STY-19`: Forwarding generator loop -> `yield from`

**Bad:**

```python
def values():
    for value in source:
        yield value
```

**Preferred:**

```python
def values():
    yield from source
```

If there is only a transformation, consider returning a generator expression directly.

#### `STY-20`: Consecutive-pair index arithmetic -> `itertools.pairwise`

**Bad:**

```python
for i in range(len(values) - 1):
    compare(values[i], values[i + 1])
```

**Preferred:**

```python
from itertools import pairwise
for left, right in pairwise(values):
    compare(left, right)
```

This is private finite-sequence syntax; mathematical ordered sets should expose their own adjacency/successor structure where appropriate.

#### `STY-21`: Running prefix accumulation -> `itertools.accumulate`

**Bad:**

```python
total = zero
prefixes = []
for value in values:
    total += value
    prefixes.append(total)
```

**Preferred:**

```python
from itertools import accumulate
prefixes = accumulate(values, initial=zero)
```

Use the mathematical additive operation when Python `+` is not the owned operation.

### Predicate/search patterns

#### `STY-22`: Boolean scan -> `all`

**Bad:**

```python
for x in xs:
    if not predicate(x):
        return False
return True
```

**Preferred:**

```python
return all(predicate(x) for x in xs)
```

#### `STY-23`: Existence scan -> `any`

**Bad:**

```python
for x in xs:
    if predicate(x):
        return True
return False
```

**Preferred:**

```python
return any(predicate(x) for x in xs)
```

#### `STY-24`: Find first matching element -> `next`

**Bad:**

```python
answer = None
for x in xs:
    if predicate(x):
        answer = x
        break
return answer
```

**Preferred:**

```python
return next((x for x in xs if predicate(x)), None)
```

If absence is exceptional, omit the default and let `StopIteration` be converted at the appropriate API boundary.

#### `STY-25`: Count matching elements -> `sum`

**Bad:**

```python
count = 0
for x in xs:
    if predicate(x):
        count += 1
```

**Preferred:**

```python
count = sum(predicate(x) for x in xs)
```

For mathematical cardinality, do not enumerate merely to count; ask the owned set/family for its cardinality.

#### `STY-26`: Manual minimum/maximum tracking -> `min`/`max` with `key=`

**Bad:**

```python
best = None
for candidate in candidates:
    if best is None or score(candidate) < score(best):
        best = candidate
```

**Preferred:**

```python
best = min(candidates, key=score)
```

Use `default=` when the empty case is meaningful and Python's API supports it.

#### `STY-27`: `if condition: return True; return False` -> return the predicate

**Bad:**

```python
if condition:
    return True
return False
```

**Preferred:**

```python
return condition
```

Negate directly when needed: `return not condition`.

### Folding and algebraic accumulation patterns

#### `STY-28`: Additive accumulator -> owned sum/linear combination or `sum`

**Bad:**

```python
total = target.zero()
for label, coefficient in coefficients.items():
    total += target.scalar_multiple(coefficient, basis[label])
return total
```

**Preferred:**

```python
return target.linear_combination(coefficients)
```

If this is plain private Python arithmetic:

```python
return sum(terms, start=zero)
```

A manual accumulator should not reimplement a parent/category operation.

#### `STY-29`: Multiplicative accumulator -> owned product or `reduce`

**Bad:**

```python
result = target.one()
for factor in factors:
    result *= factor
return result
```

**Preferred:**

```python
return target.product(factors)
```

At a plain Python/backend boundary:

```python
from functools import reduce
from operator import mul
return reduce(mul, factors, target.one())
```

#### `STY-30`: Nested bilinear sum -> `sum`/linear-combination abstraction

**Bad:**

```python
total = W.zero()
for i, a in left_coefficients.items():
    for j, b in right_coefficients.items():
        total += a * b * gram(i, j)
return total
```

**Preferred:**

```python
return sum(
    (a * b * gram(i, j)
     for i, a in left_coefficients.items()
     for j, b in right_coefficients.items()),
    W.zero(),
)
```

Better still, when this is evaluation of a represented pairing, call the pairing/Hom object rather than reimplementing coordinate evaluation.

#### `STY-31`: Useless identity-update loop -> delete it

**Bad:**

```python
for label in right.support():
    if left.multiplicity(label) == 0:
        coefficient *= 1
```

**Preferred:** delete the loop.  LLM-generated code often contains semantically inert bookkeeping left over from a more complicated derivation; simplify algebraically before preserving control flow.

### Grouping/counting/mapping patterns

#### `STY-32`: `setdefault(..., []).append(...)` -> `defaultdict(list)`

**Bad:**

```python
grouped = {}
for key, value in pairs:
    grouped.setdefault(key, []).append(value)
```

**Preferred:**

```python
from collections import defaultdict

grouped = defaultdict(list)
for key, value in pairs:
    grouped[key].append(value)
```

If input is already sorted by key and streaming behavior matters, consider `itertools.groupby`.

#### `STY-33`: Manual multiplicity dictionary -> `Counter`

**Bad:**

```python
counts = {}
for label in labels:
    counts[label] = counts.get(label, 0) + 1
```

**Preferred:**

```python
from collections import Counter
counts = Counter(labels)
```

If multiplicity is mathematical structure, prefer the owned multiset/fixed-size-selection object.

#### `STY-34`: Manual default-valued accumulation -> `defaultdict`

**Bad:**

```python
coefficients = {}
for label, value in terms:
    coefficients[label] = coefficients.get(label, zero) + value
```

**Preferred:**

```python
from collections import defaultdict
coefficients = defaultdict(lambda: zero)
for label, value in terms:
    coefficients[label] += value
```

Better still, use the parent's finite-support or `linear_combination` machinery if these are mathematical coefficients.

#### `STY-35`: Manual ordered deduplication -> owned ordered set or `dict.fromkeys` privately

**Bad:**

```python
result = []
for x in xs:
    if x not in result:
        result.append(x)
```

**Preferred mathematical form:** construct the owned ordered set.

For private hashable Python data where first-occurrence order is merely serialization order:

```python
result = list(dict.fromkeys(xs))
```

Do not use a Python sequence as the public representation of a mathematical set.

### Indexing and parallel-iteration patterns

#### `STY-36`: Parallel indexing -> `zip(..., strict=True)`

**Bad:**

```python
for i in range(len(labels)):
    use(labels[i], coefficients[i])
```

**Preferred:**

```python
for label, coefficient in zip(labels, coefficients, strict=True):
    use(label, coefficient)
```

If the two families are mathematically indexed by the same set, prefer that common index set directly instead of positional Python synchronization.

#### `STY-37`: Position counter -> `enumerate`

**Bad:**

```python
i = 0
for value in values:
    use(i, value)
    i += 1
```

**Preferred:**

```python
for i, value in enumerate(values):
    use(i, value)
```

Again, if `i` is mathematically a label rather than incidental Python position, use the owned rank/unrank/index set.

#### `STY-38`: Repeated full index lookup -> precomputed mathematical rank map / owned rank

**Bad:**

```python
for label in labels:
    position = labels_list.index(label)
```

**Preferred:** use the owned ordered set's `rank(label)`, or construct a private `{label: position}` mapping once when crossing into a backend that requires dense positions.

Do not force an infinite or abstract framing into a list merely to gain `.index`.

### Stateful traversal patterns

#### `STY-39`: FIFO worklist -> `collections.deque`

**Bad:**

```python
frontier = [seed]
while frontier:
    x = frontier.pop(0)
    ...
    frontier.append(y)
```

**Preferred:**

```python
from collections import deque
frontier = deque([seed])
while frontier:
    x = frontier.popleft()
    ...
```

#### `STY-40`: Bespoke orbit closure -> action/G-set `orbit`

**Bad:**

```python
seen = {seed}
frontier = deque([seed])
while frontier:
    point = frontier.popleft()
    for g in group_generators:
        image = act(g, point)
        if image not in seen:
            seen.add(image)
            frontier.append(image)
```

**Preferred:**

```python
return action.orbit(seed)
```

or the corresponding GAP/Sage group-action routine behind the owned action API.  If a generic orbit algorithm is missing, implement it once on the G-set/action abstraction.

#### `STY-41`: Bespoke connected-components/reachability -> graph library

**Bad:** local DFS/BFS code whose mathematical input is already a graph.

**Preferred:** use the owned graph object, Sage graph API, or `networkx` operation such as connected components, shortest paths, transitive closure, topological sorting, etc.  Do not maintain generic graph algorithms in a mathematical theory module.

#### `STY-42`: Bespoke group stabilizer/orbit algorithm -> GAP/Sage group backend through owned API

**Bad:** enumerate group action manually to recover an orbit or stabilizer when GAP/Sage already implements it.

**Preferred:**

```python
orbit = G.orbit(x)
stabilizer = G.stabilizer(x)
```

with the implementation delegated through the private group backend.  The preamble presents the group action `lean-categories` formalizes; GAP performs the generic finite-group algorithm.

#### `STY-43`: Genuine fixed-point/search algorithm -> keep explicit loop

Not every `while` should disappear.

**Appropriate:**

```python
changed = True
while changed:
    changed = False
    ...  # one mathematically meaningful closure step
```

when the fixed-point iteration itself is the algorithm and no standard library/upstream routine already owns it.  Use explicit names for state and invariants; do not contort such code into nested `reduce`/lambda expressions.

### Control-flow cleanup patterns

#### `STY-44`: `try`/`except` in mathematical code -> asserted hypotheses and total code

Exception-driven control flow is an engineering pattern, not a mathematical one.  In mathematical code, state the assumptions that make the next construction valid, assert them, and then execute code that is total under those assumptions.

**Bad mathematical code:**

```python
try:
    return optional_construction(X)
except (TypeError, ValueError, AttributeError):
    return fallback(X)
```

**Preferred:**

```python
assert X in CategoryWhereCurrentAlgorithmIsTotal(), (
    "the current implementation assumes ..."
)
return construction(X)
```

If the construction is mathematically defined only on that narrower category, move the method there instead.  `try`/`except` and `contextlib.suppress` remain legitimate inside engineering kernels—backend adapters, parsers, filesystem/network/process interfaces—where the failure is an external protocol event rather than part of the mathematics.

#### `STY-45`: Temporary immediately returned -> direct return

**Bad:**

```python
result = normalize(value)
return result
```

**Preferred:**

```python
return normalize(value)
```

Keep the temporary when its name records a real mathematical intermediate or materially improves readability/debugging.

#### `STY-46`: Nested guard-only `if` -> combined condition

**Bad:**

```python
if x in C:
    if predicate(x):
        return f(x)
```

**Preferred:**

```python
if x in C and predicate(x):
    return f(x)
```

Do not combine conditions when the inner branch represents a distinct mathematical case worth naming.

#### `STY-47`: `if/else` assignment -> conditional expression when both branches are expressions

**Bad:**

```python
if index >= 0:
    name = f"x_{index}"
else:
    name = f"x_m{-index}"
```

**Preferred:**

```python
name = f"x_{index}" if index >= 0 else f"x_m{-index}"
```

#### `STY-48`: Whole-method failure stub -> real implementation cases, `@abstract_method`, or correct placement

A visible mathematical method may legitimately fail on *currently uncomputable instances* of a mathematically meaningful notion. What is forbidden is advertising a method whose implementation contains no successful mathematical case at all.

**Bad deceitful stub:**

```python
def tensor_shape(self):
    assert False, "a tensor supplies the ranks of its indices"
```

or:

```python
def kernel(self):
    raise NotImplementedError
```

These methods expose a name under tab completion but implement no mathematics.

**Preferred for a genuine abstract implementation contract:**

```python
from sage.misc.abstract_method import abstract_method

@abstract_method
def tensor_shape(self):
    ...
```

**Preferred when the notion is only mathematically defined on a narrower category:** put/mix the method only on that category.

**Preferred when the notion is mathematically general but only some cases are currently computable:** keep the method at the mathematically correct owner and implement those cases, with an informative assertion only for the unhandled remainder. A final `assert False, ...` is acceptable *after real implemented cases* as an exhaustiveness/computability fallback; it is not acceptable as the whole implementation.

#### `STY-49`: Mathematical and algorithmic hypotheses -> assert them loudly

Assertions are executable mathematical commentary. Use them liberally to state category membership, finiteness, nondegeneracy, compatibility, shape, parentage, and identities on which the following derivation relies.

**Good proof-context assertions:**

```python
assert lattice in Lattices(R)
assert f.domain() is M
assert result in TargetCategory()
```

**Good algorithm-domain assertion:**

```python
def is_nondegenerate(self):
    assert self in FiniteRankFormedModules(R), (
        "nondegeneracy is currently decidable here only for finite-rank formed modules"
    )
    return self.gram_tensor().determinant() != 0
```

The method remains on the category where nondegeneracy is mathematically meaningful; the assertion states only the narrower domain of the current algorithm.

Do **not** replace these statements by exception-valued mathematical branches. The assertion records the proof/computability context and should fail loudly at the first unmet assumption.

**The message is read only when the assertion fails, and two people read it.** A research
mathematician, who called an operation in a session, must learn from it which mathematical
hypothesis failed and on which object. A coder must learn where the construction went wrong.
So the message states, in the field's words, the object, the hypothesis it failed, and what
the object actually is, formatted from the live values. It is never the invariant restated as
a sentence: a failed assertion printing "the action is on the supplied owned additive group"
reads as a true statement, names nothing, and uses words no mathematician owns. Internal
vocabulary — "native", "presentation", "supplied", "owned", "datum", "realization", private
method names — does not appear in a message.

**Bad:**

```python
assert module in AdditiveGroups().AdditiveCommutative(), "the action is on the supplied owned additive group"
```

**Preferred:**

```python
assert module in AdditiveGroups().AdditiveCommutative(), (
    f"{module} cannot be made an {ring}-module: a module's addition must be commutative, "
    f"but {module} is only known to be in {module.category()}"
)
```

### Representation and DRY patterns

#### `STY-50`: Parallel representation of a canonical object -> reuse the canonical construction

**Bad:** maintain a tensor-based matrix object with its own determinant/rank/kernel API while `M_{m,n}(R)` is already `Hom_R(F_R([n]), F_R([m]))`.

**Preferred:** the matrix is the Hom element.  Put matrix operations on the appropriate Hom/category refinement and delete the parallel representation.

#### `STY-51`: Equivalent universal data implemented independently -> derive one from the other

**Bad:** every adjunction subclass independently implements:

```python
unit(...)
counit(...)
hom_set_isomorphism_forward(...)
hom_set_isomorphism_inverse(...)
```

**Preferred:** choose one authoritative presentation, e.g. unit+counit, and derive the transpose maps generically:

```python
Phi(f) = U(f) * eta_A
Phi_inverse(g) = epsilon_B * F(g)
```

Do not spend hundreds of lines maintaining mathematically forced coherence by hand.

#### `STY-52`: Duplicate additive object implementation -> reuse/refine the existing additive construction

**Bad:** implement a second class with its own normalization, homogeneous components, addition, negation, scalar multiplication, equality, and display when it is already a graded direct sum with extra multiplication.

**Preferred:** use the existing graded-direct-sum parent/element as the additive/module object and refine/equip it with the additional algebra structure.

#### `STY-53`: Repeated parameterized-category boilerplate -> common parameterized base

**Bad:** several categories each repeat:

```python
@staticmethod
def __classcall_private__(cls, base_ring, group): ...
def __init__(self, base_ring, group): ...
def base_ring(self): ...
def acting_group(self): ...
```

**Preferred:** factor the common `(R, G)`-parameterized category abstraction once and derive `GroupModules`, `GroupLattices`, chosen-finite variants, etc. from it.

#### `STY-54`: Same algorithm in method and functor -> one canonical operation, functor delegates

**Bad:** `M.base_change(S)` and `ScalarExtensionFunctor._apply_object(M)` independently rebuild the same transported action/presentation.

**Preferred:** one is authoritative:

```python
class ScalarExtensionFunctor(...):
    def _apply_object(self, M):
        return M.base_change(self.target_ring())
```

or conversely the object method delegates to the functor if the functor is the mathematical owner.  There must be one implementation.

#### `STY-55`: Theory-local identity cache -> shared memoization/`UniqueRepresentation`

**Bad:**

```python
_MODULE_TENSOR_PRODUCT_CACHE = {}
_POWER_CACHE = {}
_FORM_SPACE_CACHE = {}
```

with custom `id(...)` keys and stale-entry checks in each file.

**Preferred:** `cached_function`, `cached_method`, `UniqueRepresentation`, or one shared identity-sensitive memoization helper with explicit lifetime semantics.

#### `STY-56`: Hand-written generic utility already in stdlib/dependency -> import it

**Bad:** local implementations of graph traversal, topological sort, union-find, memoization, flattening, pairwise traversal, combinations, queues, grouping, or multidispatch.

**Preferred:** use `itertools`, `collections`, `functools`, Sage/networkx, GAP, OSCAR/Singular, or another mature dependency.  Adding a dependency is preferable when it deletes substantial generic machinery and has a better semantic fit.

### Backend and boundary patterns

#### `STY-57`: Cross-backend ping-pong -> one crossing around the complete computation

**Bad:**

```python
A_engine = to_engine(A)
B_engine = engine_step_one(A_engine)
B = from_engine(B_engine)
C_engine = to_engine(B)
D_engine = engine_step_two(C_engine)
return from_engine(D_engine)
```

**Preferred:**

```python
return from_engine(adapter.complete_algorithm(to_engine(A)))
```

When practical, implement the multi-stage routine natively in Singular/Julia/OSCAR/GAP/etc. and return only the final data needed to reconstruct the owned result.

#### `STY-58`: Backend workspace leaks into mathematical code -> private adapter owns it

**Bad:** several mathematical modules directly read `_engine`, construct engine matrices, and continue computation on engine elements.

**Preferred:** one private adapter converts owned inputs, computes, and crosses back.  Ordinary mathematical consumers never receive or manipulate backend parents/elements.

#### `STY-59`: Python loops serialize every intermediate backend object -> batch/native engine operation

**Bad:** repeatedly cross individual rows/elements in a Python loop when the backend accepts a matrix/family and can execute the whole reduction internally.

**Preferred:** serialize the finite input once, invoke one engine routine, deserialize the final result once.

### Laziness and mathematical collections

#### `STY-60`: Eager `list`/`tuple` just to iterate -> iterate the owned collection

**Bad:**

```python
labels = tuple(M.module_generating_set())
for label in labels:
    ...
```

**Preferred:**

```python
for label in M.module_generating_set():
    ...
```

Use `rank`/`unrank`, indexed families, or finite support when positional access is mathematically required.  Materialize only in a private backend serializer after finiteness and order are established.

#### `STY-61`: Eager intermediate list -> generator pipeline

**Bad:**

```python
rows = [transform(x) for x in xs]
nonzero = [row for row in rows if any(row)]
return backend(nonzero)
```

**Preferred:**

```python
rows = (transform(x) for x in xs)
return backend(row for row in rows if any(row))
```

provided the backend/consumer can stream.  Do not create Python containers that have no mathematical identity and exist only to feed the next expression.

#### `STY-62`: Enumerate to decide cardinality/finiteness -> use cardinality/category

**Bad:**

```python
items = list(S)
return len(items)
```

**Preferred:**

```python
return S.cardinality()
```

or dispatch from the appropriate finite/infinite category.  Enumeration is not a proof of finiteness and may be impossible for a perfectly valid infinite object.

### String/display and small-expression patterns

#### `STY-63`: Append strings then concatenate -> comprehension + `join`

**Bad:**

```python
terms = []
for label in support:
    terms.append(format_term(label))
return " + ".join(terms)
```

**Preferred:**

```python
return " + ".join(format_term(label) for label in support)
```

#### `STY-64`: Repeated membership normalization loop -> constructor/comprehension when semantics are simple

**Bad:**

```python
normalized = []
for x in xs:
    x = normalize(x)
    if x:
        normalized.append(x)
```

**Preferred:**

```python
normalized = [y for x in xs if (y := normalize(x))]
```

Use this only when the assignment expression improves clarity; otherwise use a small helper plus comprehension.  If normalization has multiple semantic branches or mathematical assertions, retain explicit code rather than obscuring those hypotheses inside an expression.

#### `STY-65`: Repeated `.get(key, zero) + value` -> finite-support abstraction or `defaultdict`

**Bad:**

```python
result[key] = result.get(key, zero) + value
```

repeated throughout an algorithm.

**Preferred:** use the object's finite-support coefficient type.  At a private Python layer:

```python
result = defaultdict(lambda: zero)
result[key] += value
```

#### `STY-66`: Empty mutable accumulator immediately followed by a loop -> classify before accepting

The shapes `result = []`, `result = {}`, and `result = set()` immediately before an iteration are **review triggers**.  They are not automatically wrong, but they very often mean Python is being used to spell map/filter/group/fold semantics manually.

**Red flags:**

```python
result = []
for x in xs:
    ...

result = {}
for x in xs:
    ...

result = set()
for x in xs:
    ...
```

Before keeping the loop, classify the mutation:

```text
append(f(x))                 -> comprehension / map / owned image
conditional append           -> filtered comprehension / filter
extend(f(x))                 -> chain.from_iterable
add(f(x))                    -> set comprehension / owned set
d[key] = f(x)                -> dict comprehension
d[key] += value              -> defaultdict / Counter / finite-support sum
acc += term                  -> sum / linear_combination / owned fold
acc *= factor                -> product / math.prod / reduce / owned fold
queue append + pop-left      -> deque or higher traversal API
```

If none of these describe the mutation because the evolving state is the algorithm, keep the explicit state machine.

#### `STY-67`: Raw `for x in xs` -> first test map/filter/fold/quantifier/traversal forms

Every new explicit `for` loop in ordinary transformation code is a review trigger.  First ask whether the body is one of the standard forms catalogued here.

**Bad default:**

```python
for x in xs:
    result.append(f(x))
```

**Preferred:**

```python
result = [f(x) for x in xs]
```

The same trigger applies to `for key, value in mapping.items()`, nested `for` loops, and loops over mathematical generating sets.  The explicit loop is appropriate when the iteration carries genuine mutable state, early multi-branch control flow, backtracking, a protocol, or another algorithm whose transitions are the point.

#### `STY-68`: Raw `while` -> require a genuine evolving-state invariant

A `while` loop should normally correspond to a stateful algorithm: fixed point, worklist search, backtracking, iterative refinement, parsing/protocol state, or backend iteration.

**Suspicious:**

```python
while i < len(xs):
    consume(xs[i])
    i += 1
```

**Preferred:**

```python
for x in xs:
    consume(x)
```

**Legitimate:**

```python
while frontier:
    state = frontier.popleft()
    ...
```

provided the search itself is not already owned by a graph/action/group abstraction or dependency.

#### `STY-69`: `.append(...)` inside a loop -> comprehension, filter, or owned image

Treat `.append(...)` inside an ordinary `for` loop as a specific red flag.

**Bad:**

```python
rows = []
for relation in relations:
    rows.append(transform(relation))
```

**Preferred:**

```python
rows = [transform(relation) for relation in relations]
```

If the result is consumed once, prefer the lazy form:

```python
rows = (transform(relation) for relation in relations)
```

If the values form a mathematical image/family/set, construct that owned object instead of a Python list.

#### `STY-70`: `.extend(...)` inside a loop -> `chain` / `chain.from_iterable`

**Bad:**

```python
flat = []
for block in blocks:
    flat.extend(block)
```

**Preferred:**

```python
from itertools import chain
flat = chain.from_iterable(blocks)
```

For a fixed small number of iterables:

```python
flat = chain(left, middle, right)
```

Materialize with `list(...)` only at a private finite serialization boundary.

#### `STY-71`: `.add(...)` inside a loop -> set comprehension / set constructor

**Bad:**

```python
seen_types = set()
for C in categories:
    seen_types.add(type(C))
```

**Preferred:**

```python
seen_types = {type(C) for C in categories}
```

If the set is mathematical, use the owned set construction rather than Python `set`.

#### `STY-72`: `result[key] = expression` in a simple loop -> dict comprehension

**Bad:**

```python
images = {}
for label in labels:
    images[label] = f(label)
```

**Preferred:**

```python
images = {label: f(label) for label in labels}
```

If each key is assigned more than once, this is no longer a simple dict-construction pattern; use the grouping/accumulation rules instead.

#### `STY-73`: `acc += term` inside a loop -> sum/fold/owned additive operation

**Bad:**

```python
total = zero
for term in terms:
    total += term
```

**Preferred for ordinary additive values:**

```python
return sum(terms, start=zero)
```

**Preferred for module coefficients:**

```python
return M.linear_combination(coefficients)
```

Do not force Python `sum` when the mathematical parent has a more informative finite-sum or linear-combination operation.

#### `STY-74`: `acc *= factor` inside a loop -> owned product, `math.prod`, or `reduce`

**Bad:**

```python
product = one
for factor in factors:
    product *= factor
```

**Preferred when the mathematical parent owns the product:**

```python
return parent.product(factors)
```

**Preferred for ordinary numeric scalars:**

```python
from math import prod
return prod(factors, start=one)
```

**Preferred for arbitrary Python objects with associative multiplication but no owner fold:**

```python
from functools import reduce
from operator import mul
return reduce(mul, factors, one)
```

Use `math.prod` rather than `reduce(mul, ...)` for ordinary numbers.  Use the owned mathematical product rather than either Python form when it exists.

#### `STY-75`: `.get(key, zero) + value` / repeated coefficient mutation -> finite-support abstraction first

**Bad:**

```python
coefficients = {}
for key, value in terms:
    coefficients[key] = coefficients.get(key, zero) + value
```

**Preferred mathematical form:** use the repository's finite-support/linear-combination object.

**Private Python fallback:**

```python
from collections import defaultdict
coefficients = defaultdict(lambda: zero)
for key, value in terms:
    coefficients[key] += value
```

For integer multiplicities, use `Counter` instead.

#### `STY-76`: `setdefault(key, []).append(value)` -> `defaultdict(list)`

**Bad:**

```python
grouped = {}
for key, value in pairs:
    grouped.setdefault(key, []).append(value)
```

**Preferred:**

```python
from collections import defaultdict
grouped = defaultdict(list)
for key, value in pairs:
    grouped[key].append(value)
```

If the input is already sorted by the grouping key and streaming behavior is useful, consider `itertools.groupby` instead.

#### `STY-77`: Sorted streaming grouping -> `itertools.groupby`

**Bad:**

```python
# hand-maintain current_key/current_bucket while walking sorted records
```

**Preferred:**

```python
from itertools import groupby
for key, group in groupby(records, key=key_function):
    consume_group(key, group)
```

`groupby` groups adjacent equal keys; sort first only when sorting is mathematically/algorithmically appropriate.  For unsorted accumulation, `defaultdict` is usually the correct tool.

#### `STY-78`: Repeated integer counting -> `Counter` / `Counter.update`

**Bad:**

```python
counts = {}
for label in labels:
    counts[label] = counts.get(label, 0) + 1
```

**Preferred:**

```python
from collections import Counter
counts = Counter(labels)
```

For repeated batches:

```python
counts.update(more_labels)
```

Use an owned multiset when multiplicity is mathematical data in the public preamble.

#### `STY-79`: Named pure transformation -> `map`; named predicate -> `filter`

Use `map` and `filter` when they expose an already named operation directly; use comprehensions when the expression or condition is clearer inline.

**Verbose:**

```python
normalized = []
for x in xs:
    normalized.append(normalize(x))
```

**Concise:**

```python
normalized = map(normalize, xs)
```

**Verbose:**

```python
finite = []
for x in xs:
    if is_finite(x):
        finite.append(x)
```

**Concise:**

```python
finite = filter(is_finite, xs)
```

Do not wrap `list(...)` around these merely by habit; retain laziness unless a concrete sequence is actually required.

#### `STY-80`: Tuple-unpacking transformation -> `itertools.starmap` when clearer

**Bad:**

```python
values = (f(a, b) for a, b in pairs)
```

**Alternative when `f` is already named and the tuple-unpacking is the only syntax:**

```python
from itertools import starmap
values = starmap(f, pairs)
```

Prefer the generator expression when it is more readable.  The point is to recognize the standard higher-order iterator rather than build a helper loop.

#### `STY-81`: Fixed-size chunking loop -> `itertools.batched`

**Bad:**

```python
batch = []
for x in xs:
    batch.append(x)
    if len(batch) == n:
        yield tuple(batch)
        batch.clear()
```

**Preferred:**

```python
from itertools import batched
yield from batched(xs, n)
```

Use `strict=True` when an incomplete final batch is invalid.

#### `STY-82`: Repeated constant values -> `itertools.repeat`

**Bad:**

```python
values = (zero for _ in range(n))
```

**Preferred:**

```python
from itertools import repeat
values = repeat(zero, n)
```

Use this only for immutable values or when sharing the repeated object is intended.

#### `STY-83`: Manual running index paired with values -> `enumerate`; two streams -> strict `zip`

**Bad:**

```python
i = 0
for value in values:
    consume(i, value)
    i += 1
```

**Preferred:**

```python
for i, value in enumerate(values):
    consume(i, value)
```

For two logically equal-length streams:

```python
for left, right in zip(lefts, rights, strict=True):
    ...
```

Do not silently truncate mathematical data with plain `zip` when equal cardinality is part of the contract.

#### `STY-84`: Manual list concatenation with `+` in a loop -> `chain`; repeated string `+=` -> `join`

**Bad:**

```python
result = []
for block in blocks:
    result = result + block
```

**Preferred:**

```python
from itertools import chain
result = chain.from_iterable(blocks)
```

**Bad:**

```python
text = ""
for part in parts:
    text += part
```

**Preferred:**

```python
text = "".join(parts)
```

#### `STY-85`: Manual product/sum of a transformed family -> generator directly into the fold

Do not build a temporary list just to fold it.

**Bad:**

```python
terms = [weight(x) * value(x) for x in xs]
return sum(terms, start=zero)
```

**Preferred:**

```python
return sum((weight(x) * value(x) for x in xs), start=zero)
```

For ordinary numeric products:

```python
from math import prod
return prod((weight(x) for x in xs), start=one)
```

Again, an owned `linear_combination` or `product` outranks the Python fold when the family belongs to a mathematical parent.

#### `STY-86`: Multiple simple stages -> lazy generator pipeline, not repeated materialization

**Bad:**

```python
mapped = [normalize(x) for x in xs]
filtered = [x for x in mapped if valid(x)]
keys = [key(x) for x in filtered]
```

**Preferred:**

```python
mapped = map(normalize, xs)
filtered = filter(valid, mapped)
keys = map(key, filtered)
```

or a readable generator pipeline.  Materialize only the stage whose concrete sequence semantics are actually required.

#### `STY-87`: Collection-building loop with no mutation except construction -> assume a declarative replacement exists

The general red flag is:

```python
result = <empty collection>
for x in xs:
    result.<single construction mutation>(...)
return result
```

Before accepting it, prove that it is *not* one of:

- list/set/dict comprehension;
- `map` / `filter`;
- `chain` / `chain.from_iterable`;
- `defaultdict` / `Counter`;
- `sum` / `math.prod` / `reduce`;
- `any` / `all` / `next` / `min` / `max`;
- an owned set/image/family/linear-combination/product;
- a graph/action/group traversal already implemented elsewhere.

This is deliberately a review trigger because this exact “walk and accrue” pattern is heavily overproduced by generated code.

### Current live-tree exemplars behind the catalogue

The catalogue above is not hypothetical.  These are concrete patterns already observed in the current preamble; they serve as regression examples for future review.

| Current case | What is wrong | Preferred direction | Catalogue |
| --- | --- | --- | --- |
| `categories/abstract_categories/constructions.py`: global `Product`, `Coproduct`, `TensorProduct`, `Subobjects`, `Kernel`, `Cokernel`, `Pushout`; `rings/commutative_algebra.py`: global `Localization`, `PrimeLocalization`, `QuotientRing` | Free-standing operations force callers to know a global language and force implementation to rediscover mathematical ownership.  Each of these has an owner in argument position | Put the construction on the category/object/Hom/morphism that owns it; operator notation may delegate there, a named global may not | `ARC-12`, `STY-01`–`04` |
| `abstract_categories/arrow_categories.py::_morphisms_agree` | Root helper knows schemes, finite sets, groups, and modules to decide arrow equality | Homset/category owns extensional equality | `STY-02`, `05` |
| `tensors/tensor.py` determinant/rank/solve/kernel/trace/row/transpose/inverse methods | A type-(1,1) tensor is being used as a second matrix/linear-map representation | `M_{m,n}(R)=Hom_R(F_R([n]),F_R([m]))`; matrix operations live on that Hom refinement | `STY-50` |
| `categories/forms/forms.py` represented `PairingSpace`/`BilinearFormSpace` hierarchy | Parallel Hom-like representation remains after tensor products exist | Represented pairing is literally `Hom_R(X tensor Y, W)`; quadratic maps use the appropriate universal square where represented | `STY-50`–`52` |
| `functors/core.py::Adjunction` and its subclasses | Unit, counit, forward transpose, and inverse transpose are independently implemented despite determining each other | Choose one standard presentation and derive the rest by the adjunction formulas | `STY-51` |
| `ContravariantFunctor` / `Bifunctor` in `functors/core.py` | Reimplement ordinary functor cache/validation for structures already represented by opposite/product categories | Thin convenience interface over `Functor(C.op(),D)` / `Functor(C×D,E)` | `STY-51`, `54` |
| functor modules attaching `_preamble_*_source_*` attributes | Chosen preimages/provenance are hidden side channels | Explicit functor-image/chosen-preimage object, or derive maps from unit/counit | `STY-07` |
| `schemes.py` `_preamble_coordinate_algebra_morphism` and related attached structure | Affine-Spec contravariance/provenance is reconstructed by side-channel metadata | Actual `Spec` functor and scheme Hom whose pullback is intrinsic | `STY-07`, `17` |
| `rings.py::_refine_canonical_self_module_and_algebra` | Canonical structure can depend on import success and later lookups | Deterministic structure/category packet independent of import history | `STY-08` |
| pervasive `refine(...)` calls that mutate classes/state after construction | Runtime refinement can become a second history-dependent object system | Stable implementation/category structure; refinement only for genuinely established mathematical structure | `STY-08`, `18` |
| `PowerAlgebraElement` versus `GradedDirectSumElement` | Same additive/module implementation repeated in a richer object | Reuse the graded direct sum and add algebra multiplication/unit structure | `STY-52` |
| `GroupModules`, finite/free/presented group-module categories, `GroupLattices` | Same `(R,G)` canonicalization/storage/accessors repeated | Common parameterized category abstraction | `STY-53` |
| `GroupModuleHomset` / `GradedModuleHomset` assignments from `ModuleHomset` | Manual inheritance by method grafting | Common Hom implementation/category inheritance | `STY-06` |
| group-module `base_change` versus scalar-extension functor | Same action-transport algorithm implemented twice | One canonical base-change implementation; functor/object method delegates | `STY-54` |
| `_MODULE_TENSOR_PRODUCT_CACHE`, `_MODULE_POWER_CACHE`, form/Kähler/de Rham/etc. caches | Every theory invents identity/lifetime semantics | Shared identity memoization, `UniqueRepresentation`, `cached_function`/`cached_method` where correct | `STY-55` |
| Fourier/Hermite/Laurent/sinc enumerated-function parents | Same infinite indexed-parent implementation repeated | One indexed-symbol/indexed-function-set abstraction | `STY-52`, `56` |
| `_singular_presentation_kernel` | Python orchestrates a long multi-stage Singular workflow | Native/batched Singular routine behind one adapter crossing | `STY-57`–`59` |
| torsion-form orbit/stabilizer code | Specialized theory directly performs GAP orbit/stabilizer work despite owned action infrastructure | Action/G-set orbit/stabilizer API delegating privately to GAP | `STY-40`–`42`, `57`–`59` |
| `forms.py::_coordinate_values` nested `total += ...` | Hand-written finite bilinear sum | Pairing/Hom evaluation or declarative finite sum | `STY-28`, `30`, `73` |
| `sparse_free_algebras.py::_multiply_in_target` | `result=one; for factor: result *= factor` is pure fold boilerplate | Parent-owned product, otherwise `reduce`; `math.prod` for ordinary numbers | `STY-29`, `74` |
| `modules/powers.py::_divided_product_coefficient` | Manual product fold plus a second loop that only multiplies by `1` | Owned/numeric product fold; delete algebraically inert loop | `STY-29`, `31`, `74` |
| `lattices.py::decomposition_names` | `names=[]; ... names.extend(...)` flattening | Lazy owned family or `chain.from_iterable` at a private Python layer | `STY-14`, `60`, `70` |
| profinite embedding filters | `compatible=[]; for candidate: if all(...): append(candidate)` | filtered comprehension/generator or `filter` | `STY-10`, `22`, `69`, `79` |
| `schemes.py::refine_scheme` category-type accumulation | `set(); for ...: add(type(...))` | set comprehension, subject to broader refinement redesign | `STY-12`, `71` |
| multiple `setdefault(...).append(...)` / `.get(...)+...` coefficient/grouping sites | Repeated generic grouping/accumulation machinery | `defaultdict`, `Counter`, or owned finite-support object | `STY-32`–`34`, `65`, `75`–`78` |
| multiple frontier/seen loops in G-sets, orthogonal quotients, discriminant modules | Generic traversal/orbit machinery is repeatedly open-coded | owned action/G-set/graph operation or mature traversal dependency; explicit loop only if algorithm is genuinely special | `STY-39`–`43`, `68` |
| `assert False` stubs in tensor methods | A visible method is being used as a deceitful placeholder rather than a mathematical promise | Sage `@abstract_method` for a genuine abstract contract, or remove/move the method if it is not defined there | `STY-48` |
| finite-rank/nondegeneracy/category-containment assertions | These loudly record the proof context of an implementation | **Keep/add informative assertions**; move the method only when the operation itself belongs to a narrower mathematical category | `STY-49` |
| `preamble/utilities.py` helpers such as `lmap`/`lzip` have no backend callers | Internal-use grep does not measure a REPL/notebook preamble API | Preserve deliberate session conveniences and ensure they are actually exported/tested as session vocabulary | `STY-88` |

These examples are evidence for the general rules, not a finite whitelist.  When the same code shape appears elsewhere, apply the rule without waiting for that file to be named here.

#### `STY-88`: No internal callers does not imply dead code on a session surface

This repository is a research preamble.  Names may exist specifically so they are available interactively in notebooks and REPL sessions; such functions can correctly have zero call sites in `src/` and `tests/`.

**Bad review heuristic:**

```text
rg finds no internal calls to lmap/lzip -> delete them as dead code
```

**Preferred:** determine whether the name is deliberate session vocabulary.  If it is, ensure it is exported by `preamble.all`, has obvious stable semantics, and is exercised as part of the session surface.  Internal call graphs measure implementation reuse, not interactive usefulness.

Thin wrappers are therefore judged by **session ergonomics**, not by whether backend code calls them.  `lmap(f, xs)` and `lzip(xs, ys)` can be legitimate preamble conveniences precisely because their meanings are obvious and they save repetitive REPL typing.

#### `STY-89`: Method visibility follows mathematical definability, not current decidability

A method visible under tab completion says: **`lean-categories` defines this notion for this object**. It does *not* promise that the CAS can decide or compute it for every represented instance today.

Canonical example: a set such as

```python
X = {n in NN | n.is_twin_prime()}
```

unquestionably has a cardinality. Hiding `cardinality()` behind a fictional `SetsWithComputableCardinality` category would misstate the mathematics. A user may reasonably encounter an assertion explaining that the current algorithm does not cover this representation.

Likewise `is_nondegenerate()` belongs on formed modules/lattices where nondegeneracy is a defined property, even if an infinite-rank callable form is outside today's decision procedures.

The long-term goal is **hope matches reality**: every mathematically natural method is visible where it belongs, common cases compute correctly, unsupported computational cases fail immediately and informatively, and the implemented case family expands over time.

Never use `NotImplementedError` as the fallback. Never expose a method whose only behavior is failure.

#### `STY-90`: Computability routing may use explicit mathematical case tables

Most switchboards that rediscover category ownership are architectural smells. Computational routing *within an already correctly owned mathematical method* is different and often desirable.

**Good shape:**

```python
def cardinality(self):
    match self:
        case FiniteEnumeratedSet():
            return NN(self._known_size())
        case IntervalIntersectionSet():
            return self._interval_cardinality()
        case RecursivelyEnumerableSet() if self._enumeration_terminates():
            return self._enumerated_cardinality()
        case _:
            assert False, (
                "cardinality is mathematically defined for every set, but the current "
                "implementation has no algorithm for this represented case"
            )
```

The exact cases/algorithms must reflect real repository mathematics; the point is the architecture. The method is owned by `Sets`, implemented on genuine supported cases, and the final assertion documents the current computational frontier.

When static typing genuinely makes the final branch `Never`, prefer `typing.assert_never` as the exhaustiveness marker. When the runtime category/representation partition is not statically expressible, an informative final `assert False, ...` is reasonable here. The distinction from a stub is that preceding branches implement real mathematics.

Similarly:

```python
def is_nondegenerate(self):
    match self:
        case FiniteRankRepresentedForm():
            return self.gram_tensor().determinant() != 0
        case _:
            assert False, (
                "nondegeneracy is currently decidable only for represented finite-rank forms"
            )
```

Prefer specialized subcategory overrides when they give a cleaner implementation, but do not move the *mathematical notion* into a fake computability category merely because one algorithm is partial.

Mathematical code still avoids exception-driven fallback, `hasattr` probing, and try/catch routing. Engineering adapters may catch external failures; the mathematical layer routes by declared mathematical representation/category and asserts the unsupported remainder.

### Finitary-overfitting and semantic-lowering patterns

#### `STY-91`: Eagerly materialize a mathematical family -> keep the owned set/family lazy

**Red flag:**

```python
labels = tuple(M.module_generating_set())
generators = list(G.group_generators())
objects = tuple(C.object(x) for x in C.object_set())
```

The coercion silently changes "this mathematical family exists" into "this family can be exhausted now."  That is a much stronger assumption and often the source of infinite-case blast radius.

**Preferred:** keep the owned set/indexed family itself and use iteration, membership, `cardinality`, `rank`/`unrank`, finite support, images, or lazy enumeration as needed.  If a backend requires a finite array, assert the required finiteness and serialize at that private boundary only.

Concrete smell: `DiscreteCategory.objects()` must not turn an arbitrary enumerable object set into a tuple; the objects of a discrete category are the owned image of its object set, which can be infinite.

#### `STY-92`: Finite-support elements -> do not require a finite indexing set

Many mathematical objects have **finite support over an infinite family**.  Do not confuse these two notions.

**Bad:**

```python
def FormalDivisorGroup(R, prime_divisors):
    return FreshFreeModuleOn(R, finite_ordered_set(prime_divisors))
```

if the intended divisor group is the free module on an arbitrary set of prime divisors.  Individual divisors have finite support; the set of possible prime divisors need not be finite.

**Preferred:** the parent is free on the owned prime-divisor set; each divisor element stores only its finite support.  The same principle applies to free modules, group rings, sparse polynomials, formal sums, configurations, and indexed families.

#### `STY-93`: Raw matrix rows/columns implement a theorem -> ask the semantic mathematical objects instead

Rows, columns, basis matrices, and coordinate vectors are representations.  If the theorem can be stated without coordinates, the implementation should be stated that way too.

**Bad:**

```python
image_rows = matrix_of(d1).row_module()
relation_rows = presentation_matrix(M).row_module()
return image_rows == relation_rows
```

**Preferred:**

```python
return d1.image() == augmentation.kernel()
```

with subobject/Hom equality owning whatever finite-coordinate algorithm is presently available.  This allows future infinite-case equality algorithms without rewriting `FreeResolution.is_exact()`.

#### `STY-94`: Assemble block matrices by hand -> construct the block morphism on biproducts/direct sums

**Bad:** concatenate row arrays, slice columns, or call a matrix `stack` operation to represent a map

\[
A_1\oplus A_2 \longrightarrow B_1\oplus B_2.
\]

**Preferred:** construct the morphism from its four components

\[
f_{ij}:A_j\to B_i
\]

through the Hom/biproduct API.  A finite matrix backend may realize this as a block matrix privately.  The public object remains a morphism between biproducts, so the same construction can represent an infinite block family or a formal block Hom without changing consumers.

#### `STY-95`: Compute cohomology from kernel basis matrices -> `ker/im/quotient` semantics

**Bad:** build lift matrices, take a backend right kernel, choose a basis matrix, project rows, append denominator rows, re-coordinate them, and finally synthesize a presentation.

**Preferred mathematical definition:**

```python
cycles = d_n.kernel()
boundaries = d_previous.image()
return cycles.quotient(boundaries)
```

or the corresponding subobject/quotient construction already owned by the complex.  A finite-presentation backend may optimize this entire construction, but it belongs behind `kernel`, `image`, subobject inclusion, and quotient.  `Cohomology` should not know row orientation or basis-matrix conventions.

#### `STY-96`: Compute an intersection/preimage from kernel rows -> categorical pullback/kernel

The current coordinate identity may be correct while still being the wrong abstraction.

**Bad:** form matrices for inclusions, stack `(i,-j)`, compute a left kernel, extract half the coordinates, turn its rows back into generators.

**Preferred:** the intersection of subobjects is the pullback of their inclusions; the inverse image of `S -> N` along `f:M->N` is the pullback of `f` and the inclusion, equivalently the appropriate kernel construction when additive structure is available.  Construct that pullback/kernel as a subobject.  Let the finite-free Hom implementation choose the matrix algorithm privately.

Concrete current sites: `modules/subobjects.py::intersection` and `functors/subobject_images.py::_inverse_image_subobject` already describe this universal property in comments but then drop to raw rows.

#### `STY-97`: Invariants/coinvariants require finite generators -> use the action's equalizer/coequalizer semantics

**Bad:** require a chosen finite group generating set, build one kernel for every generator, intersect them, or build all relations `(g,m) -> gm-m` from a finite Cartesian product of generator sets.

**Preferred:** `M^G` is the fixed-point/equalizer subobject of the action; `M_G` is the corresponding coequalizer/quotient.  The action object owns these constructions.  A finitely generated group gives a convenient finite algorithm, but finite generation must not define the existence or public shape of invariants/coinvariants.

This also avoids the blast radius when `G` is infinitely generated but represented by a stronger action theorem/backend.

#### `STY-98`: Exhaustively test every element to recognize structure -> structural maps/theorems first, finite exhaustion only as a fallback case

**Bad default:** enumerate every element of a finite underlying set and every scalar, then test all triples to decide associativity/module laws or enumerate every element to compute an annihilator.

**Preferred:** express the structure by the mathematical maps that make the law meaningful and use structural algorithms.  For a module, the scalar action is `rho:R -> End(M)`; for the annihilator, use the kernel/ideal of the scalar-action morphism where represented.  An exhaustive finite check can remain one explicit computability case in a routing table, but must not become the ontology or the only architecture.

Concrete smell: `GeneralModuleParent.annihilator()` currently enumerates the scalar ring and entire module; `_verify_module_laws_when_decidable()` performs cubic scans of the underlying set.  Those are acceptable finite diagnostics/fallbacks, not the general mathematical implementation strategy.

#### `STY-99`: Return `tuple`/`list` for a mathematical set/family -> return an owned set/family or lazy enumeration

**Bad:**

```python
def roots_of_square(...):
    return tuple(...)

def vector_orbit_representatives(...):
    return tuple(representatives)
```

unless the Python tuple is explicitly private serialization.

**Preferred:** return the relevant owned finite set, ordered set, indexed family, orbit-representative set, or lazy enumerated set.  Finiteness is a property of that mathematical collection, not a reason to replace it by a Python sequence.

#### `STY-100`: Presentation matrix is an implementation of a presented object, not the object itself

A chosen finite presentation legitimately has a finite matrix realization.  The error is letting ordinary mathematical consumers treat that matrix as the only interface to the presentation.

**Bad:** consumer code calls `.rows()`, slices columns, counts row lengths, takes row modules, and reconstructs subobjects manually.

**Preferred:** consumers ask for the presentation morphism, its image/kernel/cokernel, its relation subobject, base change, or the corresponding universal construction.  The presentation subsystem may use a matrix internally when the chosen framings are finite.

#### `STY-101`: Fiber/rank/minimal-generators via hand-specialized relation matrix -> construct the fiber/residue module and ask it

**Bad:** specialize every relation row modulo a prime/maximal ideal, build a backend matrix, compute its rank, then subtract from a generator count inside `fiber_dimension()` or `minimal_number_of_generators()`.

**Preferred:**

```python
fiber = M.fiber(p)
return fiber.dimension()
```

and for a local ring use `M.residue_module().dimension()` as Nakayama dictates.  The vector-space/presented-module implementation may compute that dimension by matrix rank privately.  This keeps localization, base change, residue fields, and dimension as the semantic spine.

#### `STY-102`: Verify structure by checking every pair of chosen basis generators -> verify the structure morphism

**Bad:** for every chosen group generator and every pair of lattice generators, compare all pairings to verify that an action preserves the form.

**Preferred:** the action is a morphism

\[
G \longrightarrow \operatorname{Aut}(L,b)
\]

or its image maps are verified by the formed-module Hom/automorphism category.  Form preservation is equality/commutation of the correlation/form morphism, not a nested finite basis loop.  A finite Gram check may be the implementation of that Hom predicate, but callers should not know it.

Concrete current site: `group_modules/group_lattices.py::GroupLattice` explicitly assumes finite rank and finite group generation solely to run this exhaustive check.

#### `STY-103`: Coordinate/numeric algorithm appears above the semantic owner -> push it down behind the owner

Use this as the general review test.  If code in cohomology, exactness, lattice structure, group actions, subobjects, or geometry manipulates raw `rows`, `columns`, `basis_matrix`, flattened entries, or coordinate vectors, ask whether that numeric code belongs instead in the Hom/module/tensor/subobject/backend operation it is trying to compute.

**Preferred layering:**

```text
mathematical consumer
    -> semantic operation (kernel/image/pullback/product/dimension/...)
        -> category/representation-specific algorithm
            -> finite coordinates / matrix / CAS backend
```

not:

```text
mathematical consumer
    -> rows/columns/coordinates
        -> manually reconstruct the semantic result
```

The latter makes every consumer finite-coordinate-aware and gives infinite generalization a repository-wide blast radius.

#### `STY-104`: `morphism -> matrix -> nullspace -> rebuilt submodule` -> `morphism.kernel()`

This is a canonical LLM over-lowering pattern.

**Bad:**

```python
A = f.matrix()
rows = A.right_kernel().basis_matrix().rows()
K = FreeModule(R, len(rows))
inclusion = ...  # rebuild the vectors as elements of f.domain()
return K, inclusion
```

**Preferred:**

```python
return f.kernel()
```

The kernel implementation owns coordinate algorithms and returns an honest subobject/inclusion. A caller that only needs the kernel never sees a matrix.

#### `STY-105`: Numerical criterion for a structural predicate -> spell the mathematical definition

**Bad:**

```python
def is_primitive(i):
    A = i.matrix()
    return gcd(maximal_minors(A)) == 1
```

**Preferred:**

```python
def is_primitive(i):
    return i.cokernel().is_torsion_free()
```

Similarly, prefer `f.kernel().is_zero()` to rank comparison for injectivity, the correlation morphism to determinant tests for nondegeneracy, and `correlation.is_isomorphism()` to determinant-unit tests for unimodularity. Numerical criteria belong inside the implementations of these semantic predicates, where their hypotheses can be routed correctly.

#### `STY-106`: Consumer extracts coordinates because the semantic operation is missing -> add the semantic operation first

**Bad development behavior:**

```python
# There is no useful Subobject.pullback yet, so this one caller manually
# stacks inclusion matrices and takes a kernel.
```

**Preferred:** implement/fix the pullback, kernel, subobject, or other semantic operation at its mathematical owner, then make the consumer one or two semantic calls.

A missing semantic API is not external scope. It is evidence that the local feature has reached a foundational abstraction that must be strengthened. The smallest architecturally correct patch may therefore touch a lower-level category/Hom/subobject module before simplifying the original caller.

#### `STY-107`: Downstream finite/infinite case split -> move representation routing into the semantic owner

**Bad:**

```python
if M.module_rank().is_finite():
    A = f.matrix()
    ...
else:
    ...  # every consumer invents another infinite branch
```

**Preferred:**

```python
K = f.kernel()
```

with `kernel()` itself routing finite-free, finitely-presented, sparse/infinite, or engine-specific cases. Downstream mathematics should normally be representation-oblivious.

#### `STY-108`: Local helper that reconstructs a universal construction -> delete it in favor of the universal construction

**Red flags:** helpers named or behaving like `_kernel_from_matrix`, `_intersection_from_rows`, `_preimage_from_coefficients`, `_quotient_from_relations`, `_image_basis`, `_block_matrix_for_map`, or `_rank_from_presentation` in a downstream theory module.

Before retaining such a helper, ask whether it is merely rebuilding `kernel`, `image`, `pullback`, `cokernel`, `quotient`, biproduct/block-Hom, `fiber`, `dimension`, or another existing universal construction. If yes, use or repair that construction instead.

#### `STY-109`: A theorem stated semantically but implemented numerically in the caller -> make the code resemble the theorem

**Bad:** a comment says “the intersection is the pullback” or “cohomology is cycles modulo boundaries,” followed by dozens of lines manipulating matrices.

**Preferred:** the executable code should retain the same nouns and arrows as the mathematical statement:

```python
intersection = pullback(i, j)
H_n = d_n.kernel().quotient(d_previous.image())
exact = d1.image() == augmentation.kernel()
```

If these calls are not yet capable enough, repair them. A comment stating the correct abstraction does not excuse implementation at the wrong layer.

#### `STY-110`: Repeated numerical extraction is API feedback, not a reason for another extraction

The first downstream `.matrix()`/`.rows()` workaround may reveal a missing method. The second occurrence is strong evidence of a missing semantic abstraction. Do not copy the workaround into a third consumer.

When several callers need “kernel as subobject,” “span as subobject,” “block morphism,” “dimension after base change,” “torsion-free quotient,” or another recurring mathematical result, promote that operation to the common owner and delete the caller-specific numeric implementations.

#### `STY-111`: Optimize the semantic method, not each consumer

If a semantic composition is mathematically right but slow, preserve it as the mathematical route and optimize underneath it.

**Bad:** replace `i.cokernel().is_torsion_free()` in one lattice routine by a hand-written gcd/minor test because it is faster there.

**Preferred:** teach `cokernel()`/`is_torsion_free()` the efficient finite-presentation or Smith-form case. Every caller then gets the optimization, and future infinite cases still have one routing point.

This remains the preferred direction even when the low-level optimization internally collapses several semantic stages into one backend call.

#### `STY-112`: Coordinate tuple/vector as element input -> construct the element in its parent

Coordinates are observations relative to chosen data, not a second element language.

**Bad:** `x = L([1, 2])` or `y = M(tuple(coefficients))` when the bare sequence is admitted as an alternate public spelling for an element.

**Preferred:** use the parent's named generators / finite-support mathematical construction and form the element in the parent's language, e.g. `x = e + 2*f`, or an owned finite-support coefficient datum whose parent/index set is explicit.  A private backend adapter may serialize that element to a vector after construction.

#### `STY-113`: Matrix -> morphism may be construction; morphism -> matrix -> conclusion is a red flag

The coordinate boundary is directional.  A finite framed Hom constructor may consume matrix data to construct the actual morphism, validate domain/codomain/relations, and return the Hom element.  Once `f` exists, stay with `f`.

**Bad:** `A = f.matrix()` followed by a conclusion about injectivity, image, kernel, cokernel, primitivity, or form preservation.

**Preferred:** `f.kernel()`, `f.image()`, `f.cokernel()`, `f.is_injective()`, `f.is_surjective()`, composition, and Hom predicates.  The owner may internally return to a matrix for the finite case.

#### `STY-114`: Zero-matrix/entry-fill loops -> whole-object constructor, then semantic wrapper

Inside a private finite-coordinate boundary, do not manually own standard row/column layout when Sage already names it.

**Bad:** allocate a zero matrix and fill diagonal/block/column entries with nested index loops.

**Preferred finite backend idioms:** `matrix(rows)`, `column_matrix(columns)`, `diagonal_matrix`, `block_matrix`, `block_diagonal_matrix`, `identity_matrix`, `zero_matrix`, sparse constructors, `.apply_map`, and slicing.  Better still, if the object is mathematically a biproduct morphism, form, or endomorphism, construct that semantic object and let its backend choose the matrix constructor.

#### `STY-115`: Ported Sage signature -> resite the operation; never port Sage's object model

A foreign method name/signature is a fact about available computation, not a contract for the preamble API; the contract is `lean-categories`' operation.

**Red flags:** `ambient=`, `in_ambient=`, `even=`, `negative=`, mode booleans naming category membership, or a method on a bare object whose actual datum is an inclusion/morphism/base change.

**Bad:** `L.saturation(in_ambient=M)` or `Lattice(G, even=True)` when the parameter compensates for missing categorical structure.

**Preferred:** saturation on the subobject/inclusion; construct the general lattice/form and let category refinement record evenness or other derived structure.  Port **semantic capability**, not signature parity.

#### `STY-116`: Structure/category membership flag -> infer/refine it as output

Do not ask the caller to state a property the constructed mathematical datum already determines.

**Bad:** `Lattice(G, even=True)`, `Form(..., nondegenerate=True)`, `Module(..., torsion=True)` when those facts are decidable/declared from the datum.

**Preferred:** construct from the defining datum, then place/refine the result into the strongest justified categories.  A genuinely chosen structure is different and must be supplied as its actual datum, not as a boolean.

#### `STY-117`: Witness-compensating parameter -> first-class witness object

**Bad:** an operation on `A` accepts `ambient=B`, `inclusion=...`, or another optional parameter solely because `A` does not carry the relationship the operation needs.

**Preferred:** construct/use the subobject, morphism, functor image, base-changed object, or other witness-bearing object and put the operation there.  For a subobject, the “ambient” is simply `inclusion().codomain()`.

#### `STY-118`: Compatibility shim/alias after a redesign -> update callers and delete the old route

**Bad:** keep an obsolete ambiguous API and add the precise name as a wrapper over it, or retain an old constructor solely so internal callers continue to work.

**Preferred:** make the precise/canonical API the implementation, migrate all callers in the same change, and delete the superseded route.  Deliberate REPL conveniences such as `lmap` are not compatibility shims; they are intentional session vocabulary.

#### `STY-119`: Tiny internal wrapper with no semantic role -> call the existing operation directly

A short function is justified when it is a canonical semantic owner, a boundary, a constructor, or deliberate session notation.  It is not justified merely to rename an already-clear operation locally.

**Bad:** `def _make_identity(n): return identity_matrix(ZZ, n)`.

**Preferred:** call `identity_matrix(ZZ, n)` directly, or introduce a wrapper only when it centralizes mathematical validation/ownership that every caller must share.

#### `STY-120`: `globals()` mutation / dynamic sibling import -> static names and a repaired DAG

**Bad:** `globals().update(...)`, `global X` used to install exports dynamically, or `importlib.import_module(...)` used to postpone a sibling import and hide a cycle.

**Preferred:** ordinary module-scope imports/type aliases, or move the shared definition into a dependency-light defining module.  Optional external plugins may require dynamic loading at an engineering boundary; ordinary mathematical modules do not.

#### `STY-121`: QC-only statement/suppression -> fix the code or the shared tooling

Do not add executable or annotation noise whose only purpose is to silence a checker.

**Red flags:** `del arg` in an abstract/overload body, gratuitous casts, broad `Any`, `# type: ignore`, `# noqa`, or compatibility wrappers introduced only to reduce a warning count.

**Preferred:** if the diagnostic exposes a real mathematical/API defect, repair it.  If the checker lacks knowledge of Sage/category machinery, repair the shared stub/plugin/QC configuration.  A narrow suppression is admissible only for a genuinely untyped external boundary and must document that boundary.

#### `STY-122`: Test unwraps coordinates/matrices to state a semantic claim -> test the mathematical object

**Bad:** a test claims something about a kernel/image/subobject/isometry but compares matrix ranks, coordinate tuples, kernel basis rows, or raw backend objects.

**Preferred:** construct typed elements/morphisms and assert `f.kernel()`, `f.image()`, `f.cokernel()`, `f.is_surjective()`, subobject equality, isomorphism witnesses, or the named invariant.  If the test cannot state the claim without unwrapping coordinates, add the missing semantic noun/verb first.

#### `STY-123`: Numerical shadow used as the test claim -> assert the named invariant/structure

Determinants, ranks, coordinate lists, and cardinalities are legitimate when *they are the mathematical invariant under test*.  They are not substitutes for a stronger structural claim.

**Bad:** determinant equality as the sole claim that two lattices are isometric; row equality as the sole claim that two morphisms agree; rank equality as surjectivity.

**Preferred:** assert the actual isomorphism/equality/morphism predicate, and optionally cross-check the numerical shadow as a secondary invariant.

#### `STY-124`: Stale issue/docstring/comment/test after a ruling -> repair the prescription before code

A prescription that describes the rejected model is a code generator for future regressions.

**Red flags:** issue bodies naming old constructor signatures, comments explaining a coordinate workaround that policy has rejected, dead docstrings claiming a semantic implementation above numerical proxy code, generated/reference tests preserving a superseded API.

**Preferred:** update or delete the authoritative record immediately when the ruling lands, then continue implementation from the corrected record.

#### `STY-125`: Correct failure is inconvenient -> repair the defect; never launder the failure

**Bad remediation:** delete/weaken a mathematically correct assertion or red test, narrow the stated requirement after implementation fails, patch an unrelated symptom, or make the condemned representation “work” just enough to turn the check green.

**Preferred:** preserve the proposition/contract, treat the failure as evidence locating the real defect, and repair that defect.  Restarting an implementation while preserving the contract is acceptable; manufacturing success by weakening truth is not.

#### `STY-126`: Copy/port old implementation structure -> semantic reconciliation

When absorbing archived/legacy code, first map every notion onto the `lean-categories` notion the preamble presents.

**Bad:** copy a module/class hierarchy because it already implements the algorithm, or quarantine only a tiny slice while leaving duplicate notions.

**Preferred:** reuse current categories/functors/Homs where the notion is already presented; present a notion only where `lean-categories` formalizes it, and request it there otherwise.  Old code's own notions carry no authority.  Preserve the formalized semantics, not directory layout, class names, or historical architecture.

#### `STY-127`: Bare multi-structure generator name -> qualify the structure

**Bad owned vocabulary:** `generator`, `generators`, `generating_set`, `ngens`, `embedded_gens` when an object can simultaneously carry module, algebra, and group structures.

**Preferred:** `module_generator`, `module_generating_set`, `group_generators`, `algebra_generating_set`, `number_of_module_generators`, etc.  Do not keep the bare name as a compatibility alias.  Native Sage `.gens()` names remain native inside backend calls.

#### `STY-128`: Public presentation-facing constructor -> canonical constructor from mathematical datum

**Bad primary API:** `from_matrix`, `from_relations`, `with_action(G, matrices)`, or a subobject constructor from raw rows when the actual datum is a morphism/action/inclusion/presentation.

**Preferred:** construct the defining morphism in its Hom, then pass that object to the canonical constructor.  Coordinate/matrix conveniences, where mathematically unambiguous for a canonically framed Hom, immediately produce the mathematical object and are not a second downstream language.

#### `STY-129`: “Not computable in full” -> still construct the predicate-defined mathematical object

Do not confuse inability to enumerate/generate an object with inability to represent it.

**Bad:** refuse to construct `O(L)`, a stabilizer, a center, or another predicate carve-out because generators/relations are unavailable.

**Preferred:** construct the predicate-defined subgroup/subset/category, as `lean-categories` defines it, with membership and the operations that are available.  Add enumeration/generator algorithms as computable cases later.  A predicate computes its answer; it never answers `True` because construction accepted an input.

#### `STY-130`: Presentation hard-codes a hypothesis the definition lacks -> present at the formalized generality, recover the special case by refinement

**Red flags:** a framing requires a finite/ordered set although the definition only needs a set; a direct-sum notion is presented only for finite families because the first backend is matrix-based; a construction is named after one base ring even though its definition works over a wider ring class.

**Preferred:** present the notion at the hypotheses `lean-categories` states for it, then recover finite/free/projective/ordered/enumerable/commutative special cases as the axioms, subcategories, or algorithmic cases it formalizes.  If `lean-categories` states the notion under a hypothesis stronger than the literature needs, that is a request there, not a local generalization.  Use extreme infinite/nonenumerable objects as stress tests of the interface even when the current computation does not handle them.

#### `STY-131`: Hidden mathematical choice / definite article -> name the selecting datum

**Red flags:** “the dual”, “the extension”, “the normalization”, `normalize=True`, `map=True`, or another flag whose value changes which mathematical object/morphism is selected, without the choice being represented explicitly.

**Preferred:** determine whether the object is canonical.  If not, give the alternatives distinct mathematical names or accept/store the selected morphism/object/structure as first-class data.  A normalization/re-presentation is a new object together with its isomorphism; a chosen framing, orientation, action, embedding, closure presentation, or section is an actual datum, not a boolean mode.

#### `STY-132`: Subobject equality that forgets the inclusion -> compare the slice object

A subobject is not merely an object that happens to be isomorphic to something inside another object.  It is the object **together with its witnessing monomorphism**.

**Bad:**

```python
def __eq__(self, other):
    return self.underlying_object() == other.underlying_object()
```

for subobjects `i:S -> M` and `j:T -> M`.  Two isomorphic copies of the same abstract module embedded differently in `M` are different subobjects.

**Preferred:** equality of subobjects is equality in the relevant slice/subobject category: compare the underlying owned object together with the inclusion morphism (or delegate to the owned subobject/category equality that already does so).  Never reconstruct equality from common coordinates in the codomain.

#### `STY-133`: Quotient equality that forgets the projection -> compare the coslice/quotient object

The dual error occurs for quotients.  A quotient is not just its abstract codomain `Q`; it is the epimorphism `p:M ->> Q` together with that codomain.

**Bad:** treat two quotient presentations as the same quotient because their codomains are isomorphic or have equal invariant factors.

**Preferred:** keep the quotient/projection morphism first-class.  Equality as quotient objects includes the epi; an abstract codomain may be isomorphic while representing a different quotient of `M`.

#### `STY-134`: Identify an object with its image -> keep the morphism and image subobject distinct

**Bad:** because `f:X -> Y` is injective or surjective, silently identify `X` with `f(X)` or `Y` with the image, then let later code use equality where a morphism is the actual relationship.

**Preferred:** `f` is the relationship; `f.image()` is a subobject of the codomain; `X` remains the domain object.  Even when `f` is an isomorphism, equality and the exhibited isomorphism are different mathematical statements unless the construction is canonically identical by repository policy.

This applies to dual inclusions, rationalization/base change maps, quotient projections, embeddings, and all other arrows.  Do not erase the arrow merely because its image has a familiar description.

#### `STY-135`: Normalization mutates the object / hides behind a flag -> return the new object and isomorphism

A normal form or re-presentation changes chosen data.  That means it produces a different object of the framed/presented category, related to the source by an isomorphism.

**Bad:**

```python
M.normalize(in_place=True)
M.normal_form(transformation=False)
```

or replacing `M`'s chosen framing/presentation internally by a Smith/Hermite/canonical one.

**Preferred:**

```python
iso = M.invariant_factor_form()
normalized = iso.codomain()
```

where the returned isomorphism is part of the mathematical result.  The transformation is not optional metadata: it is what states why the new presentation represents the same abstract mathematics.

#### `STY-136`: Universal construction returns only a naked object -> return/attach its canonical structure morphism

A kernel, image, cokernel, quotient, pullback, pushout, product, coproduct, or similar construction is incomplete if the universal structure maps have been discarded.

**Bad:** `f.kernel()` returns a module whose basis happens to span the nullspace but has no inclusion into `f.domain()`; `f.cokernel()` returns an abstract presented module with no canonical projection from `f.codomain()`.

**Preferred:** the owned result carries or canonically exposes the relevant maps: kernel inclusion, image inclusion/factorization, cokernel projection, product projections, coproduct injections, pullback legs, pushout legs, and so on.  Downstream code should be able to use the universal property without reconstructing those arrows from coordinates.

A quotient element's `lift()` may select a representative; it is not a canonical inverse to the quotient projection and must not be presented as one.

#### `STY-137`: Test a weaker equivalence relation on equal objects -> use genuinely different objects

**Bad:** test `is_isomorphic`, `is_isometric`, same-genus, or another relation weaker than equality using `X` and `X` or two constructions that canonicalize to the same owned object.  Equality makes the weaker claim tautological.

**Preferred:** choose distinct objects/presentations known to be related in the weaker sense: two differently framed but isomorphic modules, two different Gram presentations of isometric lattices, or genuinely distinct representatives in one genus.  The test must be capable of falsifying the weaker-relation implementation.

#### `STY-138`: Implementation-role noun -> identify the standard mathematical object or datum

LLM-generated code often invents an implementation ontology around words such as `provider`, `manager`, `context`, `evidence`, `knowledge`, `metadata`, `payload`, or `wrapper` when the thing is already a standard mathematical object.

**Bad:** ask a caller for a `SubobjectEvidence`, `GeneratorProvider`, or `NormalizationContext` when the actual datum is an inclusion morphism, indexed family, isomorphism, framing, or functor.

**Preferred:** name and type the actual mathematics.  Before introducing a helper noun, ask whether a mathematician could define it independently of this codebase and whether an existing category/object/morphism/functor already is that thing.  Engineering records may exist at engineering boundaries; they do not become public mathematical ontology.

#### `STY-139`: Brainstorm wrappers/overloads/adapters before stating the mathematics -> state the mathematical model first

**Bad review sequence:** encounter a signature collision or missing operation and immediately compare overloads, optional arguments, wrappers, adapters, casts, aliases, registries, or dispatch tricks.

**Preferred sequence:** first state what `self` is mathematically, what datum the operation consumes, where it is well-defined, what object owns it, and what its mathematical return object is.  Only after that model is fixed choose the smallest Python/Sage mechanism that realizes it.  If naming the mathematics makes the engineering alternatives disappear, discard them.

#### `STY-140`: Reviewer names one symptom -> patch only that symptom while preserving the contaminated implementation

A review finding is evidence about a generator, not a specification saying “remove this exact line and preserve everything else.”

**Bad:** a reviewer flags matrix-based kernel reconstruction, so move the same reconstruction into a helper/adapter and leave all callers and tests semantically unchanged; a reviewer flags a global dispatcher, so hide the switchboard behind a registry without changing ownership.

**Preferred:** identify the architectural generator that produced the finding, inspect sibling instances and consumers, repair the semantic owner, and simplify the callers.  Do not make preservation of the currently contaminated implementation or its representation-level tests an unstated acceptance criterion.

#### `STY-141`: Invent canonical arrows from analogy -> read the actual universal diagram

Do not infer structure maps because an object “looks like” a product, quotient, tensor, or coordinate construction.  The universal property determines the canonical arrows.

**Bad:** treat `M tensor N` like a Cartesian product and invent projections `M tensor N -> M`, `M tensor N -> N`, or canonical maps `M -> M tensor N` without chosen elements.

**Preferred:** state the defining diagram.  For a tensor product, the canonical map is the bilinear set map

\[
M\times N \longrightarrow M\otimes_R N,
\]

and maps out of `M tensor N` correspond to bilinear maps out of `M × N`.  No map from either factor alone is canonical without extra selected data.  Apply the same discipline to every universal construction.

#### `STY-142`: Functor accepts too broad a category then rejects arrows -> restrict the domain category

**Bad:** define `F:C -> D`, then inside `_apply_morphism` assert/reject every non-isomorphism because the construction is only functorial on isomorphisms.

**Preferred:** declare `F:C.core() -> D`.  If the mathematical variance/domain is a slice, coslice, arrow category, subgroupoid, or other subcategory, make that the functor's actual domain.  Runtime assertions may still document internal assumptions, but they do not substitute for a mathematically wrong functor signature.

#### `STY-143`: Parameterize an intrinsic notion -> derive it from the existing structural maps

A notion with an a priori mathematical meaning is not a customization hook.

**Bad:** ask for an `integrality_submodule`, an `integral_over=` mode, or another parameter redefining what “integral” means when the existing ring map already determines integrality.

**Preferred:** derive the notion from the relevant structure already present—for example integrality in a ring extension from the specified ring morphism.  If a genuinely different notion is wanted, it is a different notion, requested from `lean-categories` under its own name, never a parameter that makes the standard one ambiguous.

#### `STY-144`: “Safe” horizontal patch during an architectural migration -> make the breaking vertical move

**Bad:** preserve every old caller, wrapper, and intermediate representation while moving one method at a time because each commit is expected to remain locally green, even though the target architecture makes much of that code disappear.

**Preferred:** move the mathematical responsibility to its final owner, migrate the affected vertical slice, delete superseded routes, and allow intermediate repository states to be broken when the active architectural work explicitly permits it.  Do not spend effort polishing code scheduled for deletion merely to preserve incremental compatibility.

#### `STY-145`: Deep specialized file owns an obviously general concern -> stop and audit placement

**Red flag:** a lattice-only file contains generic cardinality/set logic; a subobject implementation contains generic quotient machinery; a scheme leaf implements a generic product/Hom construction.

**Preferred:** stop before patching the local code and ask which more general category/object should own the concern.  Search sibling implementations for duplication and move the abstraction upward/downward to its mathematical owner.  A misplaced concern is evidence that the architecture around the site may be wrong.

#### `STY-146`: Exact mathematical result vs soft knowledge result -> use the correct codomain

Do not force every question into a Python boolean, and do not use `Unknown` to replace an exact mathematical value.

**Exact operation:** `cardinality()`, `kernel()`, etc. retain their mathematical codomain.  If today's algorithm does not cover a represented case, route known cases and assertion-gate the unsupported computational remainder as specified by `CAT-01`.

**Exact predicate:** `is_nondegenerate()`, `is_injective()`, `is_abelian()`, etc. have the codomain `Propositions` (`preamble/logic.py`).  Where the question is computable or decidable, the predicate computes or decides it and returns `True` or `False`.  Where it is not decided, it returns the `Predicate` that states it; `ask(P)` evaluates that proposition, as `sympy.ask` evaluates a sympy proposition, and answers `Unknown` only when no procedure decides it.  A predicate never returns a bare `Unknown` and never answers `False` for an undecided question.

**Soft knowledge/computability predicate:** a deliberately epistemic API such as `generators_are_computable()` or `has_computed_group_generators()` may have the explicit three-valued codomain `True | False | Unknown` when “not currently known/decided” is itself what the method is asking.

**Bad:** return `False` from `is_nondegenerate()` because no algorithm is known; return a bare `Unknown` from `is_injective()` in place of the proposition; return `Unknown` as the “cardinality” of a set; return `True` from a soft predicate merely because construction accepted an input.

#### `STY-147`: Universal-property test checks one factorization only -> test existence and uniqueness

**Bad:** construct one factorization through a tensor product/kernel/product/etc. and assert that it commutes, while never testing the uniqueness clause—or compare the same generated map to itself twice.

**Preferred:** test the actual universal property: construct the canonical factorization, verify the diagram, and verify uniqueness against a genuinely independently constructed competing morphism where practical.  Choose nonzero/nontrivial specimens so uniqueness is not vacuous.

#### `STY-148`: Parallel Set Hom / exponential / power-set objects -> canonical identification

**Bad:** implement `Hom_Set(X,Y)`, an independent function-set parent `Y^X`, and a separate power-set parent `P(X)` with overlapping iteration/cardinality/map behavior.

**Preferred:** represent the canonical identities

\[
\operatorname{Hom}_{\mathbf{Set}}(X,Y)=Y^X,
\qquad
P(X)=2^X=\operatorname{Hom}_{\mathbf{Set}}(X,2)
\]

as object identity/one owned construction with the relevant category placements.  Cardinality and set operations then follow once from that object.  Do not preserve parallel parents merely because different callers arrived through different notation.

#### `STY-149`: Literal mathematical expected values scattered through tests -> cited reusable fact data

**Bad:** dozens of tests independently write facts such as named-lattice ranks, discriminants, orbit counts, genus classes, number-field invariants, or classification-table rows as inline literals, often with duplicated or missing provenance.

**Preferred:** put the fact in the repository's topic-organized fixture/fact corpus with its construction/identifier, value(s) and citation.  Tests become thin parametrized drivers that compute the repository result and compare it to that fact.  These tests are research's own and certify nothing outside it; correctness evidence exists only in the `lean-cas-dsl` acceptance suite.

#### `STY-150`: Current implementation output used as its own expected value -> independent cited source

**Bad:** run the method being tested, copy its output into a fixture, then assert future runs reproduce that output; or treat a Sage result, or any engine's own test corpus, as mathematical truth.

**Preferred:** expected mathematical values come from an independent cited source or proof.  No implementation, including the one under test, a Sage call or research code, is the provenance for an expected result.

#### `STY-151`: Element repr exposes coordinate storage -> render the mathematical expression

**Bad:** an element of a framed/free module or lattice prints as `(2, -1, 0)` or as a backend vector, making its storage representation look like the element itself.

**Preferred:** render the owned formal linear combination in the selected generator/framing symbols, using the coefficient ring's own representation and the symbols' own representation.  Coordinates may be inspectable through an explicit framing/coordinate operation, but ordinary `repr`/LaTeX presents the mathematical element.

Do not hard-code integer-specific sign/absolute-value formatting into a generic `R`-module printer; an arbitrary coefficient ring need not have those notions.

#### `STY-152`: Free cover stored as a finite generator list -> selected epimorphism from a free module

**Bad:** define a module with selected generators as `M` plus `tuple(generators)` and then infer that the tuple is finite, ordered, injectively labelled, or a basis.

**Preferred:** a free cover is the selected epimorphism

\[
\operatorname{Free}_R(S) \twoheadrightarrow M
\]

for an owned set `S`. The distinguished-generator map is the underlying-set image of this morphism. `S` may be infinite, nonenumerable, unordered, and different labels may map to the same module element. A **categorical framing** is instead an isomorphism `Free_C(S) -> X` relative to the specified adjunction (`CAT-29`). It is a length-zero free resolution; its invertibility is not implied by an epimorphic cover.

#### `STY-153`: Backend-category graph used as mathematical taxonomy -> capability correspondence

**Bad:** mirror Sage's `super_categories()` graph, manufacture preamble categories solely so every Sage name has a destination, or use Sage category equality/edge layout to decide what a category is.

**Preferred:** `lean-categories` defines the categories and functors; the preamble's category graph presents them.  A private/versioned correspondence records which Sage categories/implementations can compute for which presented categories and operations.  Several Sage categories may provide one capability; one Sage category may require a normalized preamble expression.  Backend taxonomy is empirical implementation data, never mathematics.

#### `STY-154`: Descendants repeat inherited operations -> fulfill obligations through the preferred functor

**Bad:** lattices reimplement cardinality/iteration, modules reimplement generic set products, every structured category writes its own version of an operation already owned below a forgetful/structure functor.

**Preferred:** declare the semantic operation once and identify a preferred structure-forgetting/projection functor at the appropriate rollup point.  Delegate `X.operation()` through that functor when the target category already carries the operation.  A descendant implements only the new structure or a genuinely better algorithm justified by its refinement.

#### `STY-155`: Constructor named after a derived subcategory -> construct at the owning root and refine the result

**Bad:** require the user to choose `RootLattice(...)`, `EvenLattice(...)`, `TorsionModule(...)`, or another specialized constructor merely because the resulting object happens to satisfy that property.

**Preferred:** construct through the ordinary owning category/object constructor from the defining datum, then let the resulting object acquire every justified refinement.  The researcher should construct the mathematics they know, not predict the internal category routing first.

A specialized constructor remains justified only when the specialized name denotes genuinely additional **input structure**, not a property derivable from the supplied datum.

#### `STY-156`: Hand-authored forgetful/projection graph -> derive structural arrows from category expressions

**Bad:** maintain one table saying `C.A -> C`, another registry of ancestor forgetful functors, and hand-written forwarding paths that duplicate what the category/classifier construction already determines.

**Preferred:** if `C.A` is defined as a classifier application/pullback, its projection to `C` is part of that definition; ancestor projections are compositions of those structural arrows.  Store/implement the defining category expression and derive the canonical projection hierarchy from it rather than maintaining a second graph that can drift.

#### `STY-157`: Public `*args` / `**kwargs` option bag -> closed mathematical signature

**Red flag:**

```python
def construct(x, *args, **kwargs):
    return backend_constructor(x, *args, **kwargs)
```

on a public mathematical surface.

**Preferred:** enumerate the actual mathematical input shapes the preamble supports and give them precise signatures, named constructors, or source-grounded overloads.  A homogeneous variadic family is acceptable only when the mathematics itself is genuinely variadic and the element type/meaning is fixed; arbitrary backend option forwarding is not.

Private backend adapters may use `*args`/`**kwargs` when their entire job is literal protocol forwarding inside the boundary and the option bag cannot escape into the public mathematical contract.

#### `STY-158`: `None` sentinel selects a different mathematical operation/object -> split or make the datum explicit

**Bad:**

```python
def normalize(M, map=None): ...
def construction(X, ambient=None): ...
```

where `None` versus a value changes the mathematical object, witness, domain, codomain, or return shape.

**Preferred:** use distinct mathematical operations/constructors or accept the actual selected datum (morphism, ambient object when genuinely part of the definition, section, framing, etc.).  If omission means a genuinely canonical default such as the unit `1` or identity morphism, that default may be stated explicitly by the API; do not use `None` to conceal a noncanonical choice.

#### `STY-159`: Boolean mode flag changes mathematics or return type -> named operations / literal overloads

**Bad:** `normal_form(transformation=True)`, `roots(all=True)`, `galois_closure(map=True)` when the flag selects a different mathematical result or tuple shape.

**Preferred:** expose the mathematical objects/witnesses directly (`normal_form_isomorphism()`, chosen closure with its embedding, all-roots set, etc.), or—when compatibility with a source-level operation is intentionally retained at a non-mathematical boundary—use precise literal overloads there.  Do not make ordinary preamble callers memorize boolean modes.

#### `STY-160`: `pass` in a mathematical implementation -> implement, delete, or mark a genuine abstract contract

**Bad:** a visible concrete method/class body contains `pass` merely to postpone mathematics, silence a branch, or satisfy syntax.

**Preferred:** a genuine abstract category contract uses Sage `@abstract_method` with an ellipsis body; a concrete mathematical method is implemented; an impossible branch is asserted with its mathematical invariant; an unnecessary empty wrapper/class is deleted or replaced by the actual category refinement it represented.

`pass` remains ordinary Python in private engineering situations where “do nothing” is literally the intended protocol behavior, but it is a review flag in the mathematical subtree.

#### `STY-161`: Negated predicate where the complementary mathematical notion has a name -> expose the positive predicate

**Bad:** force users/callers to write `not L.is_nondegenerate()`, `not f.is_injective()`, or another negation when the complementary mathematical property has a standard name used in the field.

**Preferred:** expose the named positive concept (`is_degenerate()`, etc.) at its natural owner.  Do not implement a genuinely three-valued/partially decidable concept merely by Python negation: the positive predicates must preserve the intended mathematical/knowledge semantics of their codomains.

#### `STY-162`: One-use convenience wrapper hides a composable mathematical object -> expose the object

**Bad:**

```python
L1.same_genus(L2)
g.action_on_discriminant_group(x)
f.from_identity_matrix()
```

when the real mathematics is a genus value object, a group morphism, or an identity element of a Homset.

**Preferred:**

```python
L1.genus() == L2.genus()
rho = L.O().action_on(L.discriminant_module())
rho(x)
L.Mor(L).identity()
```

Expose the value/morphism/universal object because it can then be compared, composed, restricted, factored, have kernel/image taken, etc.  A wrapper that only packages one obvious use hides that structure and adds another name to memorize.

#### `STY-163`: Generic software-role suffix in the public mathematical API -> name the actual mathematical noun

**Red flags:** public names ending in or centered on `Model`, `Descriptor`, `Record`, `Info`, `Result`, `Context`, `Manager`, `Factory`, `Payload`, `Adapter`, `Backend`, `Provider`, or `Evidence` when those words merely describe the software role.

**Preferred:** identify the standard mathematical object/data: category, family, morphism, section, presentation, isomorphism, stratification, graph, action, form, quotient, etc.  If the object is genuinely an engineering record/adapter/backend, keep it private in the engineering subtree/boundary instead of promoting it into the mathematical language.

#### `STY-164`: Supplied generators returned as a canonical group -> construct a typed subgroup

**Bad:**

```python
O_L = L.orthogonal_group(generators=user_generators)
```

and then use `O_L` for canonical-group orbit/stabilizer/kernel/invariant statements.

**Preferred:**

```python
O_L = L.O()                         # canonical group object exists independently
H = O_L.subgroup(user_generators)  # exactly the group the supplied data proves
```

The supplied generators certify only `H = <generators> <= O(L)`.  Equality `H = O(L)` is a separate mathematical claim requiring an independent group-generation algorithm/theorem.  Downstream computations name the group they actually use.

#### `STY-165`: `Random*` / `Example*` / `Test*` mathematical type or category -> generate input data for the ordinary constructor

Randomness, example status, and fixture status describe a **process/use**, not a new mathematical kind.

**Bad:** `RandomLattice`, `ExampleModule`, `TestGroup`, `RandomLattices()`.

**Preferred:** a random/example generator produces legitimate defining data (Gram form, presentation, polynomial, relations, etc.) and feeds that data into the existing canonical constructor.  The returned object is an ordinary lattice/module/group and is refined by its mathematics.  Named standard examples belong in catalogues when useful; they do not automatically create new category vocabulary.

#### `STY-166`: Absence/rejection assertion can pass on a dead object -> assert positive capability/witness first

**Bad:**

```python
assert not hasattr(T, "projection")
assert invalid not in results
```

when an empty/broken `T` or empty `results` would pass equally well.

**Preferred:** state the positive mathematical structure that makes the negative claim meaningful, then test the actual positive universal/property statement.  For a tensor product, test the bilinear universal factorization and uniqueness rather than the absence of product projections.  For a filtered enumeration, first assert a sourced/nonzero expected population or independently established completeness before exclusions count as evidence.

A test of code removal that only asserts the removed name is absent is a closed loop around the edit, not a mathematical regression test.

#### `STY-167`: Sage `Element.__eq__` -> `_richcmp_` plus compatible `__hash__`

This rule is specifically for subclasses/runtime types of `sage.structure.element.Element`, not ordinary Python records or Sage `Parent` classes.

**Bad:**

```python
class MyElement(Element):
    def __eq__(self, other):
        return self.data == other.data
```

Sage's inherited zero/truthiness/coercion machinery compares elements through `_richcmp_`, so a bespoke Python `__eq__` can disagree with `is_zero()` and `bool(x)`.

**Preferred:** implement the one Sage comparison primitive:

```python
def _richcmp_(self, other, op):
    return richcmp(self.data, other.data, op)

def __hash__(self):
    return hash(self.data)
```

using the same immutable mathematical data for equality and hashing.  Let Sage's inherited `is_zero()`/`__bool__`/comparison machinery delegate to that primitive.  Put the implementation at the highest owned element type where the equality semantics are shared, not on every leaf.

#### `STY-168`: Hand-built linear-combination `repr` -> the host's symbolic representation helper

**Bad:** manually join coefficients/signs/generator labels in `_repr_`, usually assuming integer signs, absolute value, unit coefficients, or string labels.

**Preferred:** represent the element as the actual finite formal combination of its owned symbols and coefficients, and use Sage's `repr_lincomb` (or the corresponding owned formal-sum renderer) when its semantics match.  Let the coefficient ring and symbol objects supply their own representations.  Do not rebuild sign/`±1`/zero formatting by hand in every module/lattice/algebra element class.

This is not cosmetic: a symbolic `2*e - f` display reinforces that the element is a formal mathematical element, while a raw tuple or hand-formatted coordinate vector trains the numerical reading the API is trying to prevent.

#### `STY-169`: Algorithm exhausts an entire mathematical object -> use structural data/theorem or make enumeration the explicit operation

**Red flag:**

```python
for x in G:
    ...
for x in M:
    ...
all(property(x) for x in X)
```

where correctness/termination requires eventually visiting **every** element of a group, module, lattice, ring, or other potentially infinite object.

**Preferred:** ask what finite/structural datum actually proves the claim: a chosen generating family when a finite-generation theorem makes that sufficient, a presentation/relation check, a morphism identity, category membership, a backend theorem, finite support of the particular element, or another semantic invariant.  If the operation genuinely is “enumerate all elements,” return/use the owned enumerated set lazily and let the caller explicitly request/consume enumeration.

A lazy `__iter__` implementation is not the smell; an unrelated algorithm whose success assumes the iterator terminates is.  An upstream `assert X.is_finite()` added solely because a loop needs exhaustion is the loop confessing that it lowered the mathematical domain.

#### `STY-170`: “Tensor product of matrices” -> Kronecker product / tensor product of the represented morphisms

Matrices as arrays have a **Kronecker product**.  Tensor product is the mathematical construction on modules/vector spaces/algebras and on linear maps between them.

**Bad:** describe `A.tensor_product(B)` or a block array `(a_ij B)` as “the tensor product of matrices,” then reason about it as though matrices themselves carried that universal construction.

**Preferred:** if `A` and `B` are matrices representing `f:V1->W1` and `g:V2->W2`, construct/consider the tensor morphism

\[
f\otimes g:V_1\otimes V_2\to W_1\otimes W_2.
\]

In chosen finite bases, its representing matrix is the Kronecker product of `A` and `B`.  Backend calls may use the engine's historical `.tensor_product` spelling privately, but public prose/API names the correct mathematical operation.

#### `STY-171`: Euclidean vector operation on a formed object -> use the object's actual form

**Red flags:** `dot_product`, standard-coordinate `norm`, Euclidean projection, Gram-Schmidt, shortest-vector language, or orthogonality code applied to an object carrying an arbitrary bilinear/quadratic form without explicitly routing through that form.

**Preferred:** ask the formed object for `b(x,y)`, `q(x)`, its correlation morphism, orthogonal complement, radical, or the appropriately named form operation.  A Euclidean/positive-definite algorithm lives only at the mathematical subcategory where that extra structure makes it valid, and its private backend may then use standard inner-product routines after the correct form has been transported/normalized.

#### `STY-172`: Definite/nondegenerate assumption appears because the backend wants it -> keep the general form semantics and localize the algorithmic case

**Bad:** make the base formed-object API positive definite or nondegenerate because the first available matrix routine needs an invertible/PD Gram matrix.

**Preferred:** arbitrary (including degenerate/indefinite) forms are first-class at the general category.  Methods whose **mathematical definition** requires definiteness/nondegeneracy live on that narrower category; methods defined generally keep their general name/domain and route/assertion-gate the currently computable cases.  Backend assumptions never redefine the base mathematical object.

#### `STY-173`: Defect found in an owned dependency -> local facade/protocol workaround -> fix the owner

**Bad:** discover that the preamble lacks an annotation/semantic method, then add a local `Protocol`, stub, wrapper, copied helper, or workaround in the downstream consumer and merely file/report the upstream defect.

**Preferred:** if the defective dependency is part of the user's owned project stack and the fix is within the active task's mathematical dependency, correct it at its authoritative source, then consume the repaired interface.  A TODO/report is useful only when the source genuinely cannot be changed in the current ownership boundary.

#### `STY-174`: Stored backend object as long-lived implementation twin -> reconstruct ephemeral computation state when practical

**Bad:** a preamble object stores a Sage/GAP/etc. twin and ordinary downstream methods repeatedly dig into it, allowing the backend's object model to become durable hidden state.

**Preferred:** for large standard algorithms whose inputs/outputs are mathematical data, construct the private backend representation from the preamble data at the computation boundary, perform the complete operation, convert back, and discard it.  Durable backend state is justified only when the representation itself is a required long-lived computational resource and then remains behind one private owner/boundary (`BND-01`).

#### `STY-175`: Read every Sage `super_categories()` edge as inclusion -> classify the structural map first

Sage uses one graph edge mechanism for mathematically different relationships: full-subcategory inclusion, forgetting one operation/projection from a structured object, parameterized-family relationships, and implementation/MRO organization.

**Bad:** see `A in B.super_categories()` and conclude “every `B` is an `A`” or copy the edge directly into the preamble's category graph.

**Preferred:** determine which `lean-categories` map, if any, that Sage declaration corresponds to (subcategory inclusion, forgetful/projection functor, reindexing/base-family map) or whether it is merely host implementation organization, then present that construction/functor.  The Sage edge is a fact about Sage, never a theorem.

#### `STY-176`: Sage category equality/parent lists used as category equivalence -> compare the formalized categories

**Bad:** conclude two categories are mathematically different because Sage `C != D`, or identical because `C.super_categories() == D.super_categories()`.

**Preferred:** identify the `lean-categories` category each Sage category corresponds to and compare those.  Two different Sage presentations of one pullback/category may compare unequal; two genuinely different refinements can have identical declared parents.  Missing Sage edges are implementation gaps, not mathematical non-inclusions.

#### `STY-177`: Bundled object type/presentation called “the category” -> keep the levels separate

Before naming an implementation artifact, separately identify:

1. the mathematical category;
2. an object of it;
3. the runtime/bundled Python/Sage type representing such objects;
4. any category structure placed on that runtime type;
5. any chosen presentation (basis, enumeration, coordinates, generators);
6. any property-cut full subcategory.

**Bad:** call a `Fintype`-like presentation “the category of finite sets,” or identify based modules with finite free modules because choice can produce a basis.

**Preferred:** name each level explicitly.  Equivalence between presentations does not erase which choice/structure the API actually carries.

#### `STY-178`: Exact name not found -> look for the formalized composition before declaring a gap

**Bad:** search `lean-categories`, Sage or Mathlib for one class/function with the exact local spelling, find none, and conclude the concept must be requested or implemented.

**Preferred:** look in `lean-categories` for the notion as a standard composition it already formalizes: a full subcategory cut out by a property, structured objects, a Hom/category construction, slice/coslice, inclusion/forgetful functor, base change, or transport through an equivalence.  A missing packaged noun is not a missing mathematical primitive.  Composing it is `lean-categories`' work; if it does not formalize the composite, request it there.

#### `STY-179`: Upstream correspondence found -> preserve redundant local declaration -> delete/resite it if the correspondence exposes wrong ownership

**Bad:** discover that a ring-specific `size()` is exactly underlying-set cardinality and “fix” the design by delegating `Ring.size()` to that set cardinality, preserving the duplicate public word.

**Preferred:** use the correspondence diagnostically.  If `lean-categories` places the operation on `Sets`, remove the ring-local synonym and let the ring recover `cardinality()` through the forgetful/structural functor.  Alignment can prove a declaration redundant or misplaced; it does not automatically justify keeping it.

#### `STY-180`: Avoid a mature dependency because it is “heavy” -> compare maintained code and blast radius instead

**Bad reasoning:** reject `networkx`, a parser/grammar package, a multidispatch library, or another mature dependency because it adds packages, a build toolchain, or installation scaffolding, then implement the generic machinery locally.

**Preferred reasoning:** treat ordinary dependency/build/package substrate as baseline engineering.  Compare designs by the generic logic the repository must now maintain and review, the blast radius of adding/changing a case, and whether other consumers can reuse the external abstraction instead of relearning it.  Use the mature dependency when it removes substantial local machinery and is semantically appropriate.

#### `STY-181`: Hand-roll against Sage because the relevant host idiom was not checked -> inspect the host first

**Bad:** manually implement generator naming, identity construction, conformance checking, matrix reshaping, coercion, graph traversal, or another operation before checking Sage/stdlib/upstream for the native idiom.

**Preferred:** inspect the live host API/source and, when behavior matters, run a distinguishing probe.  Use the host operation where its semantics match; wrap it only at the preamble boundary if its vocabulary or object model differs.  Lack of familiarity with Sage is not a reason to create a second local language.

#### `STY-182`: Nontrivial local algorithm appears before backend search -> map the semantic operation to mature software first

**Red flag:** a new multi-step algorithm for groups, ideals, lattices/forms, polyhedra, number theory, symbolic algebra, or graph structure appears in Python without any indication that the installed/open-source capability stack was checked.

**Preferred:** name the semantic operation, search the repository capability map and relevant mature exact systems, then either delegate through the preamble boundary or document the true gap that justifies a local implementation under `ENG-06`.  “It was straightforward to code here” is not a reason for the repository to maintain it.

#### `STY-183`: Named composite/classifier spelling -> duplicate category vertex -> preserve one identity

**Bad:** represent `Semigroups` and `Magmas.Associative` as two independent categories connected by an equivalence/alias edge; similarly create a second category solely for every readable composite name.

**Preferred:** the standard name and the classifier expression are two spellings of **one category**, the one `lean-categories` formalizes.  The public name may be `Semigroups`; the defining expression may be `Magmas.Associative`; no second vertex/object is created.

#### `STY-184`: Same axiom word reused globally -> interpret classifier relative to its host category

Names such as `Commutative`, `Distributive`, `Graded`, `Finite`, etc. have meaning only together with the mathematical category/construction they classify.

**Bad:** create one global `Commutative` node because Sage happens to reuse that axiom spelling across unrelated theories.

**Preferred:** `Groups.Commutative`, `Rings.Commutative`, a lattice-poset classifier, etc. are classifier applications whose meaning is the one `lean-categories` gives on that host.  Transport a classifier to another category via the corresponding pullback where `lean-categories` states it; do not identify classifiers by string.

#### `STY-185`: Readable name for a pullback/refinement -> independent species -> retain the defining category expression

**Bad:** mint `FiniteRings`, `GradedAlgebras`, `BasedModules`, etc. as unrelated categories merely because a readable plural name is convenient.

**Preferred:** first represent the actual expression, e.g. `Rings.Finite` or `Algebras(R).Graded`, with the appropriate classifier/pullback structure.  A standard established plural may be registered as the public name/alias of that same category; the name does not replace or duplicate the construction.

#### `STY-186`: Generated “certificate/evidence/status” artifact for facts derivable from live code -> live semantic structure plus on-demand report

**Bad:** add a per-object certificate/attestation JSON, proof-metadata ABC, generated status ledger, or stored compliance manifest whose fields are all recomputable from category placement, MRO, constructors, functors, and runtime behavior.

**Preferred:** put the actual invariant into the type/category/constructor language; exercise live behavior with specimens or the host's native conformance mechanism; generate any human-readable inventory on demand.  Do not create a second ledger that must be synchronized forever.  No certificate, attestation or status an implementation produces about itself is evidence of anything; correctness evidence exists only in the `lean-cas-dsl` acceptance suite.

#### `STY-187`: Category constructibility decided by graph reachability/name lookup -> derive canonical structural maps

**Bad:** say a category/refinement is “constructible” because a named node exists or because BFS finds some path through an implementation graph; traverse projection arrows backwards to manufacture structure.

**Preferred:** use the preamble's category-expression/finite-limit grammar, which presents `lean-categories`' structural maps: canonical structural maps compose in their stated direction; classifiers/refinements are introduced only when the required map to their host exists; pullback/classifier constructions create their own projections.  Constructibility is derivability in this typed structural calculus, not arbitrary graph connectivity.

#### `STY-188`: Default display repeats the type/role -> expose mathematical data of this object

The default display of every preamble object must reduce mathematical uncertainty about the **particular object being displayed**.  A class name, noun phrase, constructor family, or paraphrase of the object's type is not a display.  The researcher already knows that a value returned by `module_generators()` is a generator family and that an object constructed by `Lattices(R)(...)` is a lattice.  Printing only `"Lattice-generator family"`, `"Lattice"`, `"placed map"`, or an equivalent type-renaming is therefore a failed display.

**Preferred:** show independently useful mathematical information that distinguishes this object from another object of the same type.  Use whichever data are already cheap and canonical for the object, for example:

- defining data or a mathematical expression/presentation;
- source and target of a map/functor, index set of a family, or selected generators/relations;
- cheap characterizing invariants such as rank, signature, degree, cardinality, or category placement;
- the actual members/values of a finite family or finite set;
- for an infinite/lazy object, a defining formula, indexing datum, or bounded cheap window when one is canonically and safely available.

An optional human-readable name may prefix this information, but it may never be the entire payload.  Category membership alone is acceptable only when it adds genuine information not already tautological from construction and no more informative cheap defining datum exists.  A canonical symbolic spelling is also meaningful data: `NN = {0, 1, 2, ...}` communicates a mathematical object; `Natural numbers` merely renames its type.

Displays must remain semantic rather than computationally invasive.  Do not enumerate an unknown/infinite set, trigger an expensive classification merely to print an object, expose backend coordinates/storage, or make display depend on nondeterministic engine state.  Prefer a concise view into already-owned defining data.  `repr`, LaTeX/`show`, rich display, and container/family displays are all governed by this rule.

Review display methods adversarially: ask what a mathematician learns from the output after deleting the Python class/type name from their memory.  If the answer is “nothing”, the display is not acceptable.

#### `STY-189`: Display leaks an internal refinement/type owner -> render through the public mathematical operation

The object that implements a result may live in a highly refined category without that refinement being part of the result the user asked to see.  Displays follow the **semantic operation and its mathematical codomain**, not the most specific internal parent/classifier that happened to compute it.

**Bad:** `L.module_generators()` for a lattice prints `"Lattice-generator family"` merely because the module is currently refined as a lattice.  The operation is module-theoretic: every represented free module `Free_R(S)` has its canonical generating set/image.  The lattice refinement adds no new datum to that result, so mentioning it leaks implementation/type-theoretic routing into the public view.

**Preferred:** display the generic mathematical result, e.g. the generator image `{e_0, e_1}` (or the indexing set/presentation when that is the operation requested).  If a genuinely stronger construction exists — for example a selected root basis with root-specific operations or invariants — then a root-specific method may return and display that refined object because the refinement is mathematically part of that result.

Use the same rule for forgetful images, underlying objects, Hom-elements, functor images, subobjects, and classifier refinements: internal refinement is allowed to improve implementation and available methods, but it does not automatically earn a word in the default display.  A public display should be invariant under replacing the implementation by an equivalent stronger internal refinement whenever the mathematical result requested by the user is unchanged.

#### `STY-190`: Derived accessor reconstructs a canonical underlying object -> construct once and reuse it

When a mathematical object is defined by applying an existing construction and then adding structure, that underlying construction is part of the object's construction data, not something to be synthesized later when an accessor is called.

**Bad:** construct a lattice from ad hoc coordinate/index fields, then have `module_generating_set()`, `module_generators()`, or `unformed_module()` manufacture module-like views post hoc.  This duplicates `Free_R(S)`, permits the synthetic view to drift from the object that should define it, and hides whether the stronger object really lies over the claimed weaker one.

**Preferred:** construct `M = Free_R(S)` first, then construct the lattice/form/module refinement from the actual object `M` and the additional form datum.  Retain `M` as defining data and establish inherited module operations through the immediate category constructor. `unformed_module()` exposes `M`; generator operations use the same selected module datum. `OWN-16` and `CON-16` prohibit constructing a second module connected by public identification maps.  Do not keep a second indexing set, generator family, presentation, or coordinate parent merely to make inherited methods appear to work.

The same rule applies to free objects, quotients, localizations, scalar restriction/extension, formed objects, group actions, graded objects, subobjects, and functor images: if `X` is mathematically constructed as `G(Y, datum)`, then `Y` and the structural maps required by that construction are first-class data.  An accessor exposes those data; it does not recreate an isomorphic substitute from metadata.

A stronger object may of course use a distinct parent so that two choices of added structure remain distinct.  That does not make its underlying object fictitious: the distinct structured parent must still retain the actual weaker datum and inherit its operations through the construction chain (`OWN-16`).

#### `STY-191`: Comment or docstring teaches standard mathematics -> state the convention, cite the source, delete the lesson

The reader of this repository's source is a mathematician.  A comment or docstring states what the reader cannot supply from the code and their own training: the convention in force where several exist (reduced or unreduced homology, left or right action, which duality functor), as `lean-categories` fixes it or as the engine returns it, an engine's input demand or output shape (with its `TRAPS.md` row), the hypothesis under which a criterion applies, and the citation.  It never derives, motivates, or teaches the mathematics the code uses.

**Bad:** a docstring explaining that a graph is a 1-dimensional complex, that \(H_1\) is therefore the whole cycle space, and that \(\pi_1\) is free of rank \(E - V + C\), above a function that calls `minimum_cycle_basis`.

**Preferred:** "Sage returns reduced homology, so \(H_0\) has rank one less than the number of components." followed by the call.

The test: delete the paragraph and ask whether a mathematician reading the code loses anything they could not supply.  If not, it was a lesson.  A derivation that genuinely belongs somewhere belongs in the docs book or a cited source, and the code cites it.

### Review rule for new imperative code

Before accepting a new global helper, explicit `for`/`while`, mutable accumulator, cache, registry, runtime probe, or bespoke data structure, check the catalogue above and answer:

1. On which mathematical object does `lean-categories` place this operation?
2. Can the user discover it from that object with tab completion?
3. Is this exactly map/filter/fold/search/group/flatten/count/queue/traversal syntax already named by Python or a dependency?
4. Is there already a repository abstraction for the same mathematical operation?
5. Does the same skeleton occur elsewhere, implying a missing abstraction rather than several loops to shorten?
6. Can the computation remain lazy or finite-support instead of materializing a whole family?
7. Is the loop genuinely stateful mathematics/algorithmics?  If yes, keep it explicit and use the standard worklist/data structure.
8. Does adding this specialized feature force an ancestor to import or name the descendant?  If yes, recheck dependency direction.
9. Does a backend already implement the generic algorithm?  If yes, delegate and cross back.

A construct that survives these questions is allowed.  The catalogue exists to make the routine cases routine and to keep review attention on the mathematics.

* * *

### 1. Presentation Architecture (`ARC-*`)

#### `ARC-00`: The Preamble Is a Closed Universe Over Its Engines

- **Rule**: Once code enters the public preamble API, it remains in the preamble universe.
  The preamble does not extend Sage, wrap Sage's public object model, or provide an interoperability layer with ordinary Sage objects.
  It is an independent interface to the mathematics `lean-categories` formalizes, built on top of computational services such as Sage, Singular, GAP, Julia, OSCAR, or Macaulay2.
  Every publicly constructible parent, element, morphism, category, subobject, tensor, ideal, group, ring, module, algebra, scheme, and derived construction is a preamble object and composes only through preamble APIs.

- **Rationale**: The backend boundary is an implementation boundary, not part of the mathematical language available to users or ordinary repository code.
  If a mathematical operation must leave the preamble universe in order to continue, then the missing result, operation, or construction is presented in the preamble; if `lean-categories` does not formalize it, it is requested there.
  Backend choice must be replaceable without changing any caller-visible object, element, signature, or method.

- **Violation Example**: Treating preamble `ZZ` as a view of Sage `ZZ`; `from sage.all import *` inside the public preamble session; leaving Sage's preparser binding `Integer` or `RealNumber` to raw Sage element constructors; returning a Sage integer, vector, ideal, group element, matrix, or homset from a public operation; requiring callers to construct a Sage object and pass it into a preamble constructor; documenting a method as "use Sage's object here"; exposing an engine so downstream code can continue the computation outside the preamble.

- **Correct Example**: `ZZ(3)` is an element of preamble `ZZ`; the session's integer-literal constructor resolves to that same preamble integer construction; `ZZ**2` has preamble module elements; `Groups.C(4)` has preamble group elements.  A Smith-form implementation may privately translate these objects to Sage `ZZ`, Sage free modules, and FGP data, but the caller sees only preamble inputs and preamble outputs.

#### `ARC-01`: Present Categories and Universal Properties Through the Category Framework

- **Rule**: Present the categories, morphisms, functors, adjunctions, and universal constructions `lean-categories` formalizes through the repository's category framework.  Never define one here; a missing one is requested from `lean-categories`.

- **Rationale**: Categories and universal properties are the mathematical foundation, and `lean-categories` is its single authority.
  Presenting them through one framework gives consistent compositional behavior across modules.

- **Violation Example**: Presenting an ideal or basis as an isolated tuple or matrix operation without the category, module, or algebra structure `lean-categories` places it in; defining a category in research because `lean-categories` lacks it.

#### `ARC-02`: Morphism-Centric Subobjects and Witness Placement

- **Rule**: Represent subobjects as pairs $(S, \iota: S \hookrightarrow M)$.
  Place predicates, isometries, embeddings, and containment checks on morphism spaces or hom-sets.

- **Rationale**: Mathematical invariants depend on the embedding morphism, not on presentation-dependent coordinate choices.

- **Violation Example**: Storing ambient coordinates or adding `ambient=` parameters directly to parent objects.

#### `ARC-03`: Build Structural Objects Before Downstream Numerical Invariants

- **Rule**: Never bypass an intermediate mathematical object or functorial stage (such as the localized module $M_{\mathfrak{p}} = M \otimes_R R_{\mathfrak{p}}$, base-changed algebras $K \otimes_R \mathcal{O}$, or derived complexes) to compute a single numerical scalar or pointwise fiber (such as $\dim_{\kappa(\mathfrak{p})}(M \otimes_R \kappa(\mathfrak{p}))$). Always construct the foundational parent object and base-change/localization functor first; derive pointwise invariants as generic operations on the resulting object.

- **Rationale**: Bypassing structural objects destroys mathematical compression and composability.
  When the structural object exists ($M_{\mathfrak{p}}$ as an $R_{\mathfrak{p}}$-module), all local invariants (rank, minimal generators, local torsion, localization of morphisms) become generic consequences of base change.
  Skipping to point queries forces every downstream invariant to reinvent ad-hoc algorithmic logic.

- **Violation Example**: Implementing `local_number_of_generators(p)` by evaluating the residue field vector-space dimension $M \otimes_R \kappa(\mathfrak{p})$ while the localized module $M_{\mathfrak{p}}$ over the local ring $R_{\mathfrak{p}}$ remains absent from the category layer.

#### `ARC-04`: Preamble Objects Over Interchangeable Computational Services

- **Rule**: The objects, elements, morphisms, categories, subobjects, universal properties, and functors a session holds are preamble objects presenting `lean-categories`' mathematics.
  Sage/Singular/GAP/Julia/OSCAR/M2/etc. are interchangeable computational services behind those objects.
  The preamble neither subclasses their mathematical universe nor exposes it as an alternate API.
  No CAS-specific object, element, category membership, constructor, or coercion is needed to state, construct, or use preamble mathematics.

- **Rationale**: `lean-categories` states what an object is, and the preamble's category graph is the single surface presenting it.
  A computational engine only supplies untrusted computations behind that surface, so the engine choice never enters the statement of the mathematics, and engines remain swappable.

- **Violation Example**: Requiring a CAS-specific category membership or class (Sage, Singular, GAP, OSCAR, or Macaulay2-specific) to state, construct, or identify an object.

#### `ARC-05`: Preamble Parents and Elements Are Outside Every Engine

- **Rule**: An owned mathematical object is a parent constructed through the owned category chain, and its elements are elements of that owned parent.
  Backend parents and backend elements are private computational representations only.
  No Sage/Julia/GAP/OSCAR object is the public parent or public element merely because an internal algorithm delegates to that system.
  No backend constructor receives an owned parent or owned element directly; private adapter code first converts every input to backend representations.

- **Rationale**: The preamble boundary is a firewall around every public value, not only around parent objects.
  If a preamble parent returns Sage elements, then Sage's element parent, coercion graph, methods, and representation remain part of the effective public object model even when the parent itself is nominally the preamble's.
  That is the same inversion at the element level.

- **Violation Example**: `ZZ(3).parent() is SageZZ`; an owned free module whose `module_generator(i)` is a Sage free-module element; an owned group whose `group_generators()` are GAP/Sage group elements; passing an owned ring element directly to `FGP_Module`, `FreeModule`, or a GAP constructor.

- **Correct Example**: Owned `ZZ` has owned integer elements.  An owned free module has owned module elements whose coefficients lie in owned `ZZ`.  A private FGP adapter converts the owned ring, presentation matrix, and elements to Sage `ZZ`, a Sage free module, and Sage FGP elements, performs the computation, and converts the answer back to owned elements and morphisms before returning.

#### `ARC-06`: Backend Adoption Creates a New Preamble Object; It Is Never Reclassification or a Facade

- **Rule**: Importing or selecting a backend representation constructs or attaches private computational state for an independently owned object.
  It does not reclass the backend parent, expose the backend parent as a facade, or reuse backend elements as the owned object's elements.
  Backend identity is never owned-object identity.

- **Rationale**: Reclassification and facade parenting both leave the backend's object model in the public one: reclassification mutates the backend object, while a facade leaves backend elements and coercions authoritative.
  The owned category must instead control parents, elements, operations, equality, morphisms, and public return types; the backend is only an implementation service behind private crossings.

- **Violation Example**: A post-init hook that refines a Sage group in place; `Parent(..., facade=sage_free_module)` for an owned module; `OwnedRingView._element_constructor_` returning `SageZZ(value)`; rebuilding or preserving a Sage Cython element class as the element class of an owned group.

- **Correct Example**: `own_group(G_backend)` returns an owned group with owned group elements and a private conversion between those elements and `G_backend` elements.  `own_free_module(F_backend)` returns an owned free module with owned coefficient-bearing elements and privately records `F_backend` only as an optional computation service.  Neither backend parent nor its elements are changed or exposed.

#### `ARC-07`: A Morphism Is Asked of Its Endpoints

- **Rule**: The morphisms from `A` to `B` are asked of the endpoints, `A.Mor(B)`, so the owned hook of their category chooses the object.
  A category is named at the call site only when the morphism deliberately lives in a coarser owned category, for a map of underlying sets.
  **Owner ruling, 2026-10-14:** "`A.Mor(B) := A.ambient_category().Mor(A, B)`. It doesn't even make sense when `A`, `B` don't share an ambient category. And the morphisms of a category are determined by the mathematics, not some random conventional choice."  The ambient category is the category whose constructor built `A`, recorded at construction, with every axiom removed whose subcategory is full, that is, has the same arrows as its base (finite sets, commutative algebras); a data subcategory, and an axiom subcategory that is not full (unital algebras, whose arrows preserve the unit), keep their arrows. In the code an axiom class marks itself non-full by declaring its own `_MorCategory`.  `A.Mor(B)` asserts that `B` lies in it; there is no default chosen by convention, linearization or a join of the endpoints' categories.
  **Owner ruling, 2026-10-16:** an object that is also a category, such as a Mor category that is also a group (`O(L) = Aut(L)`) or a monoid (`End(Δ0)`), has both readings, and they do not compete: "It's both. Obviously X.Mor(Y) = group homomorphisms for groups, because X has an entire *poset* of ambient categories and you take the \"nearest\" one: X is in G which is in Cat, even if X is in Cat itself."  So `X.Mor(Y)`, `X.End()`, `X.Aut()` and `X.identity()` are asked of `X` as an object of its nearest ambient category (`Groups` for `O(L)`), while the category-level operations of `X` as a category take its objects as arguments: `X.Mor(f, g)`, `X.End(f)`, `X.Aut(f)`, `X.Mono(f, g)`, `X.identity(f)` are the 2-arrows between the arrows `f`, `g` it holds as objects. The two are told apart by what is asked of whom, never by a convention chosen per class.
  **`Mor` is the only spelling the preamble universe ever uses.**  `Hom` names Sage's construction, which is a backend engine if it is used at all: it may appear inside a private adapter and nowhere else.

- **Rationale**: `Mor(A, B)` is a category, not a set.  Its objects are the morphisms $A \to B$, and every set is a category -- the discrete one -- so the set case is an instance rather than a competing kind of answer, and enrichment is structure carried by the same object rather than a different return.  Naming a category at the call site restates what the endpoints already know, and when the name is Sage's it asks Sage to admit owned objects it does not hold.

  Reserving `Hom` for Sage is what makes the boundary hold by construction rather than by vigilance.  Sage's coercion machinery calls `X.Hom(Y, category)` internally, naming its own `SetsWithPartialMaps`; while `Hom` was the owned spelling, those internal calls landed in owned code and failed there.  With `Mor` owned and `Hom` left to Sage, an engine call reaches the engine and an owned call reaches the owned category, and neither can be mistaken for the other.

- **Violation Example**: defining or calling `A.Hom(B)` anywhere in the preamble; `Hom(source, target, Groups())` with owned groups as endpoints; `Hom(base_ring, self, Rings())` inside an owned algebra; a category carrying `Hom` as an alias for its own morphism construction.

- **Correct Example**: `A.Mor(B)` for the morphisms between two owned objects; `Hom` appearing only where a private adapter hands objects to Sage.

#### `ARC-08`: Engine Availability Does Not Define Mathematical Existence

- **Rule**: The mathematical data of an owned object is sufficient to state and construct that object independently of any computation engine.
  A backend may be present, absent, or replaceable without changing the object's defining mathematical data or identity.
  A backend's answer never changes an object's category: it is untrusted.  Placement comes from construction, including routing on a cheap computation that a `lean-categories` theorem makes equivalent to the property (`CON-07`); a computed membership answer goes to its caller only.  The backend's class or availability is never category data either.
  Missing backend support limits a computation; it does not turn the mathematical object into a backend object or make the object cease to exist.

- **Rationale**: A chosen presentation `F_1 -> F_0 -> M`, for example, already defines the presented module.
  A Sage FGP module can accelerate Smith-form computations when the coefficient ring admits that engine, but it is not the definition of `M`.
  Keeping those facts separate makes backend choice genuinely optional and interchangeable.

- **Violation Example**: Refusing to construct a presented module because Sage cannot build an FGP module over its coefficient ring; selecting the public class or category by checking which Sage implementation class happened to be available.

- **Correct Example**: Retain the owned presentation morphism and tensor-valued relation matrix independently of any Smith engine.  Expose an algorithmic method only where its implementation is supplied by category structure, or keep a mathematically general method with an informative assertion stating the stronger mathematical hypothesis under which the current algorithm is total.  Missing engine support is handled at the private engineering boundary, never represented as a mathematical `NotImplementedError` result.

#### `ARC-09`: Fundamental Mathematical Objects Are First-Class Before Their Refinements

- **Rule**: When a standard mathematical object is not already canonically an instance of a presented universal construction, present it with a preamble parent in the category `lean-categories` places it in before implementing any of its specializations.
  When it *is* canonically an existing construction, use that construction rather than minting a parallel parent.
  Additional algebraic, geometric, topological, smooth, scheme-theoretic, group, or representation-theoretic structures are refinements or functorial constructions on the same mathematical object; they do not replace its underlying identity.
  Do not force the object to live as a backend object or one particular richer structure, but equally do not duplicate an object already supplied by `Hom`, `End`, tensor product, quotient, subobject, free object, or another universal construction.

- **Rationale**: A fundamental mathematical object can be the common domain on which many theories meet.
  If it is absent, every higher construction invents its own representation and API, so backend matrix methods appear in tensors, matrix multiplication appears in generic rings, and geometric structure has nowhere canonical to attach.
  Presenting that object first lets later category refinements contribute exactly the operations their hypotheses justify in `lean-categories`.

- **Violation Example**: Implementing every finite matrix as `tensor.matrix(...)`; returning Sage `MatrixSpace(R,m,n)` for rectangular matrices; creating a second matrix parent even though `Hom_R(F_R([n]),F_R([m]))` already is the canonical matrix object; encoding a matrix scheme or matrix group as a separate unrelated object.

- **Correct Example**: For the canonical finite ordered set `[n]`, `F_R([n])` is the free module with its canonical framing.  Define `M_{m,n}(R)` as the existing Hom object `Hom_R(F_R([n]),F_R([m]))`; its elements acquire matrix entry/row/column/normal-form methods from the Hom category when both endpoints have these canonical framings.  `M_n(R)=End_R(F_R([n]))` inherits composition as multiplication and may acquire further algebra/Lie/geometric refinements without changing object identity.

#### `ARC-10`: Canonical Identifications Are Object Identity, Not Conversion APIs

- **Rule**: When standard notation names an object that is canonically an existing owned construction, implement the notation as that construction itself rather than as a new parent plus conversion maps.
  Preserve the canonical chosen data that makes the identification literal.

- **Rationale**: Parallel parents for canonically identical objects create artificial coercions, duplicate APIs, and force downstream code to choose representations that mathematics does not distinguish.

- **Violation Example**: Creating a distinct `MatrixSpace(R,m,n)` parent plus `as_module_morphism()` even though the canonical framings identify it with `Hom_R(F_R([n]),F_R([m]))`; creating a separate endomorphism-matrix ring instead of using `End_R(F_R([n]))`.

- **Correct Example**: `[n]` is the canonical finite ordered set, `F_R([n])` is the corresponding canonically framed free module, and `MatrixSpace(R,m,n)` returns `F_R([n]).Mor(F_R([m]))` with the matrix-Mor refinement installed.  A matrix element *is* that module morphism; `matrix()` is its coordinate array/object only when such a coordinate view is requested, not another mathematical object.

#### `ARC-11`: Export Aggregators Are Not Architectural Dependencies

- **Rule**: Internal code imports a mathematical construction from the module that defines it, or from a deliberately dependency-light core module for that theory.
  Package `__init__.py` files, session aggregators such as `preamble.all`, catalogues, and convenience export surfaces are leaves of the dependency graph; foundational category/module/ring/algebra code never imports through them.

- **Rationale**: An aggregator describes what a user may import together; it does not state a mathematical dependency.  Using it internally makes every exported higher construction an implicit dependency of every lower one, creates circular imports, and lets import order determine which mathematical structures exist.

- **Violation Example**: `modules/connections.py` importing `KahlerDifferentials` from `categories.algebras.__init__`, while that aggregator imports finitely presented algebras which import the modules package; a core functor importing through `preamble.all`; loading the lattice catalogue before the categories on which its objects depend.

- **Correct Example**: A connection module imports `KahlerDifferentials` from `algebras.kahler_differentials`; the session aggregator imports both only after their defining modules are available.  The dependency graph follows mathematical construction dependencies and is independent of session import order.

#### `ARC-12`: Operations Live Where `lean-categories` Places Them

- **Rule**: Public mathematical operations are methods on the element, parent/object, category, morphism, Homset, functor, or other mathematical object whose structure determines the operation and its admissible inputs, as `lean-categories` places it.  If a category `C` has products, the product construction is a method of `C`, e.g. `C.product(factors)`; if a morphism has a kernel in its category, expose that through the morphism/Hom/category API; if an element has an operation, expose it on the element.

  **The free-standing global name is itself the defect.**  It is a violation whether or not the body is correct, whether or not the dispatch is generic, and whether or not it forwards immediately to the right owner.  A global that forwards perfectly still publishes a second name for the operation, and the second name is the thing being banned.  Judging such a global by the quality of its implementation is the standard misreading of this rule.

  The ban covers every public global whose arguments include a mathematical object, with no exemption by kind: constructions (`Product`, `Coproduct`, `TensorProduct`, `Subobjects`, `Kernel`, `Cokernel`, `Pushout`), ring and module constructors (`Localization`, `PrimeLocalization`, `QuotientRing`, `FractionField`), category factories, adopters and refiners, and predicates alike.  Reading "operations" as though it excluded constructors is the second standard misreading.  A constructor is an operation on the object it is handed.

- **Call-site test**: ask whether an object already in hand determines the operation.  `Localization(A, f)`, `Subobjects(X)`, `Product(X, Y)`, `Kernel(f)` each name their owner in argument position, so each must be written `A.localization(f)`, `X.Subobjects()`, `C.product([X, Y])`, `f.kernel()`.  Where no object is in hand, the name builds a specimen out of plain data -- `AffineSpace(2, QQ)`, `Lattices(ZZ)("E8")` -- and belongs to a catalogue namespace rather than to a global function.  There is no third case.  Reserving `Hom` for Sage so that the owned spelling is `C.Mor(A, B)` is this same rule already applied, and is why the boundary there holds by construction.

- **Notation, and its limit**: operator syntax may delegate to the owner: `X * Y`, `L + M`, `L ** n`, `~S`.  An operator publishes no name to look up, so it adds no second language.  A named global does.  "It delegates immediately to the owning object" describes how a violation is implemented; it is not a licence to write one.

- **Rationale**: Sage is a discovery-oriented mathematical language.  In an interactive session the user should be able to construct the mathematical object they know, type `<TAB>`, and discover the operations that make sense for that object.  The receiving object supplies both namespace and domain information: `C.<TAB>` answers what the category can construct; `M.<TAB>` what the module supports; `f.<TAB>` what can be done with the morphism; `H.<TAB>` what the Homset knows; `x.<TAB>` what operations belong to the element.  A flat global namespace destroys that locality.  Seeing `Product`, `Kernel`, `Orbit`, or `TensorProduct` globally does not tell the user whether the function expects categories, parents, elements, morphisms, finite families, or some mixture, so using the language requires prior knowledge of the entire global API or constant documentation lookup.  This is the GAP/Julia-style failure mode the preamble is specifically intended to avoid.

  Placement and implementation dataflow follow from the same rule.  Presenting `C` as having products includes wiring the implementation of `C` to construct its selected products.  The information flows from `C` to `C.product(...)`, not from a global `Product(...)` dispatcher back into every possible category.  Consequently the code implementing the operation belongs in the receiver's subtree, and adding the operation to a new category does not require extending a global switchboard.

- **Violation Example**: Exporting a global `Product(X, Y)` leaves its domain unknowable from the name alone: does `Product(x, y)` multiply natural-number elements, form a categorical product of `Sets()` with itself, construct a product of two objects of a category, or accept a family of categories?  Likewise global `Kernel(f)`, `TensorProduct(X, Y)`, `Orbit(G, x)`, or `_morphisms_agree(f, g)` force the user or caller to know an external function catalogue and force the implementation to rediscover the relevant receiver from its arguments.  A stand-alone `Product` that imports modules, sets, schemes, and algebras is one concrete consequence of this wrong API shape, but the free-standing operation is already the primary defect even if its dispatcher were perfectly generic.

  Two further shapes, both of which have passed review by being argued rather than seen.  Keeping `Localization(A, f)` on the grounds that its dispatch was cleaned up, or that it now forwards to `A.localization(f)`: the surviving global name is the violation, and a clean body only makes it harder to notice.  Building new code on an already-catalogued global -- writing `Subobjects(X)`, `Pushout(f, g)` or `TensorSquare(M)` in a fresh category because those names are importable -- which spreads the defect while adding a feature, and cites the presence of the global as its own justification.

- **Correct Example**: Write `C = Sets()` and inspect `C.<TAB>` to discover `C.product(...)`; if `X` and `Y` are objects with `C = X.ambient_category()`, notation such as `X * Y` may delegate to `C.product([X, Y])`.  `Modules(R)` supplies its own product/biproduct method in the module-category subtree; a scheme category supplies its product/fiber-product method in the scheme subtree.  A morphism exposes `f.kernel()` when its category supports kernels; a Homset exposes Hom-level constructions and equality; an element exposes its own operations.  The user discovers valid mathematics by navigating from objects already in hand rather than searching a global language.

#### `ARC-13`: Mathematical Structure Is Independent of Import Order and Call History

- **Rule**: The mathematical structure and category placement of a preamble object are determined by its construction data, not by which module happened to finish importing first or which accessor was called earlier in the session.
  Do not use import-cycle flags, `ImportError` fallbacks, lazy "try again on the next lookup" installation, or incidental method calls to make standard structure appear on an already existing object.
  A later refinement corresponds only to a newly supplied chosen datum passed through a construction; neither a computed answer nor runtime availability of implementation code refines an object.

- **Rationale**: Import order and call history are properties of the Python process, not of the mathematical object.
  If `R` is canonically an `R`-module and `R`-algebra, or an object carries a selected decomposition, those facts cannot depend on whether the module/algebra package had completed importing when `R` was first requested.
  History-dependent mutation makes identical mathematical expressions expose different APIs in different sessions and turns initialization order into hidden state.

- **Violation Example**: `_own_ring()` attempting to install the canonical self-module/self-algebra structure, catching `ImportError`, and deferring that mathematical structure until a later lookup; an accessor that calls `refine(...)` merely because asking the question made another category implementation importable.

- **Correct Example**: Canonical self-structure is part of the ring construction/category packet from the outset, or is supplied by a dependency-safe structure functor whose result is deterministic for the same ring.  A later refinement occurs only when a new chosen datum is supplied through a construction.

#### `ARC-14`: Equivalent Universal Data Has One Authoritative Representation

- **Rule**: When `lean-categories` gives equivalent presentations of the same universal structure, choose one datum to store and derive the others mechanically by the formulas it proves.
  Do not require subclasses or sibling implementations to independently encode mutually determining units, counits, Hom-set bijections, opposite/product-domain functor machinery, or parallel Hom-like parents for the same universal object.

- **Rationale**: Equivalent formulations are mathematical compression.  Implementing every equivalent formulation independently creates coherence obligations that the mathematics already solves and multiplies LOC without adding expressive power.
  The derived interfaces should be consequences of one structure, not separate sources of truth that can drift apart.

- **Violation Example**: Every adjunction subclass independently implementing `unit`, `counit`, `hom_set_isomorphism_forward`, and `hom_set_isomorphism_inverse`; a separate `ContravariantFunctor` reimplementing functor caching and endpoint checks instead of using a functor on `C^op`; a separate `Bifunctor` object model instead of a functor on `C x D`; represented pairings using a second `PairingSpace` even when `Hom_R(X tensor Y, W)` exists.

- **Correct Example**: An adjunction records one standard presentation—e.g. the adjoint functors with unit and counit—and derives the Hom bijection by composition.  Contravariant and bifunctor convenience syntax delegates to ordinary `Functor` on the preamble's opposite/product category.  A represented bilinear pairing is literally an element of `Hom_R(TensorProduct(X,Y), W)`.

#### `ARC-15`: Upward Knowledge of Descendants Is an Architectural Smell

- **Rule**: Treat knowledge flowing from a general category, construction, or foundational module toward one of its specialized descendants as suspicious by default.  This is a code-smell heuristic, not an absolute prohibition: there are legitimate exceptional cases, but a supercategory or generic construction should normally not import, name, enumerate, or branch on its subcategories.  Adding a new specialized category should ordinarily consist of adding a modular subtree whose imports point inward toward existing foundations; it should not require edits to unrelated ancestors merely so they learn that the new category exists.

- **Rationale**: Category inheritance and mathematical specialization are naturally extensible when dependencies point from specialized theories toward the general structures they refine.  If an ancestor must know every descendant, the blast radius of presenting one new category grows with the size of the entire hierarchy, generic code accumulates special cases, and independent subtrees cease to be independently loadable or maintainable.  The smell is especially strong when a generic construction such as products, Homs, kernels, scalar extension, or equality must be edited to mention a highly specialized descendant.

- **Smell Example**: `Cat.Products` or another generic categorical layer importing `MyVerySpecialResearchLatticeCategory` so that products work there; `Modules(R)` importing a particular arithmetic-lattice subcategory merely to recognize it; a root construction maintaining a registry or conditional chain of every specialized theory that supports it.

- **Healthy Shape**: `MyVerySpecialResearchLatticeCategory`, presenting a category `lean-categories` formalizes, imports the general category machinery, declares the supercategories `lean-categories` states, and supplies its specialized methods/refinements inside its own subtree.  Existing ancestors remain unchanged.  Imports therefore flow from the specialized subtree toward the stable foundation, while generic ancestors stay oblivious to the existence of the new descendant unless there is a specific mathematical reason otherwise.

#### `ARC-16`: Finitary Coordinates Are Computational Specializations, Not the Mathematical Architecture

- **Rule**: State objects and operations through their mathematical semantics first: preamble sets/families, finite-support elements, Homs, subobjects, kernels/images, products/coproducts, actions, quotients, tensor constructions, and universal maps.  Finite enumeration, bases, coordinates, rows/columns, block matrices, and exhaustive checks are algorithms/representations supplied underneath those objects.  Ordinary mathematical consumers do not lower to finite coordinates merely because today's easiest algorithm is finite.

- **Rationale**: Premature lowering makes finiteness contagious.  Once cohomology, exactness, intersections, actions, or divisor groups know about row counts and Python tuples, extending the underlying object to an infinite framing or another representation requires rewriting every consumer.  A semantic layer localizes the finite assumption: a finite-free Hom may use matrices while an infinite Hom later uses formal blocks, sparse operators, callable maps, or another engine without changing callers.

- **Violation Example**: `FreeResolution.is_exact()` comparing backend row modules instead of image and kernel subobjects; `Cohomology` rebuilding cycles/boundaries from basis matrices; a formal divisor group forcing its entire prime-divisor index set to be finite because individual divisors have finite support; constructing a block morphism by concatenating finite row arrays.

- **Correct Example**: State exactness as `im(d_1)=ker(epsilon)`, cohomology as `ker(d_n)/im(d_{n-1})`, subobject intersection as a pullback, and a divisor group as the free module on its prime-divisor set with finite-support elements.  The finite represented cases dispatch internally to matrix/Sage/Singular algorithms; future infinite cases supply different implementations of the same semantic methods.

#### `ARC-17`: Repair the Semantic API Before Writing a Local Numerical Workaround

- **Rule**: When a consumer needs a mathematical result canonically expressed through a presented semantic construction, the consumer calls that construction. It does not extract coordinates, matrices, rows, columns, basis vectors, engine objects, or finite presentations and reimplement the construction locally. If the required semantic method is missing, incomplete, or awkward to compose, improving that lower-level API is part of the implementation task. Do not preserve a local numerical workaround merely to keep the patch geographically small.

- **Rationale**: A common LLM failure mode is **myopic semantic lowering**: receive an honest mathematical object, immediately forget its semantics, compute on a convenient finite representation, and reconstruct an approximation to the mathematical result. One such patch looks harmless; dozens produce a second numerical implementation layer scattered through consumers. Every consumer then learns finiteness, basis choice, row/column conventions, matrix algorithms, and backend details, so an infinite-case implementation requires a repository-wide rewrite. The semantic API is the compression boundary: only `kernel`, `cokernel`, `image`, `pullback`, `quotient`, `torsion_subobject`, `is_torsion_free`, `dimension`, `Hom`, and analogous methods should know how their current representations are computed.

- **Violation Example**: Given `f : M -> N`, call `f.matrix()`, compute a backend nullspace, construct a free module on the nullspace rows, and manufacture an inclusion into `M`. This duplicates `f.kernel()` and hard-codes finite free coordinates in the caller. Likewise, decide whether an inclusion is primitive by taking gcds/minors of its matrix rather than asking whether its cokernel is torsion-free.

- **Correct Example**: `K = f.kernel()` returns the kernel together with its inclusion. A subobject inclusion `i : S -> M` is primitive exactly when `i.cokernel().is_torsion_free()`. The finite-free implementation of `kernel()` or `is_torsion_free()` may privately use nullspaces, Smith form, or determinants; an infinite implementation may use a sparse operator, formal presentation, or another engine. The consumer does not change.
  The live `ModuleMorphism.is_primitive()` already has the right shape: it asks injectivity and then returns `self.cokernel().is_torsion_free()`. Treat this as a model for structural predicates rather than replacing it with a matrix criterion in specialized consumers.

- **Extension Test**: After writing a consumer, mentally replace every finite-rank object by a plausible infinite analogue. If the consumer itself must change because it knows about matrix sizes, complete bases, exhaustive generator lists, or backend rows, the numerical boundary is probably too high. If only a low-level semantic method needs a new case, the architecture is correctly localized.

#### `ARC-18`: The Interface Is Judged by the Invalid Mathematics It Permits

- **Rule**: Design public constructors and methods adversarially against representation shortcuts.  A semantic API is insufficient if an equally public coordinate/vector/matrix path lets downstream code bypass the mathematical object and reimplement its theorems locally.  Close or privatize such hatches; force callers through parents, elements, Homs, structure morphisms, universal constructions, and preamble collections.

- **Rationale**: Encapsulation by convention does not survive repeated local implementation pressure.  An exposed numerical representation becomes training data for the next patch, and each patch silently acquires theorem hypotheses, basis conventions, and finite assumptions.  Semantic gating concentrates those proof obligations once.  The interface is therefore evaluated by asking not only “can correct mathematics be expressed?” but also “what plausible nonsense does this API make easy to express?”

- **Violation Example**: A public lattice element constructor accepts arbitrary coordinate lists; an owned morphism exposes a convenient raw matrix accessor used by ordinary consumers; a group action constructor accepts raw matrices without first constructing `rho:G->Aut(M)`.

- **Correct Example**: Elements are formed in their parent from named generators and finite-support mathematical data; matrix data may enter only at the narrow finite-framed Hom construction that returns a genuine morphism; all downstream operations stay on that morphism.  Assertions at likely misuse sites explain the mathematical ambiguity and name the correct construction.

#### `ARC-19`: Present at the Generality `lean-categories` Formalizes

- **Rule**: Present each notion at the hypotheses `lean-categories` states for it, then recover stronger cases by the parameter, axiom, subcategory, chosen structure, or algorithmic specialization it formalizes.  Before accepting an interface, test it conceptually by removing common accidental assumptions: finiteness, finite generation, freeness, projectivity, orderedness, enumerability, commutativity, and concrete coordinate realization.  An assumption the interface carries and the formalization lacks is an implementation defect; a hypothesis the formalization carries and the literature does not need is a request to `lean-categories`.

- **Rationale**: Overfitting the presentation to today's fixtures or backend makes every later generalization a migration.  A general semantic interface localizes future work: the finite/free case can have an optimized implementation without teaching every consumer that those hypotheses exist.  Extreme examples are design tests, not necessarily currently computable workloads.

- **Violation Example**: Present a framed module only for a finite ordered basis because the first implementation uses matrices; present a free module only from an integer rank; present formal divisors only over a finite list of possible prime divisors; place an operation on lattices when its definition only uses module structure and a form morphism.

- **Correct Example**: A free cover is a selected epimorphism `Free_R(S) -> M` for an arbitrary set `S`; `[n]` is the canonical finite ordered specialization. A categorical framing replaces the epimorphism by an isomorphism, relative to the same adjunction. Individual elements have finite support even when `S` is infinite or nonenumerable. Finite matrix realizations and rank-based algorithms are computational specializations; they do not restrict the category of augmented objects.

- **Sweep Question**: “If I drop one hypothesis from the current examples, does the formalized definition still apply?”  If yes, that hypothesis belongs to an implementation/subcategory, not the presentation.

#### `ARC-20`: Structured Objects Include Their Witnessing Arrows

- **Rule**: When the mathematical object is a subobject, quotient, image, re-presentation, or other structured occurrence of an underlying object, the witnessing morphism is part of the mathematical data and therefore part of identity/equality at that structured level.  Do not collapse the structured object to its underlying abstract object or to the image subset suggested by a coordinate realization.

- **Rationale**: A subobject of `Y` is represented by a monomorphism `i:X -> Y`; two copies of the same abstract `X` embedded by different monomorphisms are distinct subobjects.  Dually, quotients remember the epimorphism `Y -> Q`.  Forgetting the arrow loses exactly the relationship that downstream constructions—intersection, saturation, quotienting, pullback, factorization—consume.

- **Violation Example**: Compare subobjects only by their domains or Gram data; identify `L` with the image of `L -> L^#`; compare quotients only by invariant factors while ignoring the quotient maps.

- **Correct Example**: Subobject equality is equality in the subobject/slice construction and includes the inclusion; quotient equality includes the projection.  The underlying-object forgetful operation may return equal/isomorphic abstract objects without making the structured objects equal.

#### `ARC-21`: Categories of Arrows, Homs, and Functors Are First-Class Objects of `Cat`

- **Rule**: Present `Ar(C)`, `Fun(C,D)`, Hom categories, endomorphism/automorphism arrow categories, cores, slices, coslices, and analogous category constructions as actual objects of `Cat`, as `lean-categories` formalizes them, not as implementation namespaces around special Python classes.  Their objects/elements inherit ordinary categorical structure through the same graph as every other category.

- **Rationale**: A morphism is an element of a Hom object, Hom objects themselves participate in arrow-category structure, and functors/natural transformations form ordinary categories.  Making these constructions first-class centralizes method inheritance and eliminates parallel “morphism methods” or “functor utility” mechanisms that bypass the category graph.

- **Violation Example**: Treat morphisms as a third API species unrelated to Hom elements; attach special methods directly to a morphism wrapper because arrow categories are not represented; implement `Fun(C,D)` as a utility registry rather than a category.

- **Correct Example**: `Ar(C)` and `Fun(C,D)` are preamble categories; `Hom_C(A,B)` is the appropriate preamble Hom/category object; `End`/`Aut` refinements and their elements inherit through the same categorical construction machinery.  Convenience aliases may expose familiar syntax without creating a second object model.

#### `ARC-22`: Inherited Mathematics Propagates Through Named Functors and Composition

- **Rule**: When a structured category obtains operations from a less-structured mathematical object, represent the passage by the functor `lean-categories` formalizes and let operations propagate through composition.  Do not make every descendant independently reimplement obligations from `Sets`, modules, groups, or another underlying structure, and do not confuse a faithful/forgetful functor with literal object identity or a backend inheritance edge.

- **Rationale**: The same module can be viewed through its underlying additive group and set without those categories being identical.  A named functor records exactly what structure is forgotten and gives one route for cardinality, iteration, set maps, and other inherited operations.  Composition creates rollup points where a whole family of obligations is discharged once rather than leaf-by-leaf.

- **Violation Example**: A lattice implements `cardinality()` independently of its underlying module/set; every algebraic category duplicates set iteration; Python MRO order silently chooses one of several possible forgetful routes.

- **Correct Example**: Lattice structure maps to the underlying module by a presented functor, module structure maps toward its underlying set, and generic set operations are answered there.  Alternative canonical routes either coincide by construction or are related by a natural isomorphism `lean-categories` proves; MRO order never decides the mathematics.

#### `ARC-23`: Additional Structure Refines One Mathematical Object; It Does Not Create Wrapper Classes

- **Rule**: Prefer one generic preamble representation of a mathematical object together with categorical refinements for additional properties/structure.  Do not create a new concrete wrapper class for every combination of symmetric, alternating, integral, torsion, group-equivariant, graded, or similar refinements when the underlying datum is the same object plus additional structure/properties.

- **Rationale**: Parallel wrapper classes duplicate element behavior, Hom behavior, equality, construction, and backend conversion while obscuring the common object.  Category refinement lets one represented form/module/etc. acquire exactly the additional operations justified by its structure without changing identity or forcing conversions between wrappers.

- **Violation Example**: Separate concrete classes `SymmetricBilinearForm`, `IntegralBilinearForm`, `GroupLatticeForm`, and `TorsionBilinearForm` each storing the same module/form data and copying methods.

- **Correct Example**: Use one generic represented form/morphism object and one formed-module construction; refine it into symmetric/integral/nondegenerate/lattice/group-action categories as the construction places it.

#### `ARC-24`: Structural Functors Are Outputs of Category Constructions, Not a Parallel Hand-Written Graph

- **Rule**: A named category expression—root, classifier application, product/pullback, slice/coslice, core, or other construction—presenting a `lean-categories` category is the preamble's single source for its structural functors.  Canonical projection/forgetful/structural functors implied by that expression are derived from the construction and composed recursively.  Do not maintain a second manually authored “forgets-to” or preferred-path graph encoding the same relationships.

- **Rationale**: If `lean-categories` defines `C.A` by a classifier pullback over `C`, the projection `C.A -> C` is part of that definition.  Re-entering that edge in a separate registry duplicates truth and invites mismatches between category identity, method inheritance, and functor routing.  Structural recursion also makes adding a new category expression local rather than requiring registration in every ancestor/path table.

- **Violation Example**: Add `forgets_to = Modules(R)` beside a category whose defining expression already projects to modules; maintain BFS/preferred-functor tables for ancestor routes that the category expression canonically composes; hand-author every axiom projection.

- **Correct Example**: classifier/category constructors create their primary structural maps; `project(C.A,K)` composes the primary projection with `project(C,K)`.  Explicit alternative functors remain first-class when they are genuinely different mathematics, rather than entries in a duplicate hierarchy table.

#### `ARC-25`: Formed Mathematics Starts With the Arbitrary Form Actually Carried by the Object

- **Rule**: In formed-module/lattice mathematics, the base semantics use the declared bilinear/quadratic/sesquilinear form itself.  Do not silently import the standard Euclidean inner product, positive definiteness, nondegeneracy, or finite-dimensional coordinate geometry.  Additional hypotheses refine the category exactly where the mathematical notion requires them.

- **Rationale**: CAS vector APIs are saturated with Euclidean defaults (`dot_product`, standard norms, projections, Gram-Schmidt) whose answers are unrelated to an arbitrary form on the same underlying module.  Letting those operations leak into general formed code is a pervasive silent-wrongness source and makes degenerate/indefinite/infinite analogues impossible without rewriting consumers.

- **Violation Example**: Compute orthogonality by a backend vector dot product rather than `b`; define all lattices as nondegenerate because dual-coordinate code needs an inverse Gram matrix; use a positive-definite shortest-vector routine as the meaning of `roots()` or `norm()` on the base category.

- **Correct Example**: pairings/norms route through the object's form/correlation; radical and orthogonal complement are morphism/subobject constructions; positive-definite reduction/shortest-vector algorithms live behind the definite refinement while the general formed object remains valid for arbitrary forms.

#### `ARC-26`: Category, Object, Runtime Representation, and Presentation Are Distinct Levels

- **Rule**: Keep distinct the mathematical category, an object of that category, the runtime type representing such objects, the preamble/Sage category structure attached to that runtime type, chosen presentation data, and property-cut subcategories.  Equivalences or convenient representations do not collapse these levels into one noun or one identity relation.

- **Rationale**: Chosen enumeration/basis data can represent a finite set/free module without being the category itself; a runtime class can represent category objects without being the category; an object and its chosen presentation can be equivalent while carrying different structure.  Collapsing the levels promotes implementation choices into mathematics and makes later changes of representation appear to change the mathematics.

- **Violation Example**: Call the Python class of bundled finite-set objects “the category of finite sets”; identify finite free modules with based modules because a basis exists by choice; treat `Cat.of(SomeType)` as the mathematical category rather than one representation of its objects.

- **Correct Example**: explicitly name the `lean-categories` category and its morphisms, the objects it contains, the generated `ObjectType`/`ElementType` used at runtime, and any framing/enumeration/presentation as additional data/refinement.

* * *

### 2. Public Mathematical API (`API-*`)

#### `API-01`: Public Methods Return Owned Mathematics, Never Backend Objects or Elements

- **Rule**: Every public method on a preamble object returns a preamble value.
  Public methods never return a Sage module, Sage submodule, Sage vector, Sage matrix, Sage/GAP/Julia element, GAP model, engine pointer, engine parent, or another backend structure merely because that representation is convenient internally.
  Elements returned by an owned parent are owned elements parented by that owned parent.
  There is no public engine accessor or public engine-element escape hatch.

- **Rationale**: Once a raw backend parent or element escapes, every consumer can speak the engine's object model and the category layer no longer controls what can be stated.
  The public boundary therefore includes element identity and return types, not only method names on the parent.

- **Violation Example**: Public `cover()`, `relation_submodule()`, `coordinate_vector()`, `optimized()`, or `engine()` methods returning Sage objects from an owned presented module; `module_generator(i)` returning a Sage vector; `group_generators()` returning GAP/Sage elements; returning `kernel.V()` or a Sage submodule from an owned Hom computation.

- **Correct Example**: `presentation()` returns the preamble relation morphism, `presentation_matrix()` returns a tensor, `module_generator(i)` returns an element parented by the preamble module, `group_generators()` returns elements parented by the preamble group, `smith_form_module_generators()` returns preamble module elements in a preamble set, and `invariant_factor_form()` returns a preamble isomorphism.

#### `API-05`: Public APIs Accept Preamble Data, Never Raw Backend Objects

- **Rule**: The public boundary is closed on inputs as well as outputs.
  A public constructor or method does not accept a raw Sage/Singular/GAP/Julia/OSCAR/Macaulay2 parent, element, vector, matrix, ideal, morphism, category, or handle as an alternate input form.
  There are no convenience constructors whose purpose is to adopt, wrap, refine, or coerce a backend object into the preamble universe.
  Backend representations are created only by private adapters from preamble data.

- **Rationale**: Accepting raw backend data makes the backend object model a second public constructor language and forces public code to decide how backend identity, categories, coercions, elements, and chosen data map into preamble objects.
  That is the same backdoor as returning backend data, only on ingress.

- **Violation Example**: Public `own_ring(SageZZ)`, `own_group(SagePermutationGroup(...))`, `refine_free_module(SageFreeModule(...))`, `FinitelyPresentedModule(sage_submodule)`, or a morphism constructor that accepts a Sage `Map` as a supported public datum.

- **Correct Example**: Public `PolynomialRing(ZZ, "x")`, `FreeModule(ZZ, 3)`, `Groups.S(4)`, `presentation_morphism.cokernel()`, and `A.Mor(B)(...)` consume preamble objects and mathematical data.  Any Sage/GAP representation needed to execute them is selected and constructed privately after the public call has crossed the API boundary.

#### `API-02`: Coordinates Are a Finitely Supported Function; Support Is Its Condition Subset

- **Rule**: An element `v` of a module with a chosen basis `I` (a length-0 free resolution, `CAT-29`) is an `R`-linear combination of the basis elements.
  Its coordinates are `v.to_vector()`: the finitely supported function `a_v : I -> R`, an element of `R^(I)`, which is the subobject of `Sets().Mor(I, R)` cut out by finite support.
  `v.support()` is the condition subset `{i in I : a_v(i) != 0}` of `I` with its inclusion, lazy like every predicate subset: nothing is computed until a consumer asks for membership, a cardinality or an enumeration.
  This is the support of a divisor in `Z^1(X)`, `Pic(X)` or `Cl(X)` as well.
  Consumers evaluate `a_v`, compose it with morphisms, and enumerate the support when it is enumerable.
  No coordinate readout has a dictionary interface: `items`, `get`, `keys`, `values` and `monomial_coefficients` are Sage and Python notions with no mathematical referent.
  When an algorithm genuinely requires an ordered coordinate array, use the owned object whose mathematics describes that array.
  A coordinate vector may be a typed tensor when only variance/index data is intended.  A matrix of a linear map between finitely generated free modules is the corresponding Hom element
  `Hom_R(F_R(S), F_R(T))`, with basis the matrix units indexed by `T × S`; it is not replaced by a tensor or backend matrix.
  A public coordinate operation never returns a Sage vector or Sage matrix.

- **Rationale**: Coordinates depend on the chosen basis, but the coordinate object has intrinsic mathematics: it is a function, so its values, its support, its composites and its images are the operations of `Sets().Mor(I, R)` and its subsets.
  A dictionary keyed by labels pretends to be that function and replaces every one of those operations with index manipulation; building its support as a new finite set at each readout is also what made one rank-2 pairing cost milliseconds (2026-09-26).
  Raw backend arrays erase the structure in the same way; treating every array as a tensor erases it differently.

- **Violation Example**: `M.framing_coefficients(x).items()`; `x.monomial_coefficients()`; `coefficients.get(label, zero)`; a readout that builds the support as a new finite ordered set; `M.coordinate_vector(x)` returning `M_engine.V().coordinate_vector(...)`; representing `Hom_R(R^n,R^m)` by `tensor.matrix(...)`; passing a raw Sage matrix downstream to reconstruct a morphism later.

- **Correct Example**: `v.to_vector()(i)` is the coefficient of the basis element `i`; `v.support()` is a subset of `I` with its inclusion; `sum(a(i) * b(i) for i in v.support())` is a dot product over the support.  For finite free modules, `MatrixSpace(R,m,n)` is literally `Hom_R(F_R([n]),F_R([m]))`, and a matrix element is that module morphism itself.

#### `API-06`: The Session Namespace and Literal Constructors Are Owned

- **Rule**: The public session module exports only preamble mathematics and ordinary Python support objects explicitly chosen by the preamble.
  It never wildcard-imports a backend namespace.
  Interactive literal constructors installed or consulted by the host parser/preparser (`Integer`, `RealNumber`, complex-number constructors, generator syntax hooks, and analogous names) resolve to preamble constructions or ordinary Python literals according to the preamble language contract.

- **Rationale**: A closed object universe cannot be enforced only at method signatures if the session itself still publishes backend constructors or silently creates backend elements before the first preamble call.
  The parser is part of the public mathematical language.

- **Violation Example**: `from sage.all import *` followed by selectively shadowing a few names; leaving `Integer(3)` as Sage's integer while `ZZ(3)` is owned; allowing `matrix(...)` to remain Sage's constructor because no owned matrix spelling has shadowed it yet.

- **Correct Example**: The session binds `Integer` to the owned integer constructor, binds `MatrixSpace`/matrix notation to the matrix-Hom construction, and omits backend constructors that have no preamble meaning.  Backend imports remain module-private implementation dependencies.

#### `API-07`: The Global Session Namespace Is Not an Operation Catalogue

- **Rule**: Keep the public session namespace sparse in mathematical operations.  Global names are appropriate for canonical mathematical objects, category/object constructors, notation entry points, and deliberately chosen **session-language conveniences**; ordinary mathematical operations on already-constructed objects belong to methods on the objects where `lean-categories` places them.  Do not export a free-standing `Product`, `Kernel`, `Orbit`, etc. merely to shorten `owner.operation(...)` or to reproduce a GAP/Julia-style global operation catalogue.

- **Rationale**: Tab completion on a global namespace scales with the entire library and provides no type/domain context.  Tab completion on a preamble object is contextual documentation: the receiver already tells the user what kind of mathematics is being acted on and narrows the valid operations before any documentation is opened.  A small personal preamble may still deliberately include obvious ergonomic forms such as `lmap`/`lzip`; those are language conveniences, not alternative homes for mathematical operations that already have an owner.

- **Violation Example**: Adding `Product`, `Coproduct`, `Kernel`, `Cokernel`, `Orbit`, `Stabilizer`, `DirectSum`, `BaseChange`, `Dual`, or analogous operation functions to `preamble.all` so users call them by remembering global spellings.  Even if each function internally performs perfect categorical dispatch, the public interface still requires the user to know which arguments make each global meaningful.

- **Correct Example**: The session exposes `Sets`, `Modules`, `Groups`, rings such as `ZZ`, constructors needed to create mathematical objects, and a small deliberate set of obvious personal conveniences such as `lmap` and `lzip`.  From mathematical objects the user discovers `C.product`, `M.base_change`, `f.kernel`, `G.orbit`, `G.stabilizer`, Hom-level operations, or element methods by tab-completing the object in hand.

#### `API-08`: Session Use Is First-Class Use

- **Rule**: Do not classify a public preamble name as dead merely because repository source and tests do not call it.  The preamble exists to populate notebooks and REPL sessions, so deliberate session-only constructors, aliases, formatting helpers, and convenience functions are first-class API even when their internal call count is zero.  Before deleting an apparently unused public name, determine whether it is intentional session vocabulary and inspect its export/documentation history.

- **Rationale**: Static internal call graphs measure implementation reuse, not interactive usefulness.  A convenience such as `lmap(f, xs)` can be valuable precisely because a researcher types it at a prompt rather than because backend code imports it.  Treating all internally unused names as dead would systematically erase the purpose of a preamble.

- **Violation Example**: Running `rg lmap src tests`, finding only its definition, and deleting it as dead code without checking whether `preamble.all` is intended to expose it in research sessions.

- **Correct Example**: Keep a deliberate session helper with obvious stable semantics, export it from `preamble.all`, and assess it as part of the interactive language.  Remove a public name only after establishing that it is neither used internally nor intended as session vocabulary.

#### `API-09`: Interactive Representation Shows the Mathematical Element, Not Its Storage Coordinates

- **Rule**: Ordinary `repr`/LaTeX of owned elements should display the mathematical expression in the object's selected symbols/structure rather than a Python tuple, backend vector, flattened coordinate array, or implementation class.  Coordinate representations are explicit derived views through the selected framing and are never allowed to become the default identity of the element.

- **Rationale**: The first thing a researcher sees in a notebook trains how the object is conceptualized.  Printing `(1,2)` for elements of two different framed modules makes equal coordinate strings look like equal mathematical objects and encourages downstream coordinate programming.  A formal linear combination keeps the parent/framing semantics visible.

- **Violation Example**: A lattice element prints as `[1, 2]`; a quotient element prints only its Smith-coordinate vector; a generic module printer applies integer sign tricks that assume an ordered coefficient ring.

- **Correct Example**: An element of `Free_R(S)` renders as its finite formal `R`-linear combination of the actual symbols in `S`, using each coefficient/symbol's own representation.  Explicit `x.to_vector()` exposes coordinates when the researcher asks for them.

#### `API-10`: Public Mathematical Signatures Are Closed and Precise

- **Rule**: Public mathematical constructors and methods enumerate the exact mathematical inputs they accept and the mathematical result they return.  Do not expose arbitrary `*args`/`**kwargs` option bags, backend constructor passthrough, sentinel-driven polymorphism, or mode flags that change mathematical meaning/return shape.  Split genuinely different constructions into named methods/constructors or precise source-grounded overloads.

- **Rationale**: An open option bag delegates the definition of the preamble API to whichever backend version happens to receive it and hides required hypotheses/choices from both tab completion and static inspection.  Sentinel/mode polymorphism makes one name denote several different mathematical operations and encourages downstream branch-heavy handling.

- **Violation Example**: `NumberField(*args, **kwargs)` forwarding Sage's whole constructor surface; `foo(x, ambient=None)` where the optional ambient is actually the missing subobject witness; `normal_form(map=True)` changing the return object from a normal form to `(normal_form, map)`.

- **Correct Example**: provide named constructors for the exact number-field/presentation shapes the preamble presents; make subobject structure an inclusion morphism; return a normal-form isomorphism as the canonical result when the witness is mathematically part of the construction.  Private engine adapters may retain exact protocol-level option forwarding when it is quarantined behind the owned operation.

#### `API-11`: Expose Composable Mathematical Objects, Not Convenience Wrappers Around One Use

- **Rule**: When the useful result is itself a standard mathematical object—an invariant/value object, morphism, action, identity, inclusion, quotient map, functor, decomposition, etc.—expose that object directly.  Do not proliferate convenience predicates/actions whose bodies merely perform one obvious comparison/application of the richer object.

- **Rationale**: The object carries additional mathematics for free: equality, composition, kernel/image, restriction, factorization, transport, and reuse.  A one-use wrapper hides this structure and creates a parallel vocabulary that does not compose.

- **Violation Example**: `same_genus(other)` instead of comparing genus objects; `action_on_discriminant_element(g,x)` instead of exposing `O(L) -> O(A_L)`; constructing identity through an identity matrix instead of asking the Homset.

- **Correct Example**: return `genus()`, the induced action morphism/functor, and `Hom.identity()`; callers compose/apply/compare those objects using their ordinary mathematical APIs.

#### `API-12`: Prefer Named Positive Mathematical Predicates Over Negated API Expressions

- **Rule**: When the literature has a standard name for a complementary property, expose that positive predicate rather than requiring users to express it as `not is_X()`.  The two names retain their proper mathematical/computability semantics; do not assume ordinary Python negation is a valid implementation when the predicate is three-valued or assertion-gated.

- **Rationale**: `is_degenerate()` communicates the mathematical concept directly; `not is_nondegenerate()` makes the reader reconstruct a logical complement and can become wrong when “unknown/not currently computable” is distinct from false.

- **Violation Example**: require `not L.is_nondegenerate()` throughout code/notebooks even though degeneracy is a named property; define `is_degenerate = lambda: not self.is_nondegenerate()` across a soft/three-valued boundary.

- **Correct Example**: expose and implement the named positive predicates where `lean-categories` places them, sharing semantic lower-level constructions where appropriate.

#### `API-03`: Engine Vocabulary Is Not a Compatibility Surface

- **Rule**: The preamble API is not a name-for-name facade over Sage.
  Consumers speak the repository's mathematical vocabulary even when the engine has an analogous operation under another name.
  Do not add a public delegation solely because existing Sage code expects `.gen()`, `.gens()`, `.V()`, `.optimized()`, `.basis_matrix()`, `.coordinate_vector()`, `.submodule()`, or `.hom()`.

- **Rationale**: Compatibility delegations preserve the engine as the effective API and make later consumers depend on representation accidents.
  The preamble spelling must be the only ordinary route, so a wrong consumer fails visibly instead of silently crossing the boundary.

- **Violation Example**: Adding `M.gen(i)` to an owned free module because one lattice invariant still calls Sage's free-module API; adding `M.submodule(vectors)` because a discriminant-form routine expects Sage submodules.

- **Correct Example**: Rewrite the consumers to use `module_generator`, `module_generating_set`, `framing_morphism`, `subobject_on`, `to_vector`, `framing_morphism().lift`, `presentation_matrix`, `invariant_factors`, `smith_form_module_generators`, and `invariant_factor_form` as the mathematics requires.

#### `API-04`: Chosen Presentations Survive Engine Normalization

- **Rule**: A chosen framing or presentation is mathematical data and is never silently replaced by an engine's optimized, Smith-normalized, reduced, or otherwise canonicalized representation.
  A normalization that changes the chosen data produces a new owned object together with the owned morphism or isomorphism relating it to the original.

- **Rationale**: Isomorphic presentations are not identical chosen presentations.
  Engine normalization is algorithmic and choice-bearing; overwriting the original framing loses exactly the data the framed category says the object carries.

- **Violation Example**: Replacing the selected module generators by `smith_form_gens()` after constructing an FGP engine; mutating the relation matrix to the Smith matrix and then treating it as the original presentation; feeding the selected relation rows into a backend submodule constructor that canonicalizes its basis and then treating the backend Smith change-of-basis matrices as changes from the original selected relations.

- **Correct Example**: Keep the selected presentation unchanged and let `invariant_factor_form()` return an explicit owned isomorphism from the original framed module to the Smith-normalized framed module.  A private backend either reduces the selected presentation matrix itself or records the explicit change from the selected relation framing to any canonical backend relation basis before composing normal-form witnesses.

* * *

### 3. Construction & Witness Interfaces (`CON-*`)

#### `CON-01`: Canonical Constructors Consume the Mathematical Datum

- **Rule**: A canonical public constructor takes the datum that defines the mathematical object: a morphism, action, form, inclusion, presentation, generating map, or other named structure.
  A coordinate matrix, row list, backend object, or collection of implementation fields does not replace that datum merely because it can encode it.
  A coordinate convenience constructor is admissible only when the coordinates genuinely determine the mathematical datum, it immediately constructs that datum, and it delegates to the canonical constructor without establishing a second object model.

- **Rationale**: The constructor is where invalid states become unrepresentable.
  If the public constructor accepts a weaker representation, callers can bypass the homset, relation checks, form-preservation checks, or other structure that makes the datum mathematically meaningful.

- **Violation Example**: Constructing a presented module directly from a Sage relation submodule; `with_action(G, matrices)` constructing the group morphism internally; `submodule_from_rows(matrix)` treating rows as the subobject rather than constructing the inclusion.

- **Correct Example**: `presentation.cokernel()` consumes the selected morphism `F_1 -> F_0`; a module with a `G`-action consumes `rho: G -> Aut(M)`; a Gram-matrix convenience first constructs the corresponding form morphism on the specified framed free module and then invokes the canonical formed-module constructor.

#### `CON-02`: Structure Maps Are First-Class Morphisms Constructed by Their Caller

- **Rule**: Actions, representations, inclusions, scalar actions, form maps, comparison maps, and other structure maps exist as morphisms in their own homsets before another object consumes them.
  An object does not accept a source object plus raw generator images and secretly construct a morphism belonging to another category.

- **Rationale**: The morphism carries information that its image does not.
  For a group action `rho: G -> Aut(M)`, for example, `rho` need not be injective; replacing `G` by the subgroup generated by action matrices silently replaces the acting group by `rho(G)` and loses the kernel.

- **Violation Example**: `M.with_action(G, images)` constructing `rho` inside the module; recovering "the acting group" from the matrices appearing in a representation.

- **Correct Example**: Construct `G`, construct `Aut(M)`, construct `rho` in `G.Mor(Aut(M))`, then pass `rho` to the structured-module construction.  If the intended group literally is a subgroup of `Aut(M)`, construct that subgroup and use its inclusion.

#### `CON-03`: Transport Existing Structure Functorially

- **Rule**: When a construction changes an object carrying structure, transport that structure by the corresponding functor or named morphism construction.
  Do not reconstruct the transported structure from coordinate matrices when the defining morphism is already available.

- **Rationale**: Coordinate reconstruction duplicates the mathematics and introduces convention-dependent formulas at every consumer.
  Functorial transport states the definition once and automatically preserves composition and change of presentation.

- **Violation Example**: Building the form on a lattice direct sum by manually assembling a block Gram matrix; constructing the form on a subobject by slicing a matrix; implementing scalar extension by copying coefficients into a fresh matrix without applying the scalar-extension functor to the form morphism.

- **Correct Example**: Direct sum, tensor product, duality, and base change act on the module and on its form morphism; for an inclusion `i: S -> M` and bilinear form `b: M tensor M -> W`, the induced form is `b * (i tensor i)` in the appropriate Hom object.

#### `CON-05`: Chosen Preimages and Construction Provenance Are First-Class Data

- **Rule**: If a later mathematical operation requires not merely an output `F(A)` but the chosen presentation of that output as an image of `A`, represent the pair `(A, F(A))` or the corresponding functor-image object explicitly.
  Do not recover mathematically required preimages by attaching ad-hoc `_preamble_*_source_*` attributes to ordinary output objects and probing those attributes later.
  Incidental diagnostic provenance that is never part of a mathematical operation may remain private metadata, but it cannot be the hidden witness on which an adjunction, inverse transpose, or constructor depends.

- **Rationale**: A general functor output need not determine its preimage.  When a chosen preimage matters, that choice is mathematical data and deserves a type/construction that states it.
  Hidden source attributes create a second undocumented object model and make ordinary codomain objects behave differently depending on which constructor happened to produce them.

- **Violation Example**: Scalar extension setting `_preamble_scalar_extension_source_module` and the inverse Hom transpose later reading it; induction/coinduction attaching `_preamble_induction_source_group_module` or `_preamble_coinduction_source_group_module`; free/cofree `G`-set functors attaching source sets solely so an adjunction can recover them.

- **Correct Example**: Use the existing functor-image construction (or another explicit chosen-image object) when a chosen preimage is required, and let the adjunction consume that selected presentation.  If the inverse transpose can be derived from the unit/counit without recovering a hidden source object, derive it directly instead.  For `Spec`, make the contravariant functor's action on an algebra morphism produce the scheme morphism whose pullback is intrinsic to that morphism, rather than attaching `_preamble_coordinate_algebra_morphism` afterward as a side channel.

#### `CON-06`: Constructor Admission Is a Semantic Firewall

- **Rule**: Judge a constructor by the invalid states and alternate object models its input form admits.  The canonical constructor consumes the defining mathematical datum in its declared input form.  It does not compute the laws the construction claims (`OWN-22`).  Do not broaden constructor inputs for convenience when doing so lets callers bypass that datum.

- **Rationale**: Construction is the point where “this is an element of Hom”, “this map preserves the form”, “this action respects the relations”, or “this is the stated subobject” is claimed, through the datum that states it.  If arbitrary objects with a `.matrix()` method, coordinate arrays, or loose image lists are also admitted, every downstream caller can bypass that datum.  Whether the claim holds is judged by the `lean-cas-dsl` acceptance suite, never by the constructor.

- **Violation Example**: A Hom accepting any object with matching endpoints and a matrix; `with_action(G, images)` constructing the group morphism internally; an element constructor accepting a bare vector whose parent/framing is unstated.

- **Correct Example**: `G.Mor(Aut(M))(generator_images)` constructs the action morphism, and the structured module consumes that `rho`; a free/presented module consumes its framing/presentation morphism; a matrix convenience, when mathematically unambiguous for a canonically framed Mor, immediately constructs that Mor element and returns no parallel representation.

#### `CON-07`: Chosen Structure Is Data; a Property Is Placement, Never a Mode Flag

- **Rule**: Do not encode a mathematical property or category membership as a mode boolean or constructor switch.  If an additional *choice* is genuinely part of the structure, accept the actual chosen datum, not a boolean claiming it exists.
  Keep two things apart.  *Membership* of an object in a property subcategory `D ≤ C` is a fact about that one object.  The object's *placement* is the category it is constructed in, and it selects the operations the object has.
  - **Placement** comes from construction only, in two forms.  A constructor named for the property places its result in `D` directly: `R.maximal_ideal(...)` and `R.prime_ideal(...)` beside `R.ideal(...)`; the caller's construction is trusted (`OWN-22`).  A constructor for a specific object may decide the property from a cheap computation that a `lean-categories` theorem makes equivalent, and place the result in `D`: `ZZ.ideal(n)` is maximal exactly when `n` is prime, so it asks `n.is_prime()`.  That routing lives in the specific object's override and cites the theorem.
  - **Membership** that placement does not settle is a proposition (`Predicate`).  `ask()` decides it only when it is needed, which triggers the computation where one is available: `I in Ideals(R).Maximal()` asks whether `R/I` is a field.  The answer goes to the caller.  It never changes the object's placement, its class or its operations.  Construction never forces that computation; an explicit argument may enable an available, fast computation at construction.
  Finding that an object lies in `D` never makes it a different object.  An object's identity, its equality and every cache keyed on it depend on its defining data only, never on its placement or on how membership was decided.

- **Rationale**: Flags such as `even=True`, `negative=True`, `torsion=True`, or `nondegenerate=True` duplicate placement in a second, unchecked channel and permit contradictions between the flag and the data.  An answer from an engine is untrusted: if it could place an object, an implementation would decide which operations the object has.  A theorem cited from `lean-categories` is not such an answer; it states that the cheap computation and the property agree, so routing on it is placement by construction.  Membership asked on demand lets a caller branch on a property without letting the engine's answer reach the object.  Placement never enters identity: two equal ideals, one constructed as maximal and one not, have one quotient `R/I`.  Conversely, a selected orientation, framing, action, embedding, or volume form is real extra data and must remain explicit.

- **Violation Example**: `Lattice(G, even=True)`; `Form(..., nondegenerate=True)`; `saturation(in_ambient=M)` where the missing datum is actually an inclusion morphism; refining a lattice into `EvenLattices` because a parity computation returned `True`; a quotient constructor that computes `I.is_maximal()` to choose the category of `R/I`; a cache of `R/I` keyed on the placement of `I`, so equal ideals give two quotients.

- **Correct Example**: Construct the lattice in the even-lattice category when evenness is the claim; `L.is_even()` returns a computed answer; `ZZ.ideal(5)` is placed maximal by its cited routing, and `ZZ.quotient(ZZ.ideal(5))` is that one field; `if I in Ideals(R).Maximal():` asks the proposition; pass an actual `rho:G->Aut(M)` for an action; call saturation on the subobject/inclusion that already carries its codomain.

#### `CON-08`: A Mathematical Choice Is Represented by Its Selecting Datum

- **Rule**: Whenever several mathematically valid objects/maps could satisfy a phrase such as “the extension”, “the lift”, “the normalization”, “the dual”, “the section”, or “the presentation”, either identify the canonical construction that removes the choice or represent the chosen datum explicitly.  Do not hide a choice in a boolean, mode string, import state, or undocumented constructor convention.

- **Rationale**: A definite article silently asserts uniqueness/canonicity.  When the mathematics supplies only a family of choices, downstream functoriality and equality depend on which one was selected.  First-class selected data makes that dependency visible and composable.

- **Violation Example**: `normalize=True` mutates/re-presents an object without returning the isomorphism; `map=True` changes a constructor's mathematical return object; `dual()` ambiguously chooses among module, metric, or Pontryagin duals; a chosen preimage is recovered from hidden provenance.

- **Correct Example**: `invariant_factor_form()` returns the normalized framed module with its explicit isomorphism; different dual functors have distinct names; a selected section/lift/preimage is stored as a morphism or functor-image datum.

#### `CON-09`: Universal Constructions Return Complete Mathematical Data

- **Rule**: A universal construction returns a preamble object together with the canonical arrows that make it that construction, either as explicit components of the returned construction or as intrinsic methods on the returned structured object.  Never return only a presentation, basis, underlying abstract object, or numerical representative and require callers to reconstruct the universal maps.

- **Rationale**: The kernel is not merely an isomorphic module of solutions; it is a subobject with a canonical inclusion.  The cokernel is not merely an abstract quotient module; it comes with the canonical projection.  Products have projections, coproducts have injections, pullbacks/pushouts have their legs.  These maps are what make the construction composable and let callers state universal properties without descending to coordinates.

- **Violation Example**: `f.kernel()` returns generators/basis rows with no inclusion into `domain(f)`; `f.cokernel()` returns a normalized module but drops `codomain(f) -> coker(f)`; a pullback returns an object but not the maps to the two factors.

- **Correct Example**: `K = f.kernel()` is a subobject whose `inclusion()` has codomain `f.domain()`; `Q = f.cokernel()` carries `Q.projection(): f.codomain() -> Q`; a quotient element may provide a chosen `lift()` as representative selection, explicitly not as an inverse to the projection.

#### `CON-10`: Do Not Parameterize a Notion Already Determined by Existing Mathematical Data

- **Rule**: If the current object, morphism, base map, or category structure already determines the standard mathematical notion uniquely, derive it from that data.  Do not add a parameter, flag, policy object, or user-selected convention that silently redefines the notion.  Extra input is accepted only when the mathematics genuinely contains a choice, in which case `CON-08` requires the selecting datum itself.

- **Rationale**: Parameters suggest a family of legitimate meanings.  For intrinsic notions this creates false degrees of freedom and lets callers contradict the structure already present.  It also encourages API proliferation (`foo(..., mode=...)`) where distinct mathematical operations should either be derived canonically or have distinct names.

- **Violation Example**: Add `integral_over=D` to redefine integrality of a ring-valued form when the structural map `R -> W` already determines integrality over `R`; pass `even=True` or `torsion=True`; make “the dual” selectable by a mode string instead of using distinct dual functors.

- **Correct Example**: Compute integrality from the specified ring extension; derive evenness/torsion as properties; represent a genuinely chosen orientation, embedding, section, framing, or presentation by its actual mathematical datum.

#### `CON-11`: A Chosen Generating Set Is a Selected Epimorphism `Free_R(S) -> M`

- **Rule**: Model a module with chosen module generators by an actual set `S` and a selected epimorphism `Free_R(S) -> M`, the one-term free-cover case of `CAT-29`. The set `S` is the domain of the generating epimorphism; generator evaluation is the image of its free generators. Do not identify the chosen generators with a Python sequence, an ordered basis, or a reversible label-to-element correspondence unless stronger chosen structure supplies those properties. A categorical *framing* is the stronger, length-zero resolution in which the augmentation is an isomorphism, i.e. a chosen basis in this module case (`CAT-29`).

- **Rationale**: Finite generation, freeness, a basis, order, and enumerability are independent hypotheses.  A generating epimorphism may have an infinite/nonenumerable domain, and it may identify distinct free generators.  Treating it as a tuple/basis silently adds all of those hypotheses and creates exactly the finite-coordinate blast radius `ARC-16` forbids.

- **Violation Example**: `self._module_generators = tuple(generators)` as the definition of the chosen generators; recover a label from every generator image; require a rank integer when the natural input is an arbitrary set `S`.

- **Correct Example**: retain `S`, `Free_R(S)`, and the selected epimorphism. The canonical rank-`n` free module is the specialization `S=[n]`; its categorical framing is the selected isomorphism `Free_R(S) -> M`. An ordering or indexing of that basis is separate additional structure when not already given by `S`.

#### `CON-12`: Public Construction Enters Through the Category the Caller Names; Implementation Selection Is Private

- **Rule**: A public constructor is the category, presenting a `lean-categories` category, applied to the defining datum the caller has.  The object is placed where that construction places it; placement in a stronger category comes from constructing there, including theorem-backed routing in the constructor (`CON-07`); a membership proposition asked later answers its caller and never places the object.  Do not require callers to choose a concrete implementation class; implementation selection is private.

- **Rationale**: A researcher who knows a Gram form, presentation, group action, polynomial, scheme datum, etc. should not need to predict which backend class the finished object will occupy.  Placement is a mathematical claim made by construction; an implementation's answer cannot make it.

- **Violation Example**: Expose a private `BasedFreeModuleImpl(...)` alongside the free-module constructor; refine a constructed lattice into a root-lattice category because a root computation succeeded; select the public category from which backend class was available.

- **Correct Example**: construction enters through `Lattices(R)`, `Modules(R)`, the appropriate Hom/category, or a canonical object constructor such as `Lattice(...)`; the constructor returns the preamble object in the category it was constructed in.  Private implementation selection occurs after mathematical construction/routing.

#### `CON-13`: Supplied Generating Data Constructs the Generated Subobject/Subgroup, Never the Canonical Whole

- **Rule**: Caller-supplied generators, relations, samples, or other finite data construct exactly the mathematical object generated by that data.  They do not stand in for a canonical ambient object/group whose completeness is a separate claim.  Canonical objects are presented where `lean-categories` places them even when enumeration/generator computation is unavailable.

- **Rationale**: A list of isometries generates only a subgroup `H <= O(L)`.  Treating it as `O(L)` makes every orbit, stabilizer, kernel, index, and invariant computation silently answer the wrong group when the list is incomplete, while each local operation can remain internally valid.  The same distinction applies to supplied spanning data versus an entire canonical subobject whenever completeness is not established.

- **Violation Example**: `L.O(generators=gens)` returns the canonical orthogonal group; `Aut(X, generators=...)` substitutes a finitely generated subgroup for the automorphism group; downstream invariants are labeled as canonical-group invariants.

- **Correct Example**: `L.O()` is the canonical predicate-defined group object with membership/element operations available; `L.O().subgroup(gens)` is the supplied subgroup.  A specialized algorithm may later compute a generating family for `L.O()`, and its `group_generators()` method returns that computation's answer, untrusted like every answer and judged only by the `lean-cas-dsl` acceptance suite.

#### `CON-14`: A Free Object Is Built on a Set; an Arity Is a Chosen Set

- **Rule**: The free functor takes a set.  There is no canonical set of cardinality \(n\), so `R^n` names no object on its own, and an integer arity is sugar for *choosing* one -- it must resolve to a named set and route through the set-taking constructor.  Any construction indexed by an arity states the chosen set in its docstring, and its endpoints are the free objects on those sets.  Where the choice is what the construction records -- matrix entries indexed by row and column labels, a framing, a chosen presentation -- name the sets, never the integers.

- **Rationale**: Two free modules of the same rank on different label sets are isomorphic and not equal, and the preamble parents are deliberately not interned so that two structures on isomorphic underlying objects stay distinct.  A construction that identifies free objects by rank has thrown away the labels its own data is indexed by, and every downstream operation that reads a matrix entry, a coordinate, or a generator by name is then reading from an object the caller cannot name.

- **Violation Example**: `M_{m x n}(R) = Hom_R(R^m, R^n)` in a docstring; a matrix constructor that builds a rank-\(n\) parent directly instead of through the set-taking one; a test asserting `f.domain() is ZZ**2`, which passes for an implementation that identified free modules by rank alone.

- **Correct Example**: `M_{m x n}(R) = Hom_R(F_R(S), F_R(T))` for chosen finite sets; `FreeModule(R, n)` resolving to `FreeModuleOn(R, Sets.Delta[n-1])` through one constructor; a test asserting `FreeModule(ZZ, 2) is FreeModuleOn(ZZ, Sets.Delta[1])` and that a free module on another two-element set is not it and has a different Hom.

#### `CON-15`: A Tuple Is an Element of a Product; Name the Product

- **Rule**: An operation that yields several values yields **one element of the product of a family over an index set**.  Before writing a tuple, ask which product it is a point of *and over which index set*: a pair of naturals is the constant family \(\mathbb N\) over a chosen two-element set; a tensor's shape is the constant family \(\mathbb N\) over that tensor's own index set; the components of a commutative square are the family of its two homsets.  A bare Python tuple never appears in a public signature, a return, or an annotation.

  Ask the objects, never a global constructor.  `STY-02` governs the call: `C = X.ambient_category()` and then the category's own product, the way `ARC-07` has a morphism object asked of its endpoints as `A.Mor(B)`.  A free `Product(A, B)`, `CartesianProductOfSets(...)` or `CartesianProductOfFamily(...)` is the global-dispatcher shape `STY-02` names, and the binary forms additionally pick `Sets.Δ[n-1]` silently, which is the arity-for-a-set substitution `CON-14` forbids.

  **Known gap.** The preamble's categorical hook is binary -- `_categorical_product(left, right)`, whose body calls the binary sugar -- so a category cannot currently be asked for a product over an index set, and this rule has no compliant spelling for the general case.  That is the finding, not a licence to use the free constructor: the hook wants a family form before the conversions this policy implies can be written.

- **Rationale**: \((0, 2)\) is not a container holding two integers.  It is a point of \(\mathbb N^2\), and \(\mathbb N^2\) is an object of a category with projections, a universal property, its own equality, and morphisms into and out of it.  Writing the point as a Python tuple discards its parent, so the value arrives with no category and no equality of its own, and every caller must re-derive what it was a point of -- which is why a test given such a return has nothing owned to compare against and is forced out of the universe (`DEV-37`).  The repair needs no new type: `Product` is already an owned construction, so the work is naming the product that was always implied.  Minting a bespoke class per invariant is the wrong repair and the characteristic over-compliance with this rule; the question is never "what type should this be" but "which product is this an element of".

- **Violation Example**: `return (0, 2)` from a valence; `def signature_pair(self) -> tuple[int, int]`; returning `self.left(), self.right()` for a square's components; a shape returned as `(rank, rank)`; a test comparing any of these against a tuple display, which is the same defect observed from the far end.

- **Correct Example**: a valence as an element of `CartesianProductOfFamily(Sets.Δ[1], lambda _: NN)`, with the two-element index set written down; a tensor's shape over that tensor's own index set, so the order-2 case is a specialisation rather than the definition; a square's components as the product of the two homsets, so that projecting recovers each morphism in its own homset; invariant factors as the indexed family they are, ordered by divisibility, with the divisibility chain a property of the family rather than of a Python sequence.

#### `CON-16`: One Constructor Entry per Category; Every Other Route Computes Its Datum

- **Rule**: A category has one constructor, and it takes the datum that defines its objects (`CON-01`).  Every other way of building an object -- a convenience on presented data, a functor image, an object adopted from the engine, a universal construction -- computes that datum from its own inputs and calls the one constructor.  An input object that is defining data (the module a multiplication was stated on, the module a form or a group action equips) is retained as that exact datum and returned by the accessor the specification names, `unformed_module()`. No identification map is introduced merely to connect a separately implemented copy back to that input. `equip_*` and `forget_*` morphisms, `*_source_module` accessors and `from_*`/`to_*` identifications used for that purpose are the tell that construction was duplicated rather than routed. A free functor's generating module remains distinct from its full underlying module; its genuine source datum and unit are required, as are the actual universal maps and chosen isomorphisms of `OWN-16` and `OWN-20`.  A data subcategory `XWithChosenY` is admissible only when `Y` is a choice beyond the defining datum of `X` -- a presentation of a module, a basis of a free object; the defining datum itself never names a subcategory.  A constructor's admission check decides when the represented data supply an effective decision procedure and otherwise records `Unknown` as the hypothesis the object carries; it never asserts a finite framing as the only route.
  An \(R\)-algebra is the instance that fixed this rule: its datum is an additive group \(A\) with a biadditive multiplication together with \(\rho\in\operatorname{Hom}_{\mathbf{Rings}}(R, Z(A))\), \(Z(A)\) the centroid of \(A\) (the additive endomorphisms commuting with left and right multiplication, Mathlib `CentroidHom`), which is the centre when \(A\) is unital associative.  No unit, associativity or commutativity is assumed; those are axioms above the node, and a Lie bracket is the multiplication of its algebra.  Over commutative \(R\), which is the case this tree works in, this is nothing more than an \(R\)-module \(M\) with an \(R\)-bilinear \(m\colon M\otimes_R M\to M\): the datum \((M, m)\) already is the structure, \(\rho\) is the scalar action of \(M\), and the textbook definition of a Lie algebra over a field carries over unchanged.  The centroid is only the name of where \(\rho\) lands; it is not machinery the construction needs.

- **Rationale**: Two constructors for one category produce two kinds of object with different capabilities, and consumers start routing by which one they hold.  A copy of the input needs a map back to the input, and that map needs a name, and the name names nothing in mathematics.  The specification writes `form.unformed_module() is module` and `Modules(R[G])(M, action)`: the retained input is data, the structured object is built on that data, and elements pass between them by coercion.

- **Violation Example**: `Algebras(R)(M, m)` building a second module and retaining `M` as a "multiplication source" with `from_multiplication_source`/`to_multiplication_source`; `AlgebrasWithChosenMultiplication` as a subcategory of `Algebras(R)`, with the algebra Hom, `product` and the unit routing on membership in it; `forget_form_morphism`/`equip_form_morphism` on formed modules and lattices and `forget_action_morphism`/`equip_action_morphism` on group modules; a structure-map constructor (`_own_algebra`) that exists only for engine-adopted rings; a multiplicativity check that asserts a finite module framing.

- **Correct Example**: `Algebras(R)(A, m)` as the one entry, with \(A\) an \(R\)-module and \(m\) an \(R\)-bilinear multiplication, producing \(\rho\colon R\to Z(A)\) from the scalar action of \(A\) (for \(R\) over itself, \(A=R\) as the free rank-one module with its multiplication, so \(\rho=\mathrm{id}_R\)); `M.algebra_from_multiplication(m)` calling that entry; `M.equip_bilinear_form(R, b)` calling the form-module entry with `(M, b)`, whose result answers `unformed_module()` with `M`; a Sage polynomial ring constructed as its module with its own multiplication through the same entry; an algebra Mor admitting a linear map by asking the module Mor whether `f composed with m_A = m_B composed with (f tensor f)`, and carrying `Unknown` as its hypothesis when that is not decidable.

#### `CON-17`: The Hom Set Owns the Construction of Its Elements

- **Rule**: A space of maps \(A\to B\) -- continuous, smooth, integrable, square-summable, bounded -- is a subobject of \(X = \operatorname{Mor}_{\mathbf C}(A, B)\), cut out by its condition, with the structure its category adds. Its defining data are that inclusion and that structure. Each such space is a family of functors in both arguments: \(C^n(A, B)\), \(L^p(A, B)\), \(W^{k,p}(A, B)\), graded by \(n\), \(p\) or \((k, p)\), and possibly regarded as sheaves on \(A\). So every constructor takes \(A\) and \(B\): `C(Infinity, RR, RR)`, `Lp(2, RR, RR)`, `ell(2, NN, RR)`.

  How an element is given belongs to the element constructor of \(X\), which is the one boundary. It accepts a callable, a lambda, a formula (`f(t) = integral(x^2, x, 0, t)`), and in finitary cases a table, a matrix or a tensor. A subobject constructs its element there and admits it by its condition. A map is given by how it acts on an arbitrary element: \(t\mapsto 2^t\) says what the map does to an arbitrary \(t\in A\).

  **An arrow of another Mor is never admitted.** Owner ruling, 2026-10-16: "If f in End_Sets(X) and M is a module with U(M) = X, what could you possibly mean by End_{RMod}(X)(f)? Almost all set maps will not lift to module maps. You can't construct an arrow from the data of another arrow, you have to apply a functor....or in the very worst edge cases, you have to extract the symbolic formula, callable, matrix, whatever from f and use it to build a new arrow entirely (which is fraught with peril, because it forces you to either check well-definedness for EVERY such construction (very long) or potentially allow backdoors into constructing ill-defined morphisms)."  So the element constructor of \(\operatorname{Mor}_{\mathbf C}(A, B)\) admits an arrow already in it, which it returns unchanged, and the defining data of a new arrow; an arrow of a different Mor reaches it only as the image under a functor (a forgetful functor in the other direction, a scalar extension, a restriction), never by reading its formula, matrix or callable to rebuild it here.

  No object has a "coordinate". A ring has no coordinates and a group has no coordinates; there is no `coordinate()`, `indeterminate()` or "general element" accessor on an object, a space or a hom. A map is written by the caller as a callable, a lambda, or an expression in a variable the caller introduces itself (`var("x")`, or `f(t) = t^2 + 1` binding `t`), and the element constructor of \(\operatorname{Mor}(A, B)\) turns it into the morphism. Symbolic input is the constructor's job. Owner ruling (2026-10-14): "'coordinate' is not well-defined... a ring doesn't have 'coordinates'. A group doesn't have 'coordinates'. ... why do that at all if you could just do var(\"x\")? ... callables defined in terms of symbolics should be handled in constructors." A genuine chart on a manifold is a separate notion: its coordinate functions are morphisms \(U\to\mathbb R\) supplied by the chart, not a variable supplied by an object.

  Owner statement (2026-10-14): "the only definition is \(L^p(X,Y) := \{f\colon X\to Y \mid p\text{-integrable}\}\), using calculus on manifolds in full generality. \(L^p(X,\mathbb R)\) is the usual \(L^p\) space from intro analysis. \(L^p(X,Y)\subseteq \operatorname{Hom}_{\mathbf C}(X,Y)\) for some category: these are morphisms. They can be specified by callables, polynomial functions, whatever, but that's the constructor's job. You don't 'extract' an indeterminate from an \(L^p\) space. A space might have a local coordinate or coordinates, which you might extract in order to build a callable function to feed into a hom constructor. A hom does not 'have' indeterminates; it too might have a local coordinate, but that means a coordinate on a function space, which is entirely different."

- **Rationale**: A point of \(A\) and an element of \(\operatorname{Mor}(A, B)\) are different mathematical objects. A coordinate stands for an arbitrary element of the object that supplies it. Asking \(X\) for its coordinate and then using it as a point of \(A\) substitutes an arbitrary function for an arbitrary number. After that, expressions that mean nothing are accepted. `2^x` with \(x = \operatorname{id}_{\mathbb R}\) has no mathematical meaning and is not what anyone intends. `x**2 + 1` evaluated at \(2\) has no meaning once \(x\) is a general function. Storing a variable on the space as its "indeterminate" is the same conflation built into the object's data: the variable is meant as a point of \(A\), and it is attached to \(X\). Only \(A\) knows its own points and coordinates, so only \(A\) can supply them: one real number, a vector \((x_0, x_1)\), a chart. A one-argument constructor such as `C(Infinity, RR)` fixes the codomain without stating it. \(C^\infty(\mathbb R, \mathbb R)\), \(C^\infty(\mathbb R, \mathbb C)\) and \(C^\infty(\mathbb R, \mathbb R^n)\) are different objects, and the functoriality in \(B\), post-composition with \(B\to B'\), cannot be stated when \(B\) is not an argument. Element construction outside \(\operatorname{Mor}(A, B)\) also duplicates the one boundary where maps enter.

- **Violation Example**: `Lp(p)` built with `indeterminate=SR.var("x")` and `ell(p)` with `SR.var("n")`, storing a variable meant as a point of the domain and handing it out as `indeterminate()`, with `space(expr)` reading an expression in it as the map; a test writing `x = space.indeterminate()` and then `space(exp(-x^2))`; `x = C(Infinity, RR).coordinate()` followed by `x**2 + 1` and `f.evaluate_at(RR(2)) == RR(5)`, which uses the space's general element as a point of \(\mathbb R\).

- **Correct Example**: \(L^2(\mathbb R, \mathbb R)\) as the subobject of \(\operatorname{Mor}_{\mathbf{Set}}(\mathbb R,\mathbb R)\) of square-integrable maps, with its quotient by null functions where the classes are meant; `x = var("x")` and `C(Infinity, RR, RR)(x^2 + 1)`; `f(t) = exp(-t^2)` binding `t` in its own definition, constructed in `Sets().Mor(RR, RR)` and admitted by the space; a local parameter at a point of a scheme obtained from the scheme and used to build the map; the operator `X.Mor(X)(lambda f: exp(f))` on \(X = C^\infty(\mathbb R, \mathbb R)\), given by its action on an argument \(f\) the lambda binds.

* * *

### 4. Category Placement & Capability (`CAT-*`)

#### `CON-04`: Coordinate Matrices Belong Exactly to Free-Module Homs

- **Rule**: A matrix of a linear map is the element of `Hom_R(F_R(S),F_R(T))` determined by chosen free framings.  Do not assign a coordinate matrix to an arbitrary morphism of finitely generated or finitely presented modules merely because source and target have generating sets.  Constructions on nonfree modules use their presentations, generating morphisms, and relations directly.

- **Rationale**: A generating family of a nonfree module is not a basis.  Recording images of generators is sufficient to define a morphism subject to the source relations, but it is not a matrix in a Hom between free modules.  Confusing the two silently treats a presentation as an isomorphism with a free module.

- **Violation Example**: Constructing `coker(f: M -> N)` for presented modules by calling `f.matrix()` and appending its rows to a presentation matrix, even though `M` or `N` is not free.

- **Correct Example**: If `N` has selected presentation relations and `M` has a chosen generating morphism, present `coker(f)` by the existing relations of `N` together with the coefficient rows of `f(m_s)` in the chosen framing of `N`.  Only when both endpoints are framed free modules is that same data literally the matrix of `f`.

#### `CAT-01`: Place the Method by Mathematical Domain; Route Algorithms by Computable Case

- **Rule**: Put a mathematical method on the first category/object/element where `lean-categories` defines the notion. Do not invent computability categories merely to hide methods whose values mathematically exist more generally. Inside that correctly placed method, route among the cases for which exact algorithms are currently implemented, preferably by category/representation-aware `match`/`case` or specialized overrides. The unhandled remainder may terminate with an informative assertion stating the current computational limitation. A method whose entire implementation is immediate failure is forbidden; `NotImplementedError` is not a mathematical implementation strategy.

- **Rationale**: Mathematical domain and computational domain are different. Every set has a cardinality, but exact cardinality is undecidable/unavailable for arbitrary represented sets. Every formed module has a well-defined nondegeneracy property, but a callable form on an infinite-rank projective module may be outside current algorithms. Hiding such methods on `SetsWithComputableCardinality` or `FormedModulesWithDecidableNondegeneracy` would encode today's software limitations as false mathematics. Assertion-gated case routing instead keeps placement correct while making the present computational frontier explicit and auditable.

- **Violation Example**: Creating `SetsWithCardinality` so only those sets expose `cardinality()`; moving `is_nondegenerate()` off general formed modules merely because the current implementation needs a finite Gram tensor; exposing `kernel()` with a body consisting only of `NotImplementedError`; using `hasattr`/exception fallback to discover an algorithm.

- **Correct Example**: `Sets().ObjectType.cardinality` routes finite/enumerated/symbolic cases to exact algorithms and ends with an informative assertion for a represented case not yet handled. `FormedModules(R).ObjectType.is_nondegenerate` computes from the correlation/Gram tensor where available and assertion-gates currently undecidable representations. A truly positive-definite-only construction, by contrast, belongs on `PositiveDefiniteLattices` because its **mathematical definition**, not merely its algorithm, has that hypothesis.

#### `CAT-09`: Semantic Parity Never Means Signature Parity

- **Rule**: When importing capability from Sage, archived code, another CAS, or a reference implementation, first find in `lean-categories` the entity on which the operation is defined and the datum it consumes.  Present that operation in the preamble's category graph; do not copy the foreign method signature, placement, mode flags, or witness-compensating parameters merely because the upstream implementation exposes them.

- **Rationale**: A signature embodies a mathematical model.  APIs without first-class subobjects/morphisms often hang morphism-dependent operations on bare objects and add `ambient=` parameters; APIs without category refinement often add `even=`/`negative=` modes.  Porting those signatures imports the old mathematical model along with the computation.

- **Violation Example**: Port Sage's `saturation(in_ambient=...)` directly onto a preamble lattice; mirror an upstream `even=` constructor flag; expose `is_submodule(M)` on a bare object rather than an embedding/existence question in the appropriate Hom.

- **Correct Example**: Site saturation on the subobject/inclusion, place the object by construction (`CON-07`), and represent embedding existence by the relevant `Emb(A,B)`/Hom object.  Reuse the upstream algorithm privately after the semantic interface has been corrected.

#### `CAT-10`: The Owned Category Type Protocol Is `ObjectType` / `ElementType` / Hom-Category Types

- **Rule**: The public owned category architecture speaks in the preamble's type protocol: `ObjectType`, `ElementType`, `HomCatType`, `EndCatType`, `AutCatType`, and the corresponding arrow types (`ArrowType`, `EndArrowType`, `AutArrowType`).  `ArrowType` is conceptually the element type of the Hom-category object, not an independent third method mechanism.  Sage `ParentMethods`, `ElementMethods`, `MorphismMethods`, dynamic classes, and related machinery may remain private runtime implementation details while this protocol is completed; new doctrine and APIs do not treat those Sage names as the mathematical architecture.

- **Rationale**: The preamble's category graph is supposed to present objects, elements, and Homs uniformly.  Reusing Sage's method-container vocabulary as public vocabulary repeatedly causes contributors to think of attached mixin buckets rather than instantiated implementation types generated by the category graph.

- **Violation Example**: Specify a new preamble feature as “put this in `MorphismMethods`” without first stating the Hom/arrow category where `lean-categories` places it; document `ParentMethods` as a public mathematical type; build a separate morphism-class hierarchy because the Hom-category element type was not considered.

- **Correct Example**: State that category `C` supplies an `ObjectType`; `Hom_C` supplies its object/element types; arrows are elements of the Hom-category construction.  Map those preamble declarations onto Sage's dynamic method installation privately until the runtime migration is complete.

#### `CAT-11`: Functorial Domain Restrictions Are Categories, Not Runtime Rejection Branches

- **Rule**: A functor's declared domain is the category `lean-categories` states for it: the most general one on which the mapping is functorial.  If a construction transports only isomorphisms, declare it on `C.core()`; if it needs a slice/coslice/arrow category or a parameterized base-change category, use that category.  Do not advertise a functor on a larger domain and reject ordinary morphisms inside `_apply_morphism`.

- **Rationale**: Functoriality is part of the mathematical type.  A runtime branch that says “this morphism is unsupported” after accepting it into the functor's domain encodes a false signature and moves a categorical hypothesis into control flow.

- **Violation Example**: Define the center as a functor on all rings and assert that each incoming ring map happens to preserve centers; define a construction on `C` while every non-isomorphism branch immediately fails.

- **Correct Example**: When only isomorphisms transport the construction, use `C.core()` as the domain.  Other restrictions are modeled by the subcategory/category construction `lean-categories` formalizes, after which the functor action is total on its declared arrows.

#### `CAT-12`: Sage's Category Graph Is a Fact About Sage, Not Mathematical Authority

- **Rule**: Read Sage source/runtime behavior to learn exactly what Sage encodes and which algorithms/methods a Sage category supplies.  Category identity, inclusions, forgetful/projection functors, and equivalences are `lean-categories`', and the preamble's graph presents them.  Never treat Sage `==`, `is_subcategory`, `super_categories()`, `all_super_categories()`, or absence/presence of an edge as proof of the corresponding mathematical statement.

- **Rationale**: Sage's graph is intentionally shaped by dynamic dispatch/MRO and historical API choices.  A `super_categories()` edge can represent several kinds of structural maps; “immediate” parents are a generating set selected for linearization; equal parent lists do not imply equal categories; mathematically required edges can be absent; two presentations of the same construction can compare unequal.

- **Violation Example**: copy Sage's `Modules(R) -> Bimodules(R,R)` or a facade/category edge into the preamble's graph merely from its spelling; infer that two refinements are equivalent because their Sage parent lists coincide; infer a mathematical non-inclusion because Sage lacks the edge.

- **Correct Example**: first identify in `lean-categories` the categories and their actual functors; then maintain a backend correspondence that records how Sage's declarations/behaviors realize or approximate those categories for computation.

#### `CAT-13`: Category Identity, Standard Name, and Classifier Expression Are Three Distinct Layers

- **Rule**: Present each `lean-categories` category once.  Attach its established public noun/notation, and separately retain the classifier/category expression that constructs it.  A named composite or alias does not create another category object.  Classifier names are interpreted relative to their host/defining morphism, not as globally meaningful Boolean labels.

- **Rationale**: `Semigroups` and `Magmas.Associative` can be a standard name and a defining presentation of one category.  `Commutative` on groups and a similarly spelled property in another theory need not be the same classifier.  Conflating name, identity, and presentation creates duplicate vertices, string-based taxonomy, and ad-hoc alias edges.

- **Violation Example**: create separate `Semigroups` and `Magmas.Associative` vertices; mint one global `Finite`/`Commutative` classifier keyed only by its word; make `GradedAlgebras` an independent species instead of the relevant classifier pullback/refinement.

- **Correct Example**: one preamble category carries its standard name and its constructing expression; classifiers are declared at the host where `lean-categories` places them and transported by pullback/composition where `lean-categories` states that the same structure/property is induced.

#### `CAT-14`: Category Constructibility Is Derivability of Canonical Structural Maps, Not Graph Reachability

- **Rule**: Determine whether a classifier/category expression can be formed from the canonical structural maps supplied by the preamble's grammar, which presents `lean-categories`' structural maps: projections/forgetful functors, composition, classifier application/pullback, slice/coslice/core/etc. as defined.  Do not use arbitrary graph reachability, name presence, reverse traversal of projections, or Sage MRO paths as a proof that the mathematical construction exists.

- **Rationale**: A graph can connect vertices by arrows whose direction/type do not provide the data required by a pullback/classifier.  Reachability forgets roles and universal properties, and reverse traversal fabricates structure.  Typed structural derivation keeps construction aligned with the actual mathematical diagram and makes ephemeral classifier towers possible without minting named nodes.

- **Violation Example**: infer `C.A` because a path from `C` eventually reaches a node named `A`; search backwards from a classifier projection to claim the classified structure; require every constructible classifier tower to have a named category vertex.

- **Correct Example**: the defining structural functor `C -> H` together with classifier `H.A -> H` yields `C.A = C x_H H.A` and its projection; ancestor routes are compositions of those canonical maps.  No extra named node or graph-search witness is required.

#### `CAT-15`: A Supercategory Entry Presents a `lean-categories` Inclusion, Never a Route to a Method

- **Rule**: `super_categories()` returns the categories that every object of this one is an object of, over the same parameters, as `lean-categories` states, cited in the docstring.  Nothing else goes in the list: not the category whose `__init__` makes construction succeed, not the one that carries a method the leaf wants, not `Sets()` or `Objects()` as a root because the real parent is not in the tree yet.  When the honest parent is not presented, present it if `lean-categories` formalizes it; otherwise request it there and leave the declaration abstract so the category refuses to construct (AGENTS.md, *A supercategory entry presents a formalized inclusion*).

- **Rationale**: Sage reads the list by inheritance, so every entry installs the target's operations and axioms on every object and every descendant.  An entry chosen for convenience is a false statement that every later reader inherits and that no test can see, because each object still answers.  On 2026-09-16 thirty categories declared `Sets()`, among them sheaves, ringed spaces, pairings, arrow categories and a semiring, and twenty-one declared `Objects()`; nothing was wrong with any of their objects, only with what had been claimed about them.

- **Violation Example**: `PairedModules -> OwnedSets()` because a pairing needs a parent; `OrdinalSemirings -> Objects()` for a semiring; `AffineGroupSchemes -> Objects()` with a comment that forgetting the group structure "is a functor, not an inclusion"; `Algebras -> Sets()` for modules with a multiplication.

- **Correct Example**: `OrdinalSemirings -> OwnedSemirings()`; `Algebras(R) -> Modules(R)`; `AffineGroupSchemes -> AffineSchemes(R)`; a pairing left undeclared until `lean-categories` formalizes the comma category over the tensor functor, with the request recorded.

#### `CAT-16`: Structure Forgotten in Place Is a Declaration; a Change of Base or Parameter Is a Functor

- **Rule**: Declare `C -> D` exactly when `lean-categories` states that an object of `C`, with the structure `C` adds forgotten and every parameter unchanged, is an object of `D`: an `R`-algebra is an `R`-module, an affine group scheme over `S` is an affine scheme over `S`.  Never declare a relation whose objects change base or parameter: restriction of scalars along `S -> R`, base change of a scheme, the passage from an `R[G]`-module to a `G`-object over `R`, from an ideal to the fractional ideal it generates.  Each of those is a functor obtained from its category by a method named for the construction, citing `lean-categories`' preservation theorems on the functor.

- **Rationale**: the two are easy to confuse because both are forgetful and both are true sentences.  They differ in what inheritance does with them.  In place, the inherited operations and axioms are the object's own.  Across a base, Sage applies every axiom of the source to the target (`CategoryWithAxiom.super_categories`, category_with_axiom.py), so `Modules(QQ).FinitelyGenerated()` would inherit `Modules(ZZ).FinitelyGenerated()`, and `Modules(R[G]).FinitelyGenerated()` the R-module property, both false.  The tree had it backwards in both directions: `Algebras` refused the in-place declaration and made the cross-base one.

- **Violation Example**: `Modules(R) -> Modules(S)` for a restriction base; `Schemes(R) -> Schemes(ZZ)`; `Modules(R[G]) -> GObjects(G, Modules(R))`; `Ideals -> FractionalIdeals`; the `Algebras` docstring reasoning that the relation to modules "is the forgetful functor, not a category inclusion" and declaring `Sets` instead.

- **Most structured category (owner ruling, 2026-10-16)**: an object has many parent categories, and it is placed in the most structured one.  `QQ[x]` is a ring and a `QQ`-algebra, and every `QQ[x]`-module is a `QQ`-module by restriction of scalars along `QQ -> QQ[x]`, a functor applied when the less structured object is wanted.  The base ring of an `R`-algebra is always `R` (owner ruling, 2026-10-16): `QQ[x].base_ring()` is `QQ`.  `QQ[x]` as a module over itself is its regular module `QQ[x].regular_module()`, whose base ring is `QQ[x]`; its image under restriction of scalars is the in-place `QQ`-module of the algebra, and the two are identified by a morphism, never by a second module structure read off `base_ring()`.

- **Correct Example**: `Algebras(R) -> Modules(R)`, and `Modules(S).restriction_of_scalars(f)` for `f: S -> R` returning the functor with its image category; `Schemes(R).base_change_functor(ring_map)`; `CommutativeIdeals(R).extension_to_fraction_field()`; `GObjects(G, Modules(R)) ≃ Modules(R[G])` as an explicit equivalence with both directions.

#### `CAT-17`: A Property Is an Axiom on Its Base; a Chosen Datum Is a Subcategory Class That Declares the Axiom

- **Rule**: Before writing a class for "the `X`s that are `P`", read in `lean-categories` whether `P` is a property of the objects or a chosen datum.  A property (finitely generated, torsion, free, Noetherian, separated, symmetric, countable) is presented as a nested `class P(CategoryWithAxiom)` on the base where `lean-categories` first states it, with a `SubcategoryMethods` accessor and, for a new name, one `all_axioms` registration; there is no standalone class.  A chosen datum (a chosen multiplication, a differential, an augmentation, an enumeration, an order, a Koszul parity) is a class, and it declares the axiom category of the property it truncates to.  A chosen generating epimorphism, presentation or syzygy tower is a truncated resolution and lives in the category of resolutions over the base (`CAT-29`), whose image in the base is the relative finiteness axiom.  The crossing from property to datum is one named method that computes the datum once (AGENTS.md, *Property subcategories vs data subcategories*).  A property with more than one established name takes `lean-categories`' name, and a property class kept "because no axiom was coined" is this rule violated, not respected.

- **Rationale**: a property is the propositional truncation of the datum ("some finite framing exists"), so the two are one notion at two levels, and the class-per-notion instinct writes them as unrelated siblings.  Sage's axiom mechanism exists so that properties compose without classes; a hand-written property class cannot be joined with another and must restate every diamond.

- **Violation Example**: `class FinitelyPresentedModules(...)` beside `class ModulesWithChosenFinitePresentation(...)` with no declaration between them; `OwnedNoetherianRings`, `SeparatedSchemes`, `InfiniteEnumeratedSets` as classes; a `GradedCommutativeAlgebras(R, M, parity)` class whose parity was a category parameter, so that a parameterless axiom could not later state it.

- **Correct Example**: `OwnedRings.Noetherian`, `Schemes.Separated`, `Modules.FinitelyPresented` as nested axiom classes; a chosen finite presentation of `M` as a point of the truncation-1 resolutions over `Modules(R)`, whose image is `Modules(R).FinitelyPresented()` (`CAT-29`); the parity as part of the grading datum on `GradedModules`, read by the `Supercommutative` axiom.

#### `CAT-18`: No Class Is Named for a Combination of Properties; Joins Are Computed

- **Rule**: The category of objects with properties `P` and `Q` is spelled `Base().P().Q()`, and Sage constructs it as the join.  Writing a class for the combination is banned, whatever its docstring says, and so is writing a class for one property on a subcategory that is itself one property.  A combination that needs operations of its own puts them on the nested join class Sage already provides for it (`class Q` nested inside `class P`), never on a new top-level class.

- **Rationale**: the product of independent property axes, flattened into names, is what produced the block of 135 categories: every square in it was the same diamond declared twice, and every new axis multiplied the classes.  Computed joins are also the only place where the commutativity of the diamond is a theorem of the mechanism rather than an assertion at each site.

- **Violation Example**: `FinitelyPresentedQuadraticFormModules`, `FinitelyGeneratedFreeFormModules`, `OwnedCompleteLocalRings`, `CommutativeDifferentialGradedAlgebras`, `StrictlyCommutativeDifferentialGradedAlgebras` as classes, each declaring two parents.

- **Correct Example**: `FormModules(R).FinitelyPresented()`, `OwnedRings().Commutative().Local().Complete()`, `DifferentialGradedAlgebras(R).Supercommutative()`; a name the specification requires kept as a thin function returning that join.

#### `CAT-19`: An Axiom Name Is Global and Means What Its Defining Base Means

- **Rule**: Sage applies an axiom to every subcategory of the base that defines it, with that base's meaning, and it walks declared supercategories to find the definition.  So an axiom named `FinitelyGenerated` on `Modules` means "finitely generated as a module" on every algebra, lattice and group module too.  A property that is relative to a different structure gets a qualified name in Sage's own idiom (`FinitelyGeneratedAsMagma`, `FinitelyPresentedAsAlgebra`), registered once.  Before adding a name, check `sage.categories.category_with_axiom.all_axioms` and reuse Sage's when its meaning matches `lean-categories`'.

- **Rationale**: two bases defining the same axiom name with different meanings make one of them false on every category that declares both, and the falsehood is silent because the join still constructs.

- **Violation Example**: a `FinitelyPresented` axiom on `Algebras.Associative.Unital` while `Modules` defines `FinitelyPresented`, so that `R[x]` claims a finitely presented underlying module; a `Free` axiom on algebras meaning "free algebra".

- **Correct Example**: `FinitelyPresentedAsAlgebra` on the unital associative algebras and `FinitelyPresented` on modules; `Complete` nested under `OwnedRings.Commutative.Local` so that it means complete as a local ring.

#### `CAT-20`: A Construction on a Category Is Parameterized by It and Declares It

- **Rule**: A category whose objects are objects of `C` with added structure or selected data (`G`-objects of `C`, objects of `C` with a chosen direct-sum decomposition, arrows of `C`, presheaves on `C`), as `lean-categories` formalizes the construction, takes `C` as a parameter and declares `C` as its immediate supercategory.  Its instances then reach `C` through it; an instance does not declare `C` a second time.

- **Rationale**: the construction is a functor of `C`, and forgetting the added structure lands in `C` itself.  Declaring `Objects()` instead makes every instance restate the base, and hides that the construction is one thing across all `C`.

- **Violation Example**: `GObjects(G, C) -> Objects()` with `FiniteGSets` declaring `EnumeratedSets` itself and `ModulesOverGroupAlgebra` declaring `AdditiveGroups`; `DirectSumObjects -> Objects()` unparameterized, with `BiproductModules` declaring `Modules` beside it.

- **Correct Example**: `GObjects(G, C) -> C`; `DirectSumObjects(C) -> C` once the specification's spelling admits the parameter.

#### `CAT-21`: A Second Route Between Two Categories Is an Obligation, and a Route Through Different Objects Is Banned

- **Rule**: Before adding a declaration that creates a second path from `C` to some `D`, write down both composites of forgetful functors and cite the `lean-categories` theorem that they are the same functor; without one, the declaration waits on a request there.  If they agree because one is an axiom join Sage computes, the edge is fine.  If they agree because a category on one route is the same category as one on the other, delete the edge: it is a shortcut (`just category-graph shape` lists them) and adds a cycle with no reachability.  If they do not agree, the declaration is false: the two routes send an object to different objects of `D`.

- **Rationale**: Sage resolves a diamond by C3 linearization and never checks that it commutes; the object's inherited operations are whichever route the ordering picked.  A shortcut edge is a redundant assertion; a non-commuting one is a wrong answer waiting for the method that exposes it.

- **Violation Example**: `Ideals -> FractionalIdeals` beside `Ideals -> CommutativeIdeals`, both reaching `ModuleSubobjects`, one as a subobject of `R` and the other of `Frac R`; `AffineSchemes -> Schemes, SeparatedSchemes, QuasiAffineSchemes` when `QuasiAffineSchemes` declares the first two; `OwnedFields -> OwnedIntegralDomains` beside `OwnedPrincipalIdealDomains`.

- **Correct Example**: `AffineSchemes -> QuasiAffineSchemes` alone; `Ideals` retired into `CommutativeIdeals`, with the fractional ideal a functor image; a lattice declaring `FreeFormModules` and the symmetric axiom, both routes to `Modules(R)` being the same forgetful functor through a computed join.

#### `CAT-22`: One Notion Has One Category; a Duplicate Is Retired Into Its Owner

- **Rule**: Before presenting a category, confirm that `lean-categories` formalizes it, then search for an existing presentation: `just category-graph by-supercategory` for the parent it would declare, `rg` on the nouns of its definition across `categories/`, and the specification files for the name they use.  A category already presented is not written again; if it already exists, it is retired into the owner, its non-duplicate operations moved to the owner at the weakest sufficient structure (`OWN-18`), and its consumers rewritten.  A name the specification requires survives only as a thin function returning the owner.

- **Rationale**: duplicates arise when a category is minted where a consumer needs it and named from that vantage, which is research authoring mathematics.  Each duplicate is a second authority for one notion, and the graph then holds diamonds that are the same category twice.

- **Violation Example**: `FormedModules` ("modules with a bilinear form") beside `FormModules`; `InfiniteEnumeratedSets` beside `CountablyInfiniteSets`; `Ideals` beside `CommutativeIdeals`; a `LieAlgebras` class beside the `Lie` axiom on `Algebras`.

- **Correct Example**: `FormModules` with the parent-level `q(v) = b(v, v)` moved onto `BilinearFormModules`; `LieAlgebras` as the name of `Algebras.Lie`; `CountablyInfiniteSets` as the name of the join of `Countable` and `Infinite`.

#### `CAT-23`: Placement and Asked Property Membership Have Different Effects

- **Rule**: The category in which an object is *placed* is fixed by its construction and the declared graph; only that placement supplies operations. A `__contains__` that walks a ring's base tower or probes an attribute to invent a category relation is banned. Where a wider category relationship is true (a QQ-scheme viewed over ZZ), it is reached through the functor of `CAT-16`. The later owner ruling in `CON-07` also permits asking whether an already constructed object satisfies a property subcategory: `I in Ideals(R).Maximal()` asks the corresponding `Predicate` whether `R/I` is a field. That answer goes only to the caller. It never changes the object's placement, class, operations, or identity.

- **Rationale**: an asked proposition and construction-time placement answer different questions. Treating a successful predicate answer as placement would give the object operations its constructor did not install; forbidding the question altogether would contradict `CON-07`'s explicit property-membership rule.

- **Violation Example**: `Schemes.__contains__` answering lower-base membership by the candidate ring's base tower; `RepresentedToricSchemes.__contains__` probing `getattr(candidate, "scheme_base_ring", None)`; `QuasiCoherentSheaves.__contains__` duck-typing for want of a placement.

- **Correct Example**: `x in Schemes(R)` follows construction or a declared subcategory; a candidate over a lower base is viewed through `base_change_functor`. For an unplaced ideal `I`, `I in Ideals(R).Maximal()` asks the maximality predicate without refining `I` or installing maximal-ideal operations.

#### `CAT-24`: Every Declaration Is an Expression the Reader Can Resolve

- **Rule**: the entries of `super_categories()` and `extra_super_categories()` are category expressions built from names and parameters (`Modules(self.base_ring())`, `Schemes(R).Projective()`), never local variables, `supers + [...]`, `self.base_category().ArrowCategory()`, or anything a reader must execute to learn.  The declared graph is read from source; a declaration only a running session can evaluate is an edge the graph cannot state and the audit cannot check.

- **Rationale**: the audit's "declared from a local expression" list held twenty-six categories whose placement was invisible to every reader and every review.

- **Violation Example**: `algebra = Algebras(...).Associative().Unital(); return [algebra, graded_modules]`; `return supers or [Objects()]`; `return [self.base_category().ArrowCategory()]`.

- **Correct Example**: `return [Algebras(self.base_ring()).Associative().Unital(), GradedModules(self.base_ring(), self.grading_monoid())]`.

#### `CAT-25`: A Declaration Change Is Read on the Graph Before and After

- **Rule**: Any edit to a `super_categories()` or `extra_super_categories()` return, any new category, and any retirement is preceded and followed by `just category-graph shape` and `just category-graph cells`, and the change is judged on their delta: the breadth of the target must not grow, the shortcut list must not gain an entry, the list of generators owing a 2-cell must not gain one that is not a genuine join stated in the commit body, and the largest 2-connected block must not grow.  A grown block is the finding, never a cost to route around.

- **Rationale**: the invariant this architecture asks for, deep and narrow with computed joins, is a property of the whole graph, and every local edge is defensible on its own.  Nobody saw thirty-one declarations into `Sets` or a block of 135 categories until the graph was rendered.

- **Violation Example**: adding a supercategory because the leaf needed a method, without looking at who else declares that target; retiring a class and leaving its consumers to a later reader.

- **Correct Example**: the commit body of a declaration change quotes the before and after of `shape` (declarations, longest chain) and `cells` (H_1 rank, largest block, count owing a cell), and names each edge as shortcut, false, or new-and-immediate.

#### `CAT-26`: A Retirement or Rename Rewrites Its Consumers in the Same Delivery

- **Rule**: When a category is retired into its owner, renamed, or moved between modules, every consumer of the old name is rewritten in the delivery commit: source, the session surface `preamble/all.py` and the package export tables, and every test outside the expectation subtrees (a test's claim is preserved and only its spelling changes; a claim with no surviving spelling is reported, never deleted).  `just preamble-imports` exits zero before the commit.  Notebooks under `computations/notebooks/` are the user's; a notebook that names the old spelling is reported with its cell, not edited.

- **Rationale**: a consumer left behind is invisible while the tree cannot be run, and a lazy export table added so the package still imports hides it indefinitely; on 2026-09-16 the import audit found seventeen such imports, all older than that day, including `DeRhamAlgebra` and `KahlerDifferentials`, names no module had defined for months.  The consumer sweep that followed the axiom passes touched two source files and fourteen test files that the passes had each reported as "outside my tree".

- **Violation Example**: retiring `FormedModules` and leaving five tests importing it; renaming `DeRhamAlgebras` and leaving five modules importing `DeRhamAlgebra`; adding `_EXPORTS` with `__getattr__` so the package imports while a name in the table no longer exists.

- **Correct Example**: the retirement of `Ideals` rewrites `test_fractional_ideals_archive.py` to `CommutativeIdeals(ZZ).extension_to_fraction_field()(I) in FractionalIdeals(ZZ)`, restating the same claim, in the commit that retires the class.

#### `CAT-27`: A Name the Specification Requires Survives as a Thin Function, Never as a Class With a Body

- **Rule**: When a class becomes an axiom category or a join and the expectation files name the class, the name survives as a function of the same parameters returning that category (`def OwnedFields(): return OwnedRings().Division().Commutative()`), or as the axiom class itself under its plural name.  It never survives as a class with its own body, methods, or `super_categories`: a second implementation under the old name is the duplicate `CAT-22` retires.  Operations the retired class carried move to the axiom class at the weakest sufficient structure (`OWN-18`); a join category holds no methods, so an operation a join needs is placed on the nested join class Sage generates or on the data class that consumes the datum.

- **Rationale**: the specification is written blind and its names are the contract; the implementation meets the contract by resolving the name to the right category, not by keeping the old class alive beside the new one.

- **Violation Example**: `OwnedOrders` kept as a class "because a join holds no methods" while also declaring the join, so the name is both the join and a second class over it.

- **Correct Example**: `StrictlyCommutativeDifferentialGradedAlgebras(R)` returning `DifferentialGradedAlgebras(R).Supercommutative().Alternating()`; `PrimeFields` as the plural name of `OwnedRings.Division.Commutative.Prime`.

#### `CAT-28`: An Engine Class Is Not a Category, and It Is Never Removed for Not Being One

- **Rule**: A class that realizes objects -- a condition set driving subsets, the class computing a glued scheme, the groups \(\operatorname{Aut}(L/K)\), a module of global sections, \(L^p\) -- is an engine.  Its objects belong to a category that already exists (`Sets()`, groups, `Schemes(R)`, `Modules(R)`), and the engine is repaired by threading: its objects are constructed by that category's entry (`_object_of(C, **data)` holding the engine privately, or an engine class statically extending `C.ObjectType`), with cooperative `super().__init__`, no non-root `Parent.__init__`, and no side attributes.  An engine's class of realizations, a grouping of objects by how they were computed, is a class, never a category.  A full subcategory cut out by a mathematical condition on objects is a category even when the condition names a construction: the abelian groups that are Picard groups of schemes form the full subcategory `PicardGroups()` of `Modules(ZZ)`, and `Pic` takes values in it (owner ruling, 2026-10-16).  An engine class is never deleted because it is not a category, and a count of classes on `Parent` is never a target.  A new category class cites, in its commit body, the `lean-categories` definition giving its objects and its morphisms, and the `CAT-22` search.
- **Rationale**: `lean-categories` states what objects are and the preamble's category graph presents it; an engine states how one object is realized.  Turning an engine into a category makes a realization choice into mathematics, and consumers start routing on how an object was built (`CON-16`, `CAT-01`).  Deleting the engine is the same inversion from the other side.
- **Violation Example**: 2026-09-17, converting hand-assembled parents: `ConditionSets`, `ImageSets`, `BlackBoxGroups` (a model of computation), `FiniteExtensionAutomorphismGroups`, `GeneratedSubmonoids`, `PredicateSubmonoids`, `GluedSchemes`, `GlobalSectionModules`, `QuasiCoherentSheavesWithChosenDescentDatum`, `LebesgueSpaces`, `SequenceSpacesOfExponent`, `DifferentiabilityClassesOfOrder`, `FixedSizeSelections`, `CurvesWithChosenNormalization` (a normalization is canonical, never chosen); and, in the other direction, ruling that the engine ring class must go.
- **Correct Example**: categories defined by mathematical data whose morphisms come from morphisms of that data, such as symmetric groups \(\mathrm{Sym}(\Omega)\) on sets, general linear groups \(\mathrm{GL}_n(R)\), and quotients \(F/\langle\!\langle R\rangle\!\rangle\) of free groups, are categories `lean-categories` may formalize, presented with levels that build their engines privately from the datum; a black-box group, whose datum is an encoding with oracles, is not.  Also: a glued scheme constructed as `_object_of(Schemes(R), scheme_base_ring=R, scheme_engine=_GluedScheme(datum))`; \(\Gamma(X, F)\) a `GeneralModules(A)` module on the set equalizer of the overlap readings; `class _ConditionSet(Sets().ObjectType)` constructed by `X.condition_set(P)`, which computes its placement from the universe.

#### `CAT-29`: Categorical Framings and Resolution Conditions Are Specializations of Augmented Objects

- **Rule**: `lean-categories` is the mathematical authority. Begin with a *chosen augmented object*, not an object already certified as an exact resolution. In a suitable stable \(\infty\)-category \(\mathcal E\), an augmentation is an object \(\varepsilon:R^\bullet\to j(X)\) of the slice \(\mathcal E_{/j(X)}\), where \(j:\mathcal C\to\mathcal E\) is the specified comparison from the original category. It canonically determines the cofiber sequence

  \[
  R^\bullet\xrightarrow{\varepsilon}j(X)\longrightarrow Q_\varepsilon
  \longrightarrow \Sigma R^\bullet,\qquad Q_\varepsilon=\operatorname{cofib}(\varepsilon).
  \]

  The augmentation and cofiber always exist when the indicated stable constructions do; **\(Q_\varepsilon\simeq0\) is an optional condition**, not admission to the category of augmented objects. It characterizes an equivalence in \(\mathcal E\), hence a *full derived resolution* under the appropriate comparison hypotheses. An **epimorphic** augmentation in \(\mathcal C\) is a different condition; it need not have vanishing cofiber. In a derived category with a suitable t-structure, an epimorphism of degree-zero objects kills \(H^0(Q_\varepsilon)\), but need not kill the lower cofiber homology. Do not identify a general stabilization \(\operatorname{Sp}(\mathcal C)\) with a derived category \(D(\mathcal C)\), or use stable equivalence to assert epimorphy in \(\mathcal C\).

  A **selected graded, filtered, chain, or simplicial presentation** of \(R^\bullet\) must remain part of the defining augmented datum whenever algorithms or predicates refer to its terms. A bare object of \(D(\mathcal C)\) does not remember chosen generators, differential maps, degreewise projectivity, or exact truncation data. In an additive/abelian setting these can be presented as augmented chain complexes and compared with a suitable derived enhancement; in general use augmented simplicial or other appropriate higher-categorical objects. Neither `Ch(C)` nor `D(C)` is available for an arbitrary category without hypotheses.

  The **truncation level** \(n\), **amplitude/length**, **termwise categories** (free relative to a specified adjunction, projective, flat, flasque, \(\mathcal F\)-acyclic), **arrow conditions**, and **exactness/connectivity conditions** on \(Q_\varepsilon\) are independent refinements of this underlying construction. Termwise conditions pull back along degree-evaluation functors; they are not hard-coded into a distinct resolution constructor. A truncation does **not** force exactness at its last retained degree. `FP_n` is a property asserting existence of an appropriate finite partial projective resolution, not a selected resolution itself; state exactly which degrees count when translating between indexing conventions. Dual/coaugmented models, such as injective and flasque resolutions, use the corresponding arrow orientation and admissible category.

  For a free--forgetful adjunction \(F:\mathcal D\rightleftarrows\mathcal C:U\), a **categorical framing** of \(X\) is *precisely* a selected pair \((S,\phi)\) with \(S\in\mathcal D\) and an **isomorphism** \(\phi:F(S)\xrightarrow{\sim}X\) in \(\mathcal C\). This is the length-zero free-resolution specialization. Replacing the isomorphism by an epimorphism gives a free cover, not a framing. For a smooth \(n\)-manifold, take \(\mathcal C=\operatorname{Mod}(\mathcal O_X)\), the sheaf free-module construction, and \(\phi:\mathcal O_X^{\oplus n}\xrightarrow{\sim}\mathcal T_X\); the equivalent bundle trivialization is \(X\times\mathbb R^n\cong TX\). Applying global sections afterward is a functor, not the definition of the framing. A stable framing is a chosen trivialization after adjoining the specified trivial summand; it is not implied by passage to a derived or stable category.

- **Rationale**: An object can admit an epimorphic free cover without being free, so **"every object has a free cover" never implies "every object has a framing"**. The free--forgetful counit can supply a canonical first cover (where it is epimorphic) and a comonadic simplicial augmentation, but not a chosen invertible framing or an automatic quasi-isomorphism in an unspecified enhancement. A chosen augmentation is additional mathematical data; an existence property is a separate classifier. Sage's former global `Framed` axiom propagated a spurious property across ring/module/algebra category joins and broke `ZZ -> QQ`/`RR` coercions. The replacement must not introduce new competing categories for a free cover, a basis, a projective truncation, or a flasque resolution when they are all specializations of the same augmented-object construction. Preserve the exact selected terms and maps while retaining their universal forgetful functors. Sources for comparison: `lean-categories/FOUNDATIONS.md` §§13, 76--77; nLab *framed manifold*, *G-structure*; Quillen, *Homotopical Algebra*, II.4; Weibel, *Introduction to Homological Algebra*, §§2, 8; Barr--Beck, *Homology and standard constructions*. Verify precise source sections before citing them in mathematical code.

- **Violation Example**: a global `Framed` axiom registered in `all_axioms` and declared on objects, groups, modules and algebras (`objects.py`, `FramedModules(R)`, `FramedAlgebras(R)`); membership in `C.Framed()` decided by a framing stored on the object; `is_framed_algebra()` reading an attribute; a chosen-presentation class declaring `Framed` as its supercategory.

- **Correct Example**: In `Mod_R`, the augmentation \(R\twoheadrightarrow R/(2)\) is a free cover but **not** a framing or an equivalence of degree-zero derived objects; its cofiber has a nontrivial kernel class. The augmentation \(R^{(S)}\xrightarrow{\sim}M\) is a categorical framing with \(Q_\varepsilon\simeq0\). A selected two-term presentation \(F_1\to F_0\to M\) keeps its relation morphism and need not be exact at the leftmost term. Over \(\mathcal O_X\), \(\mathcal O_X^{\oplus n}\cong\mathcal T_X\) is a framing of the tangent sheaf. The module `QQ` over `ZZ` can have a nonfinite free cover without being finitely generated or framed. `FreeCover`, `BasedModule`, `Coord`, and selected injective/flasque resolutions are **named specializations/arrow variants of the shared augmented model**, not alternative foundations for it.

#### `CAT-30`: A Named Notion Is Unfolded Before It Is Given a Category

- **Rule**: Before declaring a category for a notion that a literature names (a vector configuration, a marking, a pointed object, a labelled family, a decorated graph), unfold the notion into the objects and maps it is made of, from `lean-categories` or an opened source, and use what already exists. A finite family of elements of an object \(X\) is a map \(I \to U(X)\), an `IndexedFamily`; an equivalence of families is an element of the transporter of the action of \(\operatorname{Aut}(X)\times\operatorname{Sym}(I)\) on \(X^I\), and its automorphisms are the stabilizer; a colouring is a map \(I\to C\) that the permutations must preserve. A subset is a subobject of the underlying set. An object together with an arrow is a slice or coslice object, not "an object with data"; several arrows are remembered by (co)slicing over pullbacks or pushouts (products or coproducts). A pair \((X, x)\), \(x\in F(X)\), is an object of the Grothendieck construction \(\int F\) of \(F\colon\mathbf C\to\mathbf{Set}\), and a property of \(x\) (primitive, isotropic) cuts out a full subcategory of \(\int F\). When \(x\) is a point of \(X\), \(F\) is the covariant hom out of the point, \(F=\operatorname{Hom}_{\mathbf C}(*,-)\), and \(\int\operatorname{Hom}_{\mathbf C}(*,-)\cong {*}/\mathbf C\): a pointed object is a coslice object, the same statement as above. A family of elements is a set map \(v\colon I\to U(X)\), where \(I\) is a set carrying whatever structure the notion needs: a colouring is a map \(I\to C\) (so \(I\) is a set over \(C\)), and a coloured multiset is the family of pairs \((v_i, c_i)_{i\in I}\), a not necessarily injective map \(I\to U(X)\times C\). An \(I\)-indexed family of objects of a category \(\mathbf C\) (of sheaves, say) is a functor from the discrete category on \(I\), an object of \(\mathbf C^{I}\). Families are never encoded through a free functor (\(\mathbb Z^{I}\to L\)): that only exists where a free functor does, and it does not generalize (owner, 2026-10-14). A family with reindexing is an object of a comma category. Owner ruling (2026-10-14): "'an object with an arrow' is not 'an object with data', it literally IS a slice or coslice object ... You should err on the side of the abstraction being actual mathematics." A new category class is admitted only for a notion whose unfolding is none of these and which `lean-categories` formalizes as a category (`CAT-22`, `CAT-28`). The name a literature gives a notion is never evidence that the notion is a category.
- **Rationale**: A category class for a named notion arrives with its own Mor, elements, identity and composition, all reimplementing what the group action or the existing construction already supplies, and every later consumer builds on the duplicate. The name makes the class look like mathematics, so review does not unfold it.
- **Violation Example**: `VectorConfigurations(R)` (introduced `0a9d7f4dc9`, 2026-09-06, from PORT_TODO 3.7 "pairing configuration graphs"): a category whose objects were "a sublattice with a chosen ordered framing", later given its own `ConfigurationMor` and `(\sigma, g)` elements; mathematically a configuration is a family \(v: I\to L\), and its isomorphisms are the transporter of \(O(L)\times\operatorname{Sym}_C(I)\) on \(L^I\). A protected expectation file was written against the class and propagated it.
- **Correct Example**: `v = finite_indexed_family_from_values(I, vectors)`; `Aut(v)` the stabilizer of \(v\) under \(O(L)\times\operatorname{Sym}_C(I)\); `Isom(v, w)` the transporter, realized by the graph-certificate and integral-structure computation behind the existing G-set operations.

#### `CAT-02`: Property Categories Do Not Manufacture Chosen Data

- **Rule**: Distinguish a property from a chosen witness of that property.
  A property category such as finitely generated or finitely presented states existence; a chosen generating morphism or presentation is a truncated resolution in the category of resolutions over `C` (`CAT-29`), which carries the operations that consume that choice.
  A property category never silently computes or selects the witness on demand.

- **Rationale**: Existence of a presentation is weaker than a chosen presentation.
  Conflating them makes algorithms depend on arbitrary hidden choices and incorrectly turns unavailable witness computation into failure of the mathematical property.

- **Violation Example**: `FinitelyPresentedGroups().ObjectType.presenting_free_group()` computing a presentation merely because the group is known finitely presented; asking every finitely generated module for a preferred generating set.

- **Correct Example**: `FinitelyPresentedGroups()` records the property; `GroupsWithChosenFinitePresentation()` carries and exposes the selected presentation. A one-term augmented free-module object with epimorphic augmentation carries a chosen cover of `M`, while `Modules(R).FinitelyGenerated()` only states that some finite one exists. Such a cover does not automatically satisfy the full-resolution (vanishing-cofiber) condition.

#### `CAT-03`: Constructibility Does Not Require Enumeration or Generators

- **Rule**: A mathematically defined object may be useful and constructible through membership, universal properties, or predicate carve-outs even when no algorithm enumerates it or returns a finite generating set.
  Do not identify "construct the object" with "compute a presentation of all of its elements."

- **Rationale**: Many important objects are first-class long before a full presentation is available.
  Orthogonal groups, stabilizers, centralizers, kernels, and ring centers can support containment, individual elements, morphisms, and further subobjects without globally enumerating generators.

- **Violation Example**: Refusing to provide `O(L)` because the available backend cannot compute generators for an indefinite lattice; replacing it by `None` or by a tuple of known isometries.

- **Correct Example**: Represent `O(L)` as the subgroup of `GL(L)` cut out by the form-preservation predicate, so membership and individual isometries are meaningful; a definite-lattice subcategory may additionally compute a finite generating set.

#### `CAT-04`: Category Placement Is a Claim Made by Construction, Not a Proof-Certificate System

- **Rule**: Category membership is placement: the construction that places an object claims the category's properties, and nothing at runtime checks or certifies that claim.
  Do not invent proof objects, evidence records, certificate registries, or trust levels to justify placement, and never let an implementation's answer justify it.

- **Rationale**: Runtime certificate machinery duplicates the category graph and certifies nothing: anything an implementation says about itself is untrusted.
  The theorems are `lean-categories`', and whether an implementation's answers are correct is judged only by the `lean-cas-dsl` acceptance suite.  An object in a data-bearing category supplies its datum; a named predicate computes its answer.

- **Violation Example**: Introducing `FinitePresentationCertificate`, `ProofOfNondegeneracy`, or an evidence registry that must accompany refinement into the corresponding category; a predicate hard-coded to return `True` offered as grounds for placement.

- **Correct Example**: A finitely generated formed module computes `is_nondegenerate` from the defining correlation when that is decidable, and that answer is an untrusted computation.  Where `lean-categories` proves that every object of a category is nondegenerate, the preamble presents that inclusion as a supercategory entry (`CAT-15`), and on that category the predicate answers by placement.  An implementation returning `True` on the strength of a theorem it asserts itself is a claim nothing supports.

#### `CAT-05`: Operations Live on the First Category Where They Are Mathematically Defined

- **Rule**: Put an operation on the appropriate `ObjectType`, `ElementType`, Hom-category/arrow type, or functor type of the most general category on which `lean-categories` defines it.
  A more structured subcategory inherits that API and adds only the operations supplied by the additional structure.  Sage method-container classes may realize this privately but are not the public placement vocabulary.
  Do not place an operation on a ubiquitous underlying object and guard it with shape, type, backend, or capability tests when category placement can state the hypothesis.
  **Placement test.** The placement of an operation introduced on `C` is correct exactly when `lean-categories` does not define it on any supercategory of `C`.  State it as a poset problem.  Let `P` be the declared category poset and `U_C = {D in P | D > C}` the up-set of `C`.  For each operation `f` introduced on `C`, the set `W_f = {D in U_C | f is well-defined on D}` is closed downward within `U_C`, and the home of `f` is `max W_f`, or `C` itself when `W_f` is empty.  When `W_f` has several maximal elements, or its maximum is not a category in `P`, the finding is a category, axiom or property `lean-categories` formalizes and the preamble does not yet present, a formalization request to `lean-categories` where it does not, or a defect in the declared graph; it is never a reason to leave the operation where it is.  The test applies equally to object, element and arrow operations; an arrow operation is judged on the Mor categories of the supercategories.

- **Rationale**: The category graph, presenting `lean-categories`' placement, is the API graph.
  An element should acquire methods because of what mathematical object it is, not because a monolithic implementation class recognizes a special runtime case.
  This also keeps multiple independent refinements composable: algebraic, Lie, scheme, smooth, topological, and arithmetic APIs can coexist on one mathematical object without one implementation pretending to own the others.

- **Violation Example**: A generic tensor element exposes `smith_form()` only when `hasattr(engine_matrix, "smith_form")`; every matrix exposes `determinant()` and raises unless it happens to be square over a commutative ring; `MatrixSpace` always installs Lie methods merely because `m == n`.

- **Correct Example**: Entry access, rows, columns, and transpose live on matrix spaces; square-matrix multiplication lives on square matrix rings; determinant lives where square matrices over commutative scalars have it; Smith normal form is available because the coefficient ring is a PID and its matrix-reduction operation acts on `M_{m,n}(R)`; the commutator bracket is inherited from a suitable associative algebra; scheme/manifold/topological methods come from their respective refinements.

#### `CAT-06`: Structure Induced by Parameters Belongs to the Parameter Categories

- **Rule**: When an operation on a mathematical object exists because one of its parameters has a mathematical property, model that capability on the parameter category and let the object use it; do not manufacture a parallel object category whose only purpose is to restate the parameter hypothesis.
  Shape-dependent structure may refine the object itself when shape changes the operations on its elements, but coefficient-ring properties remain properties of the coefficient ring.

- **Rationale**: `M_{m,n}(R)` is the same kind of matrix space whether or not `R` is a PID.  The PID hypothesis explains why Smith reduction is available; it does not create a new species of matrix.  Conversely, the distinction `m=n` genuinely changes the matrix object's intrinsic multiplication and can justify square-matrix-ring structure.

- **Violation Example**: Introducing `PIDMatrices`, `MatricesOverFields`, `MatricesOverEuclideanDomains`, or similar parallel matrix categories solely so ordinary matrices acquire algorithms implied by the coefficient ring.

- **Correct Example**: `M_{m,n}(R)=Hom_R(F_R([n]),F_R([m]))` remains the same Hom object.  When `R` is a PID, an element `A` presents `coker(A)`; invariant-factor normalization of that presentation yields the Smith diagonal and its source/target basis changes.  When `m=n`, the same object is `End_R(F_R([n]))`, whose multiplication is already composition.

* * *

### 5. Definition Fidelity (`DEF-*`)

#### `CAT-07`: Preamble Category Types Supply the Object and Element API

- **Rule**: Operations shared by every element of a mathematical category belong on that category's `ElementType`; object-wide constructions belong on its `ObjectType`; arrow operations belong on the element type of the appropriate Hom/arrow category.  Concrete/runtime classes store only representation-specific data/primitives that the categorical API delegates to.

- **Rationale**: The category graph presents the mathematics and is therefore the correct place for uniform syntax and operations.  Duplicating scalar multiplication, inversion, bracket, matrix entry, or similar methods on each concrete representation class makes those classes define the theory and causes one representation to miss operations another happens to implement.

- **Violation Example**: Adding Python-literal scalar multiplication separately to presented-module, lattice, tensor-product, and localized-module element classes; putting matrix operations on a backend matrix wrapper instead of the matrix-Hom category.

- **Correct Example**: the `ElementType` supplied by `Modules(R)` carries left scalar syntax through the object's scalar action; the matrix-Hom element type supplies entries/rows/columns; a concrete presented-module runtime element supplies only the representation primitive needed by those category methods.

#### `DEF-01`: A Predicate's Body Is Its Definition, Not a Recognition Criterion

- **Rule**: Implement a mathematical predicate from its `lean-categories` definition, expressed through the preamble objects and morphisms that occur in that definition.
  Do not substitute a theorem-equivalent determinant, rank, gcd, coordinate, or matrix criterion as the predicate body merely because it is cheaper in a familiar special case.  Such criteria are permitted **underneath the semantic method** as implementation cases, citing the `lean-categories` theorem and its hypotheses; downstream callers never see or repeat them.

- **Rationale**: A recognition criterion used as the public definition carries an unstated theorem and its hypotheses at every call site.
  A body that spells the definition has one visible review obligation: that it spells the definition correctly.  The low-level operations named by that definition may route to exact criteria in the represented categories where `lean-categories`' theorems apply, so the optimization is stated once and remains private forever.

- **Violation Example**: `is_nondegenerate()` as `gram.det() != 0`; `is_unimodular()` as `abs(gram.det()) == 1`; `is_primitive()` as a gcd of coordinates; `is_injective()` as a matrix-rank comparison.

- **Correct Example**: Nondegeneracy asks whether the correlation `M -> dual_module(M)` is injective; unimodularity asks whether that correlation is an isomorphism; primitivity asks whether the cokernel of the inclusion is torsion-free; injectivity asks whether the kernel is zero.

#### `DEF-02`: Numerical Data Does Not Replace the Structural Object It Describes

- **Rule**: When a numerical invariant or normal form is derived from a structural object, keep the structural object as the public mathematical result and quarantine the numerical computation behind its owner.
  Do not let a matrix, basis, rank, content, determinant, or invariant-factor tuple stand in for a kernel, cokernel, subobject, quotient, normal form, or morphism.

- **Rationale**: Numerical data often determines the desired object only under additional hypotheses and chosen coordinates.
  Returning the structural object preserves its universal property and lets downstream code compose mathematically instead of re-proving the reconstruction theorem.

- **Violation Example**: Returning kernel basis vectors instead of `ker(f)` with its inclusion; implementing saturation as `Matrix.saturation()`; returning a Smith matrix as "the normalized module."

- **Correct Example**: `f.kernel()` returns the kernel subobject with its inclusion; saturation is the kernel of `M -> M/S -> (M/S)/Tor(M/S)`; invariant-factor form returns a new framed module together with the explicit isomorphism from the original.

#### `DEF-03`: Return the Codomain the Definition Gives; Do Not Presume Special Cases

- **Rule**: A constructor or general operation returns the object in the codomain `lean-categories` gives it.
  Do not construct the result directly in a special subcategory merely because current examples usually land there.  A special codomain is used only where `lean-categories` states it for the operation under the operation's hypotheses; a computed property of the result is an answer to its caller, never a refinement (`CON-07`).

- **Rationale**: Presuming the special case turns an accidental property of test data into part of the operation's codomain.
  Keeping the formalized codomain lets special algorithms remain available where their hypotheses are stated.

- **Violation Example**: Presenting every cokernel of a lattice embedding as a torsion module even when the quotient can have positive rank; constructing a quotient as finite because all current fixtures are finite; refining a cokernel into the torsion category because a computation of its invariant factors reported torsion.

- **Correct Example**: Construct the cokernel as a finitely presented module from the presenting morphism; `is_torsion()` computes from its invariant factors and returns an answer.

#### `DEF-04`: Matrix Normal Forms Are Presentation Normalizations

- **Rule**: For a matrix representing a morphism of finite free modules, present Smith/invariant-factor normal form as `lean-categories` formalizes it, through equivalence of the corresponding presentation, not as an unrelated primitive matrix routine.
  Over a PID, `A : R^n -> R^m` presents `coker(A)`; the structure theorem for finitely generated `R`-modules gives an invariant-factor presentation.  The normal-form witness consists of the diagonal presentation together with the source and target basis-change isomorphisms relating it to `A`.
  A backend matrix routine may compute those basis changes privately, but the public mathematical construction is the presentation normalization.

- **Rationale**: The diagonal entries are the invariant factors of the presented module, and left/right multiplication are changes of chosen bases in the two free modules.  Treating Smith form as a standalone array algorithm duplicates the module-classification theorem and disconnects the witness from the cokernel it classifies.

- **Violation Example**: Presenting `R.smith_form(A)` as a primitive ring method whose contract is merely whatever triple Sage returns; computing invariant factors separately in the presented-module layer and Smith matrices separately in the tensor layer.

- **Correct Example**: Normalize the presentation `R^n -> R^m -> coker(A)` to its invariant-factor presentation, retaining isomorphisms of the presenting free modules.  `A.smith_form()` is then the coordinate matrix of that normalized presentation together with the coordinate matrices of those basis changes.  If a backend canonicalizes a relation submodule before reduction, its basis change must be included in this presentation isomorphism; it may not be discarded.

#### `DEF-05`: A Normal Form Is a New Object Together With an Isomorphism

- **Rule**: When normalization, reduction, canonicalization, or re-presentation changes chosen framing/presentation data, the result is a new preamble object of the same mathematical category together with an explicit isomorphism from the original.  Do not mutate the source into its normal form and do not make the comparison morphism an optional flag.

- **Rationale**: Chosen presentations are structure.  Smith/Hermite/invariant-factor reduction may produce an isomorphic abstract module while changing its framing and relations.  Without the isomorphism there is no mathematical statement connecting the two represented objects, and downstream transported structures have no witness along which to move.

- **Violation Example**: Replace a module's selected presentation with its Smith matrix in place; `normal_form(transformation=False)` returns only the diagonal object; use `normalize=True` to alter constructor semantics without representing the map.

- **Correct Example**: `M.invariant_factor_form()` returns an isomorphism `M -> M_normal`; the matrix normal form is the private/coordinate computation used to construct that arrow.  Normal forms of actual matrix objects may remain matrix operations, while normal forms of framed modules are object-plus-isomorphism constructions.

#### `DEF-06`: Exact Mathematical Questions and Soft Knowledge Questions Have Different Codomains

- **Rule**: Preserve the actual mathematical codomain of an exact operation or predicate.  Do not return `False`, `None`, or `Unknown` merely because the current implementation cannot decide/compute a represented case.  An exact operation uses the assertion-gated computational frontier of `CAT-01`.  An exact predicate returns a proposition: `True` or `False` where the question is computable or decidable and is decided, and otherwise the `Predicate` (`preamble/logic.py`) that states it, which `ask(P)` evaluates to `True`, `False` or `Unknown`.  Separately, an explicitly **soft knowledge/computability predicate** may be designed with a three-valued codomain `True | False | Unknown` when the proposition being returned is itself “what is currently known/computable/available.”

- **Rationale**: “The object is not nondegenerate” and “the current system does not know whether it is nondegenerate” are different statements.  So are “this group is not finitely generated” and “no generating-set algorithm is currently available.”  Collapsing them creates confident mathematical falsehoods; returning `Unknown` from an exact-valued operation changes its mathematics just as badly.

- **Violation Example**: `is_nondegenerate()` returns `False` when no algorithm handles an infinite callable form; `cardinality()` returns `Unknown`; `generators_are_computable()` returns `True` merely because the constructor accepted external input.

- **Correct Example**: `is_nondegenerate()` computes known cases and returns the proposition on the rest; `G_QQ.is_abelian()` returns `False` from a finite quotient isomorphic to `S_3`; `Sets().Mor(QQ, QQ)(f).is_injective()` for an arbitrary function `f` returns the proposition, and `ask` of it is `Unknown`.  A distinct `generators_are_computable()` or `has_computed_group_generators()` may return Sage's `Unknown` when that explicitly three-valued knowledge question has not been decided.

#### `DEF-07`: An Operation's Codomain Is `lean-categories`'; an Implementation Outside It Is a Finding

- **Rule**: The object an operation lands in is the codomain `lean-categories` gives it, never one read off implementations.  The typical case is not the codomain; it is a specialisation of it.  Before annotating, read every implementation: one whose values fall outside the formalized codomain is a defect in that implementation, or evidence that the mathematics wanted is not what `lean-categories` formalized, which is a request there.

- **Rationale**: An operation is usually written first for the case at hand, so its apparent codomain is the one the author had in view.  `signature_pair` looks \(\mathbb N^2\)-valued from eight of its implementations, while `_ColimitGram` returns `(Infinity, large_negative)`, `(large_positive, Infinity)`, or `(Infinity, Infinity)`.  Implementations do not settle which codomain is right; the formalization does, and the disagreement is what gets reported.

- **Violation Example**: choosing a return object from the implementation in front of you; annotating from the first case; widening an operation's codomain because an implementation returned a value outside it.

- **Correct Example**: reading the `lean-categories` codomain and all implementations, reporting each implementation that falls outside it, and recovering finite cases as the axiom-gated refinements `lean-categories` states.  See `CON-15` for naming the product once the codomain is known.

* * *

#### `CAT-08`: Mathematical Enumeration Is Lazy; Materialization Is Backend-Only

- **Rule**: Mathematical code never replaces a preamble set, framing, basis, generating family, index set, group, Hom index, or other mathematical collection by `tuple(...)`, `list(...)`, or another eagerly materialized Python container, even when the collection is known finite.  Consumers iterate the preamble collection lazily or use its membership, cardinality, rank/unrank, indexing, finite-support, image, product, or family structure.  Whole-family materialization is permitted only inside a private backend adapter whose external API specifically requires a finite concrete array; that adapter must establish finiteness before serialization and the Python container must not escape it.
- **Rationale**: Finiteness does not turn a mathematical collection into a Python sequence.  Keeping one collection interface for finite and infinite cases prevents downstream code from acquiring accidental `len`, slicing, whole-family traversal, or representation assumptions.  Enumerability, order, cardinality, and finiteness remain mathematical structure; backend arrays are only a final serialization format.
- **Violation Example**: `labels = tuple(M.module_generating_set())` before ordinary module logic, even when `M` is finite; storing `self._generators = list(generators)`; converting a finite index set to a tuple merely to enumerate it twice; checking a callable section by evaluating it at every index; implementing `Sym^n(M)` by first materializing the framing.
- **Correct Example**: Keep `M.module_generating_set()` as the preamble ordered/indexed set and iterate it directly.  Use `rank(label)`/`unrank(i)` or finite support when positional access is needed.  A private Sage/GAP/Julia bridge may serialize a mathematically finite ordered set to a Python row/column array immediately before the backend call and discard that array on return.  A finite-presentation algorithm dispatches from `ModulesWithChosenFinitePresentation`, not merely from a weaker existence property.

### 6. Mathematical Vocabulary & Public Types (`LEX-*`)

#### `LEX-01`: Every Public Name and Type Has a Standard Mathematical Referent

- **Rule**: A public name denotes a standard mathematical object, morphism, construction, invariant, property, or chosen structure with its defining data understood from the category.
  Do not mint public wrapper types or names for implementation roles, storage formats, backend distinctions, or local workflow conveniences.

- **Rationale**: A type name presents `lean-categories`' mathematics to the session.
  An implementation-flavored noun creates a parallel vocabulary that downstream code will start treating as mathematics.

- **Violation Example**: `ExactScalar`, `NativeLattice`, `DiscriminantGroup` as a new type distinct from the finite abelian group underlying a discriminant form, or a wrapper whose only purpose is to package a tuple of constructor arguments.

- **Correct Example**: Use `RingElement`, `RealApproximation`, `FiniteAbelianGroup`, `DiscriminantForm`, `ModuleMorphism`, and the existing categorical constructions whose definitions state the actual mathematics.

#### `LEX-02`: Names State the Structure They Belong To

- **Rule**: When the same noun exists for several structures on one object, the public name states the structure explicitly.
  Use `group_generators`, `module_generators`, `algebra_generators`, `module_generating_set`, and similarly qualified dual or action names.
  Do not keep a bare ambiguous name as a compatibility alias underneath the precise one.
  When one predicate name is true of an object under two of its structures -- `is_framed` on a framed module that is also a framed algebra -- qualify both (`is_framed_module`, `is_framed_algebra`); never resolve the collision by deleting one in favour of category membership, and never by surveying Sage, which has no such notion: this rule is the standard.

- **Rationale**: An algebra can simultaneously have group, module, and algebra generators; an object can carry several dualities.
  A bare `generators()` or `dual()` therefore has no stable mathematical referent even when today's concrete class happens to have only one candidate.

- **Violation Example**: `generators()`, `gens()`, `generating_set()`, or `dual()` on an owned multi-structured object; `module_generators()` implemented as a delegation to the still-public ambiguous `generators()`.

- **Correct Example**: The module framing exposes `module_generating_set()` and `module_generator(label)`; a group exposes `group_generators()`; metric, module, and group dualities have distinct names tied to the functors that produce them.

#### `LEX-03`: Exact Mathematics Is the Default; Approximation Carries the Adjective

- **Rule**: Public mathematical nouns denote exact objects unless approximation is explicitly part of the type or operation name.
  Approximate numerical representations are extracted at plotting, display, numerical-analysis, or other explicitly approximate boundaries.

- **Rationale**: Marking the exact case as exceptional reverses the mathematical default and can make exact objects such as algebraic or symbolic reals impossible to state.

- **Violation Example**: Using `RealNumber` to mean an MPFR approximation while exact `sqrt(2)` needs a separate exceptional type; a public `ExactScalar = Integer | Rational` union that describes implementation classes rather than the mathematical field `QQ`.

- **Correct Example**: `RealNumber` denotes an exact real in the repository's mathematical vocabulary where represented; `RealApproximation` or an explicitly precision-bearing operation denotes an MPFR approximation.

#### `LEX-04`: Software Roles Are Not Mathematics

- **Rule**: Interpret fields, accessors, aliases, wrappers, helper classes, registries, and implementation edges by the mathematics they denote, not by their software role.  Public mathematical nouns must be standard mathematical objects/data whenever such a referent exists.  Do not create an epistemic or administrative vocabulary (`knowledge`, `evidence`, `provider`, `manager`, `context`, `metadata`, `model`, `descriptor`, `record`, `info`, `result`, `factory`, `payload`, `adapter`, `backend`) to stand in for morphisms, functors, bases, sections, predicates, isomorphisms, or other standard data.

- **Rationale**: Code is one presentation of mathematics.  Treating declaration shape as mathematics causes real mathematical content to be demoted to “plumbing” and then replaced by project-private concepts.  That private vocabulary expands rapidly because every later operation has to translate between it and the actual mathematical objects.

- **Violation Example**: `SubobjectEvidence` containing an inclusion; `GeneratorProvider` containing an indexed family; `NormalizationContext` containing an isomorphism; dismissing a local functor as a mere “realization edge” because it is stored in a helper field.

- **Correct Example**: Name the inclusion morphism, indexed family, isomorphism, or functor directly.  An engineering cache/adapter may have engineering vocabulary privately, but the mathematical layer exposes the standard object it implements.

#### `LEX-05`: Standard Mathematical Vocabulary Outranks Backend Vocabulary

- **Rule**: Public names follow `lean-categories`' names, which follow the standard terminology of the mathematical literature, even when Sage or another backend uses a different historical spelling.  Backend class/method names are preserved only inside backend calls and adapters; they do not determine the public noun or verb.

- **Rationale**: The preamble presents a mathematical language, not a compatibility facade.  Importing backend terminology into the public API imports its historical conventions, implementation distinctions, and sometimes mathematically misleading names.  Standard vocabulary makes the same concept recognizable independently of the current engine.

- **Violation Example**: Call invariant factors merely `invariants` because Sage does; expose an FGP/backend class name as a mathematical category; retain an implementation-specific normal-form name for the object rather than the literature's object/invariant.

- **Correct Example**: Use `invariant_factors`, standard signature terminology, standard dual/functor names, and ordinary categorical nouns.  Private adapters may call Sage's `.invariants()`, `.gens()`, or exact backend class names while converting the result back into preamble vocabulary.

#### `LEX-06`: Processes and Named Examples Do Not Become Mathematical Kinds

- **Rule**: A public type/category/constructor name must denote a reusable mathematical concept, not the process by which an ordinary object was generated or its role in a test/example.  Randomness, fixture/example status, “standard test object”, and similar modifiers generate/select data for existing constructors.  A named specimen may live in a catalogue without becoming a new category-level concept.

- **Rationale**: Reifying process labels produces artificial `Random*`, `Example*`, `Test*`, `Factory*` taxonomies and then forces routing, methods, and documentation to distinguish objects that are mathematically just ordinary members of an existing category.

- **Violation Example**: `RandomLattices`, `RandomLatticeOfSignature`, `ExampleModule`, or a category API obligation for a local `rankTwo` example.

- **Correct Example**: `random_gram(...)` produces legitimate construction data and the ordinary lattice constructor consumes it; named objects such as `E8` live as catalogue specimens constructed by the same public lattice language.

#### `LEX-07`: Public Mathematical Names Never Encode the Current Algorithm or Computability Frontier

- **Rule**: Name a public operation by the mathematical concept it denotes.  Words describing the present decision procedure, engine, performance profile, or implementation branch—`partial`, `fast`, `cached`, `sage`, `gap`, `brute`, `PDOnly`, theorem-name-as-algorithm-adjective, etc.—belong in implementation notes/private adapters, not in the mathematical noun/verb.

- **Rationale**: The mathematical predicate stays the same as algorithms improve.  Encoding today's route in the name freezes a temporary computational boundary into the public vocabulary and invites duplicate methods when a second algorithm arrives.

- **Violation Example**: `eichler_partial_is_isometric`, `sage_computable_genus`, `fast_kernel`, `cached_discriminant_group` as public mathematical operations.

- **Correct Example**: `is_isometric`, `genus`, `kernel`, `discriminant_group`; their implementations route among exact algorithms and assertion-gate the current frontier as needed.  The docstring/private implementation records which `lean-categories` theorem or backend handles each case.

#### `LEX-08`: Distinguish a Mathematical Construction From the Numerical Operation Representing It

- **Rule**: When a numerical operation is the coordinate representation of a mathematical construction, name each at its own level.  In particular, matrices have a **Kronecker product**; linear maps/modules have tensor products.  Similar distinctions apply to Gram matrices versus forms, Smith matrices versus invariant-factor presentations, and coordinate vectors versus elements.

- **Rationale**: Reusing the mathematical noun for its representation makes callers reason about arrays as if they satisfied the universal property themselves and obscures where basis choices entered.

- **Violation Example**: “tensor product of two matrices”; “the Smith form of the module” when referring to the backend matrix; “the vector is primitive because its coordinate gcd is one.”

- **Correct Example**: the tensor product of morphisms has a Kronecker matrix in chosen bases; Smith normal form is the matrix computation producing an invariant-factor re-presentation; primitivity is the cokernel torsion-freeness predicate.

#### `LEX-09`: Public Category Names Are Standard Names for Identities, Not Substitutes for Their Definitions

- **Rule**: Use `lean-categories`' plural/category name, and retain the construction/classifier expression that presents its definition.  Project/Sage aliases are metadata on that one category, never extra categories whose existence must be reconciled later.

- **Rationale**: Good names make the interactive language readable; presenting the formalized definition makes the graph coherent.  Treating either as the other yields the two bad extremes: unreadable classifier-only APIs or a forest of independently named categories with duplicated semantics.

- **Violation Example**: expose only `Magmas.Associative.Unital.Inverse` when `Groups` is the established mathematical noun; or create `Groups` as a separate wrapper category around that classifier expression.

- **Correct Example**: `Groups` is the standard public name of the one preamble category, presented by the classifier/category expression for `lean-categories`' definition; aliases and backend names resolve to that identity.

#### `LEX-10`: Every Generator, Dual and Basis Names Its Structure -- and No Alias Omits It

- **Rule**: Public accessors for generated or derived structure state which structure they mean: `module_generators`, `group_generators`, `algebra_generators`, `ideal_generators`, `monoid_generators`, `dual_module`, `dual_lattice`, `dual_group`.  A bare `gens`, `generators`, `dual`, `basis` or `ngens` is not a public method, **and not a permitted alias for one**.

- **Rationale**: Every object here sits in several categories at once, so an unqualified request names no operation.  `ZZ` is at once a ring, a rank-one \(\mathbb Z\)-module, a rank-one \(\mathbb Z\)-algebra, a group and a monoid; its module generators are \(\{1\}\) and its multiplicative monoid generators are the primes together with \(-1\).  An ideal of \(R\) is both an ideal and an \(R\)-submodule of \(R\), with different generating sets.  The question has no answer until the structure is named.  An alias is worse than a bad name: it makes an ill-posed question answerable, and whatever it returns is a silent choice of one structure among several, made by the implementer and invisible at the call site.  Sage can afford `gens()` because a Sage object usually has one privileged structure baked into its class; the preamble cannot, because multi-category placement is the design.

- **Violation Example**: `gens = ideal_generators` or `generators = gens` on a preamble class; `def basis(self)` on an object that is a module and a formed module at once; a caller reaching for `.gens()` because the class offers it.

- **Correct Example**: `ideal_generators()` as the only accessor, with callers renamed; Sage's `.gens()` retained only on an engine handle inside a private adapter, where the receiver is a Sage object with one structure.

#### `LEX-11`: One Name, One Operation -- a Different Codomain Is a Different Operation

- **Rule**: Every definition sharing a name implements the **same** operation: the same mathematical question, answered in the same codomain.  Specialisation is welcome -- a concrete representation may answer faster, and a category may answer generically -- but a definition that lands somewhere else is not an override of that operation, it is a different operation, and it takes its own name.  When adding a definition of an existing name, read the others and confirm the codomain agrees.

- **Rationale**: Overriding is how specialisation is supposed to look here, so a long list of definitions is not itself a smell and the real defect hides among them.  `signature_pair` had ten definitions: six per-Gram shortcuts, a category-level owner, a stored value on a genus -- all returning a pair -- and one on `CoxeterDiagram` returning `(positive, negative, zero)`, the inertia including the degenerate part.  Nine implementations of one operation and one of another, indistinguishable at every call site, and a rename or a return-type change applied across the name would silently corrupt the tenth.  The shared name also concealed that the two answers live in different objects, \(\mathbb N^2\) against \(\mathbb N^3\), which is the same defect `CON-15` names from the other side.

- **Diagnostic**: count the definitions of a name and compare their codomains before touching any of them.  Divergence in arity, in value type, or in what the answer is *of* means the name covers more than one operation.

- **Violation Example**: `signature_pair` returning a pair on nine owners and a triple on a tenth; a predicate that answers `bool` on one class and a three-valued unknown on another; an accessor returning an element on one owner and a family on another.

- **Correct Example**: the inertia named as the inertia, distinct from the signature pair; `tensor_valence`, whose four definitions are a contract, a computation, a delegation and a constant, all answering the same question in the same place.

#### `LEX-12`: An Annotation Names the Codomain, and Its Reader Is a Mathematician

- **Rule**: A return annotation states **which mathematical object the value belongs to**, so that a reader can check the method against the definition it implements without executing anything.  Write the annotation for that reader first.  Whether a checker accepts it is a second, weaker requirement, and an annotation chosen to satisfy the checker rather than the reader has been chosen against its purpose.

- **Rationale**: In this repository the type surface is a mathematical claim: `-> tuple[int, int]` on a valence says the answer is a pair of integers, and a mathematician auditing the method compares that claim with the definition of the operation.  Optimising instead for "will this typecheck" reliably produces the annotations that convey least, because the easiest way to be accepted is to say nothing.  The checker is a machine that will accept the empty statement; the reader is the one who can tell that the empty statement is empty.

- **Violation Example**: choosing an annotation by trying candidates until the checker stops complaining; annotating a mathematical operation with the most general thing that fits; leaving the signature uninformative because the body is short and "obvious".

- **Correct Example**: an annotation a mathematician can read off against the operation's stated codomain, and which they would notice was wrong if the operation changed.

#### `LEX-13`: A Type That Excludes Nothing Asserts Nothing

- **Rule**: Before writing an annotation, answer: **which wrong implementation does this reject?**  If no plausible wrong return is excluded, the annotation is empty and does not count as typed.  `object`, `Any`, and framework universals used as returns -- `Element`, `Parent`, `SageObject`, `CategoryObject` -- are all in this class.

- **Rationale**: `object` is banned because a function annotated with it "passes on literally anything, which means it asserts nothing".  A framework universal fails the same test and hides it better.  Every element of every parent in Sage is an `Element`: an integer, a matrix, a polynomial, a group automorphism, a scheme point, a lattice vector.  So `-> Element` admits every value the preamble produces, catches no wrong return ever, and reads to a reviewer like a real type.  The class-tree ancestry is irrelevant; the discrimination is what matters, and there is none.

- **Violation Example**: `-> Element`, `-> Parent`, `-> SageObject` on a mathematical operation; a union so wide that every plausible return satisfies it; a bound so loose that the checker could not fail.

- **Correct Example**: an annotation naming the codomain, or -- where that is not yet expressible -- the named alias of `LEX-15`, which is honest about asserting nothing instead of disguising it.

#### `LEX-14`: Do Not Annotate From the Framework's Class Tree

- **Rule**: When the mathematical type is hard to name, do not walk up the implementation's class hierarchy until something fits.  Sage's class tree is a taxonomy of *representation*; a return annotation is a claim about a *codomain*.  The two are different questions, and an answer to the first is not an answer to the second.

- **Rationale**: This is the characteristic engineering-brained substitution, and it feels like diligence because the result is a real class that really is an ancestor.  But `Element` records that the value participates in Sage's coercion system, which is an implementation fact true of everything, while the question was which object the value is a point of.  The obstacle that prompts the walk -- "the parent is constructed at runtime, so there is no static name" -- is an implementation obstacle, and the mathematics does not move to accommodate one.  A codomain that cannot be named statically is a finding about the type surface, never a licence to write the universal base class.

- **Violation Example**: reaching for `Element` because the concrete element class is generated at runtime; annotating with a Sage abstract base because it is the nearest common ancestor of the observed returns; picking the ancestor that makes `mypy` quiet.

- **Correct Example**: naming the mathematical object -- the product, the homset, the module -- and, where the static surface cannot yet express it, recording that as a gap under `LEX-15` rather than papering it with an ancestor.

#### `LEX-15`: An Inexpressible Mathematical Type Aliases `Any` Once, Under Its Own Name

- **Rule**: When a value's mathematical type is known but not yet statically expressible, declare **one** alias in the central typing layer, named for the mathematics and carrying a comment stating what it stands for, and use that name in every signature:

  ```python
  # (n_1, ..., n_k) in the product monoid NN^k
  ProductOfNaturalNumbers = Any
  ```

  Never inline `Any` at the signature, never substitute a framework universal, and never leave the annotation off.

- **Rationale**: The alias and the base class both check nothing, so the alias costs nothing the universal was buying -- and on every other axis it dominates.  It names the codomain, so the reader learns it.  It is falsifiable by a human: change the return to a triple or to a pair of rationals and the name is visibly wrong in review, where `Element` could never become wrong and so could never flag anything.  It quarantines the ignorance to one site, which is what this repository already requires of a genuine `Any`.  It provides a single upgrade point, so that when the type becomes expressible one line improves every signature at once, instead of a hunt in which each site's intent must be re-derived because the annotation destroyed it.  And it makes the gap countable: `grep ProductOfNaturalNumbers` measures exactly how much of the surface is deficient and where, while a base class is indistinguishable from correct code and so cannot be paid down deliberately.

  This is not the invention `LEX-10` bans.  That prohibition is on minting a name to satisfy a rule -- `MyCustomClassCreationDatum` -- which has no referent.  `ProductOfNaturalNumbers` denotes \(\mathbb N^k\), which a mathematician recognises.  Naming real mathematics is the welcome case even when the name is currently an alias.

  The trade is explicit and correct: it costs minting one name, it buys zero code guarantees, and it buys mathematical expressiveness.  Do not weigh the zero guarantees against the cost -- the guarantees were never available at that site, and expressiveness is what is being purchased.  What the name additionally buys is set out in `LEX-17` and `LEX-18`: the alias is not a placeholder waiting to be tidied but a staging ground for a refinement whose errors are its yield.

- **Violation Example**: `-> Any` written at the signature; a different ad-hoc alias per file; an alias named for its representation (`IntPair`) rather than its mathematics; an alias with no comment saying what it stands for.

- **Correct Example**: one aliased name per mathematical notion, in the central layer, with its comment; every site using it; the alias replaced by the real type in a single edit when the surface grows to carry it.

#### `LEX-16`: An Annotation Falsified by a Change Is Corrected, Never Deleted

- **Rule**: When a change makes an existing annotation false, correct it to the new codomain.  Deleting it, widening it to a universal, or replacing it with `Any` are all prohibited, and deleting is the worst of the three because it leaves no trace that a claim was ever made.

- **Rationale**: A falsified annotation is a signal that the change is incomplete -- it is the type surface reporting that the codomain moved -- and the three prohibited responses all discard the signal instead of acting on it.  `AGENTS.md` names deleted annotations alongside `Any` and `# type: ignore` for exactly this reason.  A false annotation is at least a falsifiable claim that review can catch; an absent one asserts nothing and looks deliberate.  The observed sequence, which is the one to recognise: a correct annotation, made false by an edit, deleted to make the edit go through, then replaced with a base class to look typed again -- three moves, each worse than the last, two of them explicitly banned.

- **Violation Example**: removing `-> tuple[int, int]` because the return became an owned element; changing it to `-> Any` or `-> Element` for the same reason; leaving the old annotation in place and false.

- **Correct Example**: the annotation updated to name the new codomain in the same edit that changes the return, or the `LEX-15` alias introduced if that codomain is not yet expressible.

#### `LEX-17`: The Central Typing Layer Is an Independently Auditable Artifact

- **Rule**: The typing layer is reviewed, refined and improved **on its own schedule**, as an object of study separate from any call site.  An audit of it asks one question -- does `lean-categories` give this name a sharper referent than it currently carries -- and answering that question is ordinary maintenance, not a change to the code that uses it.  A `LEX-15` alias is deliberately left in place until such an audit refines it; it is not debt awaiting cleanup.

- **Rationale**: Once the mathematics is named in one place, the collection of names becomes a readable account of how the repository presents its objects, checkable against `lean-categories` by reading it alone.  `ProductOfNaturalNumbers` can be recognised as admitting a much better refinement without opening a single consumer, because the name already states the intent that the refinement must respect.  This is only possible when the ignorance was localised: inlined `Any`, ad-hoc per-file aliases, and framework universals leave nothing to audit, since each site must first be reverse-engineered to learn what it meant.

- **Violation Example**: treating the alias file as scaffolding to be minimised; refining a type only when a call site forces it; discovering the intent of a site by reading its body because its annotation records none.

- **Correct Example**: a scheduled read of the typing layer that proposes refinements from the names and `lean-categories` alone; an alias that survives several releases because no sharper referent is yet formalized, and is none the worse for it.

#### `LEX-18`: Narrowing a Type Is a Designed Experiment; Its Errors Are the Result

- **Rule**: When a `LEX-15` alias is refined to a real type, the errors that appear are the **output of the experiment**, not damage to be minimised.  Read every one before changing anything.  Suppressing them, widening the refinement to make them stop, or reverting the narrowing discards the result.

- **Rationale**: Because every consumer already declared its intent by using the name, the checker is doing two things at once when the name narrows: it is checking the new definition, and it is checking each site's declared intent against that definition.  Each error is therefore a specific disagreement between a usage and the refinement, and lights up the complete census of consumers at once.  Three kinds of finding come out of it, and each is worth more than the narrowing itself:

  - a call site needs an operation the refined type does not offer, which names a **missing API** and is a gap discovered rather than guessed;
  - a call site uses less structure than the refinement supplies, which distinguishes the sites needing only the **set** structure from those needing the **monoid** structure -- a distinction across the corpus that no reading of individual files would surface, and that is checked against the codomain `lean-categories` gives;
  - a call site is simply wrong, and was wrong before, invisibly.

  A narrowing that produces no errors has told you something too, but a narrowing whose errors are suppressed has told you nothing and cost the opportunity.

- **Violation Example**: narrowing an alias and immediately loosening it until the suite is quiet; adding `# type: ignore` at the sites that failed; treating the error count as the cost of the change rather than as its findings.

- **Correct Example**: narrowing, then reading the errors as a census -- these sites want an operation we do not have, these sites only ever needed the underlying set, this one is a real defect -- and letting that reading determine what changes, including possibly the refinement itself.

* * *

### 7. Sets, Collections & Cardinality (`SET-*`)

#### `SET-01`: Mathematical Collections Are Preamble Sets or Families, Never Python Sequences

- **Rule**: Every mathematical collection inside the preamble—not only a public return value—is represented by its mathematical collection object: set, ordered set, multiset, ordered multiset, indexed family, image, product, coproduct, or another named construction.  Raw Python `list` and `tuple` are not mathematical storage types.  They may appear only as transient serialization at a private backend boundary after finiteness and ordering have already been established mathematically.

- **Rationale**: The mathematical collection determines equality, multiplicity, order, membership, cardinality, ranking/unranking, and available morphisms.  A Python sequence silently supplies finiteness and eager materialization.  Once a mathematical family is stored as a sequence, every downstream consumer is encouraged to use `len`, indexing, slicing, and whole-family traversal even when the same construction should work for an infinite ordered/indexed set.

- **Violation Example**: `self._generators = tuple(generators)`; `labels = list(M.module_generating_set())`; `module_generators() -> tuple[...]`; returning a list of subgroup representatives; converting an index set to a tuple merely to enumerate it twice; widening an input type to `Sequence` because callers pass lists.

- **Correct Example**: A generating family is a preamble ordered/indexed set with `__iter__`, membership, cardinality, and when appropriate `rank`/`unrank`; repeated framing images form an indexed family over the framing set; conjugacy representatives form a preamble set.  Consumers iterate lazily.  A private CAS adapter may finally serialize a *known finite* ordered set to the row/column array demanded by that backend, and that sequence does not escape the adapter.

#### `SET-02`: Cardinality and Order Are Cardinal-Valued; Finiteness Is Never Smuggled in by `len`

- **Rule**: Cardinality, group order, and element order use the repository's mathematical cardinal/integer objects appropriate to their definitions and do not silently assume finiteness.
  Use `cardinality()` for mathematical sets; use sequence length only for a private implementation container already known to be finite.

- **Rationale**: `len` is a programming operation with a finite machine-integer result.
  Treating it as cardinality makes infinite ordinary inputs unanswerable or converts a missing enumeration algorithm into a false mathematical finiteness claim.

- **Violation Example**: `order() -> int: return len(elements)`; raising from `cardinality()` merely because a module has positive rank; refusing to state the cardinality of a finitely generated infinite group because only finite groups are enumerable by the current engine.

- **Correct Example**: A finite free module over `F_q` has cardinality `q^n`; a finitely generated infinite group has countable underlying set when that theorem applies; an unknown cardinality is represented as unknown rather than forced through `len`.

#### `SET-03`: Set-Level Operations Live Once at Sets and Standard Constructions

- **Rule**: Cardinality, finiteness, countability, membership, enumeration, products, coproducts, and other generic set operations live at the preamble set layer or the standard construction where `lean-categories` first defines them.
  Structured descendants obtain those operations through their canonical forgetful/construction path rather than reimplementing the same set theory at every leaf.

- **Rationale**: A lattice, module, algebra, or group has an underlying set; it does not acquire a second definition of cardinality because it has extra structure.
  Centralizing set behavior prevents coordinate models and leaf-specific enumerators from becoming alternate definitions of the underlying set.

- **Violation Example**: A lattice-specific `cardinality()` multiplying invariant factors directly while the underlying finite group already carries cardinality; a module-level iterator returning coordinate tuples instead of module elements because a basis is available.

- **Correct Example**: A discriminant form inherits cardinality from its underlying finite abelian group; a chosen basis may supply an isomorphism with a coordinate product for computation, but iteration crosses back through the inverse and returns elements of the preamble module.

#### `SET-04`: Finite Support Does Not Imply a Finite Underlying Family

- **Rule**: Distinguish an element having finite support from its parent/indexing set being finite.  Free modules, formal divisor groups, group/algebra monoid rings, sparse polynomial-like objects, and indexed sums may be built on infinite sets while each represented element uses only finitely many indices.  Do not coerce the whole indexing family to a finite ordered set merely because the current element or backend input is finite.

- **Rationale**: Conflating finite support with finite parent data is one of the main ways finitary assumptions spread through the API.  The correct abstraction keeps the parent infinite/lazy and lets each element expose its finite support.

- **Violation Example**: Defining the group of formal divisors by `finite_ordered_set(prime_divisors)`; materializing every module generator before forming a sparse linear combination; requiring a group ring's entire group to be enumerable in order to represent one finite group-ring element.

- **Correct Example**: `FormalDivisorGroup(R,S)` is the free `R`-module on the set `S`; a divisor is a finite-support coefficient map on `S`.  Algorithms consume only that support unless their theorem genuinely requires a finite parent.

#### `SET-05`: The Set API Is Closed Under Standard Set Constructions and Canonical Identifications

- **Rule**: Every preamble object that is mathematically a set—ordinary sets, exponentials/function sets, Set-Homs, power sets, Cartesian products, coproducts, images, subobjects, and similar constructions—participates in the same preamble set API.  Canonically identical set constructions are represented by one parent/object, not parallel implementations reached through different notation.

- **Rationale**: Set-level operations such as membership, cardinality, enumeration, indexing, maps, products, and coproducts should propagate through the standard construction graph.  If `Hom_Set(X,Y)` and `Y^X` are implemented separately, each acquires its own cardinality/enumeration/equality behavior and the architecture immediately forks.

- **Violation Example**: Maintain an independent power-set implementation beside exponentials; make Set-Homs a Homset object that does not receive ordinary set methods; compute function-set cardinality separately from Set-Hom cardinality.

- **Correct Example**: Present the canonical identifications `Hom_Set(X,Y)=Y^X` and `P(X)=2^X` that `lean-categories` states; the one resulting parent has both Hom/exponential placements and inherits the complete set interface.  Cartesian products/coproducts likewise carry their standard projections/injections and cardinal arithmetic at the set-construction level.

* * *

### 8. Computational Backend Delegation (`ENG-*`)

#### `ENG-01`: Delegate Heavy Algorithmic Computations to Exact Engines

- **Rule**: Route algorithmic algebra to established exact backends (SageMath, Singular, OSCAR, Macaulay2, PARI/GP) when a reliable implementation exists.

- **Scope**: Gröbner bases, syzygies, primary decompositions, Hilbert series, polynomial reduction, and local algebra computations.

- **Rationale**: Battle-tested engines provide numerical stability and optimized C/C++ implementations, and they carry their own maintenance.  Their answers are untrusted like every computation's; only the `lean-cas-dsl` acceptance suite judges them.

- **Violation Example**: Writing custom Python algorithms for multivariate polynomial division or Gröbner basis calculation.

#### `ENG-02`: Prohibition of Hand-Rolled Standard Mathematics

- **Rule**: Do not hand-roll algorithms or data structures available in mature upstream dependencies.

- **Rationale**: Custom mathematical algorithms create high maintenance overhead without making any answer more trustworthy.

- **Violation Example**: Implementing custom Smith Normal Form or LLL reduction instead of delegating to native library routines.

#### `ENG-03`: Minimal Owned Computation and Ecosystem Offloading

- **Rule**: Keep owned algorithmic logic strictly minimal.
  Always offload engine computations to established computational backends:

  - Upstream SageMath native modules

  - Heavy Python libraries (`networkx`, `numpy`, `scipy`)

  - Julia / OSCAR / Hecke (routed via `sage_julia_bridge`)

  - GAP (routed via `libgap`)

  - Singular, Macaulay2, Maxima, and PARI/GP

- **Rationale**: The preamble presents the categories, universal properties, and structures `lean-categories` formalizes.
  Concrete computations belong to dedicated, maintained engines, whose answers are untrusted.

- **Violation Example**: Writing custom graph connectivity or automorphism algorithms instead of delegating to `networkx` or Sage graph backends.

#### `ENG-04`: Native Engine Implementation with Preamble Category Wrappers

- **Rule**: When an algorithm requires multi-step engine computations, implement the engine logic directly in the target engine language (such as Julia/OSCAR or Singular) and wrap it with preamble category interfaces, whenever this reduces complexity or eliminates excessive cross-bridge data transport.
  First apply `OWN-08`: use an existing suitable high-level engine operation.
  Native engine glue composes maintained operations; writing a replacement
  algorithm in the engine's language still requires the `ENG-06` engineering decision.
  The Python mathematical layer should prepare the preamble input, cross once into the engine routine, and reconstruct the preamble output; it should not become a line-by-line orchestration language for the engine's matrices, syzygies, lifts, or stabilizer workspaces.

- **Rationale**: Executes compute-heavy algebra natively in the host engine while exposing a uniform categorical interface to Sage sessions.
  A long Python routine whose dominant content is translating and reshaping intermediate engine objects is backend code in the wrong language and location.

- **Violation Example**: Transporting intermediate matrices back and forth across a language bridge in a loop when one native Julia routine can perform the reduction and return the final invariant; a hundreds-of-lines Python kernel routine manually building Singular augmented matrices, calling `syz` twice, reshaping every intermediate result, and calling `lift` before finally reconstructing the preamble kernel.

- **Correct Example**: Pass the finite presentation and morphism data through one private Singular adapter whose native routine computes kernel generators, their relations, and lift data; cross back once and construct the preamble presented kernel together with its inclusion and lifting morphism.

#### `ENG-05`: Rank Architectures by Maintained Complexity and Change Blast Radius, Not Dependency Weight

- **Rule**: Do not count an ordinary external dependency, build toolchain, package scaffold, or install step as an architectural disadvantage by itself.  When choosing between mature reusable infrastructure and a local implementation, compare the amount/scrutability of logic humans in this project must maintain, the future edit/review blast radius, and whether understanding is centralized for reuse rather than reimplemented by each consumer.

- **Rationale**: Most substrate complexity is shifted rather than eliminated.  Avoiding one dependency by writing a parser, graph algorithm, dispatcher, traversal, or algebra engine locally transfers the same conceptual cost into bespoke code that this project must reason about indefinitely and often multiplies it across consumers.

- **Violation Example**: reject a maintained tree-sitter grammar because it adds a C/build dependency and instead maintain handwritten parsing logic; avoid `networkx` to save a package while maintaining DFS/SCC/toposort implementations; avoid a mature dispatch library and accumulate hand-written case registries.

- **Correct Example**: prefer the dependency when it centralizes the generic problem and leaves the preamble only its presentation and adaptation.  Reject a dependency for semantic mismatch, maintenance/reliability, or inability to satisfy the preamble boundary—not merely because it exists.

#### `ENG-06`: A New Nontrivial Mathematical Algorithm Requires a Demonstrated Backend Gap

- **Rule**: Before the preamble implements a new nontrivial mathematical algorithm, search the repository's backend/capability references and the relevant mature open-source systems for the semantic operation.  If a suitable exact implementation exists, wire it behind the preamble method.  Bespoke implementation is justified only after the relevant alternatives have been checked and a real semantic/capability gap is established; if maintaining the algorithm materially expands the project's burden, it requires an explicit project/user decision rather than an agent convenience choice.  The algorithm is an untrusted computation; any correctness argument written for it is not evidence.  An algorithm that needs mathematics `lean-categories` does not formalize is not written: that mathematics is requested there first.

- **Rationale**: The preamble should present `lean-categories`' mathematics through thin semantic routing, not duplicate decades of exact algebra/group/geometry algorithms.  LLMs readily write plausible local algorithms because doing so completes the immediate method; that silently transfers maintenance, performance, and edge-case responsibility into this repository.

- **Violation Example**: implement local orbit/stabilizer enumeration without checking GAP; write polynomial syzygy/Groebner logic instead of Singular; implement lattice/form equivalence from scratch while Oscar/Hecke/Indefinite.jl/Sage already provide an exact route.

- **Correct Example**: identify the `lean-categories` operation first, inspect the capability map/upstream documentation, add the narrow backend crossing, and return the preamble result.  If no mature implementation actually exists, record that concrete gap and only then design the smallest algorithm the project deliberately chooses to maintain.

#### `ENG-07`: Friction With the Engine Is the Datum; It Is Never Routed Around

- **Rule**: When a Sage route is slow, rejects an input, or returns a result of the wrong shape, the task changes at that point.  Before any other edit: isolate the engine from the preamble on a specimen of the same order and shape; measure the cost as wall time against the size parameter, at more than one size; search inside Sage for the alternate route (the method's `algorithm=` choices, a backend Sage ships reached through Sage's own interface, a different constructor, a sibling module), reading the source; and record what was found under `DEV-63`.  Only then choose the route the preamble name delegates to.  Replacing the library, hand-rolling the routine, adding a cache, or deleting the call that exposed the cost before that record exists is banned, whatever the size of the tool and whether or not the code is preamble mathematics.

- **Rationale**: A gap in Sage has three kinds, absent, present and wrong, and present but unaffordable, and the preamble name exists to absorb whichever one is found.  The measurement is the admission ticket: `ENG-06` lets the preamble implement an algorithm only on a demonstrated gap, so discarding the measurement forecloses the one route by which the project could ever legitimately take the computation on.  The finding is also the most durable thing the task can produce: it does not expire, it does not depend on the state of the tree, and it costs a researcher's afternoon to rediscover every time it is lost.  See *The artifacts are instruments; the product is a map of Sage* under the design philosophy.

- **Observed**: the declared-category-graph tool, 2026-09-16.  The first version hand-rolled a spanning forest and a cycle basis where `Graph.minimum_cycle_basis` exists; the second, on a speed complaint, replaced Sage's graph library with `networkx`.  Neither examined the Sage routine.  The result was zero knowledge of `Graph.minimum_cycle_basis`, `longest_path`, or `SimplicialComplex.homology` on the one graph that Sage itself traverses to join and linearize the preamble's own categories, and the swap would have left the tool looking fine while the fact stayed hidden.  The measurement is scheduled as the TODO node `category-graph-engine`.

- **Violation Example**: `import networkx` added to a module because a Sage call felt slow; a depth-first search written in place of the Sage routine because a Sage constructor rejected the input as given; a `cached_method` added to a slow path before anyone found out why it is slow; a slow view deleted from a tool so that the tool passes.

- **Correct Example**: build a Sage graph of the same order and shape with no preamble in the process, time the call at three sizes, read the method's source for its `algorithm=` choices, record the curve and the chosen route in `TRAPS.md`, and route the preamble operation through that spelling.  If the route is unaffordable at every size the research uses, that record is the `ENG-06` gap, and implementing the algorithm becomes a decision the project can now make.

#### `ENG-08`: A Second Engine Is Adopted Only on a Recorded Measurement

- **Rule**: The Sage ecosystem is searched to exhaustion before any computation leaves it: Sage's own spelling, then the backends Sage ships and reaches through its own interface (GAP through `libgap`, PARI, Singular, its graph and numerical backends).  A library outside that ecosystem is adopted for an operation only when a `DEV-63` record shows the Sage route absent, wrong, or unaffordable at the sizes the research uses, and the adoption is recorded beside that measurement with the route it replaces.  `ENG-03` and `ENG-05` say which engines are acceptable; this rule says when a change of engine is.

- **Rationale**: The preamble routes one name to one computation so that the researcher never learns there was a choice.  That works only when the choice was made on evidence and written down.  An engine swapped in to dodge an unmeasured cost is a second computation path with no reason attached, and it removes the site at which the Sage fact would have been measured.  The fragmentation is also real: two graph libraries in one tree are two sets of input conventions, two output shapes, and two homes for the same defect.

- **Violation Example**: replacing `sage.graphs.graph.Graph` with `networkx.Graph` in a tool because one view was slow, with no timing of the Sage call; adding `sympy` for a factorization Sage's rings already perform; a justfile recipe that installs a package to run a computation Sage's own interpreter already provides.

- **Correct Example**: measure the Sage route first; if a shipped backend answers, select it through Sage's own keyword and record that; if nothing inside the ecosystem answers, record the gap with its measurement, then adopt the outside library under `ENG-05` with the record cited at the crossing.

#### `ENG-09`: An Engine Is Called, Never Registered; Its Absence Fails at the Call

- **Rule**: The preamble operation imports the engine that computes it and calls it. There is no registry of operations, providers or availability, no availability predicate, no provisioning message, and no ordered list of providers to try. If the engine is not installed, or does not yet define the operation, the call raises `ImportError` or `AttributeError` at the site that needs it, and the tests that reach that site fail. Those failures are the record of what is missing. One operation has one engine; a branch that asks whether an engine is present and takes another route when it is not is a fallback, and it is deleted.
- **Rationale**: A failing call already is the stated absence: it names the module and the attribute, at the operation that needed them, and the test suite lists every such site. A registry restates that fact in a second place, where it is maintained by hand and goes stale: it reports "unavailable" for an operation that an engine has never defined, so a missing implementation reads as a provisioning state instead of as missing code. It also invites the fallback, because a caller that can ask "is it available" will take another route when the answer is no.
- **Observed**: 2026-09-06, commits `599128fa5` and `0b6e9ad78` built `engine_capabilities`: named capabilities, providers with availability predicates and provisioning strings, and consumers that branched on `is_available`. On 2026-10-02 the operations of `sage-indefinite-port` were registered there with module `None`, so each one reported itself unavailable although the port had never defined it.
- **Violation Example**: `engine_capabilities.compute("lattice.isometry_witness", gram_1, gram_2)`; `if engine_capabilities.is_available(...): ... else: <another route>`; a table row `(capability, kernel, None, None)` for an operation the engine lacks.
- **Correct Example**: inside the preamble method, `from sage_indefinite_port.indefinite.recursive import isometry` and `return isometry(L_1, L_2)`. While the port lacks `isometry`, every caller raises `ImportError` and the tests that reach it fail.

* * *

### 9. Engine Crossing Boundaries (`BND-*`)

#### `BND-01`: Backend State Has One Private Owner and One Controlled Crossing

- **Rule**: Durable backend state is private to the preamble object or private adapter that holds that computational realization.
  A backend datum has one private accessor or boundary helper at its owning layer; do not create public accessors, aliases, or unrelated direct field reads.
  Protected contracts satisfy `OWN-05`: name the owner, permitted roles, exact
  types and invariants at the declaration. Mathematical subsystems exchange
  preamble values, not raw handles. A comment authorizing a convenient private
  read is not a protected contract.

- **Rationale**: Multiple ways to reach the same engine are multiple APIs.
  A single visible crossing makes the representation dependency auditable and prevents backend operations from spreading through ordinary mathematical consumers.

- **Violation Example**: Reading `_preamble_pid_engine` directly from discriminant modules while Internal Hom uses a separate engine accessor and a third consumer reaches Sage's `V()` through the owned module.

- **Correct Example**: A private presented-module adapter owns one optional Smith engine and one documented conversion boundary used by the few algorithms that require the FGP implementation; ordinary consumers never receive its parent or elements.

#### `BND-02`: Cross In, Compute, Cross Back

- **Rule**: A backend crossing converts preamble inputs to the backend representation, performs the backend computation, and converts the result back before the boundary returns.
  Backend parents, elements, vectors, matrices, submodules, homsets, normal-form workspaces, GAP objects, and all other representation structures do not propagate past that computation site.
  There is no element exception: a backend element is backend data and must be converted to a preamble element before return.

- **Rationale**: Backend delegation is safe only when the backend computes behind the preamble objects rather than becoming a second universe used by downstream code.
  Immediate conversion back keeps representation-specific assumptions local and makes backend replacement possible without changing mathematical callers.

- **Violation Example**: Internal Hom computes an FGP kernel and returns that Sage FGP module or its elements for later consumers to inspect; a lattice invariant returns a Sage kernel basis and expects its caller to reconstruct the lattice; an owned group operation returns a GAP element because GAP performed the multiplication.

- **Correct Example**: Cross a preamble module morphism and its coefficients into Sage's FGP representation to compute a kernel, then construct the preamble presented kernel, its elements, and its inclusion before returning.

#### `BND-05`: Backend Conversion Is Private and Non-Exported

- **Rule**: Conversions such as "owned ring to Sage ring", "owned element to Sage element", "owned group to GAP group", and their inverses are private implementation functions or private adapter methods.
  They are not exported from `preamble.all`, package `__init__` modules, public classes, or notebook-facing namespaces.
  Ordinary repository code outside the owning adapter does not call them merely to continue computation in the backend.

- **Rationale**: A public `engine_ring`, `engine_element`, `engine_group`, `to_sage`, `from_sage`, or similar helper is an intentional escape hatch even if individual parents hide their `_engine` field.
  The firewall is real only when backend representations are unreachable through the public API and crossings are confined to the implementation that immediately converts back.

- **Violation Example**: Exporting `engine_ring(R)` so callers can construct Sage matrices over it; exposing `_smith_engine()` broadly enough that unrelated modules perform FGP operations directly; retaining `own_ring(raw_sage_ring)` as a notebook-facing adoption constructor.

- **Correct Example**: A private FGP adapter owns `_to_sage_ring`, `_to_sage_element`, and `_from_sage_element` locally, performs the whole Smith computation, and returns an owned tensor/module/morphism.  No public caller can obtain or supply those Sage objects.

#### `BND-03`: Dispatch on Declared Placement, Never by Type Peeking

- **Rule**: Public and category-level behavior is selected by category membership, the structure the object was constructed with, or its category operations.
  Do not use `isinstance`, `type(...)`, `hasattr`, `getattr`-probing, or `try/except AttributeError` to discover what mathematical structure a preamble object has or which mathematical operation it supports.
  Matching on engine classes is permitted only inside a private engine boundary whose job is to select an engine-specific implementation after the mathematical operation has already been chosen.

- **Rationale**: Python class identity and method presence answer how an object happened to be implemented, not what mathematical structure it carries.
  Type- and capability-peeking recreate implementation hierarchies as hidden second category graphs and let consumers infer stronger structure than was declared.

- **Violation Example**: A scalar-multiplication routine branches on `FreeModule_generic`, FGP module, and quotient-module classes after receiving a preamble module; code asks `hasattr(M, "presentation_matrix")` to decide whether `M` is presented; a public group method decides group structure by inspecting the Sage class of the preamble parent.

- **Correct Example**: Ask the preamble module for its scalar action or `scalar_multiple`; inside the private group-engine boundary, match on the Sage engine class only to choose the corresponding GAP/Sage algorithm and return preamble results.

#### `BND-06`: Backend Correspondence Provides Capabilities; It Does Not Define the Category Taxonomy

- **Rule**: Maintain backend mappings as implementation/capability correspondences from the preamble's presented categories/constructions to available Sage/GAP/Julia/etc. realizations and algorithms.  The correspondence need not be injective and is not an equality of taxonomies.  Backend category names, graph edges, MRO order, and equality do not create or identify categories; `lean-categories` does.

- **Rationale**: Several backend categories may implement the same mathematics, and one backend category may package a combination of structures differently from the preamble graph.  The useful question is “which backend capabilities are available for this preamble object/operation?”, not “how do I make the preamble hierarchy mirror Sage's?”.

- **Violation Example**: Add a preamble category only because a Sage category has no current target; require one-to-one mapping between Sage category names and preamble categories; copy `super_categories()` edges into the preamble graph as authoritative inclusions.

- **Correct Example**: the preamble graph is fixed by `lean-categories`; a private/versioned bridge records each meaningful backend realization and the operations it can supply.  Multiple backend realizations may inhabit the same capability fiber, and updating Sage versions changes only the bridge, never the category graph.

#### `BND-07`: Reuse Engine Computation Without Adopting Its Public Objects

- **Rule**: `lean-categories` defines the mathematics; the preamble presents it
  through its own public objects; maintained engines perform the computations,
  whose answers are untrusted. Private engine representations
  may be ephemeral or privately cached under `OWN-10`. Reuse of host runtime
  primitives for generated preamble types does not authorize adopting, reclassing,
  subclassing, or returning an engine's concrete mathematical parent or elements
  as preamble objects. An audit does not waive `ARC-05`, `ARC-06`, or `OWN-04`.

- **Rationale**: Algorithm reuse and the preamble's own public objects are
  simultaneous requirements. Treating runtime adoption as another way to supply
  public objects makes an engine's inherited API an alternate mathematical language.

- **Violation Example**: Replace a Sage algorithm with local Smith reduction to
  obtain preamble elements; alternatively, return Sage elements from a preamble
  parent because its concrete runtime type was declared audited.

- **Correct Example**: The preamble module holds its selected presentation;
  a private Sage/Singular computation returns data that the adapter raises into
  preamble elements and a preamble normalization isomorphism through the
  sanctioned constructor. Sage `Parent`/`Element` primitives may implement the
  preamble runtime without making Sage's concrete modules the public objects.

#### `BND-04`: Never Repair a Boundary Violation with Compatibility Machinery

- **Rule**: When a preamble object or element has been placed inside an engine object, an engine object has been reclassed as a preamble object, or a preamble parent has been made a facade over backend elements, fix that boundary seam.
  Do not compensate by joining Sage categories into preamble parents, teaching Sage constructors to accept preamble rings, adding coercion hooks, skipping problematic engine element types, preserving backend elements through facade parents, or installing backend protocol methods solely to keep the invalid embedding working.

- **Rationale**: These patches are symptoms of the same inversion: the engine has become responsible for understanding the preamble's objects.
  Each workaround expands the coupling and creates the next failure at coercion, element identity, category comparison, or constructor dispatch.

- **Violation Example**: Joining a Sage engine category into a preamble ring so `FreeModule(preamble_ring, n)` succeeds; skipping Cython element refinement because a reclassed permutation group loops in coercion; declaring Sage vectors to be the elements of a preamble free module; adding `_im_gens_` only because a Sage algebra constructor received a preamble module parent.

- **Correct Example**: A private adapter converts preamble ring elements to Sage ring elements, builds a Sage free module or FGP workspace entirely on the backend side, computes there, and converts all outputs back.  A private group adapter may use a Sage/GAP group model, but public group parents and elements remain preamble objects.  No backend category join, facade parent, reclassification, or backend-element exception is required.

#### `BRG-01`: Structured Engine Bridges Over Ad-Hoc Shelling

- **Rule**: Route communication with external systems (such as Julia, OSCAR, or Macaulay2) through persistent bridge interfaces (`sage_julia_bridge`, `JuliaHandle`, or C-APIs).

- **Rationale**: Shelling out via subprocesses with temporary disk files causes process overhead, unmanaged temporary state, and fragile error handling.

- **Violation Example**: Using `subprocess.run(["julia", "script.jl", tmp_file])` inside an inner loop instead of calling a persistent `JuliaHandle`.

#### `BRG-02`: Explicit Mathematical Interface Boundaries

- **Rule**: Translate data explicitly across bridge boundaries.
  Validate input types and convert results into preamble types immediately upon return.

- **Rationale**: Keeps engine-specific representation leaks out of the public category API.

- **Violation Example**: Leaking raw engine pointers or un-wrapped backend matrix wrappers into user-facing category elements.

* * *

### 11. Environment, Execution & Tooling (`ENV-*`)

#### `ENV-01`: Strict Physical Path Resolution for Commands

- **Rule**: Use exact physical filesystem paths (such as `/home/dzack/research`) for shell commands, execution targets, and subprocess invocations.

- **Rationale**: Virtual mount aliases (such as `/research`) fail in standard POSIX shells and background tasks.

- **Violation Example**: Passing virtual root `/research` to a shell execution tool.

#### `ENV-02`: Deterministic Recipe Execution via Justfile

- **Rule**: Declare all project orchestration, gates, and documentation generators in the root [`justfile`](justfile).

- **Rationale**: Ensures reproducible execution across developer environments, CI pipelines, and automation tools.

- **Violation Example**: Running undocumented one-off ad-hoc bash scripts for builds or tests.

* * *

### 14. Formalization Requests and Search (`FSA-*`)

Research writes no formal statements: no definition, theorem, decomposition or
Lean file, not even temporarily
([AGENTS.md](AGENTS.md#a-missing-foundation-parks-the-work-that-found-it-always-on)).
Formal work, its decomposition, its sourcing standard and its semantic review
belong to `lean-categories`' formalization author, blind to research and to every
implementation. What research does is find out whether `lean-categories`, and
the libraries it builds on, already has what the work needs, and when it does
not, request it there, stating the mathematics wanted and its sources. These
rules govern that search and that request.

#### `FSA-01`: Search Is the Instrument; a Request Is the Response to Absence

- **Rule**: The response to a missing dependency is to search for it in `lean-categories` and the libraries it builds on, until the surfaces of `FSA-02` are exhausted.  If it is absent, the response is a formalization request to `lean-categories` and a parked node (`DEV-59`), never a definition written here.

- **Rationale**: A found notion is `lean-categories`' and arrives formalized and reviewed; a notion written in research is mathematics research does not own and would have to be discarded.  Searching also compounds: a hit teaches the file, its neighbours and the vocabulary that corner of the library is phrased in, which makes the next lookups cheaper and tells you whether a nearby gap is real.

- **Violation Example**: on finding that the library has no orthogonal group of a bilinear form, writing one in research; closing a graph's open rows by authoring definitions in a session.

- **Correct Example**: reporting that the notion is absent, with the searches that establish it, filing the `lean-categories` request with its sources, and parking the work that needs it.

#### `FSA-02`: Exhaust the Named Surfaces Before Any Absence Claim

- **Rule**: "`lean-categories` does not have this" is admissible only after all of: `lean-categories` at its released revision, and the libraries it builds on, searched by path *and* by semantic query; the registry's linked repositories; the package index as cloned; the index refreshed against its live source; the project-tracker and coverage lists; and the community forum, which the registry names explicitly as the place to search before concluding nonexistence.  A surface not searched is named in the claim.

- **Rationale**: Each surface fails differently.  A path search misses a notion under another name; a semantic search misses one nobody has phrased that way; a cloned index misses what was published since; the forum catches work in progress that exists nowhere else yet.  An absence claim is load-bearing — it is the premise of a formalization request and of parking the work that needs it — so it must be the best-supported claim in the document, not the weakest.

- **Violation Example**: concluding that almost-complex structures, analytic spaces and Weil divisors exist in no Lean code anywhere, on the strength of identifier greps for guessed names, with the semantic search tools available and unused and the forum never opened.

#### `FSA-03`: An Identifier Grep Is Not a Search

- **Rule**: Search for the *notion*, not for a spelling you predicted.  Use type-pattern and natural-language search over the library before any grep, and when grepping, search for the mathematical words and the neighbourhood, never only for the identifier you expect.

- **Rationale**: Declarations are namespaced, renamed, deprecated behind aliases, and phrased in vocabulary a reader would not guess.  A grep for a predicted name tests your prediction, not the library, and it fails in the direction that files a needless request and parks work that was never blocked.

- **Violation Example**: `rg "def Commensurable"` returning nothing, and the absence recorded as a missing primitive, when the declaration is `def Subgroup.Commensurable`; citing `JordanRing` on the strength of a file name when the class is `IsJordan`.

- **Correct Example**: a natural-language query for "commensurable subgroups", a type-pattern query for the shape of the statement, then a grep for the word `commensurab` over the tree, and only then a conclusion.

#### `FSA-04`: A Negative Result Names Its Instrument, Surface and Revision

- **Rule**: Every recorded absence states what was searched, with what tool, over which revision or snapshot, and what the search does **not** cover.

- **Rationale**: A negative result is a claim about the world made from a partial view, and its value to a later reader is exactly the part that says where the view ended.  Without the instrument named, a reader cannot tell a thorough search from a guessed grep, and will either redo it or trust it — both wrong.

- **Correct Example**: "searched 94,764 `.lean` files in 734 packages, the index as cloned on a stated date, by identifier and word search, no build; does not cover packages added since, a formalization under a name none of these searches guessed, or unpublished work."

#### `FSA-05`: Tooling Silently Falsifies Searches; Defeat It Explicitly

- **Rule**: Assume the search tool is lying by default.  Disable ignore rules over vendored and cloned trees; distinguish matches in prose from matches in code; and never treat a build artifact's absence as a declaration's absence.

- **Rationale**: Three independent mechanisms produce empty results over full trees: ignore files suppress whole clones, a word match counts documentation that says the opposite of what is being looked for, and a partial build means a module that exists cannot be elaborated.  Each of them produces the same output as genuine absence, and each of them was mistaken for genuine absence in practice.

- **Violation Example**: a search over cloned repositories returning zero files because ignore rules applied; counting occurrences of `sorry` and finding files whose text reads "no `sorry` in this file"; recording a notion as unavailable because its module had no compiled artifact locally.

#### `FSA-06`: A Request Is Transcribed From a Source Open at the Time

- **Rule**: Write no statement of the mathematics a request asks for, and no citation, from memory.  Open the source and transcribe the statement with a locator that identifies it: a citation key or a publicly resolvable URL, plus section, numbered item and page.  Never a bare author name, never "standard", never "see the literature".

- **Rationale**: A statement recalled is a statement generated, and the generated one is fluent and plausible whether or not it is right.  There is no internal signal separating the two cases, so the only available discipline is procedural: the source is open, or the statement is not written.  The locator is what lets `lean-categories`' formalization author test the request against its source.

- **Violation Example**: requesting a normal analytic space, a Weil divisor and Milgram's theorem in one message without opening a text, and afterwards being unable to say whose definitions were meant.

#### `FSA-10`: Environment State Never Enters a Durable Document

- **Rule**: What a particular machine has compiled, installed, cached or configured is not recorded in a design document, a docstring, a policy file, or a verdict about what exists.

- **Rationale**: Durable documents are read by people and agents on other machines and at other times, for whom such a statement is false or meaningless, and it is read as a fact about the mathematics because that is what surrounds it.

- **Violation Example**: a design document recording that a library module is "present as source and not built in this checkout" as though that were a property of the library.

#### `FSA-15`: Report the Neighbourhood, Not Only the Hit

- **Rule**: A search that succeeds reports what else is there: the file, the adjacent declarations, the vocabulary the area is phrased in, and what the area does *not* contain.

- **Rationale**: This is where the compounding lives.  The value of finding a declaration is mostly in what the finding teaches about the region, which is what makes the next search cheap and what tells a later reader whether a nearby gap is real.  A bare hit throws that away and the region has to be learned again.

- **Correct Example**: reporting not just that a lemma exists but that its subtree also holds a sorry-free classification, seven files of decomposition machinery, and no analogue of the notion actually wanted.

#### `FSA-16`: Introspective Confidence Is Never Offered as Evidence

- **Rule**: Do not report that a definition, name, statement or absence is right because it is recalled, familiar, or standard.  A claim carries a locator — file, declaration, section, page — or it is marked unverified.  Phrases asserting recalled correctness are banned outright: "this is the standard definition", "as usual", "the canonical form is", "I'm confident that", "obviously", said of anything not just read.

- **Rationale**: The faculty being appealed to does not exist: recall and confabulation are the same operation from the inside, so the assertion adds no information while consuming a reader's trust.  Observed calibration shows it — confident false claims about file contents appeared beside confident true ones, indistinguishable.

- **Violation Example**: "normality is integral closedness of the local ring, which is standard", written without opening a source; "`JordanRing` is the class", from a filename.

- **Correct Example**: "Grauert–Remmert Ch. 6 §2 defines it as …, transcribed"; or "unverified: no source consulted, do not build on this".

* * *

