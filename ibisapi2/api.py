import falcon
from wsgiref import simple_server

import ibisapi2.resources as resources
import ibisapi2.middleware as middleware



api = falcon.API(
    media_type='application/json; charset=utf-8',
    middleware=[middleware.JSONTranslator()]
)


api.add_route('/info', resources.info.Info())


# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
