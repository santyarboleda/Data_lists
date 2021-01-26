from list_pep.utilities import Utilities
import re 
import string

utl_pep = Utilities()

def browser_settings():
    assert utl_pep.browser_settings()
browser_settings()

def browser_settings_1():
    assert utl_pep.browser_settings_1()
browser_settings_1()

def read_data():
    list_ = ['ivan duque']
    assert utl_pep.read_data(list_)
read_data()