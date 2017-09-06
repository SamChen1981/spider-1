import requests


class HttpClient(object):

    def request(self, url):
        response = requests.get(url)
        return response
