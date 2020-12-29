from django.contrib import admin

from manager.models import Source, Target


@admin.register(Source)
class SourceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')


@admin.register(Target)
class TargetModelAdmin(admin.ModelAdmin):
    list_display = ('get_source_name', 'url', 'traffic', 'publish_time', 'created_at')
    search_fields = ('url', 'source__name')

    def get_source_name(self, obj):
        return obj.source.name
