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
#from flask import json
from flask import Response
from flask import request
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


#-------------------------------------------------------------------------------

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
      return jsonify(
        name = "kerofis database",
        last_file_import = date_last_import,
        file_imports = {}
      )

      # closing cursor and connection to the database
      pgCursor.close()
      pgDB.close()

    except Exception,e:
      # out the error to the log
      track= get_current_traceback(skip=1, show_hidden_frames=True, ignore_system_exceptions=False)
      track.log()
      # send ton special function that response HTTP 500 error
      abort(500)



#-------------------------------------------------------------------------------

# /kerofis/stats/municipalities
# /kerofis/stats/municipalities/insee/{code_insee}
# /kerofis/stats/municipalities/name/{name}


@app.route("/kerofis/stats")
@app.route("/kerofis/stats/")
def stats():
    return "API kerofis : stats"
    # TODO renvoyer plutôt une page HTML explicative des méthodes"""



@app.route("/kerofis/municipalities")
@app.route("/kerofis/municipalities/")
def municipalities_index():
    # return a json response with the list of all the municipalities concerned in the database
    # datas provided by the v_stats_kumun table
    # insee | kumun | nb

    # return "API kerofis : stats : par commune : toutes les communes"

    try:
      # get a connection, if a connect cannot be made an exception will be raised here
      pgDB = psycopg2.connect(sConnPostgre)

      # pgDB.cursor will return a cursor object, you can use this cursor to perform queries
      pgCursor = pgDB.cursor()

      #-------------------------------------------------------------------------------
      # first : get count of municipality in the database

      pgCursor.execute("""SELECT COUNT(*) AS count FROM v_stats_kumun""")
      oneRecord = pgCursor.fetchone()
      NbOfMunicipalities = str(oneRecord[0])


      #-------------------------------------------------------------------------------
      # second : loop on all the municipalities

      # the query
      pgCursor.execute("""SELECT * FROM v_stats_kumun""")
      # get all the records
      records = pgCursor.fetchall()

      # return raw json records in  text/html + no attributes name
      #return str(json.dumps(records))

      # return correct application/json answer BUT no attributes name
      #return jsonify({'municipalities':records})

      # declare array
      json_array = []

      # loop on each record to built handmade json
      for record in records:
        json_str = "{'insee': '" + record[0] + "',"
        json_str += "'name': '" + record[1] + "',"
        json_str += "'nb': " + str(record[2]) + "}"
        json_array.append(json_str)

      # then return a beautiful json
      #return jsonify({'municipalities':json_array})
      return jsonify(
        count = NbOfMunicipalities,
        municipalities = json_array
      )

      #return "json_response"

      # closing cursor and connection to the database
      pgCursor.close()
      pgDB.close()

    except Exception,e:
      # out the error to the log
      track= get_current_traceback(skip=1, show_hidden_frames=True, ignore_system_exceptions=False)
      track.log()
      # send ton special function that response HTTP 500 error
      abort(500)



@app.route("/kerofis/stats/municipalities/insee/<code_insee>")
def stats_communes_filter_insee(code_insee):
    
    return code_insee



#-------------------------------------------------------------------------------

@app.route("/kerofis/search/")
def search():
    return "API kerofis : search"



#-------------------------------------------------------------------------------


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

