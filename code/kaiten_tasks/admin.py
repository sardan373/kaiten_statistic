from django.contrib import admin

from kaiten_tasks.models import KaitenUser, KaitenTask


@admin.register(KaitenUser)
class KaitenUserAdmin(admin.ModelAdmin):
    search_fields = ("name", "email")
    list_display = ("kaiten_id", "name", "email", "active")


@admin.register(KaitenTask)
class KaitenTaskAdmin(admin.ModelAdmin):
    search_fields = ("kaiten_id", "name")
    list_display = ("kaiten_id", "name")
