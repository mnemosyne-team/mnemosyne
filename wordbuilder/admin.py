from django.contrib import admin

from wordbuilder import models


class LexicalEntryInline(admin.TabularInline):
    model = models.LexicalEntry


class WordAdmin(admin.ModelAdmin):
    inlines = (LexicalEntryInline,)


class SenseInline(admin.TabularInline):
    model = models.Sense


class LexicalEntryAdmin(admin.ModelAdmin):
    inlines = (SenseInline,)


class DefinitionInline(admin.TabularInline):
    model = models.Definition
    extra = 1


class ExampleInline(admin.TabularInline):
    model = models.Example
    extra = 1


class SenseAdmin(admin.ModelAdmin):
    inlines = (DefinitionInline, ExampleInline)


class UserWordInline(admin.StackedInline):
    model = models.UserWord
    extra = 1


class DictionaryAdmin(admin.ModelAdmin):
    inlines = (UserWordInline,)


admin.site.register(models.Dictionary, DictionaryAdmin)
admin.site.register(models.UserWord)
admin.site.register(models.Word, WordAdmin)
admin.site.register(models.LexicalEntry)
admin.site.register(models.LexicalCategory)
admin.site.register(models.Sense, SenseAdmin)
admin.site.register(models.Definition)
admin.site.register(models.Example)
admin.site.register(models.Pronunciation)
admin.site.register(models.Category)
admin.site.register(models.WordSet)
admin.site.register(models.Statistics)
