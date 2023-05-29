# import requests
# import time
# import json
# from osgeo import ogr
#
# prj=QgsProject.instance()
# layer=prj.mapLayersByName('Hydranten')[0]
# res = requests.get('https://fiwaredev.msgis.net/ngsi-ld/v1/types', auth=('', ''))
# print(res.json())
# offset = 0
# limit = 20
# _type = 'Hydrant'
#
# features=[]
# while res.status_code == 200:
#     req = 'https://fiwaredev.msgis.net/ngsi-ld/v1/entities?type={0}&offset={1}&limit={2}'.format(_type, offset, limit)
#     res = requests.get(req, auth=('', ''))
#     print(req, res.status_code)
#     for enty in res.json():
#         geojson = enty['location']['value']
#         print(geojson)
#         string = json.dumps(geojson)
#         geom = ogr.CreateGeometryFromJson(string)
#         geom = QgsGeometry.fromWkt(geom.ExportToWkt())
#         feat=QgsVectorLayerUtils.createFeature(layer)
#         feat.setGeometry(geom)
#         features.append(feat)
#     time.sleep(0.05)
#     offset = offset + limit
#     if offset > 100:
#         print('mehr als 1000')
#         break
# layer.dataProvider().truncate()
# layer.dataProvider().addFeatures(features)
# layer.dataProvider().reloadData()
# layer.updateExtents()
# iface.layerTreeView().refreshLayerSymbology(layer.id())
# if iface.mapCanvas().isCachingEnabled():
#     layer.triggerRepaint()
# else:
#     iface.mapCanvas().refresh()