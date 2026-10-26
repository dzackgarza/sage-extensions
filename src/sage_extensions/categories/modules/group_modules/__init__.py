'Modules over group algebras and lattices with a group action.'

from importlib import import_module as _import_module

_EXPORTS = {'GroupModuleMor': ('sage_extensions.categories.modules.group_modules.group_modules',
                       'GroupModuleMor'),
 'FiniteFreeGroupRepresentations': ('sage_extensions.categories.modules.group_modules.group_modules', 'FiniteFreeGroupRepresentations'),
 'OrdinaryCharacterRepresentations': ('sage_extensions.categories.modules.group_modules.group_modules', 'OrdinaryCharacterRepresentations'),
 'BrauerCharacterRepresentations': ('sage_extensions.categories.modules.group_modules.group_modules', 'BrauerCharacterRepresentations'),
 'GroupModuleMorphism': ('sage_extensions.categories.modules.group_modules.group_modules',
                         'GroupModuleMorphism'),
 'ModulesOverGroupAlgebra': ('sage_extensions.categories.modules.group_modules.group_modules',
                             'ModulesOverGroupAlgebra'),
 'LatticesOverGroupAlgebra': ('sage_extensions.categories.modules.group_modules.group_lattices',
                             'LatticesOverGroupAlgebra')}

__all__ = ['GroupModuleMor',
 'FiniteFreeGroupRepresentations',
 'OrdinaryCharacterRepresentations',
 'BrauerCharacterRepresentations',
 'GroupModuleMorphism',
 'ModulesOverGroupAlgebra',
 'LatticesOverGroupAlgebra',
]

def __getattr__(name):
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as error:
        raise AttributeError(name) from error
    value = getattr(_import_module(module_name), attribute)
    globals()[name] = value
    return value

def __dir__():
    return sorted((*globals(), *__all__))
