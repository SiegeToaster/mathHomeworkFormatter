# run from \mathHomeworkFormatter with "py mathHomeworkFormatter.py"

from __future__ import print_function

import os.path
import argparse
import json
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID = '1p21l34ih6o_aiOtmaZTnJ-fuXvU9W6nY5ZMDDXGSrYQ'
TOKEN_PATH = "token.json"

parser = argparse.ArgumentParser(description='Process Homework Numbers.')
parser.add_argument('Numbers', metavar='N', type=int, nargs='+',
                    help='The homework number(s) you want printed')

args = parser.parse_args()
# print(args.Numbers)


def main():
	creds = auth()

	try:
		service = build('docs', 'v1', credentials=creds)

		# Retrieve the documents contents from the Docs service.``
		document = service.documents().get(documentId=DOCUMENT_ID).execute()
		document = document.get('body').get('content')[4].get('table').get('tableRows')
			# each index is a different assignment

		for assignment in document:
			assignment = assignment.get('tableCells')[0].get('content')
			with open('content.json', 'w') as path:
				path.write(json.dumps(assignment, indent = 4))

			# print('\n')
			hw_string = ''

			for assignment_num in assignment:
				assignment_num = assignment_num.get('paragraph').get('elements')[0].get('textRun').get('content')

				# if assignment_num.lower().startswith('hw'):
				# 	assignment_num = assignment_num[2:-1]
				# if assignment_num.lower().startswith('test') or assignment_num.lower().startswith('chap'):
				# 	assignment_num = assignment_num[4:-1]

				if assignment_num.lower() == 'hw':
					continue

				if 'hw' in assignment_num.lower():
					assignment_num = assignment_num[2:-1]

				assignment_num = assignment_num.strip('\n')
				assignment_num = assignment_num.strip()

				hw_string += assignment_num + ' '
				""" if len(re.findall("[0-9]+-[0-9]+", assignment_num)) > 0:
					print(assignment_num)
				elif len(re.findall("[0-9]+/[0-9]+", assignment_num)):
					print(assignment_num)
				elif len(re.findall("[0-9]+", assignment_num)) > 0:
					print(assignment_num)
				else:
					print(assignment_num) """

			hw_string = hw_string.strip()
			print(hw_string)
	except HttpError as err:
		print(err)

def auth():
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists(TOKEN_PATH):
		creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(TOKEN_PATH, 'w') as token:
			token.write(creds.to_json())

	return creds

if __name__ == '__main__':
	main()