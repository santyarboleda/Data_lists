import itertools
from numpy.core.numeric import identity
import pandas as pd
import re


class Utilities:
    def __init__(self):
        self.text = ""
        self.option = ""

    # function to validate form request
    def request_validation(self, request):
        if request.method == "POST":
            self.text = request.form["list"]
            self.option = request.form["choice"]
        list_ = []
        # fill a list with values
        for i in self.text:
            if i != "":
                list_.append(i)
        list_ = "".join(list_).split("\r\n")
        list_ = [str(i).strip(" ") for i in list_]
        return self.option, list_

    def digit_input_validation(self, list_):
        return list(map(lambda x: bool(re.search(r"\d", x)), list_))

    def alphanum_input_validation(self, list_):
        return list(map(lambda x: bool(re.search(r"^[0-9]*$", x)), list_))

    # function to extract entities names
    def get_entities_names(self, df):
        elements = []
        for index, row in df.iterrows():
            elements.append(row["nombre"].split(","))
        elements = list(itertools.chain(*elements))
        elements = [str(i).strip(" ") for i in elements]
        return elements

    # function to validate lists coincidences
    def list_validation(self, values, list):
        coincidences = []
        for i in list:
            if i in values:
                coincidences.append("X")
            else:
                coincidences.append("O")
        return coincidences

    # function to validate pep coincidences
    def pep_list_validation(self, df_people_pep):
        coincidences = []
        for index, row in df_people_pep.iterrows():
            if row["cantidad"] == 0:
                coincidences.append("O")
            elif row["cantidad"] > 0:
                coincidences.append("X(" + str(row["cantidad"]) + ")")
        return coincidences

    def flat_column(self, column):
        column = list(
            map(
                lambda x: str(x)
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace(" ", "")
                .strip()
                .split(","),
                column,
            )
        )
        # flat onu list
        column = list(itertools.chain(*column))
        return column

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

    # function to build result view by name selection
    def result_by_name(
        self,
        list_,
        df_people_eu,
        df_entities_eu,
        df_entities_ss,
        df_people_ofac,
        df_entities_ofac,
        df_people_onu,
        df_entities_onu,
        df_thirdpart_fv,
        df_people_pep,
    ):
        # european union validation
        df_people_eu["nombre_completo"] = (
            df_people_eu["nombre"] + " " + df_people_eu["apellido"]
        )
        entities_names_eu = self.get_entities_names(df_entities_eu)
        names_eu = list(df_people_eu["nombre_completo"].values) + entities_names_eu

        # add onu data
        df_people_onu["nombre_completo"] = ""
        for index, row in df_people_onu.iterrows():
            row["nombre_completo"] = (
                str(row["primer_nombre"])
                + " "
                + str(row["segundo_nombre"])
                + " "
                + str(row["tercer_nombre"])
                + " "
                + str(row["cuarto_nombre"])
                + " "
            )
            row["nombre_completo"] = (
                row["nombre_completo"].replace("None", "").replace("nan", "").strip()
            )

        # create result dataframe
        df_result = pd.DataFrame()
        df_result["Nombre Completo"] = list_
        df_result["Lista de la Unión Europea"] = self.list_validation(names_eu, list_)
        df_result[
            "Lista de la Secretaria de Estado de Estados Unidos"
        ] = self.list_validation(list(df_entities_ss["nombre"].values), list_)

        df_result["Lista OFAC - Clinton"] = self.list_validation(
            list(df_people_ofac["nombre"].values)
            + list(df_entities_ofac["nombre"].values),
            list_,
        )

        df_result["Lista de las Naciones Unidas"] = self.list_validation(
            list(df_people_onu["nombre_completo"].values)
            + list(df_entities_onu["nombre"].values),
            list_,
        )

        df_result["Lista de proveedores fictios en Colombia"] = self.list_validation(
            list(df_thirdpart_fv["nombre"].values), list_
        )

        df_result["Lista PEPs en Colombia"] = self.pep_list_validation(df_people_pep)

        return df_result

    # function to build result view by id selection
    # def result_by_id(self, list_, df_people_eu):
    #     # european union validation
    #     df_people_eu["full_name"] = (
    #         df_people_eu["nombre"] + " " + df_people_eu["apellido"]
    #     )
    #     df_people_eu["identificacion"].fillna(0, inplace=True)
    #     id_eu = list(df_people_eu["identificacion"].astype(int))
    #     list_ = filter(None, list_)
    #     list_ = [int(i) for i in list_]
    #     # list_ = [str(i) for i in list_]

    #     # create result dataframe
    #     df_result = pd.DataFrame()
    #     df_result["id"] = list_
    #     df_result["eu_list"] = self.list_validation(id_eu, list_)
    #     return df_result

    # function to build result view by id selection
    def result_by_id(self, list_, df_people_eu, df_people_onu, df_thirdpart_fv):
        # european union list data
        id_eu = self.flat_column(list(df_people_eu["identificacion"].astype(str)))

        # onu list data
        id_onu = self.flat_column(list(df_people_onu["identificacion"].astype(str)))

        id_fv = self.flat_column(list(df_thirdpart_fv["identificacion"].astype(str)))

        # create result dataframe
        df_result = pd.DataFrame()
        df_result["Identificación"] = list_
        df_result["Lista de la Unión Europea"] = self.list_validation(id_eu, list_)
        df_result["Lista de las Naciones Unidas"] = self.list_validation(id_onu, list_)
        df_result["Lista de proveedores fictios en Colombia"] = self.list_validation(
            id_fv, list_
        )
        return df_result

    # function to build result view by id selection
    def result_by_passport(self, list_, df_people_eu, df_people_onu):
        # european union list data
        pp_eu = self.flat_column(list(df_people_eu["pasaporte"].astype(str)))

        # onu list data
        pp_onu = self.flat_column(list(df_people_onu["pasaporte"].astype(str)))

        df_result = pd.DataFrame()
        df_result["Número de pasaporte"] = list_
        df_result["Lista de la Unión Europea"] = self.list_validation(pp_eu, list_)
        df_result["Lista de las Naciones Unidas"] = self.list_validation(pp_onu, list_)
        return df_result
