import requests
import pandas as pd
import re
from pyparsing import *
from datetime import date
from bs4 import BeautifulSoup
import os
import string

# import datetime
from datetime import date, datetime, timezone
import pytz

URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"


class Utilities:
    def __init__(self):
        pass

    def read_page(self, soup):
        # read elements in tag
        list = soup.find_all("sdnEntry")
        people = []
        entities = []

        # store data in a dictionary
        ind = 0
        d = {}
        for i in list:
            ds = {}
            for j in i.children:
                ds[j.name] = j.string
            d[ind] = ds
            ind = ind + 1

        # fill lists with data
        for i in d:
            if d[i]["sdnType"] == "Individual":
                try:
                    people.append(d[i]["firstName"] + " " + d[i]["lastName"])
                except:
                    people.append(d[i]["lastName"])
            elif d[i]["sdnType"] == "Entity":
                entities.append(d[i]["lastName"])
        return people, entities

    # function to create dataframe with entities data
    def fill_people_entities_data(self, people, entities):
        df_people = pd.DataFrame(people)
        df_entities = pd.DataFrame(entities)
        df_people.rename(columns={0: "nombre"}, inplace=True)
        df_entities.rename(columns={0: "nombre"}, inplace=True)
        df_people["nombre"] = df_people["nombre"].str.replace(".", "")
        df_people["nombre"] = df_people["nombre"].str.replace("-", " ")
        df_people["nombre"] = df_people["nombre"].apply(lambda x: self.normalize(x))
        df_entities["nombre"] = df_entities["nombre"].str.replace(".", "")
        df_entities["nombre"] = df_entities["nombre"].str.replace("-", " ")
        df_entities["nombre"] = df_entities["nombre"].str.replace(" - ", " ")
        df_entities["nombre"] = df_entities["nombre"].apply(lambda x: self.normalize(x))
        df_people["hora_consulta"] = datetime.now(
            pytz.timezone("America/Bogota")
        ).strftime("%Y%m%d %H%S %p")
        df_entities["hora_consulta"] = datetime.now(
            pytz.timezone("America/Bogota")
        ).strftime("%Y%m%d %H%S %p")
        return df_people, df_entities

    # function to clean vowels
    def normalize(self, s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    # function to remove punctuation
    def remove_punctuation(self, text):
        return re.sub("[%s]" % re.escape(string.punctuation), "", text)

    # function to update list of people and entities terrorists of European Union
    def get_data_ofac_list(self):
        req = requests.get(URL)
        soup = BeautifulSoup(req.content, "xml")

        # read xml file
        people, entities = self.read_page(soup)

        # fill people and entities data
        df_people, df_entities = self.fill_people_entities_data(people, entities)
        df_people["nombre"] = df_people["nombre"].str.lower()
        df_entities["nombre"] = df_entities["nombre"].str.lower()

        return df_people.to_csv(
            "./list_ofac/data/list_ofac_people_"
            + date.today().strftime("%d%m%Y")
            + ".csv",
            sep=";",
            index=False,
        ), df_entities.to_csv(
            "./list_ofac/data/list_ofac_entities_"
            + date.today().strftime("%d%m%Y")
            + ".csv",
            sep=";",
            index=False,
        )

    def read_data(self):
        data_files = os.listdir("./list_ofac/data/")
        files_people = []
        files_entities = []
        for i in data_files:
            if "list_ofac_people" in i:
                files_people.append(datetime.strptime(i[17:-4], "%d%m%Y").date())
            elif "list_ofac_entities" in i:
                files_entities.append(datetime.strptime(i[19:-4], "%d%m%Y").date())

        return pd.read_csv(
            "./list_ofac/data/list_ofac_people_"
            + max(files_people).strftime("%d%m%Y")
            + ".csv",
            sep=";",
        ), pd.read_csv(
            "./list_ofac/data/list_ofac_entities_"
            + max(files_entities).strftime("%d%m%Y")
            + ".csv",
            sep=";",
        )
