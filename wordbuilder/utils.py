import os
import typing
import requests


BASE_API_URL = os.environ.get('OXFORD_API_URL')


def get_word_data(word: str) -> typing.Optional[typing.Dict]:
	result = {}
	try:
		response = requests.get(
			f'{BASE_API_URL}/entries/en/{word.lower()}/regions=us',
			headers={
				'app_id': os.environ.get('OXFORD_APP_ID'),
				'app_key': os.environ.get('OXFORD_APP_KEY')
			}
		)
		response.raise_for_status()

		result['text'] = response.json()['results'][0]['id']
		result['lexical_entries'] = []
		lexical_entries = response.json()['results'][0]['lexicalEntries']

		for i, lexical_entry in enumerate(lexical_entries):
			result['lexical_entries'].append(
				{'lexical_category': lexical_entry['lexicalCategory']}
			)

			result['lexical_entries'][i]['pronunciation'] = []
			if 'pronunciations' in lexical_entry:
				for pronunciation in lexical_entry['pronunciations']:
					if pronunciation['phoneticNotation'] == 'IPA':
						result['lexical_entries'][i]['pronunciation'].append(
							{
								'phonetic_spelling':
									pronunciation['phoneticSpelling'],
								'audio':
									pronunciation['audioFile']
							}
						)

			result['lexical_entries'][i]['senses'] = []
			for entry in lexical_entry['entries']:
				for sense in entry['senses']:
					if 'definitions' in sense:
						result['lexical_entries'][i]['senses'].append(
							{
								'definitions': sense['definitions'],
								'examples': []
							}
						)
					if 'examples' in sense:
						for example in sense['examples']:
							result[
								'lexical_entries'
							][i][
								'senses'
							][-1][
								'examples'
							].append(
								example['text']
							)

	except requests.exceptions.RequestException as e:
		print('Request Error: ', e)
		return None

	return result
