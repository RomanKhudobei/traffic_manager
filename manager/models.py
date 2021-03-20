import uuid

from django.db import models
from django.utils import timezone


class Source(models.Model):
    """
    Source of targets. Basically url to site RSS feed
    """
    name = models.CharField(max_length=50)
    url = models.URLField(unique=True, help_text='Посилання на RSS стрічку')
    limit = models.PositiveIntegerField()
    remaining_traffic = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    statistic_view_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.id:
            self.remaining_traffic = self.limit

        super().save(*args, **kwargs)


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
    traffic = models.PositiveIntegerField(default=0)
    last_reset_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
