import requests
import pandas as pd
import re
from pyparsing import *
from datetime import date
from bs4 import BeautifulSoup
import itertools
import numpy as np

URL = "https://eur-lex.europa.eu/legal-content/es/TXT/HTML/?uri=CELEX:32019D1341&from=en"

class Utilities:
      
    def __init__(self):
        pass

    # function to extract a name of dataframe column     
    def name_validation(self, x):
        if len(x) == 2: return x[1].lower().strip()
        elif len(x) == 3:
            if (x[1][0].isupper() & ~x[1][-1].isupper()) & (x[2][0].isupper() & ~x[2][-1].isupper()): return (x[1].lower() + ' ' + x[2].lower())
            else: return x[2].lower()    

    # function to extract a lastname of dataframe column 
    def lastname_validation(self, x):
        if len(x) == 3:
            if (x[0][0].isupper() & x[0][-1].isupper()) & (x[1][0].isupper() & x[1][-1].isupper()): return x[0].lower() +' '+ x[1].lower().strip()
            else: return x[0].lower()
        else: return x[0].lower()

    def separate_names_lastnames(self):
        pass    

    # function to update list of people and entities terrorists of European Union
    def get_data_eu_list(self):
        req = requests.get(URL)
        soup = BeautifulSoup(req.content, "html.parser")
        
        # read tables
        tabla = soup.find(id='L_2019209ES.01001701')
        tabla = tabla.find_all('tr')
        contenido = []
        for i in tabla:
            contenido.append(i.text)

        # delete '\n'
        contenido = list(map(lambda x: x.replace('\n', ''), contenido))

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
        df_personas['col4'] = ''

        # delete start line numbers
        for index, row in df_personas.iterrows():
            row['col1'] = re.sub('\d+.|$', '',row[0])

        # define patterns to search
        persona = OneOrMore( Word(alphanums) ) + "(" | OneOrMore( Word(alphanums) ) + "," + OneOrMore( Word(alphanums) ) + "," \
          | OneOrMore( Word(alphanums) ) + "," + OneOrMore( Word(alphanums) ) + "(" | OneOrMore( Word(alphanums) ) + "," \
          | OneOrMore( Word(alphanums) ) + "-" + OneOrMore( Word(alphanums) ) + "," + OneOrMore( Word(alphanums) ) + "," \
          | OneOrMore( Word(alphanums) ) + "-" + OneOrMore( Word(alphanums) ) + "-" + OneOrMore( Word(alphanums) ) +"," + OneOrMore( Word(alphanums) ) \
          | Regex('(.+?)\(')

        #identificacion = "pasaporte:" + Word(alphanums) | "identidad:" + Word(alphanums)
        pasaporte = "pasaporte:" + Word(alphanums)
        identificacion = "identidad:" + Word(alphanums)

        # get text
        for index, row in df_personas.iterrows():
            try:
                row['col2'] = ' '.join(persona.parseString(row['col1'])).replace(" - ","-").replace(" ,",",").strip()
                psw = (pasaporte.searchString(row[0].lower()))
                idn = (identificacion.searchString(row[0].lower()))
                
                # delete first element in each list
                for i in psw:
                    i.pop(0)
                for i in idn:
                    i.pop(0)
                row['col3'] = list(itertools.chain(*psw))
                row['col4'] = list(itertools.chain(*idn))
            except: pass
       
        # clean dataframe
        df_personas['col2'] = df_personas['col2'].str.replace(r'\(', '')
        df_personas['col2'] = df_personas['col2'].str.strip()
        df_personas['col2'] = df_personas['col2'].str.replace(r',$', '')
        df_personas.drop(columns=[0, 'col1'], inplace = True)
        df_personas.rename(columns={'col3':'pasaporte', 'col4':'identificacion', 'col2':'nombre'}, inplace=True)
              
        # clean identification and passport
        for index, row in df_personas.iterrows():
            row['pasaporte'] = str(row['pasaporte']).replace('[','').replace(']','').replace("'",'')

        for index, row in df_personas.iterrows():
            row['identificacion'] = str(row['identificacion']).replace('[','').replace(']','').replace("'",'')
                
        # separate names and lastnames
        nombres = df_personas['nombre'].tolist()
        nombres_ = list(map(lambda x: x.split(','), nombres))
        indice = 0
        for i in nombres_:
            if len(i)<2: nombres_[indice] = i[0].split(' ')
            indice += 1

        # fill dataframe columns 
        df_personas['apellido'] = list(map(self.lastname_validation, nombres_))
        df_personas['nombre_'] = list(map(self.name_validation, nombres_))
        df_personas.drop(columns=['nombre'], inplace = True)
        df_personas.rename(columns={'nombre_':'nombre'}, inplace=True)
        df_personas.loc[df_personas['pasaporte'] == '', 'pasaporte'] = np.NaN 
        df_personas.loc[df_personas['identificacion'] == '', 'identificacion'] = np.NaN
        

        # fill dataframe entities
        df_entidades = pd.DataFrame(entidades)
        df_entidades['col1'] = ''

        # define patterns to search
        entidad = Regex('«(.+?)»') 
        for index, row in df_entidades.iterrows():
            row['col1'] = str(entidad.searchString(row[0].lower())).replace('[','').replace(']','').replace("'«",'').replace("»'",'').replace('"«','').replace('»"','')

        # define patterns to search
        entidad = Suppress(Regex('\d+.')) + restOfLine
        for index, row in df_entidades.iterrows():
            if row['col1'] == "": row['col1'] = str(entidad.searchString(row[0].lower())).replace('[','').replace(']','').replace("'",'')

        # clean dataframe
        df_entidades.drop(columns=[0], inplace = True)
        df_entidades.rename(columns={'col1':'nombre'}, inplace=True)
        
        
        return df_personas.to_csv('./list_eu/data/list_eu_people_'+ date.today().strftime("%d%m%Y") + '.csv', sep=";", index= False), \
               df_entidades.to_csv('./list_eu/data/list_eu_entities_'+ date.today().strftime("%d%m%Y") + '.csv', sep=";", index= False)