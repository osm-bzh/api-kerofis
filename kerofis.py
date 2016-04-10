#!usr/local/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        API Kerofis
#
# Author:      Maël REBOUX
#
# Created:     04/2016
# Licence:     GNU GPL ?
#
#  Provides methods to access to kerofos data data
#  data provides from open data files
#


# for web REST API
from flask import Flask
from flask import render_template
# for accessing the postgreSQL database
import psycopg2



#-------------------------------------------------------------------------------

app = Flask(__name__)

#-------------------------------------------------------------------------------

# general config parameters

sConnPostgre = "host='localhost' dbname='osm-br' user='osmbr' password='osmbr'"


#-------------------------------------------------------------------------------

@app.route("/kerofis/")
def index():
    return "API kerofis : index"


@app.route("/kerofis/infos")
def infos():
    #return "API kerofis : infos"

    try:
        # get a connection, if a connect cannot be made an exception will be raised here
        pgDB = psycopg2.connect(sConnPostgre)
        #print "connexion à la base : OK"

        # pgDB.cursor will return a cursor object, you can use this cursor to perform queries
        pgCursor = pgDB.cursor()
        # the query
        pgCursor.execute("""SELECT * FROM v_infos_deiziad_restr LIMIT 1""")
        # get only first record
        record = pgCursor.fetchone()
        date_last_import = str(record[0])
        # pass the data to the JSON template
        return render_template('kerofis/infos.json', date_last_import=date_last_import)

        # closing cursor and connection to the database
        pgCursor.close()
        pgDB.close()

    except:
        return "I am unable to connect to the database"

    

@app.route("/kerofis/stats")
def stats():
    return "API kerofis : stats"


@app.route("/kerofis/search/")
def search():
    return "API kerofis : search"





#-------------------------------------------------------------------------------

if __name__ == "__main__":
    app.debug = True
    app.run()

