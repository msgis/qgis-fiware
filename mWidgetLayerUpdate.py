# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt, QStandardPaths, QTimer
from qgis.PyQt.QtWidgets import QApplication, QWidget, QAction, QSizePolicy, QProgressDialog

from qgis.PyQt import uic

from qgis.core import QgsProject, QgsGeometry, QgsVectorLayerUtils

import os
import requests
import time
import json
from osgeo import ogr


class WidgetLayerUpdate(QWidget):
    def __init__(self, app, parent=None):
        super(WidgetLayerUpdate, self).__init__(parent)
        # QWidgetAction.__init__(self,parent)
        self.app = app
        self.debug = self.app.debug
        self.info = self.app.info
        self.iface = self.app.iface
        self.canvas = self.iface.mapCanvas()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.prj = QgsProject.instance()
        self.metadata = self.app.metadata
        try:
            uic.loadUi(os.path.join(os.path.dirname(__file__), 'widgetLayerUpdate.ui'), self)
            self.cboLayer = self.cboLayer
            self.btnGetData = self.btnGetData
            # init
            res = requests.get(self.metadata.req_types(), auth=(self.metadata.req_user, self.metadata.req_password))
            if res.status_code == 200:
                dic = res.json()
                typeList = dic['typeList']
                for _type in typeList:
                    layers = self.prj.mapLayersByName(_type)
                    if layers:
                        self.cboLayer.addItem(_type, layers[0])
            self.btnGetData.setEnabled(self.cboLayer.count())
            # signals
            self.btnGetData.clicked.connect(self.get_data)
        except Exception as e:
            self.info.err(e)

    def get_data(self):
        try:
            if self.debug:
                self.info.err(None, 'get_data')
            iface = self.iface
            offset = 0
            features = []
            req_max_feat = self.metadata.req_max_feat()
            limit = self.metadata.req_limit()
            _type = self.cboLayer.currentText()
            layer = self.cboLayer.currentData()
            req_trigger = self.metadata.req_trigger()
            req = self.metadata.req_get_data().format(_type, offset, limit)
            if self.debug:
                self.info.err(None, req)
            res = requests.get(req, auth=(self.metadata.req_user(), self.metadata.req_password()))
            # dialog
            pd = QProgressDialog(self.iface.mainWindow())
            pd.setWindowFlag(Qt.FramelessWindowHint)
            pd.setWindowModality(Qt.WindowModal)
            pd.setWindowTitle('Update Layer: {0}'.format(_type))
            pd.setMinimum(0)
            pd.setMaximum(req_max_feat)
            pd.setLabelText('Geladene features...')
            pd.setAutoClose(False)
            pd.show()
            QApplication.processEvents()
            while res.status_code == 200:
                j = res.json()
                if len(j):
                    pd.setValue(offset)
                    for enty in j:
                        geojson = enty['location']['value']
                        if self.debug:
                            self.info.err(None, geojson)
                        string = json.dumps(geojson)
                        geom = ogr.CreateGeometryFromJson(string)
                        geom = QgsGeometry.fromWkt(geom.ExportToWkt())
                        feat = QgsVectorLayerUtils.createFeature(layer)
                        feat.setGeometry(geom)
                        features.append(feat)
                else:
                    break
                if req_trigger > 0:
                    time.sleep(req_trigger)
                offset = offset + limit
                if offset >= req_max_feat:
                    break
                req = self.metadata.req_get_data().format(_type, offset, limit)
                if self.debug:
                    self.info.err(None, req)
                if pd.wasCanceled():
                    break
                res = requests.get(req, auth=(self.metadata.req_user(), self.metadata.req_password()))

            if not pd.wasCanceled():
                layer.dataProvider().truncate()
                layer.dataProvider().addFeatures(features)
                layer.dataProvider().reloadData()
                layer.updateExtents()
                iface.layerTreeView().refreshLayerSymbology(layer.id())
                if iface.mapCanvas().isCachingEnabled():
                    layer.triggerRepaint()
                else:
                    iface.mapCanvas().refresh()
        except Exception as e:
            self.info.err(e)
        finally:
            pd.cancel()
