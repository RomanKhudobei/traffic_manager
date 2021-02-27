import urllib.error
import datetime as dt

from django.contrib import admin, messages
from django.db.models import Sum
from django.utils.safestring import mark_safe

from manager.models import Source, Target, StaticTarget
from manager.source_parser import SourceParser


@admin.register(Source)
class SourceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'todays_traffic', 'limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')

    actions = ['test_parser']

    change_form_template = 'admin/source/change_form_template.html'

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

    def todays_traffic(self, obj):
        return Target.objects.filter(
            source=obj,
            publish_time__date=dt.date.today()
        ).aggregate(todays_traffic_count=Sum('traffic')).get('todays_traffic_count')

    todays_traffic.short_description = 'Today\'s traffic'


@admin.register(Target)
class TargetModelAdmin(admin.ModelAdmin):
    list_display = ('get_source_name', 'get_hyperlinked_title', 'traffic', 'publish_time', 'created_at')
    fields = ('source', 'title', 'url', 'traffic', 'publish_time', 'created_at')
    # readonly_fields = ('source', 'title', 'url', 'traffic', 'publish_time', 'created_at')
    readonly_fields = ('created_at', )
    search_fields = ('url', 'source__name')
    list_filter = ('source__name', 'publish_time', 'created_at')

    def get_source_name(self, obj):
        return obj.source.name

    def get_hyperlinked_title(self, obj):
        external_link_icon = """<svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="12" height="12" viewBox="0 0 226 226" style=" fill:#000000;"><g fill="none" fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="none" font-weight="none" font-size="none" text-anchor="none" style="mix-blend-mode: normal"><path d="M0,226v-226h226v226z" fill="none"></path><g fill="#3498db"><path d="M192.85775,23.44971c-0.34782,0.01143 -0.69473,0.04213 -1.03915,0.09196h-59.98527c-3.39599,-0.04803 -6.55477,1.7362 -8.26678,4.66947c-1.71201,2.93327 -1.71201,6.56113 0,9.49439c1.71201,2.93327 4.87079,4.7175 8.26678,4.66947h38.47591l-63.96712,63.96712c-2.46002,2.36186 -3.45098,5.8691 -2.5907,9.16909c0.86028,3.3 3.43736,5.87708 6.73736,6.73736c3.3,0.86028 6.80724,-0.13068 9.16909,-2.5907l63.96712,-63.96712v38.47591c-0.04803,3.39599 1.7362,6.55477 4.66947,8.26678c2.93327,1.71201 6.56113,1.71201 9.49439,0c2.93327,-1.71201 4.7175,-4.87079 4.66947,-8.26678v-60.04964c0.36774,-2.73828 -0.4855,-5.49992 -2.33376,-7.55354c-1.84826,-2.05362 -4.50507,-3.19204 -7.26682,-3.11378zM58.85417,37.66667c-19.38568,0 -35.3125,15.92682 -35.3125,35.3125v94.16667c0,19.38568 15.92682,35.3125 35.3125,35.3125h94.16667c19.38568,0 35.3125,-15.92682 35.3125,-35.3125v-44.72917c0.04803,-3.39599 -1.7362,-6.55477 -4.66947,-8.26678c-2.93327,-1.71201 -6.56113,-1.71201 -9.49439,0c-2.93327,1.71201 -4.7175,4.87079 -4.66947,8.26678v44.72917c0,9.16566 -7.31351,16.47917 -16.47917,16.47917h-94.16667c-9.16566,0 -16.47917,-7.31351 -16.47917,-16.47917v-94.16667c0,-9.16566 7.31351,-16.47917 16.47917,-16.47917h44.72917c3.39599,0.04803 6.55477,-1.7362 8.26678,-4.66947c1.71201,-2.93327 1.71201,-6.56113 0,-9.49439c-1.71201,-2.93327 -4.87079,-4.7175 -8.26678,-4.66947z"></path></g></g></svg>"""
        return mark_safe(f'<a href="{obj.url}" target="_blank">{obj.title} {external_link_icon}</a>')

    get_source_name.short_description = 'Source name'
    get_source_name.admin_order_field = 'source__name'

    get_hyperlinked_title.short_description = 'Title'
    get_hyperlinked_title.admin_order_field = 'title'


@admin.register(StaticTarget)
class StaticTargetModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active')
    search_fields = ('name', 'url')
    list_filter = ('is_active',)
