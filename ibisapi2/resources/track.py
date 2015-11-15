import sqlalchemy.sql
import ibisapi2.api.db_tables

class List(object):
    @staticmethod
    def on_get(req, resp):
        """Handles GET requests"""
        tracks = ibisapi2.db_tables['tracks']
        ibisapi2.db_tables['foo'] = 'bar'

        # default 25, admins are allowed to override
        track_limit = 25
        if req.context['auth'] > 10:
            track_limit = int(req.context['req']['num'])

        track_start = 0
        if req.context['req']['start'] is not None:
            track_start = int(req.context['req']['start'])

        where_condition = tracks.c.public == True
        if req.context['tracks'] is not None:
            where_condition = sqlalchemy.sql.or_((tracks.c.public == True), (tracks.c.id.in_(req.context['tracks'])))

        s = sqlalchemy.sql.select([tracks]).where(where_condition).limit(track_limit).offset(track_start).order_by(
            tracks.c.id)
        # result = db_connection.ex

        info = {
            'author': 'iBis Project Team',
            'info': 'iBis API version 2',
            'version': "2.0.0"
        }
        req.context['resp'] = info
