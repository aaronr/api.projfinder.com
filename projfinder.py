# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g

from projfinderapi.web import index, documentation
from projfinderapi.api import api_landing, reproject, projfinder

app = Flask(__name__)
app.config.from_pyfile('default.cfg')
app.config.from_pyfile('local.cfg')

# URLs
app.add_url_rule('/', 'index', index)
app.add_url_rule('/documentation', 'documentation', documentation)
app.add_url_rule('/api', 'api', api_landing)
app.add_url_rule('/api/reproject', 'reproject', reproject, methods=['GET', 'POST'])
app.add_url_rule('/api/projfinder', 'projfinder', projfinder, methods=['GET', 'POST'])
  
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
