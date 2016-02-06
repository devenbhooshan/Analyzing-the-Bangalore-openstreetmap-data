import re
INPUT_FILE = 'bengaluru_india.osm'
TAG = 'tag'
KEY = 'k'
VALUE = 'v'


OSM_POST_CODE_KEY = 'addr:postcode'
OSM_CITY_KEY = 'addr:city'
OSM_HOUSE_NUMBER_KEY ='addr:housenumber'
MONGO_HOUSE_NUMBER_KEY ='housenumber'
OSM_HIGHWAY_KEY = 'highway'
MONGO_POST_CODE_KEY = 'postcode'
MONGO_CITY_KEY = 'city'
OSM_USER_KEY = 'user'
OSM_STREET_KEY = 'addr:street'
MONGO_STREET_KEY = 'street'
REGULAR_EXPRESSION_BANGALORE_AT_THE_END = re.compile('[,\s]*bangalore[,\s]*$')
REGULAR_EXPRESSION_PROBLEM_CHAR = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
REGULAR_EXPRESSION_STREET_TYPE = re.compile(r'\b\S+\.?$', re.IGNORECASE)