"""
Number of node and way tags : 34,67,549
number of nodes

('node', 2818712),
 ('nd', 3498457),
 ('bounds', 1),
 ('member', 4604),
 ('tag', 758108),
 ('relation', 894),
 ('way', 648837),
 ('osm', 1)

Problems
Post code of
 1 non numeric postal code
 2 560 090 - > 560090
 3 79 -> 560079


 <osm version="0.6" generator="osmconvert 0.7T" timestamp="2016-01-30T00:31:01Z">
	<bounds minlat="12.75" minlon="77.35" maxlat="13.23" maxlon="77.85"/>
	[12.75,77.35]
	[77.35, 12.75]
"""

import xml.etree.cElementTree as et
from pprint import pprint
import constants
from collections import defaultdict
import json
import codecs

check_data = defaultdict(int)
mapping = {"Rd.": "Road","Rd": "Road"}


def correct_postal_code(postcode):
    postcode = "".join(postcode.split(" "))
    if unicode(postcode).isnumeric() and len(postcode) == 6:
        return postcode
    else:
        return None


def update_street_name(name):
    m = constants.REGULAR_EXPRESSION_STREET_TYPE.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping:
            return constants.REGULAR_EXPRESSION_STREET_TYPE.sub(mapping[street_type],name)

    return name


def correct_street(street):
    street = " ".join([st.title() for st in street.split(" ")])
    result = constants.REGULAR_EXPRESSION_BANGALORE_AT_THE_END.search(street.lower())
    if result is not None:
        street = street[0:result.start()]

    return update_street_name(street)


def clean_element(element):
    node = {}
    parent_attrib = element.attrib

    try:
        node[constants.OSM_USER_KEY] = parent_attrib[constants.OSM_USER_KEY]
    except:
        pass

    for child in element.iter(constants.TAG):
        attributes = child.attrib

        if attributes[constants.KEY] == constants.OSM_POST_CODE_KEY:
            corrected_postal_code = correct_postal_code(attributes[constants.VALUE])
            if corrected_postal_code is not None:
                node[constants.MONGO_POST_CODE_KEY] = corrected_postal_code
            else:
                return None
        elif attributes[constants.KEY] == constants.OSM_STREET_KEY:

            street = correct_street(attributes[constants.VALUE])
            if street:
                node[constants.MONGO_STREET_KEY] = street
            else:
                return None

        elif attributes[constants.KEY] == constants.OSM_HIGHWAY_KEY:
            node[attributes[constants.KEY]] = attributes[constants.VALUE]



    #print node
    return node


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    node['created'] = {}
    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag
        attributes = element.attrib
        node['id'] = attributes['id']
        tag_keys = ['addr:housenumber', 'addr:street', 'addr:postcode' ]

        if 'lat' in attributes:
            node['pos'] = [float(attributes['lat']) ,float(attributes['lon']) ]
        if 'visible' in attributes:
            node['visible'] = attributes['visible']

        for cr in CREATED:
            node['created'][cr] = attributes[cr]
        for el in element.iter("tag"):

            if el.attrib[constants.KEY] in tag_keys:
                if 'address' not in node:
                    node['address'] = {}
                if el.attrib[constants.KEY] == constants.OSM_POST_CODE_KEY:
                    corrected_postal_code = correct_postal_code(el.attrib[constants.VALUE])
                    if corrected_postal_code is not None:
                        node['address'][constants.MONGO_POST_CODE_KEY] = corrected_postal_code
                    else:
                        return None
                elif el.attrib[constants.KEY] == constants.OSM_STREET_KEY:
                    street = correct_street(el.attrib[constants.VALUE])
                    if street:
                        node['address'][constants.MONGO_STREET_KEY] = street
                    else:
                        return None
            elif 'addr' in el.attrib[constants.KEY]:
                pass
            else:
                node[el.attrib[constants.KEY]] = el.attrib[constants.VALUE]
        for el in element.iter("nd"):
            if 'node_refs' not in node:
                node['node_refs'] = []
            node['node_refs'].append(el.attrib['ref'])
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
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
