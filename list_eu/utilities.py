import requests
import pandas as pd
import re
from pyparsing import *
from datetime import date
from bs4 import BeautifulSoup

URL = "https://eur-lex.europa.eu/legal-content/es/TXT/HTML/?uri=CELEX:32019D1341&from=en"

class Utilities:
      
    def __init__(self):
        pass

    # Function to update list of people and entities terrorists of European Union
    def get_data_eu_list(self):
        

        req = requests.get(URL)
        soup = BeautifulSoup(req.content, "html.parser")
        
        # read tables
        tabla = soup.find(id='L_2019209ES.01001701')
        tabla = tabla.find_all('tr')
        contenido = []
        for i in tabla:
            contenido.append(i.text.lower())

        # delete '\n'
        indice = 0
        for i in contenido:
            contenido[indice] = i.replace('\n', '')
            indice = indice + 1

        # get last record of people 
        lim = -1
        for i in contenido:
            if ('«' not in i): lim = lim + 1
            else: break

        personas = contenido[0:lim+1]
        entidades = contenido[lim+1:len(contenido)]

        # fill dataframe
        df_personas = pd.DataFrame(personas)
        df_personas['col1'] = ''
        df_personas['col2'] = ''
        df_personas['col3'] = ''

        # delete start line numbers
        for index, row in df_personas.iterrows():
            row['col1'] = re.sub('\d+.|$', '',row[0])

        # define patterns to search
        persona = OneOrMore( Word(alphanums) ) + "(" | OneOrMore( Word(alphanums) ) + "," + OneOrMore( Word(alphanums) ) + "," \
          | OneOrMore( Word(alphanums) ) + "," + OneOrMore( Word(alphanums) ) + "(" | OneOrMore( Word(alphanums) ) + "," \
          | OneOrMore( Word(alphanums) ) + "-" + OneOrMore( Word(alphanums) ) + "," + OneOrMore( Word(alphanums) ) + "," \
          | OneOrMore( Word(alphanums) ) + "-" + OneOrMore( Word(alphanums) ) + "-" + OneOrMore( Word(alphanums) ) +"," + OneOrMore( Word(alphanums) ) \
          | Regex('(.+?)\(')

        identificacion = "pasaporte:" + Word(alphanums) | "identidad:" + Word(alphanums)
        
        # get text
        for index, row in df_personas.iterrows():
            try:
                row['col2'] = ' '.join(persona.parseString(row['col1'])).replace(" - ","-").replace(" ,",",").strip()
                row['col3'] = str(identificacion.searchString(row[0])).replace('[','').replace(']','').replace("'",'').replace(',','')#
            except: row['col2'] = ""

        # clean dataframe
        df_personas['col2'] = df_personas['col2'].str.replace(r'\(', '')
        df_personas['col2'] = df_personas['col2'].str.strip()
        df_personas['col2'] = df_personas['col2'].str.replace(r',$', '')
        df_personas.drop(columns=[0, 'col1'], inplace = True)
        df_personas.rename(columns={'col2':'nombre', 'col3':'id'}, inplace=True)

        # fill dataframe
        df_entidades = pd.DataFrame(entidades)
        df_entidades['col1'] = ''

        # define patterns to search
        entidad = Regex('«(.+?)»') 
        for index, row in df_entidades.iterrows():
            row['col1'] = str(entidad.searchString(row[0])).replace('[','').replace(']','').replace("'«",'').replace("»'",'').replace('"«','').replace('»"','')

        # define patterns to search
        entidad = Suppress(Regex('\d+.')) + restOfLine
        for index, row in df_entidades.iterrows():
            if row['col1'] == "": row['col1'] = str(entidad.searchString(row[0])).replace('[','').replace(']','').replace("'",'')

        # clean dataframe
        df_entidades.drop(columns=[0], inplace = True)
        df_entidades.rename(columns={'col1':'nombre'}, inplace=True)
        
        
        return df_personas.to_csv('./list_eu/data/list_eu_people_'+ date.today().strftime("%d%m%Y") + '.csv', sep=";", index= False), \
               df_entidades.to_csv('./list_eu/data/list_eu_entities_'+ date.today().strftime("%d%m%Y") + '.csv', sep=";", index= False)