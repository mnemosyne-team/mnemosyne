import os
import typing
import requests
import json


OXFORD_API_URL = os.environ.get('OXFORD_API_URL')


def get_word_data(word: str) -> typing.Optional[typing.Dict]:
	result = {}
	try:
		response = requests.get(
			f'{OXFORD_API_URL}/entries/en/{word.lower()}/regions=us',
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

			result['lexical_entries'][i]['pronunciation'] = {}
			if 'pronunciations' in lexical_entry:
				for pronunciation in lexical_entry['pronunciations']:
					if pronunciation['phoneticNotation'] == 'IPA':
						result['lexical_entries'][i]['pronunciation'].update(
							{
								'phonetic_spelling':
									pronunciation['phoneticSpelling'],
								'audio':
									pronunciation['audioFile']
							}
						)
						break

			result['lexical_entries'][i]['senses'] = []
			for entry in lexical_entry['entries']:
				for sense in entry['senses']:
					if 'definitions' in sense:
						result['lexical_entries'][i]['senses'].append(
							{
								'definitions': sense['definitions'][0],
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


def get_text(audio, lang='en-US', format='detailed'):
	params = f'language={lang}&format={format}'
	url = f'{os.environ.get("MICROSOFT_SPEECH_API_URL")}?{params}'
	headers = {
		'Accept': 'application/json',
		'Ocp-Apim-Subscription-Key': os.environ.get('MICROSOFT_SPEECH_API_KEY'),
		'Transfer-Encoding': 'chunked',
		'Content-type': 'audio/wav; codec=audio/pcm; samplerate=16000'
	}
	r = requests.post(url, headers=headers, data=stream_audio_file(audio))
	results = json.loads(r.content)
	return results


def stream_audio_file(speech_file):
	for chunk in speech_file:
		yield chunk
