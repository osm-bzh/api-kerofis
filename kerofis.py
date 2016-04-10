#!usr/local/bin/python
# coding: utf-8 


from flask import Flask
from flask import render_template

import psycopg2

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

app = Flask(__name__)



@app.route("/kerofis/")
def index():
    return "API kerofis : index"


@app.route("/kerofis/infos")
def infos():
    #return "API kerofis : infos"

    try:
        conn = psycopg2.connect("dbname='osm-br' user='osmbr' host='localhost' password='osmbr'")
        #return "connexion à la base : OK"

        cur = conn.cursor()
        cur.execute("""SELECT * FROM v_infos_deiziad_restr LIMIT 1""")
        # get only first record
        record = cur.fetchone()
        date_last_import = str(record[0])
        return render_template('kerofis/infos.json', date_last_import=date_last_import)


    except:
        return "I am unable to connect to the database"

    

@app.route("/kerofis/stats")
def stats():
    return "API kerofis : stats"


@app.route("/kerofis/search/")
def search():
    return "API kerofis : search"






if __name__ == "__main__":
    app.debug = True
    app.run()

