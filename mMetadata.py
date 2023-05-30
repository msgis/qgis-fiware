# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject
from qgis.core import QgsProject


class Metadata(QObject):
    def __init__(self, app, parent=None):
        super(Metadata, self).__init__(parent)

        self.app = app
        self.iface = app.iface
        self.info = app.info
        self.debug = app.debug
        self.plugin_dir = app.plugin_dir
        self.metadata = self
        self.prj = QgsProject.instance()

    def check(self):
        # check metadata
        try:
            self.layer_hydrant()
            return True
        except:
            pass

    def layer_hydrant(self):
        return self.prj.mapLayersByName('Hydrant')[0]

    def layer_schwimmbad(self):
        return self.prj.mapLayersByName('Schwimmbad')[0]

    def layer_trinkbrunnen(self):
        return self.prj.mapLayersByName('Trinkbrunnen')[0]

    def req_user(self):
        return ''

    def req_password(self):
        return ''

    def req_limit(self):
        return 200

    def req_trigger(self):
        return 0.05  # sec

    def req_max_feat(self):
        return 15000

    def req_types(self):
        return 'https://fiwaredev.msgis.net/ngsi-ld/v1/types'

    def req_get_data(self):
        return 'https://fiwaredev.msgis.net/ngsi-ld/v1/entities?type={0}&offset={1}&limit={2}'
