from list_ssus.utilities import Utilities
import requests
from bs4 import BeautifulSoup
import re 
import string

utl_ssus = Utilities()
URL = "https://www.state.gov/foreign-terrorist-organizations/"

def read_page():
    req = requests.get(URL)
    soup = BeautifulSoup(req.content, "html.parser")
    assert utl_ssus.read_page(soup)
read_page()

def remove_punctuation(text):
    assert utl_ssus.remove_punctuation(text), 'Falla'
remove_punctuation('Con esto termina la frase.')

def read_data():
    df = utl_ssus.read_data()
    assert len(df.columns) > 1, 'Falla'
read_data()

def get_data():
    assert utl_ssus.get_data_ssus_list(), 'Falla'
get_data()