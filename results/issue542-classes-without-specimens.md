# #542: six element classes have no specimen, and four library calls that would build one fail

The issue's acceptance asks for one test per element class that declares
`__hash__ = None`: a test that equal elements hash alike and a finite ordered
set of them that builds.  Ten classes are covered.  Six are not, and this
report is what #542 owes them: none of the six can be tested yet, because the
library call that would build a specimen fails.  Three of those failures are
reproduced below at `bbb0dd6` on the adopted runtime; the rest of the state is
named so the next round starts from the measurement and not from a search.

The connector of this session reads and pushes the repository and cannot create
an issue, so this file is the filing: each section is a defect at the owner the
failure belongs to, with the command and the pasted answer.

## 1. `QuasiCoherentSheaves(scheme)` cannot build a sheaf from a cover

Blocks the chosen-trivialization arrow and the pullback-line-bundle arrow.

    >>> QuasiCoherentSheaves(ProjectiveSpaces(QQ)(1))(1, 2)
    TypeError: Category._call_() takes 2 positional arguments but 3 were given

The category is called with the cover (and the rank of the free sheaf on it),
which is two arguments, and the owned category call admits one.  The same
arity appears one level down:

    >>> QuasiCoherentSheaves(ProjectiveSpaces(QQ)(1)).Mor(line, line)
    TypeError: CategoryPacketMethods.Mor() takes 2 positional arguments but 3 were given

and a single argument reaches an empty constructor:

    >>> QuasiCoherentSheaves(ProjectiveSpaces(QQ)(1))(1)
    NotImplementedError:

Owner: `QuasiCoherentSheaves` and `CategoryPacketMethods.Mor` must state which
constructor a sheaf has, and the call must accept the cover datum the sheaf is
built on.  Both messages are the ones a caller gets, not a decision the library
made.

## 2. The complex manifolds' own `an_object` does not build

Blocks `HolomorphicMap`.

    >>> ComplexManifolds().an_object()
    TypeError: __init__() got an unexpected keyword argument 'engine_manifold'

`ComplexManifolds._call_` takes `(dimension, name)`, so the specimen the
category states for itself is the only route to a manifold without a chart
argument, and it raises before constructing anything.

Owner: `ComplexManifolds.an_object`, at the keyword it passes to the engine
manifold.  Until it returns, `HolomorphicMap` has no specimen: a map needs a
domain with a chart, and the category's own object supplies none.

## 3. `BilinearFormModules(ring).an_object` states no unique constructor

Blocks `FiberedFormedModuleMorphism`.

    >>> BilinearFormModules(ZZ).an_object()
    NotImplementedError: Category of symmetric even modules with a bilinear form
    over Integer Ring has no unique constructor among its declared branches

The category's `an_object` is

    return BilinearFormModules(ring).Symmetric().Even()(form)

and the branch it calls states no constructor.  The formed-module witness is
what a formed-module morphism is an arrow between, so without it there is no
arrow to test.

Owner: the formed-module category's `_call_` (or the branch `an_object` names).

## 4. `_WordClass` has no public specimen either

`_WordClass` is the element class of `word_modules._WordClasses`, which the
free-algebra and tensor-algebra constructions intern.  The elements those
constructions hand back are not of that class: the tensor algebra of a free
module returns the native free algebra's element class

    >>> Algebra = Modules(ZZ).free_module(2).tensor_algebra()
    >>> Algebra.zero().underlying_element()
    AttributeError: 'Owned_NativeFreeAlgebraParent_with_category.element_class' object has no attribute 'underlying_element'

and the tensor product quotient's underlying class is `Sets.element_class[_TensorClass]`,
not `_WordClass`:

    >>> Modules(ZZ).tensor_product((Modules(ZZ)(QQ), Modules(ZZ)(QQ))).zero().underlying_element()
    <sage... _TensorClass ...>

So the class is reached only through a word-module construction that the tests
do not otherwise use.  Owner: `word_modules`, whose public route to its own
quotient is not the one the session's constructions take; the test it needs
belongs beside that route, not beside the tensor product's.

## 5. `RelativeProjectivizationQuasiCoherentMorphism` depends on 1 and 2

Its category is built on a quasi-coherent sheaf on a relative projective
scheme, so both failures above are on its path.

## 6. Two further calls fail while reaching for a specimen

Neither is needed by a class above; both were reached on the way and both
return a failure a caller cannot act on.

    >>> QuasiCoherentSheaves(ProjectiveSpaces(QQ)(2)).an_object()
    RecursionError: maximum recursion depth exceeded

    >>> ProjectiveSpaces(QQ)(2).coordinate_ring()
    AttributeError: 'OwnedJoinCategory.parent_class' object has no attribute 'coordinate_ring'

The second is the plane cubic's structure sheaf route: `closed_projection`
raises `TypeError` there, which is the reviewer's measurement and which this
session could not reach past the two failures above, so it is recorded as
reported and not as reproduced here.

## What is delivered

The ten classes #542's earlier rounds covered hold their tests.  These six do
not, and until the four calls above build, no honest test of them can: a test
written against a private construction path would state what the session can
reach and not what the class owes.
