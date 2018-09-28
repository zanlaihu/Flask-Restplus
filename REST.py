import json


import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

import time
import requests
import operator

from pymongo import MongoClient



###################################################


app = Flask(__name__)
api = Api(app,
          default="Worldbank",  # Default namespace
          title="Worldbank Dataset",  # Documentation Title
          description="This is assignment2 of COMP9321.")  # Documentation Description

bank_model = api.model('Bank', {
    'indicator_id': fields.String,
})

parser = reqparse.RequestParser()
parser.add_argument('order', choices=list(column for column in bank_model.keys()))



@api.route('/collections')
class BooksList(Resource):
    @api.response(201, 'Created')
    @api.response(200, 'OK')
    @api.response(404, 'Error')
    @api.doc(description="This is question 1: Import a collection from the data service")
    @api.expect(bank_model, validate=True)
    def post(self):
        # Question1
        bank = request.json
        indicator_id = bank['indicator_id']

        collection_id = indicator_id + '_collection'

        # check if the given identifier does not exist
        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]

        cidlist = db.list_collection_names()
        if collection_id in cidlist:
            return {"location": "/collections/{}".format(collection_id)}, 200


        world_bank_url1 = f'http://api.worldbank.org/v2/countries/all/indicators/{indicator_id}?date=2012:2017&format=json&page=1'
        world_bank_url2 = f'http://api.worldbank.org/v2/countries/all/indicators/{indicator_id}?date=2012:2017&format=json&page=2'

        # 3.Make sure this indicator is valid.
        try:
            r = requests.get(world_bank_url1)
            json_r = r.json()
            parsed_resp = json_r[1]

            r2 = requests.get(world_bank_url2)
            json_r2 = r2.json()
            parsed_resp2 = json_r2[1]
        except IndexError:
            return "Error", 404


        # Create formatted collections
        format_col = {}
        format_col['collection_id'] = collection_id  # problem with collection_id, how to create it automatically
        format_col['indicator'] = indicator_id
        format_col['indicator_value'] = parsed_resp[0]['indicator']['value']
        format_col['creation_time'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time()))
        format_col['entries'] = []
        for i in parsed_resp:
            newdic = {}
            newdic['country'] = i['country']['value']
            newdic['date'] = i['date']
            newdic['value'] = i['value']
            format_col['entries'].append(newdic)
        for i in parsed_resp2:
            newdic = {}
            newdic['country'] = i['country']['value']
            newdic['date'] = i['date']
            newdic['value'] = i['value']
            format_col['entries'].append(newdic)

        # 5.Store formatted collections in the mlab.
        c = db[collection_id]
        c.insert_many([format_col])

        # 6.Return location, collection_id, creation_time, indicator
        return {"location": "/collections/{}".format(collection_id),
                "collection_id": "{}".format(collection_id),
                "creation_time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time())),
                "indicator": "{}".format(indicator_id)}, 201

    @api.response(200, 'OK')
    @api.doc(description="This is question 3: Retrieve the list of available collections")
    def get(self):

        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]

        cidlist = db.list_collection_names()
        dontlike = ['objectlabs-system.admin.collections', 'system.indexes', 'objectlabs-system']
        cidlist2 = []
        for i in cidlist:
            if i not in dontlike:
                cidlist2.append(i)

        l = []

        for collection_id in cidlist2:
            c = db[collection_id]
            list1 = list(c.find())
            list2 = list1[0]
            cvalue = list2['creation_time']
            ivalue = list2['indicator']

            newdic = {}
            newdic['location'] = "/collections/{}".format(collection_id)
            newdic['collection_id'] = "{}".format(collection_id)
            newdic['creation_time'] = cvalue
            newdic['indicator'] = ivalue

            l.append(newdic)
        return l, 200


@api.route('/collections/<string:id>')
@api.param('id', 'The collection identifier')
class Books(Resource):
    @api.response(404, 'Collection was not found.')
    @api.response(200, 'OK')
    @api.doc(description="This is question 2: Deleting a collection with the data service")
    def delete(self, id):
        collection_id = id

        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]

        cidlist = db.list_collection_names()
        if collection_id not in cidlist:
            return "Error, there is no {} in this database.".format(collection_id), 404

        c = db[collection_id]
        c.drop()
        return {"message": "Collection = {} is removed.".format(id)}, 200

    @api.response(404, 'Collection was not found')
    @api.response(200, 'Successful')
    @api.doc(description="This is question 4: Retrieve a collection by its collection_id")
    def get(self, id):
        collection_id = id

        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]

        try:
            c = db[collection_id]
            list1 = list(c.find())
            list2 = list1[0]
            del list2['_id']
            return list2, 200
        except IndexError:
            return "Collection was not found.", 404


@api.route('/collections/<string:id>/<string:year>/<string:country>')
@api.param('id', 'The collection identifier')
@api.param('year', 'The year')
@api.param('country', 'The country')
class Booksyear(Resource):
    @api.response(404, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="This is question 5: Retrieve a collection by its collection_id")
    def get(self, id, year, country):
        collection_id = id
        collection_year = year
        collection_country = country


        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]

        try:
            c = db[collection_id]
            list1 = list(c.find())
            list2 = list1[0]
            del list2['_id']
        except IndexError:
            return "Collection was not found.", 404

        # indicator_id = list2['indicator']
        indicator_value = list2['indicator_value']

        newdic = {}
        newdic['collection_id'] = collection_id
        newdic['indicator'] = indicator_value
        newdic['country'] = collection_country
        newdic['year'] = collection_year


        entrylist = list2['entries']

        for i in entrylist:
            if i['country'] == collection_country and i['date'] == collection_year:
                newdic['value'] = i['value']
                return newdic, 200

        return "No data for the year and country.", 404

parser2 = reqparse.RequestParser()
parser2.add_argument('query')
@api.route('/collections/<string:id>/<string:year>')
@api.param('id', 'The collection identifier')
@api.param('year', 'The year')
class Booksquery(Resource):
    @api.response(404, 'Error')
    @api.response(200, 'OK')
    @api.expect(parser2)
    @api.doc(description="This is question 6: Retrieve top/bottom economic indicator values for a given year")
    def get(self, id, year):
        query = parser2.parse_args().get('query')

        collection_id = id
        collection_year = year

        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]

        try:
            c = db[collection_id]
            list1 = list(c.find())
            list2 = list1[0]
            del list2['_id']
        except IndexError:
            return "Collection was not found.", 404

        del list2['collection_id']
        del list2['creation_time']

        en_list = list2['entries']
        # filter year
        year_list = []
        for i in en_list:
            if i['date'] == collection_year:
                year_list.append(i)

        if year_list == []:
            return "invalid Year", 404

        # sort by value
        year_list.sort(key=operator.itemgetter('value'), reverse=True)

        # choose top num
        cho_list = []
        if 'top' in query:
            try:
                numquery = int(query[3:])
                for i in range(0, numquery):
                    cho_list.append(year_list[i])
            except IndexError:
                return "query number our of range, enter a smaller number", 404
        if 'bottom' in query:
            try:
                numquery = int('-' + query[6:])
                for i in range(-1, numquery - 1, -1):
                    cho_list.append(year_list[i])
            except IndexError:
                return "query number out of range, enter a smaller number", 404

        if 'top' not in query and 'bottom' not in query:
            return "Wrong query", 404

        list2['entries'] = cho_list
        return list2, 200



if __name__ == '__main__':
    db_name = 'k_database'
    mongo_port = 25912
    mongo_host = 'mongodb://Zanlai:hzl13579@ds125912.mlab.com:25912/k_database'

    # run the application
    app.run(debug=True)
