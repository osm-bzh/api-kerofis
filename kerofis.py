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

sConnPostgre = "host='localhost' dbname='kerofis' user='kerofis' password='kerofis'"

licence = "Open Database License (ODbL) v1.0"
attribution_en = "KerOfis by osm-bzh"
attribution_fr = "KerOfis par osm-bzh"
attribution_br = "KerOfis gant osm-bzh"

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

@app.route("/kerofis/")
def index():
    return "API KerOfis : index"



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# /kerofis/infos
# -> return global informations on the kerofis database
#  last date import / refresh
#  array of all the imports


@app.route("/kerofis/infos")
@app.route("/kerofis/infos/")
def infos():
    #return "API kerofis : infos"

    try:
      # get a connection, if a connect cannot be made an exception will be raised here
      pgDB = psycopg2.connect(sConnPostgre)

      # pgDB.cursor will return a cursor object, you can use this cursor to perform queries
      pgCursor = pgDB.cursor()

      # the query
      pgCursor.execute("""SELECT * FROM infos_file_import LIMIT 1""")
      # get only first record
      record = pgCursor.fetchone()
      date_last_import = str(record[0])

      # pass the data to the JSON template
      return jsonify(
        name = "KerOfis data provided by Ofis publik ar brezhoneg",
        licence = licence,
        attribution_en = attribution_en,
        attribution_fr = attribution_fr,
        attribution_br = attribution_br,
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
      # return customized error message in JSON
      return jsonify(error = str(e)), 500



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# /kerofis/stats/


@app.route("/kerofis/stats")
@app.route("/kerofis/stats/")
def stats():
    return "API kerofis : stats"
    # TODO renvoyer plutôt une page HTML explicative des méthodes"""


# stats_municipality_type_of_place  -->  pour avoir les formes


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# /kerofis/municipalities
# -> return all municipalities

# /kerofis/municipalities/search/?insee={insee}
# /kerofis/municipalities/search/?name:br{name:br}
# /kerofis/municipalities/search/?name:fr{name:fr}
# -> return 0, 1 or more municipality


@app.route("/kerofis/municipalities")
@app.route("/kerofis/municipalities/")
def municipalities_index():
    # return a json response with the list of all the municipalities concerned in the database
    # datas provided by the stats_municipality table
    # insee | kumun | nb

    # return "API kerofis : stats : par commune : toutes les communes"

    try:
      # get a connection, if a connect cannot be made an exception will be raised here
      pgDB = psycopg2.connect(sConnPostgre)

      # pgDB.cursor will return a cursor object, you can use this cursor to perform queries
      pgCursor = pgDB.cursor()

      #-------------------------------------------------------------------------------
      # first : get count of municipality in the database

      pgCursor.execute("""SELECT COUNT(*) AS count FROM stats_municipality""")
      oneRecord = pgCursor.fetchone()
      NbOfMunicipalities = str(oneRecord[0])


      #-------------------------------------------------------------------------------
      # second : loop on all the municipalities

      # the query
      pgCursor.execute("""SELECT * FROM stats_municipality""")
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
        licence = licence,
        attribution_en = attribution_en,
        attribution_fr = attribution_fr,
        attribution_br = attribution_br,
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
      # error
      return jsonify(error = str(e)), 500



@app.route("/kerofis/municipalities/search/", methods=['GET'])
def municipalities_search():
    # search by  insee  OR  name_fr  OR name_br

    # get all arguments
    code_insee = request.args.get('insee', '')
    name_br = request.args.get('name:br', '')
    name_fr = request.args.get('name:fr', '')

    sSQL = ""

    if (code_insee != '') :
      # search by code insee
      # if lenght = 2 -> search by departement
      if len(code_insee) == 2 :
        sSQL = "SELECT * FROM stats_municipality  WHERE insee LIKE '" + code_insee + "%'"
        return municipalities_search_query(sSQL)
        pass
      # if lenght = 5 -> searching one municipality
      if len(code_insee) == 5 :
        sSQL = "SELECT * FROM stats_municipality  WHERE insee = '" + code_insee + "'"
        return municipalities_search_query(sSQL)
        pass
      # else : output error
      else :
        # error
        return jsonify(error = "code insee : bad argument"), 400
        pass
    
    if (name_br != '') :
      # search by breton name
      if len(name_br) < 3 :
        # error
        return jsonify(error = "name:br argument is too short"), 400
      else :
        sSQL = "SELECT * FROM stats_municipality  WHERE LOWER(name_br) LIKE LOWER('%" + name_br + "%')"
        return municipalities_search_query(sSQL)
        pass
    
    if (name_fr != '') :
      # search by french name
      if len(name_fr) < 3 :
        # error
        return jsonify(error = "name:fr argument is too short"), 400
      else :
        sSQL = "SELECT * FROM stats_municipality  WHERE LOWER(name_fr) LIKE LOWER('%" + name_fr + "%')"
        return municipalities_search_query(sSQL)
        pass

    # if nothing -> error 500
    return jsonify(error = "error in municipality search"), 500
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
        licence = licence,
        attribution_en = attribution_en,
        attribution_fr = attribution_fr,
        attribution_br = attribution_br,
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
      # error
      return jsonify(error = str(e)), 500
    
    #return sSQL






#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# /kerofis/search/?insee={insee}
# -> return all records for one municipality
# 
# /kerofis/search/?
#   insee={insee} [mandatory] : '12345' OR *
#   lang={br|fr} [mandatory] : langage of the name to request
#   name={name} [mandatory] : 'XXXX' OR *
#   type={type} [optionnal] : cf table stats_municipality_type_of_place
#   sortby={br_asc|br_desc|fr_asc|fr_desc} [optionnal] : sorting key
# 


@app.route("/kerofis/search/", methods=['GET'])
def kerofis_search():

    # get all arguments
    code_insee = request.args.get('insee', '')  # mandatory
    lang = request.args.get('lang', '')         # mandatory
    name = request.args.get('name', '')         # mandatory
    stype = request.args.get('type', '')        # optionnal
    sortby = request.args.get('sortby', '')     # optionnal -> default = requested langage + ascendant

    args = "args = code_insee:"+code_insee+" | lang:"+lang+" | name:"+name+" | type:"+stype

    # for say if the query args are welcomed
    control = False

    #
    # basic tests : insee
    if len(code_insee) == 1 :
      if code_insee == '*':
        # ok
        control = True
        pass
      else:
        # error
        control = False
        # return customized error message in JSON
        return jsonify(error = "bad code insee argument"), 400
    elif len(code_insee) == 5 :
      # test if integer TODO
      # ok
      control = True
      pass
    else:
      # error : too short
      control = False
      # return customized error message in JSON
      return jsonify(error = "bad code insee argument"), 400

    #
    # basic tests : lang
    if len(lang) == 2 :
      if (lang == "fr") or (lang == "br") :
        # ok
        control = True
        pass
      else :
        # error
        control = False
        # return customized error message in JSON
        return jsonify(error = "bad langage argument"), 400
    else :
      # error
      control = False
      # return customized error message in JSON
      return jsonify(error = "bad langage argument"), 400

    #
    # basic tests : name
    # first : trim spaces
    name = name.replace(" ","")
    # checks
    if (name == "*") and (code_insee == "*") :
      # not allowed to return all the database
      return jsonify(error = "not allowed to return all the database : supply insee or name argument"), 400

    if (name != "*") :
      if len(name) < 3 :
        # error
        control = False
        # return customized error message in JSON
        return jsonify(error = "name argument too short"), 400
      elif len(name) > 50 :
        # error
        control = False
        # return customized error message in JSON
        return jsonify(error = "name argument too long"), 400

    #
    # basic tests : type of objects queried
    # TODO
    if stype :
      control = False
      return jsonify(error = "type argument not yet managed"), 500

    #
    # basic tests : sort by
    if sortby :
      # test all the cases
      if (sortby == "fr_asc") or (sortby == "fr_desc") or (sortby == "br_asc") or (sortby == "br_desc") :
        control = True
        pass
      else :
        # error
        control = False
        # return customized error message in JSON
        return jsonify(error = "bad sortby argument"), 400
    else :
      # apply the queried langage + ascendant sort
      sortby = lang + "_asc"



    # test control, in case of…
    if control == False :
      # stop
      return jsonify(error = "something went wrong, check arguments"), 400
    else :
      # all is right, let's built the query
      sSQL = "SELECT niv, deiziad_degemer, insee, kumun, rummad, stumm_orin, stumm_dibab FROM kerofis WHERE"
      
      # code insee + name
      if (code_insee != "*") and (name != "*") : sSQL += " insee='" + str(code_insee) + "' AND"
      # code insee alone
      elif (code_insee != "*") and (name == "*") : sSQL += " insee='" + str(code_insee) + "'"


      # langage impacts column choice for the name request
      # comparison is done case insensitive
      # TODO : manage accents
      # first : define if query an entire municipality or not
      if (name != "*") : 
        if (lang == "fr") : sSQL += " LOWER(stumm_orin) LIKE '%" + name.lower() + "%'"
        elif (lang == "br") : sSQL += " LOWER(stumm_dibab) LIKE '%" + name.lower() + "%'"
      # no need else

      # type
      # TODO
      # exclude municipality record because we looking for way or POI
      sSQL += " AND rummad <> 'Kumun'"

      # sorting
      if (sortby == "fr_asc") : sSQL += " ORDER BY stumm_orin ASC"
      elif (sortby == "fr_desc") : sSQL += " ORDER BY stumm_orin DESC"
      elif (sortby == "br_asc") : sSQL += " ORDER BY stumm_dibab ASC"
      elif (sortby == "br_desc") : sSQL += " ORDER BY stumm_dibab DESC"

      # for test / debug
      #return jsonify(query = sSQL, lang = lang), 404

      # go to the query
      return kerofis_search_query(sSQL)
      #pass

    #args += " | sortby:"+sortby
    #return args + " | control = " + str(control) + "   FIN"
    pass



def kerofis_search_query(sql):

    # perform the query
    try:
      pgDB = psycopg2.connect(sConnPostgre)
      pgCursor = pgDB.cursor()

      pgCursor.execute(sql)
      records = pgCursor.fetchall()

      # declare array + counter
      json_array = []
      loop_counter = 0

      # loop
      for record in records:

        # store attributes from order of the database attributes
        niv = record[0]
        deiziad_degemer = record[1]
        insee = record[2]
        kumun = record[3]
        rummad = record[4]
        stumm_orin = record[5]
        stumm_dibab = record[6]

        # building the json
        json_str = "{'insee':'" + insee + "',"
        json_str += "'municipality':'" + kumun + "',"
        json_str += "'validation_date':'" + str(deiziad_degemer) + "',"
        json_str += "'id':'" + str(niv) + "',"
        json_str += "'type':'" + rummad + "',"
        json_str += "'name:br':'" + stumm_orin + "',"
        json_str += "'name:fr':'" + stumm_dibab + "}"
        json_array.append(json_str)
        loop_counter += 1

      # then return a beautiful json
      return jsonify(
        licence = licence,
        attribution_en = attribution_en,
        attribution_fr = attribution_fr,
        attribution_br = attribution_br,
        count = loop_counter,
        places = json_array
      )

      # closing cursor and connection to the database
      pgCursor.close()
      pgDB.close()
      pass

    except Exception, e:
      # out the error to the log
      track= get_current_traceback(skip=1, show_hidden_frames=True, ignore_system_exceptions=False)
      track.log()
      return jsonify(error = str(e)), 500
      #raise e





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

