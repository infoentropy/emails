import requests


class CalmAPI():
    URL = "https://api.app.aws-prod.useast1.calm.com"

    def get(self, path, *args, **kwargs):
        try:
            r = requests.get(self.URL + path, params=kwargs)
            return r.json()
        except Exception as e:
            raise e
