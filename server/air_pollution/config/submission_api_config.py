'''
***********************************************
* DataSc - submission_api_config
* created by : AHMED SGHAIER
* created on : 10.05.18 - 12:40
* copyright : all right reserved @LMU 2018
***********************************************
'''
import datetime
import os

submission_config = {
    "user_id": os.environ.get("KDD_USER_ID", "your-user-id"),
    "team_token": os.environ.get("KDD_TEAM_TOKEN", "your-team-token"),
    "description": os.environ.get("KDD_SUBMISSION_DESCRIPTION", "MAD Pandas Submission"),
    "filename": os.environ.get("KDD_SUBMISSION_FILENAME", "mad_pandas" + str(datetime.datetime.now().date())),
}
