import requests
import urllib.request
import pandas as pd
import re
import string
from pyparsing import *
from bs4 import BeautifulSoup
import os
import glob
import tabula


# import datetime
from datetime import date, datetime, timezone
import pytz


URL = (
    "https://www.dian.gov.co/Proveedores_Ficticios/Proveedores_Ficticios_"
    + date.today().strftime("%d%m%Y")
    + ".pdf"
)


class Utilities:
    def __init__(self):
        pass

    def download_file(self):
        URL = "https://www.dian.gov.co/Proveedores_Ficticios/Proveedores_Ficticios_02092020.pdf"
        response = requests.get(URL)
        flag = True
        if response.status_code == 200:
            with open("./list_fv/download/proveedores_ficticios.pdf", "wb") as f:
                f.write(response.content)
        elif response.status_code == 404:
            flag = False
        return flag

    def read_file(self):
        # reading file
        file = "./list_fv/download/proveedores_ficticios.pdf"
        table = tabula.read_pdf(file, pages="all")

        # create dataframe
        df = pd.DataFrame()
        for i in table:
            df_1 = i.rename(
                columns={
                    i.columns[0]: "col1",
                    i.columns[1]: "col2",
                    i.columns[2]: "col3",
                    i.columns[3]: "col4",
                    i.columns[4]: "col5",
                    i.columns[5]: "col6",
                    i.columns[6]: "col7",
                }
            )
            df = pd.concat([df, df_1])
        return df

    def clean_data(self, df):
        df.columns = df.iloc[0]
        df.drop([0], inplace=True)
        df = df.rename(
            columns={"NIT": "identificacion", "NOMBRE O RAZON SOCIAL": "nombre"}
        )

        df["nombre"] = df["nombre"].apply(lambda x: x.lower())
        df["nombre"] = df["nombre"].apply(lambda x: x.replace(".", ""))
        df["nombre"] = df["nombre"].apply(lambda x: self.normalize(x))
        return df

    # function to create dataframe with people and entities data
    def fill_people_entities_data(self, df):
        df = df.reset_index()
        values = list(df["col1"].str.contains("LEVANTADO").values)
        df.drop(range(values.index(True), len(df)), inplace=True)
        df = df[["col2", "col3"]]
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

    def clean_directory(self):
        files = glob.glob("./list_fv/download/*")
        for f in files:
            os.remove(f)
        return "Folder content deleted"

    # function to update list of people and entities terrorists of European Union
    def get_data_fv_list(self):
        # clean download directory
        self.clean_directory()

        df_people_entities = pd.DataFrame()

        flag = False
        try:
            # download xml file
            flag = self.download_file()

            # read pdf file
            df_people_entities = self.read_file()

            # fill list dataframe
            df_people_entities = self.fill_people_entities_data(df_people_entities)

            # clean data
            df_people_entities = self.clean_data(df_people_entities)

            if flag == True:
                return df_people_entities.to_csv(
                    "./list_fv/data/list_fv_data_"
                    + date.today().strftime("%d%m%Y")
                    + ".csv",
                    sep=";",
                    index=False,
                )
        except:
            return print("No se pudo descargar el archivo")

    def read_data(self):
        data_files = os.listdir("./list_fv/data/")
        files = []
        for i in data_files:
            if "list_fv_data" in i:
                files.append(datetime.strptime(i[13:-4], "%d%m%Y").date())
        return pd.read_csv(
            "./list_fv/data/list_fv_data_" + max(files).strftime("%d%m%Y") + ".csv",
            sep=";",
        )