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

parser = argparse.ArgumentParser(description='Process Homework Number.')
parser.add_argument('Numbers', metavar='N', type=str, nargs='+',
                    help='The homework number you want printed')

args = parser.parse_args()
REQUESTED_HW = ' '.join(args.Numbers)

def main():
	document = None

	try:
		service = build('docs', 'v1', credentials=auth())

		# Retrieve the documents contents from the Docs service.``
		document = service.documents().get(documentId=DOCUMENT_ID).execute()
		document = document.get('body').get('content')[4].get('table').get('tableRows')
			# each index is a different assignment
			
	except HttpError as err:
		print(err)

	for assignment in document:
		assignment = assignment.get('tableCells')[0].get('content')
		hw_string = construct_hw_string(assignment)
		valid_numbers = construct_valid_numbers(hw_string)
		valid_numbers = filter_valid_numbers(valid_numbers, hw_string)

		print(valid_numbers)
		if REQUESTED_HW in valid_numbers:
			# print(hw_string)
			1 + 1

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

def construct_hw_string(assignment):
	hw_string = ''

	for assignment_num in assignment:
		assignment_num = assignment_num.get('paragraph').get('elements')[0].get('textRun').get('content')

		if assignment_num.lower() == 'hw':
			continue

		if 'hw' in assignment_num.lower():
			assignment_num = assignment_num[2:-1]

		assignment_num = assignment_num.strip('\n')
		assignment_num = assignment_num.strip()

		hw_string += assignment_num + ' '

	hw_string = hw_string.strip()
	return hw_string

def construct_valid_numbers(hw_string):
	valid_numbers = []
	if hw_string[0].isnumeric():
		if '/' in hw_string:
			valid_numbers = hw_string.split('/')
		elif '-' in hw_string:
			valid_numbers = hw_string.split('-')
			for x in range(int(valid_numbers[0]) + 1, int(valid_numbers[1])):
				valid_numbers.append(str(x))
		else:
			valid_numbers.append(hw_string)
	else:
		valid_numbers.append(hw_string)
	
	return valid_numbers

def filter_valid_numbers(valid_numbers: list[str], hw_string: str):
	for hw in valid_numbers:
		if str(hw).isnumeric() or str(hw).lower().startswith('test') or str(hw).lower().startswith('chap'):
			continue

		if len(valid_numbers) <= 1 and not 'test' in str(hw).lower():
			continue

		# exceptions (tried to make robust but they are pretty unique): 
		if len(valid_numbers) > 1:
			valid_numbers = [hw_string]
			continue

		if 'test' in hw_string.lower():
			index = valid_numbers[0].find(' ')
			valid_numbers[0] = valid_numbers[0][0:index]
			valid_numbers.append(hw_string[index:].strip())
	
	return valid_numbers

if __name__ == '__main__':
	main()