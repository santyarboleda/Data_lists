import requests
import pandas as pd
import re
from pyparsing import *
from datetime import date
from bs4 import BeautifulSoup, element
import itertools
import numpy as np
import os
import string
from datetime import date, datetime, timezone
import pytz


URL = (
    "https://eur-lex.europa.eu/legal-content/es/TXT/HTML/?uri=CELEX:32019D1341&from=en"
)
PEOPLE_FILE = "./list_eu/data/list_eu_people_"
ENTITIES_FILE = "./list_eu/data/list_eu_entities_"
DATA_PATH = "./list_eu/data/"

class Utilities:
    def __init__(self):
        # This is the build method
        pass

    # function to extract a name of dataframe column
    def name_validation(self, x):
        if len(x) == 2:
            return x[1].lower().strip()
        elif len(x) == 3:
            if (x[1][0].isupper() & ~x[1][-1].isupper()) & (
                x[2][0].isupper() & ~x[2][-1].isupper()
            ):
                return x[1].lower() + " " + x[2].lower()
            else:
                return x[2].lower()

    # function to extract a lastname of dataframe column
    def lastname_validation(self, x):
        if len(x) == 3:
            if (x[0][0].isupper() & x[0][-1].isupper()) & (
                x[1][0].isupper() & x[1][-1].isupper()
            ):
                return x[0].lower() + " " + x[1].lower().strip()
            else:
                return x[0].lower()
        else:
            return x[0].lower()

    # function to separate names and lastnames
    def separate_names_lastnames(self, df):
        # separate names and lastnames
        nombres = df["nombre"].tolist()
        nombres = list(map(lambda x: x.split(","), nombres))
        indice = 0
        for i in nombres:
            if len(i) < 2:
                nombres[indice] = i[0].split(" ")
            indice += 1

        # fill dataframe columns
        df["apellido"] = list(map(self.lastname_validation, nombres))
        df["nombre_"] = list(map(self.name_validation, nombres))
        df.drop(columns=["nombre"], inplace=True)
        df.rename(columns={"nombre_": "nombre"}, inplace=True)
        df.loc[df["pasaporte"] == "", "pasaporte"] = np.NaN
        df.loc[df["identificacion"] == "", "identificacion"] = np.NaN
        return df

    def read_page(self, soup):
        # read tables
        tabla = soup.find(id="L_2019209ES.01001701")
        tabla = tabla.find_all("tr")
        contenido = []
        for i in tabla:
            contenido.append(i.text)

        # delete '\n'
        contenido = list(map(lambda x: x.replace("\n", ""), contenido))

        # get last record of people
        lim = -1
        for i in contenido:
            if "«" not in i:
                lim = lim + 1
            else:
                break

        personas = contenido[0 : lim + 1]
        entidades = contenido[lim + 1 : len(contenido)]
        return personas, entidades

    # function to create dataframe with people data
    def fill_people_data(self, personas):
        # fill dataframe
        df = pd.DataFrame(personas)
        df["col1"] = ""
        df["col2"] = ""
        df["col3"] = ""
        df["col4"] = ""

        # delete start line numbers
        for index, row in df.iterrows():
            row["col1"] = re.sub("\d+.|$", "", row[0])

        # define patterns to search
        persona = (
            OneOrMore(Word(alphanums)) + "("
            | OneOrMore(Word(alphanums)) + "," + OneOrMore(Word(alphanums)) + ","
            | OneOrMore(Word(alphanums)) + "," + OneOrMore(Word(alphanums)) + "("
            | OneOrMore(Word(alphanums)) + ","
            | OneOrMore(Word(alphanums))
            + "-"
            + OneOrMore(Word(alphanums))
            + ","
            + OneOrMore(Word(alphanums))
            + ","
            | OneOrMore(Word(alphanums))
            + "-"
            + OneOrMore(Word(alphanums))
            + "-"
            + OneOrMore(Word(alphanums))
            + ","
            + OneOrMore(Word(alphanums))
            | Regex("(.+?)\(")
        )

        pasaporte = "pasaporte:" + Word(alphanums)
        identificacion = "identidad:" + Word(alphanums)

        # get text
        for index, row in df.iterrows():
            try:
                row["col2"] = (
                    " ".join(persona.parseString(row["col1"]))
                    .replace(" - ", "-")
                    .replace(" ,", ",")
                    .strip()
                )
                psw = pasaporte.searchString(row[0].lower())
                idn = identificacion.searchString(row[0].lower())

                # delete first element in each list
                for i in psw:
                    i.pop(0)
                for i in idn:
                    i.pop(0)
                row["col3"] = list(itertools.chain(*psw))
                row["col4"] = list(itertools.chain(*idn))
            except Exception as e:
                print('no fue posible parsear los valores')
                raise e
        return df

    def clean_people_data(self, df):
        # clean dataframe
        df["col2"] = df["col2"].str.replace(r"\(", "")
        df["col2"] = df["col2"].str.strip()
        df["col2"] = df["col2"].str.replace(r",$", "")
        df["col2"] = df["col2"].str.replace("-", " ")
        df.drop(columns=[0, "col1"], inplace=True)
        df.rename(
            columns={"col3": "pasaporte", "col4": "identificacion", "col2": "nombre"},
            inplace=True,
        )
        df["hora_consulta"] = datetime.now(pytz.timezone("America/Bogota")).strftime(
            "%Y%m%d %H %M %p"
        )

        # clean identification and passport
        # for index, row in df.iterrows():
        #     row["pasaporte"] = (
        #         str(row["pasaporte"]).replace("[", "").replace("]", "").replace("'", "")
        #     )
        # for index, row in df.iterrows():
        #     row["identificacion"] = (
        #         str(row["identificacion"])
        #         .replace("[", "")
        #         .replace("]", "")
        #         .replace("'", "")
        #     )
        return df

    def fill_entities_data(self, entidades):
        # fill dataframe entities
        entidades = list(
            map(
                lambda x: self.normalize(x)
                .replace("-", " ")
                .replace(" – ", " ")
                .replace("\xa0", " ")
                .replace(".", "")
                .replace("/", " "),
                entidades,
            )
        )

        df = pd.DataFrame(entidades)
        df["col1"] = ""

        # define patterns to search
        entidad = Regex("«(.+?)»")
        for index, row in df.iterrows():
            row["col1"] = (
                str(entidad.searchString(row[0].lower()))
                .replace("[", "")
                .replace("]", "")
                .replace("'«", "")
                .replace("»'", "")
                .replace('"«', "")
                .replace('»"', "")
            )

        # define patterns to search
        entidad = Suppress(Regex("\d+.")) + restOfLine
        for index, row in df.iterrows():
            if row["col1"] == "":
                row["col1"] = (
                    str(entidad.searchString(row[0].lower()))
                    .replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                )

        # clean dataframe
        df.drop(columns=[0], inplace=True)
        df.rename(columns={"col1": "nombre"}, inplace=True)
        df["hora_consulta"] = datetime.now(pytz.timezone("America/Bogota")).strftime(
            "%Y%m%d %H %M %p"
        )
        return df

    # function to clean vowels
    def normalize(self, s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ü", "u"),
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    # function to remove punctuation
    def remove_punctuation(self, text):
        return re.sub("[%s]" % re.escape(string.punctuation), "", text)

    # function to update list of people and entities terrorists of European Union
    def get_data_eu_list(self):
        req = requests.get(URL)
        soup = BeautifulSoup(req.content, "html.parser")
        
        # read tables
        personas, entidades = self.read_page(soup)
        print('sitio de terroritas de la union europea leido correctamente')

        # fill people data
        df_personas = self.fill_people_data(personas)

        # clean dataframe
        df_personas = self.clean_people_data(df_personas)

        # separate names and lastnames
        df_personas = self.separate_names_lastnames(df_personas)

        # fill entities dataframe
        df_entidades = self.fill_entities_data(entidades)

        return df_personas.to_csv(
            PEOPLE_FILE + date.today().strftime("%d%m%Y") + ".csv",
            sep=";",
            index=False,
        ), df_entidades.to_csv(
            ENTITIES_FILE
            + date.today().strftime("%d%m%Y")
            + ".csv",
            sep=";",
            index=False,
        )

    def read_data(self):
        data_files = os.listdir(DATA_PATH)
        files_people = []
        files_entities = []
        for i in data_files:
            if "list_eu_people" in i:
                files_people.append(datetime.strptime(i[15:-4], "%d%m%Y").date())
            elif "list_eu_entities" in i:
                files_entities.append(datetime.strptime(i[17:-4], "%d%m%Y").date())

        return pd.read_csv(
            PEOPLE_FILE
            + max(files_people).strftime("%d%m%Y")
            + ".csv",
            sep=";",
        ), pd.read_csv(
            ENTITIES_FILE
            + max(files_entities).strftime("%d%m%Y")
            + ".csv",
            sep=";",
        )

if __name__ == "__main__":
    utl = Utilities()
    utl.get_data_eu_list()