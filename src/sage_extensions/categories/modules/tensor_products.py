r"""Categorical tensor products and bilinear maps of represented modules."""

from sage_extensions.categories.modules.pure.modules import Modules, _tensor_pair
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import Sets


def _nested_tensor_label(module, word):
    r"""Return the label of the iterated left-associated tensor word."""
    iterator = iter(word)
    try:
        first = next(iterator)
    except StopIteration:
        return 0
    current_module = module
    current_label = first
    modules = Modules(module.base_ring())
    for next_label in iterator:

        current_module = modules.tensor_product((current_module, module))
        current_label = _tensor_pair(
            current_module.module_generating_set(),
            current_label,
            next_label,
        )
    return current_label


def _flatten_tensor_label(label, degree):
    r"""Return the indexed family of factors of a left-associated tensor label."""

    degree = int(degree)
    indices = Sets.Δ[degree - 1]

    def factor(position):
        position = int(position)
        current = label
        current_degree = degree
        while current_degree > 1:
            left = current.component(0)
            right = current.component(1)
            if position == current_degree - 1:
                return right
            current = left
            current_degree -= 1
        if position == 0:
            return current
        raise IndexError(
            f"a pure tensor of {degree} factors has no factor at position {position}"
        )

    return indexed_family(indices, factor, name="Tensor-factor word")



def _tensor_product_morphism(left_morphism, right_morphism, source=None, target=None):
    r"""Return ``f tensor g`` on the chosen tensor products."""
    if left_morphism.domain().base_ring() != right_morphism.domain().base_ring():
        raise ValueError(
            f"cannot form {left_morphism} tensor {right_morphism}: the tensor product of maps needs "
            f"modules over one ring, but the domains are over {left_morphism.domain().base_ring()} "
            f"and {right_morphism.domain().base_ring()}"
        )
    if source is None:
        source = Modules(left_morphism.domain().base_ring()).tensor_product(
            (left_morphism.domain(), right_morphism.domain())
        )
    if target is None:
        target = Modules(left_morphism.codomain().base_ring()).tensor_product(
            (left_morphism.codomain(), right_morphism.codomain())
        )
    if (
        source.tensor_factor(0) is not left_morphism.domain()
        or source.tensor_factor(1) is not right_morphism.domain()
    ):
        raise ValueError(
            f"cannot form {left_morphism} tensor {right_morphism} on {source}: its factors are not "
            f"the domains {left_morphism.domain()} and {right_morphism.domain()}"
        )
    if (
        target.tensor_factor(0) is not left_morphism.codomain()
        or target.tensor_factor(1) is not right_morphism.codomain()
    ):
        raise ValueError(
            f"cannot form {left_morphism} tensor {right_morphism} into {target}: its factors are not "
            f"the codomains {left_morphism.codomain()} and {right_morphism.codomain()}"
        )

    classified = source.from_bilinear_map(
        target,
        lambda left, right: target.pure_tensor(left_morphism(left), right_morphism(right)),
    )
    # ``f tensor g`` is the image of ``(f, g)`` under the tensor bifunctor,
    # so it is linear exactly when ``f`` and ``g`` are.
    return classified.parent()._from_constructed_element_map(
        lambda element: classified(element),
        premises=(left_morphism, right_morphism),
    )



__all__ = [
    "_flatten_tensor_label",
    "_nested_tensor_label",
]
