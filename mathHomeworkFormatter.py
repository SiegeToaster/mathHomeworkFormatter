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
SCOPES = ['https://www.googleapis.com/auth/documents']
DOCUMENT_ID = '1p21l34ih6o_aiOtmaZTnJ-fuXvU9W6nY5ZMDDXGSrYQ'
TEMPLATE_ID = '165mIRq4syA7NC_nO68JdFFPzLVHQlKpZaW8_-Fmeaz8'
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
					
		output = service.documents().get(documentId=TEMPLATE_ID).execute()
		output = output.get('body').get('content')[2].get('table').get('tableRows')[0].get('tableCells')

		with open('test.json', 'w') as path:
			path.write(json.dumps(output, indent=4))

	except HttpError as err:
		print(err)

	for assignment in document:
		assignment = assignment.get('tableCells')
		assignment_title = assignment[0].get('content')
		hw_string = construct_hw_string(assignment_title)
		valid_numbers = construct_valid_numbers(hw_string)
		valid_numbers = filter_valid_numbers(valid_numbers, hw_string)

		if REQUESTED_HW in valid_numbers:
			assignment_pages = assignment[3].get('content')
			assignment_problems = assignment[4].get('content')
			pages = get_pages(assignment_pages)
			problems = get_problems(assignment_problems)
			due_date = problems[1]
			problems = problems[0]


			print("HW " + hw_string)
			print(due_date)
			print(pages)
			print(problems)
			print('\n\n')

			assigned_problems_string = ''
			for i, page in enumerate(pages):
				assigned_problems_string += page + ' '
				if i >= len(problems): break
				if problems[i] != '' and not 'added' in page.lower():
					assigned_problems_string += '#' + problems[i] + '; '
			
			print(assigned_problems_string)
			print('\n')
			print(output[0].get('content')[0].get('startIndex'))
			print(output[0].get('content')[0].get('endIndex') - 1)
			print(output[1].get('content')[0].get('startIndex'))
			print(output[1].get('content')[0].get('endIndex') - 1)


			request1 = [ 	# requests are in order where index is higher because changing higher indexes don't affect lower ones
							# if it were left to right (lower index to high), the indexes would have to be recalculated for each change
				{
					'deleteContentRange': {
						'range': {
							'startIndex': output[2].get('content')[2].get('startIndex'),
							'endIndex': output[2].get('content')[2].get('endIndex') - 1,
						}
					}
				},
				{
					'insertText': {
						'location': {
							'index': output[2].get('content')[2].get('startIndex')
						},
						'text': due_date
					}
				},

				{
					'deleteContentRange': {
						'range': {
							'startIndex': output[1].get('content')[0].get('startIndex'),
							'endIndex': output[1].get('content')[0].get('endIndex') - 1,
						}
					}
				},
				{
					'insertText': {
						'location': {
							'index': output[1].get('content')[0].get('startIndex')
						},
						'text': assigned_problems_string
					}
				},

				{
					'deleteContentRange': {
						 'range': {
							'startIndex': output[0].get('content')[0].get('startIndex'),
							'endIndex': output[0].get('content')[0].get('endIndex') - 1,
 						}
					}
				},
				{
					'insertText': {
						'location': {
							'index': output[0].get('content')[0].get('startIndex')
						},
						'text': "HW " + hw_string
					}
				},
			]
			
			result = service.documents().batchUpdate(
				documentId=TEMPLATE_ID, body={'requests': request1}
			).execute()
			
			print(result)
			break

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

def get_pages(assignment_pages):
	pages = []

	for page in assignment_pages:
		page = page.get('paragraph').get('elements')[0].get('textRun').get('content')
		if page == '\n':
			continue

		page = page.strip('\n')
		page = page.strip()

		pages.append(page)
	
	return pages

def get_problems(assignment_problems):
	due_date = ''
	problems = []

	for problem in assignment_problems:
		with open('output.json', 'w') as path:
			path.write(json.dumps(problem, indent=4))

		problem = problem.get('paragraph').get('elements')[0]
		if not 'textRun' in problem.keys():
			return [problems, due_date]
		problem = problem.get('textRun').get('content')

		if re.match(r'^do +mml', problem, re.I):
			return [problems, due_date]

		if (problem.lower().startswith('due')):
			index = re.search(r"\d", problem).start()
			due_date = problem[index:].strip('\n') + '/22'
		else:
			problems.append(problem.strip('\n'))

	return [problems, due_date]

if __name__ == '__main__':
	main()