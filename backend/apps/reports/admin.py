from django.contrib import admin
from .models import DailyStatistics, MonthlyStatistics, ReportTemplate, NightAudit, AuditLog


@admin.register(DailyStatistics)
class DailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ('property', 'date', 'rooms_sold', 'occupancy_percent', 'adr', 'revpar', 'total_revenue')
    list_filter = ('property', 'date')


@admin.register(MonthlyStatistics)
class MonthlyStatisticsAdmin(admin.ModelAdmin):
    list_display = ('property', 'year', 'month', 'avg_occupancy', 'avg_adr', 'total_revenue')
    list_filter = ('property', 'year')


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'property', 'is_scheduled', 'created_by')
    list_filter = ('report_type', 'is_scheduled')


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0


@admin.register(NightAudit)
class NightAuditAdmin(admin.ModelAdmin):
    list_display = ('property', 'business_date', 'status', 'total_revenue', 'rooms_sold', 'completed_at')
    list_filter = ('property', 'status')
    inlines = [AuditLogInline]
