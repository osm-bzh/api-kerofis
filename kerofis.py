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
#-------------------------------------------------------------------------------

@app.route("/kerofis/")
def index():
    return "API kerofis : index"



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# /kerofis/infos
# -> return global informations on the kerofis database
#  last date import / refresh
#  array of all the imports


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
#-------------------------------------------------------------------------------

# /kerofis/stats/


@app.route("/kerofis/stats")
@app.route("/kerofis/stats/")
def stats():
    return "API kerofis : stats"
    # TODO renvoyer plutôt une page HTML explicative des méthodes"""



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# /kerofis/municipalities
# -> return all municipalities

# /kerofis/municipalities/search/{insee}
# /kerofis/municipalities/search/{name:br}
# /kerofis/municipalities/search/{name:fr}
# -> return 0, 1 or more municipality


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
        json_str = "{'insee':'" + record[0] + "',"
        json_str += "'name:br':'" + record[1] + "',"
        json_str += "'name:fr':'" + record[2] + "',"
        json_str += "'nb': " + str(record[3]) + "}"
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



@app.route("/kerofis/municipalities/search/", methods=['GET'])
def municipalities_search():
    # search by  insee  OR  name_fr  OR name_br
    # currently : name:fr not present in kerOfis database

    # get all arguments
    code_insee = request.args.get('insee', '')
    name_br = request.args.get('name:br', '')
    name_fr = request.args.get('name:fr', '')

    sSQL = ""

    if (code_insee != '') :
      # search by code insee
      # if lenght = 2 -> search by departement
      if len(code_insee) == 2 :
        sSQL = "SELECT * FROM v_stats_kumun  WHERE insee LIKE '" + code_insee + "%'"
        return municipalities_search_query(sSQL)
        pass
      # if lenght = 5 -> searching one municipality
      if len(code_insee) == 5 :
        sSQL = "SELECT * FROM v_stats_kumun  WHERE insee = '" + code_insee + "'"
        return municipalities_search_query(sSQL)
        pass
      # else : output error
      else :
        return "abort code insee search"
        abort(400)
        pass
    
    if (name_br != '') :
      # search by breton name
      if len(name_br) < 3 :
        # return error 400 TODO : customize error message
        abort(400)
      else :
        sSQL = "SELECT * FROM v_stats_kumun  WHERE LOWER(name_br) LIKE LOWER('%" + name_br + "%')"
        return municipalities_search_query(sSQL)
        pass
    
    if (name_fr != '') :
      # search by french name
      if len(name_fr) < 3 :
        # return error 400 TODO : customize error message
        abort(400)
      else :
        sSQL = "SELECT * FROM v_stats_kumun  WHERE LOWER(name_fr) LIKE LOWER('%" + name_fr + "%')"
        return municipalities_search_query(sSQL)
        pass

    # if nothing -> error 400
    abort(400)
    pass


def municipalities_search_query(sSQL):

    # perform the query
    try:
      pgDB = psycopg2.connect(sConnPostgre)
      pgCursor = pgDB.cursor()

      pgCursor.execute(sSQL)
      records = pgCursor.fetchall()

      # declare array + counter
      json_array = []
      loop_counter = 0

      # loop
      for record in records:
        json_str = "{'insee':'" + record[0] + "',"
        json_str += "'name:br':'" + record[1] + "',"
        json_str += "'name:fr':'" + record[2] + "',"
        json_str += "'nb': " + str(record[3]) + "}"
        json_array.append(json_str)
        loop_counter += 1

      # then return a beautiful json
      return jsonify(
        count = loop_counter,
        municipalities = json_array
      )

      # closing cursor and connection to the database
      pgCursor.close()
      pgDB.close()
      pass

    except Exception, e:
      # out the error to the log
      track= get_current_traceback(skip=1, show_hidden_frames=True, ignore_system_exceptions=False)
      track.log()
      abort(500)
      #raise e
    
    #return sSQL






#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

@app.route("/kerofis/search/")
def search():
    return "API kerofis : search"




#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

@app.errorhandler(400)
def internal_error(error):
    strResponse = str(error)
    response = Response(strResponse, status=400, mimetype='text/html')
    return response

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
#-------------------------------------------------------------------------------


if __name__ == "__main__":
    app.debug = True
    app.run()

