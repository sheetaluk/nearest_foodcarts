import app

class Datastore:
  def __init__(self, riak_client):
    self._riak_client = riak_client

  def get_foodcarts_bucket(self):
    return self._riak_client.bucket(
      app.app.config['riak_foodcarts_bucket'])

  def get_foodcarts_for_geohash_bucket(self):
    return self._riak_client.bucket(
      app.app.config['riak_foodcarts_for_geohash_bucket'])
