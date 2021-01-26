from utilities import Utilities

def Normalize(s):
    assert Utilities.normalize(s), 'Falla'
Normalize('aplicación')

def digit_input_validation():
    list_ = ["1234"]
    assert Utilities.digit_input_validation(list_)
digit_input_validation()
    
def alphanum_input_validation():
    list_ = ["carro"]
    assert Utilities.alphanum_input_validation(list_)
alphanum_input_validation()





