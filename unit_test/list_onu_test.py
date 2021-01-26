from list_onu.utilities import Utilities
import re 
import string

utl_onu = Utilities()

def normalize(s):
    assert utl_onu.normalize(s), 'Falla'
normalize('aplicación')

def remove_punctuation(text):
    assert utl_onu.remove_punctuation(text), 'Falla'
remove_punctuation('Con esto termina la frase.')

def get_data():
    assert utl_onu.get_data_onu_list(), 'Falla'
get_data()