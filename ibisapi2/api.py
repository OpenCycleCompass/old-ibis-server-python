import falcon
from wsgiref import simple_server

import ibisapi2.resources as resources


api = falcon.API()
api.add_route('/info', resources.info.Info())


# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
