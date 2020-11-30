#%%
import requests
import pandas as pd
import re
from pyparsing import *
from datetime import date
from bs4 import BeautifulSoup

URL = "https://www.state.gov/foreign-terrorist-organizations/"
#%%
class Utilities:
      
    def __init__(self):
        pass

    # Function to update list of people and entities terrorists of European Union
    def get_data_ssus_list(self):

        req = requests.get(URL)
        soup = BeautifulSoup(req.content, "html.parser")
        
        # read tables
        tabla = soup.find_all("div", {"class": "table-responsive double-scroll"})
        tabla = soup.find_all('td')
        entidades = []
        #patron = Suppress(Regex('*[0-9]\/'))
        for i in tabla:
            entidades.append(i.text.strip())

        entidades = entidades[4:len(entidades)]

        indice = -1
        for i in entidades:
            if "Delisted" in i: indice = entidades.index(i)

        if indice > -1:
            for i in range(indice, len(entidades)):
                entidades.pop(indice)

        # # delete '\n'
        indice = 0
        for i in entidades:
             if "/" in i: entidades.remove(i)
             elif indice != 0:
                 entidades[indice] = i.lower().replace('\n', '')
                 indice = indice + 1
            

        df_entities = pd.DataFrame(entidades)
        return df_entities.to_csv("./list_ssus/data/list_ssus" + date.today().strftime("%d%m%Y") +".csv", sep=";", index = False)  
