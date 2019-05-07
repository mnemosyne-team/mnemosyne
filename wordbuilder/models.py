import datetime

from django.contrib.auth.models import User
from django.db import models


class Word(models.Model):
    class Meta:
        verbose_name = 'word'
        verbose_name_plural = 'words'
        indexes = [models.Index(fields=['name'])]

    name = models.CharField(unique=True, max_length=40)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.name,
            'lexical_entries': [
                lexical_entry.to_dict()
                for lexical_entry in self.lexical_entries.all()
            ]
        }
      
    @classmethod
    def from_dict(cls, dict):
        if dict['text'] not in list(Word.objects.values_list('name').all()):
            word = cls.objects.create(name=dict['text'])
            for entry in dict['lexical_entries']:
                if entry['pronunciation']:
                    if entry['pronunciation']['phonetic_spelling'] not in \
                            list(
                                Pronunciation.objects.values_list(
                                    'phonetic_spelling', flat=True
                                ).all()
                            ):
                        pronunciation = Pronunciation.from_dict(
                            entry['pronunciation']
                        )
                    else:
                        pronunciation = Pronunciation.objects.get(
                            phonetic_spelling=entry['pronunciation'][
                                'phonetic_spelling'
                            ]
                        )
                else:
                    pronunciation = None
                if entry['lexical_category'].lower() not in \
                        list(
                            LexicalCategory.objects.values_list(
                                'name', flat=True
                            )
                        ):
                    lexical_entry = LexicalEntry.from_dict(
                        word,
                        LexicalCategory.from_dict(
                            entry['lexical_category'].lower()
                        ),
                        pronunciation
                    )
                else:
                    lexical_entry = LexicalEntry.from_dict(
                        word,
                        LexicalCategory.objects.get(
                            name=entry['lexical_category'].lower()
                        ),
                        pronunciation
                    )
                for sense in entry['senses']:
                    Sense.from_dict(lexical_entry, sense)
            return word


class LexicalCategory(models.Model):
    class Meta:
        verbose_name = 'lexical category'
        verbose_name_plural = 'lexical categories'
        indexes = [models.Index(fields=['name'])]

    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, name):
        return cls.objects.create(name=name)


class Pronunciation(models.Model):
    class Meta:
        verbose_name = 'pronunciation'
        verbose_name_plural = 'pronunciations'

    phonetic_spelling = models.CharField(max_length=30)
    audio = models.URLField(
        blank=True, null=True, verbose_name='audio file url'
    )

    def __str__(self):
        return self.phonetic_spelling

    def to_dict(self):
        result = {
            'id': self.id,
            'phonetic_spelling': self.phonetic_spelling
        }
        if self.audio:
            result['audio'] = self.audio
        return result

    @classmethod
    def from_dict(cls, pronunciation):
        return cls.objects.create(
            phonetic_spelling=pronunciation['phonetic_spelling'],
            audio=pronunciation['audio']
        )


class LexicalEntry(models.Model):
    class Meta:
        verbose_name = 'lexical entry'
        verbose_name_plural = 'lexical entries'

    word = models.ForeignKey(
        Word, on_delete=models.CASCADE,
        related_name='lexical_entries'
    )
    lexical_category = models.ForeignKey(
        LexicalCategory, on_delete=models.CASCADE,
        related_name='lexical_entries'
    )
    pronunciation = models.ForeignKey(
        Pronunciation, on_delete=models.CASCADE,
        related_name='lexical_entries', blank=True, null=True
    )

    def __str__(self):
        return f'{self.word} {self.lexical_category}'

    def to_dict(self):
        result = {
            'id': self.id,
            'lexical_category': self.lexical_category.to_dict(),
            'pronunciation': [],
            'senses': [sense.to_dict() for sense in self.senses.all()]
        }
        if self.pronunciation:
            result['pronunciation'].append(self.pronunciation.to_dict())
        return result

    @classmethod
    def from_dict(cls, word, lexical_category, pronunciation=None):
        return cls.objects.create(
            word=word,
            lexical_category=lexical_category,
            pronunciation=pronunciation
        )


