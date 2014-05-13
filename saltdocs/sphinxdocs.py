#!/usr/bin/env python
# coding: utf-8
'''
CherryPy server configuration to serve SaltStack documentation

Development: add /etc/hosts entries for a given domain; run::

    ./sphinxdocs.py

Production: run::

    cherryd -e production -d \\
        -c /path/to/config.ini \\
        -p /var/run/sphinxdocs.pid \\
        sphinxdocs.py
'''
#pylint: disable=W0142
import cherrypy

class SphinxDocs(object):
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/en/latest/')

    @cherrypy.expose
    def r(self):
        '''
        Short-URL redirects to Sphinx index entries
        '''
        raise cherrypy.HTTPRedirect('/the/url')

class Redirect(object):
    def __init__(self, url_map):
        self.url_map = url_map

    @cherrypy.expose
    def default(self, path=None):
        url = self.url_map.get(path) if path else self.url_map.get('index')

        if not url:
            raise cherrypy.NotFound()

        raise cherrypy.HTTPRedirect(url)

if __name__ == '__main__':
    cherrypy.config.update('sphinxdocs.ini')

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.VirtualHost(
                **cherrypy.config.get('vhost_urls', {})),
        },
    }

    site_paths = {
        'saltdocs': SphinxDocs(),
        'raetdocs': SphinxDocs(),
        'bootstrap': Redirect(cherrypy.config.get('bootstrap_urls', {})),
    }

    Root = type('Root', (object,), site_paths)
    app = cherrypy.tree.mount(Root(), '/', conf)
    app.merge('sphinxdocs.ini')

    if cherrypy.config.get('server.user'):
        cherrypy.process.plugins.DropPrivileges(cherrypy.engine,
            umask=022,
            uid=cherrypy.config.get('server.user'),
            gid=cherrypy.config.get('server.group'),
        ).subscribe()

    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
