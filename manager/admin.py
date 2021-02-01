import urllib.error

from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from manager.models import Source, Target, StaticTarget
from manager.source_parser import SourceParser


@admin.register(Source)
class SourceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')

    actions = ['test_parser']

    def test_parser(self, request, queryset):
        results = []

        for source in queryset:
            parser = SourceParser(source)

            try:
                parser.parse()
            except ValueError:
                results.append((source.name, False, '- Не знайдено записів в стрічці. Імовірно невідомий формат стрічки'))
                continue

            except urllib.error.URLError:
                results.append((source.name, False, '- Сервер не відповідає, перевірте правильність URL'))
                continue

            results.append((source.name, True, ''))

        passed_img = '<img style="vertical-align: sub;" src="/static/admin/img/icon-yes.svg" alt="True">'
        failed_img = '<img style="vertical-align: sub;" src="/static/admin/img/icon-no.svg" alt="False">'

        results_html = '<br>'.join(
            f"\t{passed_img if passed else failed_img} {source_name} {description}" for source_name, passed, description in results
        )

        self.message_user(request, mark_safe(f"Результати тестування:<br>{results_html}"), level=messages.WARNING)

    test_parser.short_description = 'Тест парсера'


@admin.register(Target)
class TargetModelAdmin(admin.ModelAdmin):
    list_display = ('get_source_name', 'get_hyperlinked_title', 'traffic', 'publish_time', 'created_at')
    fields = ('source', 'title', 'url', 'traffic', 'publish_time', 'created_at')
    # readonly_fields = ('source', 'title', 'url', 'traffic', 'publish_time', 'created_at')
    readonly_fields = ('created_at', )
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
