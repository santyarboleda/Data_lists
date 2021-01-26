from list_fv.utilities import Utilities
import re 
import string

utl_fv = Utilities()

def download_pdf():
    assert utl_fv.download_file(), 'Falla'
download_pdf()

# def read_pdf():
#     assert utl_fv.read_file(), 'Falla'
# read_pdf()

def clean_directory():
    assert utl_fv.clean_directory(), 'Falla'
clean_directory()

# def read_data():
#     assert utl_fv.read_data(), 'Falla'
# read_data()

def normalize(s):
    assert utl_fv.normalize(s), 'Falla'
normalize('aplicación')

def get_data():
    assert utl_fv.get_data_fv_list, 'Falla'
get_data()