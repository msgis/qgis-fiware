# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, QObject
from qgis.PyQt.QtWidgets import QDockWidget, QAction, QWidgetAction, QToolBar, QLabel,QWidget,QHBoxLayout

from qgis.core import QgsProject

from .mMetadata import Metadata

import os
import sys


class App(QObject):
    def __init__(self, plugin):
        super(App, self).__init__()
        self.setObjectName(__name__)
        self.app = self
        self.iface = plugin.iface
        self.info = plugin.info
        self.plugin = plugin
        self.plugin_name = plugin.plugin_name
        self.plugin_dir = plugin.plugin_dir
        self.debug = plugin.debug
        self.metadata = Metadata(self)
        self.started = False
        try:
            if self.metadata.check() and not self.started:
                self.started = True
                tb = self.iface.mainWindow().findChild(QToolBar, 'mFWtoolbar')
                if tb is None:
                    tb = QToolBar()
                    tb.setObjectName('mFWtoolbar')
                    tb.setWindowTitle(u'Update layers')
                    tb.setAllowedAreas(Qt.BottomToolBarArea | Qt.TopToolBarArea)
                    self.iface.addToolBar(tb)
                else:
                    tb.clear()
                    tb.setHidden(False)
                self.wact=FmActionLayerUpdate(self,tb)
                tb.addAction(self.wact)
                if self.debug:
                    self.info.log("Main:init")
        except Exception as e:
            self.info.err(e)


class FmActionLayerUpdate(QWidgetAction):
    def __init__(self, app, parent=None):
        super(FmActionLayerUpdate, self).__init__(parent)
        self.setObjectName('mFwWidgetLayerUpdate')
        self.app = app

    def createWidget(self, parent):
        from .mWidgetLayerUpdate import WidgetLayerUpdate
        return WidgetLayerUpdate(self.app, parent)
