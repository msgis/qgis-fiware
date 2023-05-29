# -*- coding: utf-8 -*-

from builtins import str
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QStandardPaths

from qgis.core import Qgis, QgsMessageLog, QgsFeature
import os
import sys


class Info(QObject):
    def __init__(self, logobject):
        super(Info, self).__init__()
        self.log_suffix = __name__
        self.iface = None
        self.metadata = None
        self.parent = None
        self.debug = False
        self.logfile = None
        self.panel_name = __name__.split(".")[0]  # friendly displayname for panel AND messageboxes
        try:
            self.log_suffix = logobject.objectName()  # technical: class name
            if self.log_suffix == '': self.log_suffix = __name__
        except:
            pass  # dont touch!

        if "." in self.log_suffix: self.log_suffix = self.log_suffix.split(".")[-1]

        try:
            self.iface = logobject.iface
            self.parent = self.iface.mainWindow()  # messagebox
        except:
            pass  # dont touch!
        try:  # logfile
            log_path = os.path.join(os.path.dirname(__file__), "log")
            self.debug = os.path.exists(log_path)  # platform indepentend
            if self.debug:
                self.logfile = os.path.join(log_path, __name__ + '.log')
            else:
                self.logfile = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0]
                self.logfile = os.path.join(self.logfile,
                                            self.panel_name + '_err.log')  # c:\Users\guenter\AppData\Roaming\QGIS\QGIS3\
            if os.path.isfile(self.logfile) and (os.path.getsize(self.logfile) > 10123456):
                self.do_backup()
        except Exception as e:
            self.err(e)

    def do_backup(self):
        try:
            if os.path.isfile(self.logfile):
                bakfile = self.logfile + ".bak"
                if os.path.isfile(bakfile): os.remove(bakfile)
                os.rename(self.logfile, bakfile)
        except Exception as e:
            self.err(e)

    def getlogfile(self):
        return self.logfile

    def getLogPanelName(self):
        return self.panel_name

    def dl(self, *args):  # debug log
        try:
            objectname = ''
            try:
                objectname = self.sender().objectName()
            except:
                pass
            suffix = self.log_suffix + ":{0}:".format(objectname)
            text = suffix + self.ArgsToText(*args)
            if self.debug:
                QgsMessageLog.logMessage(text, "GTO-dev-debug", Qgis.Info)
        except Exception as e:
            self.err(None)

        # dl...dev only
        # log...if debug, all logs
        # err...always Exceptions and warnings (err(None,....) for configurators

    def log(self, *args):
        try:
            objectname = ''
            try:
                objectname = self.sender().objectName()
            except:
                pass
            suffix = self.log_suffix + ":{0}:".format(objectname)
            text = suffix + self.ArgsToText(*args)
            QgsMessageLog.logMessage(text, self.panel_name, Qgis.Info)
            if self.debug:
                self.write_debug_file(text)
        except Exception as e:
            self.err(None)

    def write_debug_file(self, text):
        try:
            with open(self.logfile, 'a') as f:
                f.write(text + '\n')
        except Exception as e:
            try:
                self.err(e)
            except:
                pass

    def ArgsToText(self, *args):
        if args is None: return
        try:
            text = ""
            for arg in args:
                if args is None:
                    text = text + " None"
                elif arg == '':
                    text = text + " Empty string"
                else:
                    if isinstance(arg, list):
                        tmp = []
                        for obj in arg:
                            if isinstance(obj, QgsFeature):
                                tmp.append(str(obj.id()))
                            else:
                                tmp.append(str(obj))
                        text = text + ' [' + ','.join(tmp) + ']'
                    elif isinstance(arg, dict):
                        tmp = []
                        for k, v in arg.items():
                            if isinstance(v, QgsFeature):
                                tmp.append(str(k) + ':' + str(v.id()))
                            else:
                                tmp.append(str(k) + ':' + str(v))
                        text = text + ' {' + ','.join(tmp) + '}'
                    else:
                        text = text + " " + str(arg)
            text = text.strip()
            return text
        except Exception as e:
            self.err(e)

    def err(self, e, *args):
        if args is None and e is None: return
        try:
            suffix = self.log_suffix + "::"
            err_panel = "GTO-ERROR"
            if e is not None:
                level = Qgis.Critical
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                text = self.ArgsToText(suffix, 'ERROR:', exc_type, fname, "| line:", exc_tb.tb_lineno,
                                       "|") + self.ArgsToText(e.args) + self.ArgsToText(*args)
                if self.debug:
                    QgsMessageLog.logMessage(text, err_panel, level)
            else:
                level = Qgis.Warning
                text = self.ArgsToText(suffix, 'WARNING:', self.ArgsToText(*args))
            if self.debug:
                QgsMessageLog.logMessage(text, err_panel, level)
            QgsMessageLog.logMessage(text, self.panel_name, level)
            self.write_debug_file(text)
            return text
        except Exception as e:
            QgsMessageLog.logMessage(str(e.args), self.panel_name)

    def msg(self, *args, parent=None):
        try:
            if parent is None:
                parent = self.parent
            self.getdialog(parent, self.panel_name, self.ArgsToText(*args), QMessageBox.Information).exec_()
        except Exception as e:
            self.err(e)

    def gtoWarning(self, *args):
        try:
            self.getdialog(self.parent, self.panel_name, self.ArgsToText(*args), QMessageBox.Warning).exec_()
        except Exception as e:
            self.err(e)

    def gtoCritical(self, *args):
        try:
            self.getdialog(self.parent, self.panel_name, self.ArgsToText(*args), QMessageBox.Critical).exec_()
        except Exception as e:
            self.err(e)

    def gtoQuestion(self, text, title=None, btns=QMessageBox.Yes | QMessageBox.No, stndBtn=QMessageBox.Yes,
                    parent=None):
        try:
            if not title: title = self.panel_name
            if parent is None: parent = self.parent
            return QMessageBox.question(parent, title, text, btns, stndBtn)
        except Exception as e:
            self.err(e)

    def getdialog(self, parent, title, text, icon=QMessageBox.Information, btns=QMessageBox.Ok | QMessageBox.Default):
        try:
            if self.debug: self.log("getdialog", parent)
            if parent is None: parent = self.parent
            msg = QMessageBox(parent)
            if icon: msg.setIcon(icon)
            msg.setText(text)
            msg.setWindowTitle(title)
            msg.setStandardButtons(btns)
            return msg
        except Exception as e:
            self.err(e)
