import requests
import pandas as pd
import re
import string
import wget
from pyparsing import *
from bs4 import BeautifulSoup
import os
import glob
import xml.etree.cElementTree as ET
import numpy as np
from datetime import date, datetime, timezone
import pytz


URL = "https://scsanctions.un.org/resources/xml/sp/consolidated.xml"
PEOPLE_FILE = "./list_onu/data/list_onu_people_"
ENTITIES_FILE = "./list_onu/data/list_onu_entities_"
DATA_PATH = "./list_onu/data/"
XML_FILE = "./list_onu/download/consolidated.xml"
DOWNLOAD_FILES = "./list_onu/download/*"

class Utilities:
    def __init__(self):
        # This is the build method
        pass

    def download_file(self):
        return wget.download(URL, XML_FILE)

    def read_page(self, xtree):

        # read people data
        d = {}
        xtree = ET.parse(xtree)
        xroot = xtree.getroot()
        cont = 0
        for node in xroot[0]:
            ds = {}
            id_ = []
            ty = []
            for v in node.getchildren():
                if v.tag == "INDIVIDUAL_DOCUMENT":
                    for n in v.getchildren():
                        if n.tag == "NUMBER":
                            id_.append(n.text)
                        if n.tag == "TYPE_OF_DOCUMENT":
                            ty.append(n.text)
                    ds[v.tag] = list(
                        map(
                            lambda x: x.replace("-", " ").replace("None", "").lower(),
                            id_,
                        )
                    )
                    ds["TYPE_DOCUMENT"] = list(
                        map(
                            lambda x: x.replace("-", " ").replace("None", "").lower(),
                            ty,
                        )
                    )
                else:
                    ds[v.tag] = v.text
            d[cont] = ds
            cont += 1

        # create dataframe
        df = pd.DataFrame.from_dict(d, orient="index")
        df = df[
            [
                "FIRST_NAME",
                "SECOND_NAME",
                "THIRD_NAME",
                "FOURTH_NAME",
                "TYPE_DOCUMENT",
                "INDIVIDUAL_DOCUMENT",
            ]
        ]
        df["TYPE_DOCUMENT"].fillna("[]", inplace=True)
        df["INDIVIDUAL_DOCUMENT"].fillna("[]", inplace=True)

        # organize column values to divide in id and pasports
        df2 = pd.DataFrame(df["TYPE_DOCUMENT"].tolist(), index=df.index)
        df3 = pd.DataFrame(df["INDIVIDUAL_DOCUMENT"].tolist(), index=df.index)
        merge = df2.merge(df3, left_index=True, right_index=True)
        df_people = self.extract_id_passaport(df, merge)

        # reading entities data
        d = {}
        cont = 0
        for node in xroot[1]:  # 0 INDIVIDUALS 1 ENTITIES
            ds = {}
            ty = []
            for v in node.getchildren():
                ds[v.tag] = v.text
            d[cont] = ds
            cont += 1

        df_entities = pd.DataFrame.from_dict(d, orient="index")
        df_entities = df_entities[["FIRST_NAME"]]
        return df_people, df_entities

    def extract_id_passaport(self, df, merge):
        size = len(merge.columns) / 2
        merge["pasaporte"] = ""
        merge["identificacion"] = ""
        for index, row in merge.iterrows():
            pasaporte = []
            identificacion = []
            for i in range(len(merge.columns)):
                if (row[i] != None) & (i < size):
                    if "pas" in row[i].lower():
                        pasaporte.append(row[str(i) + "_y"])
                    elif i < size:
                        identificacion.append(row[str(i) + "_y"])
            row["pasaporte"] = pasaporte
            row["identificacion"] = identificacion
        # merge with original dataframe
        df = df.merge(
            merge[["pasaporte", "identificacion"]], left_index=True, right_index=True
        )
        # clean dataframe
        del df["TYPE_DOCUMENT"]
        del df["INDIVIDUAL_DOCUMENT"]
        return df

    def clean_people_data(self, df):
        df["hora_consulta"] = datetime.now(pytz.timezone("America/Bogota")).strftime(
            "%Y%m%d %H%M %p"
        )
        df.rename(
            columns={
                "FIRST_NAME": "primer_nombre",
                "SECOND_NAME": "segundo_nombre",
                "THIRD_NAME": "tercer_nombre",
                "FOURTH_NAME": "cuarto_nombre",
            },
            inplace=True,
        )

        df["primer_nombre"] = df["primer_nombre"].str.lower()
        df["primer_nombre"] = df["primer_nombre"].str.replace("-", " ")
        df["segundo_nombre"] = df["segundo_nombre"].str.lower()
        df["segundo_nombre"] = df["segundo_nombre"].str.replace("-", " ")
        df["tercer_nombre"] = df["tercer_nombre"].str.lower()
        df["tercer_nombre"] = df["tercer_nombre"].str.replace("-", " ")
        df["cuarto_nombre"] = df["cuarto_nombre"].str.lower()
        df["cuarto_nombre"] = df["cuarto_nombre"].str.replace("-", " ")
        df["primer_nombre"] = df["primer_nombre"].str.replace("'", "")
        df["segundo_nombre"] = df["segundo_nombre"].str.replace("'", "")
        df["tercer_nombre"] = df["tercer_nombre"].str.replace("'", "")
        df["cuarto_nombre"] = df["cuarto_nombre"].str.replace("'", "")
        df["primer_nombre"] = df["primer_nombre"].str.strip()
        df["segundo_nombre"] = df["segundo_nombre"].str.strip()
        df["tercer_nombre"] = df["tercer_nombre"].str.strip()
        df["cuarto_nombre"] = df["cuarto_nombre"].str.strip()
        df["primer_nombre"] = df["primer_nombre"].apply(
            lambda x: self.remove_punctuation(str(x))
        )
        df["segundo_nombre"] = df["segundo_nombre"].apply(
            lambda x: self.remove_punctuation(str(x))
        )
        df["tercer_nombre"] = df["tercer_nombre"].apply(
            lambda x: self.remove_punctuation(str(x))
        )
        df["cuarto_nombre"] = df["cuarto_nombre"].apply(
            lambda x: self.remove_punctuation(str(x))
        )
        df = df.fillna(value=np.nan)
        return df

    def clean_entities_data(self, df):
        df.rename(columns={"FIRST_NAME": "nombre"}, inplace=True)
        df["nombre"] = df["nombre"].apply(lambda x: str(x).strip())
        df["nombre"] = df["nombre"].apply(lambda x: x.lower())
        df["nombre"] = df["nombre"].apply(lambda x: self.normalize(x))

        return df

    # function to create dataframe with entities data
    def fill_entities_data(self, df):
        pattern = Regex("(.+?)\(") | Regex("(.+?)+")
        entities = []
        entity = df["nombre"].tolist()
        for i in entity:
            entities.append(
                str(pattern.searchString(i)[0].asList())
                .replace("(", "")
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace('"', "")
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
        df = pd.DataFrame()
        df["nombre"] = list(map(lambda x: self.remove_punctuation(x), result))
        df["hora_consulta"] = datetime.now(pytz.timezone("America/Bogota")).strftime(
            "%Y%m%d %H%M %p"
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
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    # function to remove punctuation
    def remove_punctuation(self, text):
        return re.sub("[%s]" % re.escape(string.punctuation), "", text)

    def clean_directory(self):
        files = glob.glob(DOWNLOAD_FILES)
        for f in files:
            os.remove(f)
        return "Folder content deleted"

    # function to update list of people and entities terrorists of European Union
    def get_data_onu_list(self):

        # clean download directory
        self.clean_directory()

        # download xml file
        self.download_file()
        print('\narchivo de lista onu descargado correctamente')

        # read file content
        xtree = XML_FILE
        df_people, df_entities = self.read_page(xtree)
        print('archivo de lista onu leido correctamente')

        # clean people data
        df_people = self.clean_people_data(df_people)

        # clean entites data
        df_entities = self.clean_entities_data(df_entities)
        df_entities = self.fill_entities_data(df_entities)
        return df_people.to_csv(
            PEOPLE_FILE
            + date.today().strftime("%d%m%Y")
            + ".csv",
            sep=";",
            index=False,
        ), df_entities.to_csv(
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
            if "list_onu_people" in i:
                files_people.append(datetime.strptime(i[16:-4], "%d%m%Y").date())
            elif "list_onu_entities" in i:
                files_entities.append(datetime.strptime(i[18:-4], "%d%m%Y").date())

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
