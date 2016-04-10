#!usr/local/bin/python
# coding: utf-8 


from flask import Flask
from flask import render_template


app = Flask(__name__)



@app.route("/kerofis/")
def index():
    return "API kerofis : index"


@app.route("/kerofis/infos")
def infos():
    #return "API kerofis : infos"

    return render_template('kerofis/infos.json', date_last_import='2016-02-09')


@app.route("/kerofis/stats")
def stats():
    return "API kerofis : stats"


@app.route("/kerofis/search/")
def search():
    return "API kerofis : search"






if __name__ == "__main__":
    app.debug = True
    app.run()

