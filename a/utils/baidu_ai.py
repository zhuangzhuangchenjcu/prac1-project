import requests
import base64
import os

class BaiduRecognizer:
    def __init__(self):
        # Please enter your Baidu AI Open Platform API Key and Secret Key here
        # Application address: https://console.bce.baidu.com/ai/
        self.API_KEY = "fnVEObq91sEOVWKvoUUfqM4a"
        self.SECRET_KEY = "2xISgzIUHSe4ZQ8kovgeLo0hVW4HcU03"
        self.access_token = None

    def get_access_token(self):
        """
        Use AK, SK to generate authentication signature (Access Token)
        :return: access_token, or None (if error)
        """
        if self.API_KEY == "Please replace with your API_KEY" or self.SECRET_KEY == "Please replace with your SECRET_KEY":
            print("Please configure your API_KEY and SECRET_KEY in utils/baidu_ai.py first")
            return None
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            print(f"Failed to get Access Token: {e}")
            return None

    def recognize_ingredient(self, image_data):
        """
        Call Baidu Fruit and Vegetable Recognition API
        :param image_data: Image binary data
        :return: Recognition result list [{"name": "Apple", "score": 0.9}, ...] or None
        """
        token = self.get_access_token()
        if not token:
            # If Key is not configured, return simulated data for demonstration
            return [{"name": "Simulated Recognition Result - Red Fuji Apple", "score": 0.95}]

        request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/classify/ingredient"
        
        # Open image file in binary mode
        img = base64.b64encode(image_data)
        
        params = {"image": img}
        request_url = request_url + "?access_token=" + token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(request_url, data=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            if 'result' in result:
                return result['result']
            else:
                print(f"API returned error: {result}")
                return None
        except Exception as e:
            print(f"Recognition failed: {e}")
            return None
