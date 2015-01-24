import json

from app import app
from flask import request

import foodcarts

"""
Function to get nearest foodcarts within a radius.

Param user_lat string latitude of user.
Param user_long string longitude of user.

Returns Json list of foodcart objects.
"""
@app.route('/api/v1.0/nearest_foodcarts', methods=['GET'])
def get_nearest_foodcarts():
  #lat = float(request.args.get('user_lat'))
  #long = float(request.args.get('user_long'))

  lat = 37.776775
  long = -122.416791

  if not lat or not long:
    app.logger.error(
      "get_nearest_foodcarts: lat and long required")
    raise Exception("lat and long required")

  return foodcarts.get_foodcarts_within_radius(
    lat, long, app.config['radius'])
