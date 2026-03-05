from django.contrib import admin
from django.utils.html import format_html
from .models import *

class OyuncuSportInline(admin.TabularInline):
    model = OyuncuSport
    extra = 1

@admin.register(Fakultet)
class FakultetAdmin(admin.ModelAdmin):
    list_display = ['ady', 'gysgaltma', 'binasy']
    search_fields = ['ady', 'gysgaltma']

@admin.register(SportGornushi)
class SportGornushiAdmin(admin.ModelAdmin):
    list_display = ['ady', 'toparlygy']
    list_filter = ['toparlygy']
    search_fields = ['ady']

@admin.register(Oyuncu)
class OyuncuAdmin(admin.ModelAdmin):
    list_display = ['familiyasy', 'ady', 'fakultet', 'kurs', 'topar', 'esasgy_sport', 'surat_gorkez']
    list_filter = ['fakultet', 'kurs', 'esasgy_sport', 'aktiv']
    search_fields = ['ady', 'familiyasy', 'topar']
    inlines = [OyuncuSportInline]
    
    def surat_gorkez(self, obj):
        if obj.surat:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.surat.url)
        return "Surat ýok"
    surat_gorkez.short_description = 'Suraty'

@admin.register(Yarys)
class YarysAdmin(admin.ModelAdmin):
    list_display = ['ady', 'sport_gornushi', 'baslanjak_sene', 'yer', 'status']
    list_filter = ['status', 'sport_gornushi', 'baslanjak_sene']
    search_fields = ['ady', 'yer']
    date_hierarchy = 'baslanjak_sene'

@admin.register(YarysGatnashyk)
class YarysGatnashykAdmin(admin.ModelAdmin):
    list_display = ['yarys', 'oyuncu', 'netije', 'orun']
    list_filter = ['netije', 'yarys__sport_gornushi']
    search_fields = ['oyuncu__ady', 'oyuncu__familiyasy', 'yarys__ady']