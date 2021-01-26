from list_ofac.utilities import Utilities
import re 
import string

utl_ofac = Utilities()

def normalize(s):
    assert utl_ofac.normalize(s), 'Falla'
normalize('aplicación')
    
def remove_punctuation(text):
    assert utl_ofac.remove_punctuation(text), 'Falla'
remove_punctuation('Con esto termina la frase.')

def get_data():
    assert utl_ofac.get_data_ofac_list(), 'Falla'
get_data()