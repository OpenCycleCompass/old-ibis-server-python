from wsgiref import simple_server

import falcon

import middleware
import database.helper
import resources.info
import resources.track


api = falcon.API(
    media_type='application/json; charset=utf-8',
    middleware=[middleware.JSONTranslator()]
)

db_engine = database.helper.create_engine('postgres', '132456', 'ibis')
db_tables = database.helper.create_tables()

api.add_route('/info', resources.info.Info())
api.add_route('/track/list', resources.track.List())

# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
