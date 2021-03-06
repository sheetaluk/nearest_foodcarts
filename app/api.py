import json

from app import app
from flask import request
from flask.ext.cors import cross_origin

import foodcarts

"""
Function to get nearest foodcarts within a radius.

Param user_lat string latitude of user.
Param user_long string longitude of user.

Returns Json list of foodcart objects.
"""
@app.route('/api/v1.0/nearest_foodcarts', methods=['GET'])
@cross_origin(origins="*")
def get_nearest_foodcarts():
  lat = float(request.args.get('user_lat'))
  long = float(request.args.get('user_long'))

  return foodcarts.get_foodcarts_within_radius(
    lat, long, app.config['radius'])
