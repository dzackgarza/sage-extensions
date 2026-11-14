from sage_extensions.all import *

def show(label, thunk):
    try:
        print(label, '->', thunk())
    except Exception as error:
        print(label, '->', type(error).__name__, ':', str(error)[:160])

print('NN:', NN, '| parent:', NN.parent() if hasattr(NN, 'parent') else '-')
show('NN(2)', lambda: NN(2))
show('NN(QQ(3)/2)', lambda: NN(QQ(3) / 2))
show('NN(-1)', lambda: NN(-1))
show('in NN of NN(2)', lambda: NN(2) in NN)
show('QQ(3)/2 in NN', lambda: (QQ(3) / 2) in NN)
show('-1 in NN', lambda: (-1) in NN)
show('-1 in ZZ', lambda: (-1) in ZZ)
print('sets over NN:', Sets().Δ[2].subsets_of_size(2))
show('subsets_of_size(NN(2))', lambda: Sets.Δ[2].subsets_of_size(NN(2)))
show('subsets_of_size(QQ(3)/2)', lambda: Sets.Δ[2].subsets_of_size(QQ(3) / 2))
show('subsets_of_size(-1)', lambda: Sets.Δ[2].subsets_of_size(-1))
show('Sets.Δ[2] ** NN(2)', lambda: Sets.Δ[2] ** NN(2))
