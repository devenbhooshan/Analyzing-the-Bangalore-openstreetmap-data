"""
This file finds the problem in the map data and then cleans it.

The data is a grid of following parameters

min lat long = [12.75,77.35]
max lat long = [13.23, 77.85]

"""

import xml.etree.cElementTree as et
from pprint import pprint
import constants
from collections import defaultdict
import json
import codecs

# Only these high level tags are put in the document
VALID_TAGS = ['way', 'node']
# Transformation mapping used while transforming the street names
MAPPING = {"Rd.": "Road","Rd": "Road"}
# Keys used to create the 'created' sub document
CREATED_KEYS = ["version", "changeset", "timestamp", "user", "uid"]
# Keys to be check for 'address' sub document
TAG_XML_ADDRESS_KEYS = ['addr:housenumber', 'addr:street', 'addr:postcode' ]


# This function takes the raw postal code and returns the corrected one. If it is not able to correct it ,
#  it returns None
def correct_postal_code(postcode):
    postcode = "".join(postcode.split(" "))
    if unicode(postcode).isnumeric() and len(postcode) == 6:
        return postcode
    else:
        return None


# This function takes the raw street code and returns the corrected one. If it is not able to correct it ,
#  it returns None
def correct_street(street):

    # removes any spaces between the postalcodes
    street = " ".join([st.title() for st in street.split(" ")])

    # search for 'bangalore' city name at the end. It also search for trailing commas and spaces.
    result = constants.REGULAR_EXPRESSION_BANGALORE_AT_THE_END.search(street.lower())
    if result:
        # if 'bangalore' is found remove it
        street = street[0:result.start()]

    # search for street type
    result = constants.REGULAR_EXPRESSION_STREET_TYPE.search(street)
    if result is not None:
        street_type = result.group()
        if street_type in MAPPING:
            return constants.REGULAR_EXPRESSION_STREET_TYPE.sub(MAPPING[street_type],street)

    return street


# this function shapes/corrects the element of presents as the xml tags. If it is not able to correct
# the element, it returns None

def shape_element(element):
    node = dict()
    node['created'] = {}
    # only uses 'node' or 'way' xml tags
    if element.tag in VALID_TAGS:
        node['type'] = element.tag

        # element.attrib gives all the attributes of the element
        attributes = element.attrib
        node['id'] = attributes['id']

        # puts lat long as an list inside 'pos' doc
        if 'lat' in attributes:
            # flat(attributes['lat']) type casts attributes['lat'] to 'float'
            node['pos'] = [float(attributes['lat']), float(attributes['lon'])]

        if 'visible' in attributes:
            node['visible'] = attributes['visible']

        # iterates through all the CREATED_KEY and puts key value pair in the node
        for cr in CREATED_KEYS:
            node['created'][cr] = attributes[cr]

        # iterate through all the 'tag' sub element
        for el in element.iter("tag"):
            # Allow 'tag' with keys like postal and
            if el.attrib[constants.KEY] in TAG_XML_ADDRESS_KEYS:
                # creates address sub document if it not there
                if 'address' not in node:
                    node['address'] = {}
                # puts corrected post code. if not able to correct it, returns None
                if el.attrib[constants.KEY] == constants.OSM_POST_CODE_KEY:
                    corrected_postal_code = correct_postal_code(el.attrib[constants.VALUE])
                    if corrected_postal_code is not None:
                        node['address'][constants.MONGO_POST_CODE_KEY] = corrected_postal_code
                    else:
                        return None
                # puts corrected street. if not able to correct it, returns None
                elif el.attrib[constants.KEY] == constants.OSM_STREET_KEY:
                    corrected_street = correct_street(el.attrib[constants.VALUE])
                    if corrected_street:
                        node['address'][constants.MONGO_STREET_KEY] = corrected_street
                    else:
                        return None
                # puts house number.
                elif el.attrib[constants.KEY] == constants.OSM_HOUSE_NUMBER_KEY:
                    node['address'][constants.MONGO_HOUSE_NUMBER_KEY] = el.attrib[constants.VALUE]

            # Ignore all other 'tag' with 'addr' keys
            elif 'addr' in el.attrib[constants.KEY]:
                pass
            else:
                node[el.attrib[constants.KEY]] = el.attrib[constants.VALUE]
        # put all the node ref in 'node_refs' subdocument
        for el in element.iter("nd"):
            if 'node_refs' not in node:
                node['node_refs'] = []
            node['node_refs'].append(el.attrib['ref'])
        return node
    else:
        return None


def process_map(file_in, pretty=False):

    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in et.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


if __name__ == '__main__':
    process_map(constants.INPUT_FILE)
