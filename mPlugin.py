# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication

from .mInfo import Info
from .mMain import App

import os

plugin_name = 'Fiware'
plugin_objectName = 'mFW'


class plugin(QObject):

    def __init__(self, iface):
        super(plugin, self).__init__()

        self.setObjectName(plugin_objectName)
        self.plugin_name = plugin_name
        self.plugin_dir = os.path.dirname(__file__)
        self.plugin_actions = []
        self.first_start = True
        # qgis interface
        self.iface = iface
        # app info
        self.info = Info(self)
        self.app = None
        # debug ?
        path = os.path.join(self.plugin_dir, 'log')
        self.debug = os.path.exists(path)
        if self.debug:
            self.info.log(plugin_name, "debug:", self.debug)

        # initialize locale
        locale = QgsApplication.locale()
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'mPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '3.0.0':
                QCoreApplication.installTranslator(self.translator)
        # signals
        self.iface.projectRead.connect(self.project_read)
        # start
        self.run()

    def tr(self, message):
        return QCoreApplication.translate('plugin', message)

    def add_action(
            self,
            text,
            objname,
            callback,
            icon_path=None,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=None,
            whats_this=None,
            parent=None):
        try:
            action = QAction(text)
            icon = QIcon()
            if isinstance(icon_path, QIcon):
                icon = icon_path
            else:
                if icon_path and os.path.isfile(icon_path):
                    icon = QIcon(icon_path)
                    if self.debug: self.info.log(icon_path)
            action.setIcon(icon)
            action.setParent(parent)
            if callback is not None:
                action.triggered.connect(callback)
            action.setEnabled(enabled_flag)
            action.setObjectName(objname)

            if status_tip is not None:
                action.setStatusTip(status_tip)

            if whats_this is not None:
                action.setWhatsThis(whats_this)

            if add_to_toolbar:
                # Adds plugin icon to Plugins toolbar
                self.iface.addToolBarIcon(action)

            if add_to_menu:
                self.iface.addPluginToMenu(self.plugin_name, action)
            self.plugin_actions.append(action)
            self.iface.mainWindow().addAction(action)
            return action
        except Exception as e:
            self.info.err(e)

    def initGui(self):  # must be named like that!
        try:
            mw = self.iface.mainWindow()
            # app icon
            app_icon = os.path.join(self.plugin_dir, 'icon.png')
            # run action
            self.add_action(text="Version " + self.get_version(), objname='mAction' + plugin_objectName, icon_path=app_icon,
                            callback=self.run, add_to_menu=True, add_to_toolbar=True, parent=mw)
            # set app icon
            self.setPluginIcon(app_icon)
            self.first_start = False
        except Exception as e:
            self.info.err(e)

    def setPluginIcon(self, app_icon):
        try:
            for action in self.iface.pluginMenu().actions():
                if action.text() == self.plugin_name:
                    action.setIcon(QIcon(app_icon))
        except Exception as e:
            self.info.err(e)

    def get_version(self):
        try:
            file = os.path.join(self.plugin_dir, 'metadata.txt')
            text = None
            msg = ''
            if os.path.isfile(file):
                f = open(file, 'r')
                text = f.readlines()
                f.close()
            for line in text:
                if "version=" in line:
                    line = line.replace('\n', '')
                    msg = msg + str.replace(line, "version=", "")
                    break
            return msg
        except Exception as e:
            self.info.err(e)

    def unload(self):
        try:
            """Removes the plugin menu item and icon from QGIS GUI."""
            for action in self.plugin_actions:
                self.iface.removePluginMenu(self.tr(plugin_name), action)
                self.iface.removeToolBarIcon(action)
        except Exception as e:
            self.info.err(e)

    def run(self):
        try:
            if self.debug:
                self.info.log(plugin_objectName + ":run")
            self.unload()
            self.initGui()
            self.app = App(self)
        except Exception as e:
            self.info.err(e)

    def project_read(self):
        try:
            self.run()
        except Exception as e:
            self.info.err(e)
