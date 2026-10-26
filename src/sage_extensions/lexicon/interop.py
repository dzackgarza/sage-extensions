"""Technical Sage-interop nouns."""

from sage.categories.category import Category as SageCategory
from sage.categories.morphism import Morphism as SageMorphism
from sage.combinat.root_system.cartan_matrix import CartanMatrix as SageCartanMatrix
from sage.groups.additive_abelian.qmodnz import QmodnZ as SageQmodnZ
from sage.groups.matrix_gps.isometries import GroupOfIsometries as SageIsometryGroup
from sage.modules.fg_pid.fgp_module import FGP_Module_class
from sage.modules.free_module import FreeModule_generic
from sage.modules.free_quadratic_module_integer_symmetric import (
    FreeQuadraticModule_integer_symmetric as SageLattice,
)
from sage.modules.torsion_quadratic_module import TorsionQuadraticModule as SageDiscriminantForm
from sage.quadratic_forms.genera.genus import Genus_Symbol_p_adic_ring as SageLocalGenusSymbol
from sage.quadratic_forms.genera.genus import GenusSymbol_global_ring as SageGenus
from sage.quadratic_forms.quadratic_form import QuadraticForm as SageQuadraticForm
from sage.rings.infinity import MinusInfinity, PlusInfinity
from sage.structure.element import Element as SageElement
from sage.structure.parent import Parent as SageParent
from sage.structure.unique_representation import UniqueRepresentation as SageUniqueRepresentation

type SageInfinity = PlusInfinity | MinusInfinity
type SageFreeModule = FreeModule_generic | FGP_Module_class

__all__ = [
    "SageCartanMatrix",
    "SageCategory",
    "SageDiscriminantForm",
    "SageElement",
    "SageFreeModule",
    "SageGenus",
    "SageInfinity",
    "SageIsometryGroup",
    "SageLattice",
    "SageLocalGenusSymbol",
    "SageMorphism",
    "SageParent",
    "SageQmodnZ",
    "SageQuadraticForm",
    "SageUniqueRepresentation",
]
