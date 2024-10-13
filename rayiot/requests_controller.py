import requests

class RequestsController:
    def __init__(self, endpoint, access_token, account_id):
        self.endpoint = endpoint
        self.access_token = access_token
        self.account_id = account_id

    def make_request(self, method=False, payload=False, res_id=1, res_model=False):
        data = {
            "params": {
                "res_model": res_model,
                "access_token": self.access_token,
                "account_id": self.account_id,
                "res_method": method,
                "res_id": res_id,
                "res_params": payload
            }
        }

        try:
            response = requests.request("POST", self.endpoint, data, timeout=60)
        except requests.exceptions.ConnectionError:
            print(response.json())

