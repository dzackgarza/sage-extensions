'Modules equipped with bilinear or quadratic forms.'

from importlib import import_module as _import_module

_EXPORTS = {'DiscriminantBilinearModules': ('sage_extensions.categories.modules.framed.formed.discriminant_modules',
                                 'DiscriminantBilinearModules'),
 'DiscriminantModules': ('sage_extensions.categories.modules.framed.formed.discriminant_modules',
                         'DiscriminantModules'),
 'DiscriminantQuadraticModules': ('sage_extensions.categories.modules.framed.formed.discriminant_modules',
                                  'DiscriminantQuadraticModules'),
 'BilinearFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                         'BilinearFormModules'),
 'FiberedFormedModuleMor': ('sage_extensions.categories.modules.framed.formed.form_modules',
                               'FiberedFormedModuleMor'),
 'FiberedFormedModuleMorphism': ('sage_extensions.categories.modules.framed.formed.form_modules',
                                 'FiberedFormedModuleMorphism'),
 'FormedModuleMor': ('sage_extensions.categories.modules.framed.formed.form_modules',
                        'FormedModuleMor'),
 'FormedModuleMorphism': ('sage_extensions.categories.modules.framed.formed.form_modules',
                          'FormedModuleMorphism'),
 'FormEmbedding': ('sage_extensions.categories.modules.framed.formed.form_modules',
                   'FormEmbedding'),
 'FormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                 'FormModules'),
 'NondegenerateGenericFibreFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                                          'NondegenerateGenericFibreFormModules'),
 'FreeFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                     'FreeFormModules'),
 'PairingObjects': ('sage_extensions.categories.modules.framed.formed.form_modules',
                    'PairingObjects'),
 'PairedModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                   'PairedModules'),
 'QuadraticFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                          'QuadraticFormModules'),
 'SymmetricBilinearFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                                  'SymmetricBilinearFormModules'),
 'TorsionBilinearFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                                'TorsionBilinearFormModules'),
 'TorsionFormIsometry': ('sage_extensions.categories.modules.framed.formed.torsion_form_modules',
                         'TorsionFormIsometry'),
 'TorsionQuadraticFormModules': ('sage_extensions.categories.modules.framed.formed.form_modules',
                                 'TorsionQuadraticFormModules')}

__all__ = [
 'BilinearFormModules',
 'DiscriminantBilinearModules',
 'DiscriminantModules',
 'DiscriminantQuadraticModules',
 'FormEmbedding',
 'FormedModuleMor',
 'FormedModuleMorphism',
 'FiberedFormedModuleMor',
 'FiberedFormedModuleMorphism',
 'FormModules',
 'NondegenerateGenericFibreFormModules',
 'FreeFormModules',
 'PairingObjects',
 'PairedModules',
 'QuadraticFormModules',
 'SymmetricBilinearFormModules',
 'TorsionBilinearFormModules',
 'TorsionFormIsometry',
 'TorsionQuadraticFormModules']

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
