r"""Acceptance tests for foundational architectural repairs.

Verifies deterministic provider ordering, strict construction contract
validation, validator execution under strict checking, base ring
propagation across category joins, and boundary hypothesis checks on
lattices, discriminant modules, and form base changes.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.owned_category import (
    ConstructionContract,
    ConstructionParameter,
    _category_provider_order_key,
)
from sage_extensions.validation import validator, strict_checking, run_object_validators


def test_category_provider_order_key_is_deterministic() -> None:
    r"""The provider ordering key depends on structural signature and class name, not session counter."""
    key1 = _category_provider_order_key(Sets())
    key2 = _category_provider_order_key(Sets())
    assert key1 == key2
    assert isinstance(key1, tuple)
    assert len(key1) >= 5


def test_construction_contract_rejects_none_for_required_data() -> None:
    r"""A required construction parameter passed as None raises ValueError."""
    param = ConstructionParameter(
        name="base_ring",
        provider=type,
        kind="POSITIONAL_OR_KEYWORD",
        required=True,
        default=None,
        annotation=None,
    )
    contract = ConstructionContract(
        owner="TestOwner",
        parameters=(param,),
        variadic_providers=(),
        opaque_providers=(),
        hook_providers=(),
    )
    try:
        contract.validate({})
        assert False, "should have raised TypeError"
    except TypeError:
        pass

    try:
        contract.validate({"base_ring": None})
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_strict_checking_and_object_validators() -> None:
    r"""Validators marked on object run when strict checking is enabled."""
    class SampleObject:
        def __init__(self, value: int) -> None:
            self.value = value

        @validator
        def validate_positivity(self) -> None:
            if self.value <= 0:
                raise ValueError("value must be positive")

    obj_invalid = SampleObject(-1)

    strict_checking(False)
    run_object_validators(obj_invalid)

    strict_checking(True)
    try:
        run_object_validators(obj_invalid)
        assert False, "should have raised ValueError"
    except ValueError:
        pass
    finally:
        strict_checking(False)


def test_owned_join_category_base_ring_propagation() -> None:
    r"""An owned category join over a base ring propagates base_ring correctly."""
    cat = Modules(ZZ)
    join_cat = cat._with_axiom("Finite")
    assert join_cat.base_ring() is ZZ
    assert join_cat.base() is ZZ


def test_lattice_discriminant_module_boundary_hypotheses() -> None:
    r"""Discriminant module on a degenerate lattice raises ValueError."""
    degenerate_lattice = Lattices(ZZ)([[0]])
    try:
        degenerate_lattice.discriminant_module()
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_discriminant_module_base_change_and_twist() -> None:
    r"""Discriminant modules propagate base changes and value twists through the source lattice."""
    U = Lattices(ZZ)("U")
    disc = U.discriminant_module()
    assert disc.source_lattice() is U
    twisted_disc = disc.twist(2)
    assert twisted_disc.source_lattice() == U.twist(2)
