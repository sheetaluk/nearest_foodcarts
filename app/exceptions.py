"""
Exception class for input validation.
"""
class FoodcartsInputException(Exception):
  def __init__(self, value):
    self.value = value

"""
Exception class for riak read exception.
"""
class FoodcartsRiakReadException(Exception):
  def __init__(self, value):
    self.value = value

"""
Exception class for riak write exception.
"""
class FoodcartsRiakWriteException(Exception):
  def __init__(self, value):
    self.value = value
