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
from flask import jsonify
from flask import Response
from flask import render_template

# for debug and error handling
from flask import abort
from  werkzeug.debug import get_current_traceback

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

    except Exception,e:
      # out the error to the log
      track= get_current_traceback(skip=1, show_hidden_frames=True, ignore_system_exceptions=False)
      track.log()
      # send ton special function that response HTTP 500 error
      abort(500)

    

@app.route("/kerofis/stats")
def stats():
    return "API kerofis : stats"


@app.route("/kerofis/search/")
def search():
    return "API kerofis : search"


@app.errorhandler(500)
def internal_error(error):
    strResponse = str(error)
    response = Response(strResponse, status=500, mimetype='text/html')
    return response

@app.errorhandler(404)
def internal_error(error):
    strResponse = str(error)
    response = Response(strResponse, status=404, mimetype='text/html')
    return response

#-------------------------------------------------------------------------------


if __name__ == "__main__":
    app.debug = True
    app.run()

