import json
import pprint
import sseclient


def with_urllib3(url, headers):
    """Get a streaming response for the given event feed using urllib3."""
    import urllib3
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False, headers=headers)


def with_requests(url, headers):
    """Get a streaming response for the given event feed using requests."""
    import requests
    return requests.get(url, stream=True, headers=headers)


url = 'https://fiwaredev.msgis.net/ngsi-proxy/eventsource/de72ef30-f969-11ed-926f-1bdc1977e2d3'
headers = {'Accept': 'text/event-stream'}
# response = with_urllib3(url, headers)
response = with_requests(url, headers)
client = sseclient.SSEClient(response)
for event in client.events():
    pprint.pprint(json.loads(event.data))
    # 'payload': '{"id":"urn:ngsi-ld:Notification:f6284a8a-fedc-11ed-aaff-0242ac120003","type":"Notification","subscriptionId":"urn:ngsi-ld:Subscription:de7b7358-f969-11ed-b542-0242ac120003","notifiedAt":"2023-05-30T11:27:29.442Z","data":[{"id":"urn:ngsi-ld:Hydrant:HYDRANTOGD.36612499","type":"Hydrant","OBJECTID":36612499,"location":{"type":"Point","coordinates":[16.45231,48.157012,161.78]}}]}'}
