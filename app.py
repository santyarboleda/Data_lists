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
from list_eu.utilities import Utilities as eu_utilities
from list_ssus.utilities import Utilities as ss_utilities
from list_ofac.utilities import Utilities as ofac_utilities
from list_onu.utilities import Utilities as onu_utilities
import utilities

# initializations
app = Flask(__name__)
utl = utilities.Utilities()
utl_eu = eu_utilities()
utl_ss = ss_utilities()
utl_ofac = ofac_utilities()
utl_onu = onu_utilities()

# Settings
app.secret_key = "secretkey"

# routines
@app.route("/")
def Index():
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

    # read list onu-clinton
    df_people_onu, df_entities_onu = utl_onu.read_data()
    # print(df_people_onu)

    # check selected option
    if option == "nombre":
        # print(utl.digit_input_validation(list_))
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
            df_result = utl.result_by_name(
                list_,
                df_people_eu,
                df_entities_eu,
                df_entities_ss,
                df_people_ofac,
                df_entities_ofac,
                df_people_onu,
                df_entities_onu,
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
            df_result = utl.result_by_id(list_, df_people_eu, df_people_onu)
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
        return render_template(
            "result.html",
            tables=[df_result.to_html(classes="data", index=False)],
            titles=[df_result.columns],
        )


# starting the app
if __name__ == "__main__":

    app.run(port=3000, debug=True)