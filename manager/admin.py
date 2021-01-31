from django.contrib import admin
from django.utils.safestring import mark_safe

from manager.models import Source, Target, StaticTarget


@admin.register(Source)
class SourceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')
    # TODO: add action "Test parser" which gonna test if feed is valid for parser


@admin.register(Target)
class TargetModelAdmin(admin.ModelAdmin):
    list_display = ('get_source_name', 'get_hyperlinked_title', 'traffic', 'publish_time', 'created_at')
    fields = ('source', 'title', 'url', 'traffic', 'publish_time', 'created_at')
    readonly_fields = ('source', 'title', 'url', 'traffic', 'publish_time', 'created_at')
    search_fields = ('url', 'source__name')
    list_filter = ('source__name',)

    def get_source_name(self, obj):
        return obj.source.name

    def get_hyperlinked_title(self, obj):
        return mark_safe(f'<a href="{obj.url}">{obj.title}</a>')

    get_source_name.short_description = 'Source name'
    get_source_name.admin_order_field = 'source__name'

    get_hyperlinked_title.short_description = 'Title'
    get_hyperlinked_title.admin_order_field = 'title'


@admin.register(StaticTarget)
class StaticTargetModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active')
    search_fields = ('name', 'url')
    list_filter = ('is_active',)