class Sense(models.Model):
    lexical_entry = models.ForeignKey(
        LexicalEntry, on_delete=models.CASCADE, related_name='senses'
    )

    def __str__(self):
        return str(self.lexical_entry)

    def to_dict(self):
        return {
            'id': self.id,
            'definitions': [
                definition.text
                for definition in self.definitions.all()
            ],
            'examples': [
                example.text
                for example in self.examples.all()
            ]
        }

    @classmethod
    def from_dict(cls, lexical_entry, sense):
        obj = cls.objects.create(lexical_entry=lexical_entry)
        obj.definitions.add(Definition.from_dict(obj, sense['definitions']))
        if sense['examples']:
            for example in sense['examples']:
                obj.examples.add(Example.from_dict(obj, example))
        return obj


class Definition(models.Model):
    sense = models.ForeignKey(
        Sense, on_delete=models.CASCADE, related_name='definitions'
    )
    text = models.TextField()

    def __str__(self):
        return (
            f'{self.sense.lexical_entry.word} '
            f'{self.sense.lexical_entry.lexical_category} '
            f'{self.text}'
        )

    def to_dict(self):
        return {'id': self.id, 'text': self.text}

    @classmethod
    def from_dict(cls, sense, text):
        return cls.objects.create(sense=sense, text=text)


class Example(models.Model):
    sense = models.ForeignKey(
        Sense, on_delete=models.CASCADE, related_name='examples'
    )
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f'{self.sense.lexical_entry.word} '
            f'{self.sense.lexical_entry.lexical_category} '
            f'{self.text}'
        )

    def to_dict(self):
        if self.text:
            return {'id': self.id, 'text': self.text}

    @classmethod
    def from_dict(cls, sense, text):
        return cls.objects.create(sense=sense, text=text)


class Dictionary(models.Model):
    class Meta:
        verbose_name = 'dictionary'
        verbose_name_plural = 'dictionaries'

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='dictionary'
    )

    def __str__(self):
        return f'dictionary of {self.user}'


class Category(models.Model):
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    name = models.CharField(max_length=30)

    def __str__(self):
        return f'Category {self.name}'


class WordSet(models.Model):
    title = models.CharField(max_length=30)
    image = models.ImageField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='word_set'
    )

    def __str__(self):
        return f'WordSet {self.title}'


class UserWord(models.Model):
    class Meta:
        ordering = ('-added',)

    dictionary = models.ForeignKey(
        Dictionary, on_delete=models.CASCADE, related_name='words'
    )
    word = models.ForeignKey(
        Word, on_delete=models.CASCADE, related_name='user_words'
    )
    lexical_category = models.ForeignKey(
        LexicalCategory, on_delete=models.CASCADE, related_name='user_words'
    )
    pronunciation = models.ForeignKey(
        Pronunciation, on_delete=models.CASCADE, related_name='user_words',
        blank=True, null=True
    )
    sense = models.ForeignKey(
        Sense, on_delete=models.CASCADE, related_name='user_words'
    )
    study_progress = models.IntegerField(default=0)
    added = models.DateTimeField(default=datetime.datetime.utcnow)
    learn_date = models.DateTimeField(blank=True, null=True)
    word_set = models.ForeignKey(
        WordSet, on_delete=models.CASCADE, related_name='user_words',
        blank=True, null=True
    )

    def __str__(self):
        return str(self.word)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word.name,
            'lexical_category': self.lexical_category.to_dict(),
            'pronunciation': (
                self.pronunciation.to_dict()
                if self.pronunciation is not None else None
            ),
            'sense': self.sense.to_dict(),
            'study_progress': self.study_progress
        }


class Statistics(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_statistics'
    )
    last_training = models.DateField(null=True, blank=True)
    day_streak = models.IntegerField(default=0)
    record_day_streak = models.IntegerField(default=0)
