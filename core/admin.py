

# Register your models here.
from django.contrib import admin
from .models import Profile, Cow
from django.utils.html import format_html


class ProfileAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'age', 'image_preview')
	readonly_fields = ('image_preview',)

	def image_preview(self, obj):
		if obj.image and hasattr(obj.image, 'url'):
			return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
		return "-"
	image_preview.short_description = 'Preview'


class CowAdmin(admin.ModelAdmin):
	list_display = ('cow_id', 'temperature', 'heart_rate', 'activity_level', 'battery_level', 'latitude', 'longitude', 'timestamp')
	list_filter = ('cow_id', 'timestamp')
	search_fields = ('cow_id',)
	readonly_fields = ('timestamp', 'raw_data')
	ordering = ('-timestamp',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Cow, CowAdmin)
