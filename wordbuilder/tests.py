from django.contrib.auth.models import User
from django.test import TestCase, Client

from wordbuilder import utils
from wordbuilder.models import Word, Dictionary


class TestWordFunctions(TestCase):
    word_communism = {
        'text': 'communism',
        'lexical_entries':
            [
                {
                    'lexical_category': 'Noun',
                    'pronunciation': {
                        'phonetic_spelling': 'ˈkɑmjəˌnɪzəm',
                        'audio': 'http://audio.oxforddictionaries.com/en/mp3/communism_us_1.mp3'
                    },
                    'senses': [
                        {
                            'definitions': 'a political theory derived from Karl Marx,'
                                           ' advocating class war and leading to a society in which'
                                           ' all property is publicly owned and each person works'
                                           ' and is paid according to their abilities and needs.',
                            'examples': []
                        }
                    ]
                }
            ]
        }

    word_dict = {
        'id': 1,
        'text': 'communism',
        'lexical_entries':
            [
                {
                    'id': 1,
                    'lexical_category': {
                        'id': 1,
                        'name': 'noun'
                    },
                    'pronunciation': [
                        {
                            'id': 1, 'phonetic_spelling': 'ˈkɑmjəˌnɪzəm',
                            'audio': 'http://audio.oxforddictionaries.com/en/mp3/communism_us_1.mp3'
                        }
                    ],
                    'senses': [
                        {
                            'id': 1,
                            'definitions': [
                                'a political theory derived from Karl Marx,'
                                ' advocating class war and leading to a society '
                                'in which all property is publicly owned and each'
                                ' person works and is paid according to their'
                                ' abilities and needs.'
                                ],
                            'examples': []
                        }
                    ]
                }
            ]
        }

    def test_get_word_data(self):
        self.assertNotEqual(utils.get_word_data('treasure'), None)
        self.assertEqual(utils.get_word_data('communism'), self.word_communism)

    def test_from_and_to_dict(self):
        word = Word.from_dict(self.word_communism)
        self.assertEqual(word, Word.objects.get(id=1))  # from_dict test
        self.assertEqual(word.to_dict(), self.word_dict)  # to_dict test


class WordbuilderTest(TestCase):
    client = Client()

    def test_anonymous_user_redirect(self):
        response1 = self.client.get('')
        response2 = self.client.get('/dictionary/')
        response3 = self.client.get('/profile/')
        self.assertEqual(302, response1.status_code)
        self.assertEqual(302, response2.status_code)
        self.assertEqual(302, response3.status_code)

    def test_user_status_code(self):
        user = User.objects.create(username='test_user', first_name='Test', last_name='User', email='test@user.co')
        user.set_password('12345')
        user.save()
        dictionary = Dictionary.objects.create(user_id=1)
        dictionary.save()
        self.client.login(username='test_user', password='12345')
        with self.settings(STATIC_URL='/static/',
                           STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            response1 = self.client.get('')
            response2 = self.client.get('/dictionary/')
            response3 = self.client.get('/profile/')
            self.assertEqual(200, response1.status_code)
            self.assertEqual(200, response2.status_code)
            self.assertEqual(200, response3.status_code)
