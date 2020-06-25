import os
import sys

from flask import Flask
from tinydb import TinyDB, Query
from flask_restful import reqparse
from flask_restful import Resource, Api

abs_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(abs_dir, '..'))
from apis.gmail import Gmail
from utils import grouped

app = Flask(__name__)
api = Api(app)

class EventLister(Resource):
    def __init__(self):
        self.types = ['keyword', 'url']
        self.apis = []
        self.apis.append(Gmail())

    def parsing(self, parser, tp, lens):
        for idx in range(lens):
            parser.add_argument('link{}'.format(idx), type=str)

        args = parser.parse_args()
        links = {'links' : {}}
        for k, v in args.items():
            if not k.startswith('link'):
                continue
            link, value = v.split('\n')[0], v.split('\n')[1:]
            links['links'][link] = {t: p for t, p in grouped(value, 2)}
        return links

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('type', type=str)
            parser.add_argument('lens', type=int)
            parser.add_argument('name', type=str)

            args = parser.parse_args()

            if args['type'] not in self.types:
                return {'error': 'none type'}

            datas = self.parsing(parser, args['type'], args['lens']) 
            datas.update(args)
            print(datas)
            for api in self.apis:
                api.parsing(datas)
            
        except Exception as e:
            print(e)
            return {'error' : str(e)}
    

api.add_resource(EventLister, '/gateway')

if __name__ == "__main__":
    app.run(debug=True)
