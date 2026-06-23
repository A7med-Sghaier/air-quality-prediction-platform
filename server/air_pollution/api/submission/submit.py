"""
***********************************************
* server - stations
* created by : AHMED SGHAIER
* created on : 10.05.18 - 12:24
* copyright : all right reserved @LMU 2018
***********************************************
"""
import requests
from air_pollution.config.submission_api_config import submission_config
import codecs

class PredictorSubmitter:
    def __init__(self):
        self.configs = submission_config
        self.url = 'https://biendata.com/competition/kdd_2018_submit/'


    def submit(self, file_to_submit_path):
        self.files = {'files': codecs.open(file_to_submit_path,'rb', 'utf-8')}
        response = requests.post(self.url, files=self.files, data=self.configs)
        print(response.text)
