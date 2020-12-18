from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(unique=True, help_text='Посилання на RSS стрічку')
    limit = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)


class Target(models.Model):
    source = models.ForeignKey(Source, related_name='targets', on_delete=models.CASCADE)
    url = models.URLField(help_text='Посилання, яке поміщатиметься в iframe у віджеті')
    publish_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
