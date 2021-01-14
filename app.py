from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    send_from_directory,
)
import pandas as pd
import utilities
import os
from list_eu.utilities import Utilities as eu_utilities
from list_ssus.utilities import Utilities as ss_utilities
from list_ofac.utilities import Utilities as ofac_utilities
from list_onu.utilities import Utilities as onu_utilities
from list_fv.utilities import Utilities as fv_utilities
from list_pep.utilities import Utilities as pep_utilities

from datetime import date, datetime, timezone


# initializations
app = Flask(__name__)
utl = utilities.Utilities()
utl_eu = eu_utilities()
utl_ss = ss_utilities()
utl_ofac = ofac_utilities()
utl_onu = onu_utilities()
utl_fv = fv_utilities()
utl_pep = pep_utilities()


# Settings
app.secret_key = "secretkey"

# routines
@app.route("/")
def Index():
    data_files = os.listdir("./lists_result/download/")
    for file in data_files:
        file_path = os.path.join('./lists_result/download/', file)
        os.remove(file_path)    
    return render_template("index.html")


@app.route("/result", methods=["POST"])
def result():
    # read form content
    option, list_ = utl.request_validation(request)

    # read list european union
    df_people_eu, df_entities_eu = utl_eu.read_data()

    # read list state secretary
    df_entities_ss = utl_ss.read_data()

    # read list ofac-clinton
    df_people_ofac, df_entities_ofac = utl_ofac.read_data()

    # read list onu
    df_people_onu, df_entities_onu = utl_onu.read_data()

    # read list ficticial vendors
    df_thirdpart_fv = utl_fv.read_data()

    # check selected option
    if option == "nombre":
        list_ = list(filter(None, list_))
        list_ = list(map(lambda x: str(x).strip(), list_))
        list_ = list(map(lambda x: utl.normalize(x), list_))

        if len(list_) == 0:
            flash("Debe ingresar al menos un valor a buscar, Inténtelo de nuevo")
            return redirect(url_for("Index"))
        elif True in utl.digit_input_validation(list_):
            flash(
                "Algunos de los parámetros de búsqueda contiene números, Inténtelo de nuevo"
            )
            return redirect(url_for("Index"))
        else:
            list_ = list(map(lambda x: x.lower(), list_))
            # read pep people
            df_people_pep = utl_pep.read_data(list_)
            df_result = utl.result_by_name(
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
            )
    elif option == "identificacion":
        list_ = list(filter(None, list_))
        list_ = list(map(lambda x: str(x).strip(), list_))

        if len(list_) == 0:
            flash("Debe ingresar al menos un valor a buscar, Inténtelo de nuevo")
            return redirect(url_for("Index"))
        # elif False in utl.alphanum_input_validation(list_):
        #   flash(
        #      "Algunos de los parámetros de búsqueda contiene letras, Inténtelo de nuevo"
        # )
        # return redirect(url_for("Index"))
        else:
            df_result = utl.result_by_id(
                list_, df_people_eu, df_people_onu, df_thirdpart_fv
            )
    else:
        list_ = list(filter(None, list_))
        if len(list_) == 0:
            flash("Debe ingresar al menos un valor a buscar, Inténtelo de nuevo")
            return redirect(url_for("Index"))
        else:
            list_ = list(map(lambda x: x.lower(), list_))
            df_result = utl.result_by_passport(list_, df_people_eu, df_people_onu)
    if df_result.shape[0] > 0:
        flash("Información procesada correctamente")
        df_result.to_excel('./lists_result/download/result.xls')
        return render_template(
            "result.html",
            tables=[df_result.to_html(index=False)],
            titles=[df_result.columns],
            column_names=df_result.columns.values,
            row_data=list(df_result.values.tolist()),
            zip=zip,
            option=option,
            eu_date = datetime.strptime(df_people_eu.iloc[0]['hora_consulta'], "%Y%m%d %H %M %p"),
            ss_date = datetime.strptime(df_entities_ss.iloc[0]['hora_consulta'], "%Y%m%d %H %M %p"),
            onu_date = datetime.strptime(df_people_onu.iloc[0]['hora_consulta'], "%Y%m%d %H%M %p"),
            ofac_date = datetime.strptime(df_people_ofac.iloc[0]['hora_consulta'], "%Y%m%d %H%M %p"),
            tr_date = datetime.strptime(df_thirdpart_fv.iloc[0]['hora_consulta'], "%Y%m%d %H %M %p"),
        )


# function to load lists page
@app.route('/lists')
def lists():
    return render_template('lists.html')

# function to load about page
@app.route('/about')
def about():
    return render_template('about.html')

# Función para descargar el archivo
@app.route('/download')
def download():
    return send_file('./lists_result/download/result.xls', as_attachment=True)


# starting the app
if __name__ == "__main__":

    app.run(port=3000, debug=True, host='0.0.0.0')