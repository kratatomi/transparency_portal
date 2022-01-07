from flask import render_template
from app import app
import json

@app.errorhandler(404)
def not_found_error(error):
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    return render_template('404.html', sidx_stats=sidx_stats), 404