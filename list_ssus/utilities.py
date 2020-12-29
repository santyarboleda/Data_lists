#%%
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

URL = "https://www.state.gov/foreign-terrorist-organizations/"
#%%
class Utilities:
    def __init__(self):
        pass

    def read_page(self, soup):
        # read tables
        # tabla = soup.find_all("div", {"class": "table-responsive double-scroll"})
        tabla = soup.find_all("td")
        entity = []
        # patron = Suppress(Regex('*[0-9]\/'))
        for i in tabla:
            entity.append(i.text.strip())

        entity = entity[4 : len(entity)]

        indice = -1
        for i in entity:
            if "Delisted" in i:
                indice = entity.index(i)

        if indice > -1:
            for i in range(indice, len(entity)):
                entity.pop(indice)

        # # delete '\n'
        indice = 0
        for i in entity:
            if "/" in i:
                entity.remove(i)
            elif indice != 0:
                entity[indice] = i.replace("\n", "")
                indice = indice + 1

        return entity

    # function to remove punctuation
    def remove_punctuation(self, text):
        return re.sub("[%s]" % re.escape(string.punctuation), "", text)

    # function to create dataframe with people data
    def fill_entities_data(self, entity):
        pattern = Regex("(.+?)\(") | Regex("(.+?)+")
        entities = []
        for i in entity:
            entities.append(
                str(pattern.searchString(i)[0].asList())
                .replace("(", "")
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .strip()
            )

        initials = []
        for i in entity:
            if len(pattern.searchString(i)) == 1:
                pass
            else:
                initials.append(
                    str(pattern.searchString(i)[1].asList())
                    .replace(")", "")
                    .replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                    .strip()
                )

        result = initials + entities
        result = list(
            map(
                lambda x: x.replace("–", " ").replace("-", " ").replace("   ", " "),
                result,
            )
        )
        result = list(map(lambda x: self.remove_punctuation(x), result))

        df_entities = pd.DataFrame(result)
        df_entities.rename(columns={0: "nombre"}, inplace=True)
        df_entities["hora_consulta"] = datetime.now(
            pytz.timezone("America/Bogota")
        ).strftime("%Y%m%d %H %S %p")
        df_entities["nombre"] = df_entities["nombre"].str.lower()
        return df_entities

    # function to update list of people and entities terrorists of European Union
    def get_data_ssus_list(self):

        req = requests.get(URL)
        soup = BeautifulSoup(req.content, "html.parser")

        entity = self.read_page(soup)

        df_entities = self.fill_entities_data(entity)

        return df_entities.to_csv(
            "./list_ssus/data/list_ssus_entities_"
            + date.today().strftime("%d%m%Y")
            + ".csv",
            sep=";",
            index=False,
        )

    def read_data(self):
        data_files = os.listdir("./list_ssus/data/")
        files_entities = []
        for i in data_files:
            if "list_ssus_entities" in i:
                files_entities.append(datetime.strptime(i[19:-4], "%d%m%Y").date())
        return pd.read_csv(
            "./list_ssus/data/list_ssus_entities_"
            + max(files_entities).strftime("%d%m%Y")
            + ".csv",
            sep=";",
        )
