class Info(object):
    @staticmethod
    def on_get(req, resp):
        """Handles GET requests"""
        info = {
            'author': 'iBis Project Team',
            'info': 'iBis API version 2',
            'version': "2.0.0"
        }
        req.context['resp'] = info
