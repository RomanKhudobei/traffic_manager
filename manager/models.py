from django.db import models
from django.utils import timezone


class Source(models.Model):
    """
    Source of targets. Basically url to site RSS feed
    """
    name = models.CharField(max_length=50)
    url = models.URLField(unique=True, help_text='Посилання на RSS стрічку')
    limit = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Target(models.Model):
    """
    Url, which will receive traffic. Url, that going to be pasted to iframe
    """
    source = models.ForeignKey(Source, related_name='targets', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='Немає')
    url = models.URLField(help_text='Посилання, яке поміщатиметься в iframe у віджеті') # TODO: think whether to add unique constraint
    traffic = models.PositiveIntegerField(default=0)
    publish_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)


class StaticTarget(models.Model):
    """
    Static target is permanent target (without traffic limit)
    """
    name = models.CharField(max_length=50)
    url = models.URLField(unique=True)
    is_active = models.BooleanField(default=True)
