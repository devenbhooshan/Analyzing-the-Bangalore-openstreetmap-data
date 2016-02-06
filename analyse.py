"""
Helper file used while doing some analytics on top of data
"""
import pymongo


def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [
        {'$match': {'node_refs.591':{'$exists': True}}},
        {'$unwind' : '$node_refs'},
        {'$project' : {'node_refs': 1}}
    ]
    return pipeline


def aggregate(db, pipeline):
    return [doc for doc in db.tags.aggregate(pipeline)]


if __name__ == '__main__':
    # The following statements will be used to test your code by the grader.
    # Any modifications to the code past this point will not be reflected by
    # the Test Run.
    db = get_db('maps')

    '''
    Finding average distance between school and nearest hospital
    all schools ->

    sum = 0
    schools = db.tags.find({'amenity': 'school', 'pos': {'$exists': True}})
    school_count = schools.count()
    for school in schools:
        hospitals = db.tags.find({'amenity': 'hospital', 'pos' : {'$near': { '$geometry' : { 'type': "Point" , 'coordinates' : school['pos']}, '$maxDistance': 500}}})

        sum += hospitals.count()
        if hospitals.count() == 0:
            print(school['id'])
    print 'total', sum
    print 'average', sum/school_count
        # for hospital in hospitals:
        #     print hospital
    '''

    '''
    # finding most common amenity in 2km radius of any hospital
    hospitals = db.tags.find({'amenity': 'hospital', 'pos': {'$exists': True}})
    from collections import defaultdict
    amenities = defaultdict(int)
    for hospital in hospitals:
        pos = hospital['pos']
        data = db.tags.find({'pos' : {'$near': { '$geometry' : { 'type': "Point" , 'coordinates' : pos}, '$maxDistance': 2000}}})

        for d in data:
            if 'amenity' in d:
                print d['amenity']
                amenities[d['amenity']] += 1

    print amenities
    '''

    # data = db.tags.aggregate([{'$group': {'_id': '$created.user', 'adds' : {'$sum':1}}}, {'$match': {'adds': 1}}])
    # i =0
    # for d in data:
    #     i += 1
    #
    # print(i)
    # print(pymongo.GEO2D)
    # pipeline = make_pipeline()
    # result = aggregate(db, pipeline)
    # nodes = [data['node_refs'] for data in result]
    #
    # print db.tags.create_index([('pos', pymongo.GEO2D)])
    # for data in db.tags.aggregate([{'$match': {'id': {'$in': nodes}}}, {'$group' : {'_id': '$created.user'}}]):
    #     print data
    # for data in db.tags.aggregate([{'$match': {'id': {'$in': nodes}}}, {'$group' : {'_id': '$name'}}]):
    #     print data

    # import pprint
    # pprint.pprint(result)