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


class LexicalCategory(models.Model):
    class Meta:
        verbose_name = 'lexical category'
        verbose_name_plural = 'lexical categories'
        indexes = [models.Index(fields=['name'])]

    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Pronunciation(models.Model):
    class Meta:
        verbose_name = 'pronunciation'
        verbose_name_plural = 'pronunciations'

    phonetic_spelling = models.CharField(max_length=30, blank=True, null=True)
    audio = models.URLField(
        blank=True, null=True, verbose_name='audio file url'
    )

    def __str__(self):
        return self.phonetic_spelling


class Sense(models.Model):
    word = models.ForeignKey(
        Word, on_delete=models.CASCADE, related_name='senses'
    )
    lexical_category = models.ForeignKey(
        LexicalCategory, on_delete=models.CASCADE,
        related_name='senses'
    )
    pronunciation = models.ForeignKey(
        Pronunciation, on_delete=models.CASCADE, related_name='senses',
        blank=True, null=True
    )

    def __str__(self):
        return (
            f'{self.word} {self.lexical_category} '
            f'{self.pronunciation.phonetic_spelling}'
        )


class Definition(models.Model):
    sense = models.ForeignKey(
        Sense, on_delete=models.CASCADE, related_name='definitions'
    )
    text = models.TextField()

    def __str__(self):
        return self.text


class Example(models.Model):
    sense = models.ForeignKey(
        Sense, on_delete=models.CASCADE, related_name='examples'
    )
    text = models.TextField()

    def __str__(self):
        return self.text


class Dictionary(models.Model):
    class Meta:
        verbose_name = 'dictionary'
        verbose_name_plural = 'dictionaries'

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='dictionary'
    )

    def __str__(self):
        return f'dictionary of {self.user}'


class UserWord(models.Model):
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
    definition = models.ForeignKey(
        Definition, on_delete=models.CASCADE, related_name='user_words',
    )
    example = models.ForeignKey(
        Example, on_delete=models.CASCADE, related_name='user_words',
        blank=True, null=True
    )
    study_progress = models.IntegerField(default=0)
    added = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return str(self.word)
