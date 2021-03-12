# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from main.filemanager.models import FileManager
from django.utils.html import format_html
from main.core.utils import USER_SEARCH_FIELDS

@admin.register(FileManager)
class FileManagerAdmin(admin.ModelAdmin):
	list_display = ("title", "is_active", "user", "storage", "filetype", "extension", "get_byte2size", "get_preview",
					"created",)
	list_filter = ("filetype", "storage",)
	search_fields = ("title",) + USER_SEARCH_FIELDS
	def get_preview(self, obj):
		return format_html('<a href="{}" target="_blank"><i class="icon-search"></i></a>'.format(obj.src))
	get_preview.allow_tags = True
	get_preview.short_description = _("Preview")

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ("user", "is_active", "get_byte2size", "extension", "size", "tags", "mimetype", "download",
						"filetype", "storage")
		form = super(FileManagerAdmin, self).get_form(request, obj, **kwargs)
		return form

