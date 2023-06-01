# -*- coding: utf-8 -*-

def classFactory(iface): 
    from .mPlugin import plugin
    return plugin(iface)
