"""Free algebra constructions on a chosen set of generators."""


from sage_extensions.categories.algebras.algebras import (
    Algebras,
)
from sage_extensions.categories.algebras.finitely_presented_algebras import _tensor_algebra_from_module_presentation
from sage_extensions.categories.algebras.free_algebras import (
    GradedFreeAlgebras,
    SymmetricAlgebras,
    _symmetric_algebra_on,
    _tensor_algebra_on,
    _native_free_algebra,
    _finite_labels,
    _variable_names,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.algebras.sparse_free_algebras import (
    _sparse_symmetric_algebra_of,
    _sparse_tensor_algebra_of,
)
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import _relation_morphism
from sage_extensions.categories.modules.pure.modules import ModulesWithChosenFinitePresentation
from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
)
from sage_extensions.categories.sets.indexed_families import indexed_family
def _has_represented_finite_framing(module) -> bool:
    r"""Return whether the selected framing is finite construction data."""
    ring = module.base_ring()

    return module in ModulesWithChosenFinitePresentation(ring)

def _tensor_algebra_of(module):
    r"""Return \(T_R(M)\), including the linear relations of ``M``."""
    if not _has_represented_finite_framing(module):

        return _sparse_tensor_algebra_of(module)

    base = module.base_ring()
    # The presenting tensor algebra is free on the source of M's framing;
    # only its quotient by M's relations has M as its degree-one module.
    generating = module if module in FramedFreeModules(base) else module.framing_source()
    presentation_ring = _tensor_algebra_on(
        base,
        module.module_generating_set(),
        source_module=generating,
    )
    return _tensor_algebra_from_module_presentation(presentation_ring, module)


def _symmetric_algebra_of(module):
    r"""Return \(\operatorname{Sym}_R(M)\) with ``M``'s linear relations."""
    if not _has_represented_finite_framing(module):

        return _sparse_symmetric_algebra_of(module)

    base = module.base_ring()
    labels = _finite_labels(module.module_generating_set())
    relation_morphism = _relation_morphism(module)
    relation_labels = relation_morphism.domain().module_generating_set()
    generator_labels = tuple(relation_morphism.codomain().module_generating_set())
    if all(
        relation_morphism(relation_morphism.domain().module_generator(label)) == relation_morphism.codomain().zero()
        for label in relation_labels
    ):
        # A zero relation morphism proves the presented module is free only
        # when its parent carries the corresponding free-module structure.
        # Otherwise retain the chosen module object as degree one through the
        # sparse word quotient rather than falsely presenting it as a native
        # polynomial algebra on a free module.
        if module in FramedFreeModules(base):
            return _symmetric_algebra_on(base, labels, source_module=module)
        return _sparse_symmetric_algebra_of(module)

    # Keep the actual R[x] symmetric algebra as the owned presentation cover
    # even when the relation is nonmonic (e.g. 2*x over ZZ). The finite-
    # presentation constructor selects a one-variable multivariate engine as
    # its private quotient backend and retains the cover map/lift there; making
    # that backend the owned presentation ring would create a second R[x]
    # object and lose the canonical polynomial-cover identity.
    presentation_ring = _symmetric_algebra_on(
        base,
        labels,
        source_module=module.framing_source(),
    )


    engine = _engine_ring(presentation_ring)

    def relation_value(relation_label):
        image = relation_morphism(relation_morphism.domain().module_generator(relation_label)).to_vector()
        backend = engine.zero()
        for position, generator_label in enumerate(generator_labels):
            coefficient = image(generator_label)
            if coefficient:
                backend += _engine_element(base, coefficient) * engine.gen(position)
        return _owned_engine_element(presentation_ring, backend)

    relations = indexed_family(
        relation_labels,
        relation_value,
        name="Symmetric-algebra defining relations",
    )
    return (presentation_ring).quotient_by_relations(relations,
        _extra_categories=(
            GradedFreeAlgebras(base),
            SymmetricAlgebras(base),
            Algebras(base).Associative().Unital().Commutative(),
            GradedAlgebras(base),
        ),
        _generating_module=module,
    )
