# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.conf import settings

from main.core.models import TimeStampedModel
from main.core.utils.cryptography import sha1

import os, re, math, mimetypes, uuid

def _handle_file(instance, filename):
	fn, fx = os.path.splitext(filename)
	return "{0}/{1}".format("hacktive-files", "{0}{1}".format(slugify(sha1(uuid.uuid4().hex)), fx))

class FileManager(TimeStampedModel):
	class Meta:
		verbose_name = _("File Manager")
		verbose_name_plural = _("Files Manager")
		ordering = ("-created",)
		
	STORAGES = (
		('local', _("Local")),
		('remote', _("Remote")),
	)

	VIDEO = "video"
	IMAGE = "image"
	AUDIO = "audio"
	DOCUMENT = "document"
	ZIPPED = "zipped"
	URL = "url"
	UNKNOWN = "unknown"

	FILETYPES = (
		(VIDEO,_("Video"),),
		(IMAGE,_("Image"),),
		(AUDIO,_("Audio"),),
		(DOCUMENT,_("Document"),),
		(ZIPPED,_("Zipped"),),
		(URL, _("URL")),
		(UNKNOWN,_("Unknown"),),
	)
	is_active 	= models.BooleanField(verbose_name=_("Is Active"), default=True)
	title 		= models.CharField(_("Title"), max_length=155, default=_("Untitled"))
	storage 	= models.CharField(_("Storage"), max_length=24, default="local", choices=STORAGES)
	url         = models.URLField(verbose_name=_("URL"), blank=True, help_text=_("YouTube link e.g. https://youtu.be/0bj4i-sW44s"))
	source 		= models.FileField(_("File"), upload_to=_handle_file, blank=True)
	size 		= models.BigIntegerField(default=0, verbose_name=_("Size"))
	filetype	= models.CharField(_("File Type"), max_length=24, blank=False, null=True, choices=FILETYPES)
	mimetype 	= models.CharField(_("Mime Type"), max_length=100, blank=False, null=True)
	extension 	= models.CharField(_("Extension"), max_length=10, blank=False, null=True)
	user 		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.deletion.CASCADE ,blank=False, null=True, verbose_name=_("Publisher"))
	
	def __init__(self, *args, **kwargs):
		super(FileManager, self).__init__(*args, **kwargs)
		self._source = self.source
	def __str__(self):
		return self.title
	def delete(self, *args, **kwargs):
		#self.source.delete(save=False)
		super(FileManager, self).delete(*args, **kwargs)
	def save(self, *args, **kwargs):
		if self.url:
			self.storage = "remote"
			self.filetype = "url"
		elif self.source:
			if self._source != self.source and self._source:
				pass
				#self._source.delete(save=False)
			filename = self.source.name
			name, extension = os.path.splitext(filename)
			self.extension = extension.lower()[1:]
			mimetype = mimetypes.guess_type(self.source.path)[0]
			self.mimetype = mimetype if mimetype else ''
			self.size = self.source.size
			if self.extension in ["mp4", "avi", "ogg", "flv", "qt", "webm", "3gp", "wmv", "mpeg"]:
				self.filetype = "video"
				destination = "{0}/{1}".format(settings.DEFAULT_MEDIAHUB_FOLDER, self.source.name)
			elif self.extension in ["png", "tiff", "bmp", "jpeg", "jpg", "gif"]:
				self.filetype = "image"
			elif self.extension in ["wav", "opus", "flac", "acc", "mp3"]:
				self.filetype = "audio"
			elif self.extension in ["pdf", "doc", "docx", "docm", "dotm", "dotx", "xls", "xlsx", "html", "htm", "odt", 
				"rtf", "txt", "wps", "xml", "xps", "csv", "dbf", "dif", "odt", "odp", "ppt", "pptx"]:
				self.filetype = "document"
			elif self.extension in ["zip", "rar", "7z", "tar.gz", "gz"]:
				self.filetype = "zipped"
			else:
				self.filetype = "unknown"
			if not self.title or self.title == _("Untitled"):
				"""Given title name for untitled obj"""
				self.title 	= re.sub(r'[\W_]', ' ', name)
				self.title 	= ' '.join(self.title.split())

		super(FileManager, self).save(*args, **kwargs)
	@property
	def src(self):
		url = ""
		if self.source:
			url = self.source.url
		elif self.url:
			url = self.url
		return url
	def get_byte2size(self):
		size = self.size if self.size else 0
		sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
		if size == 0:
			return '0 Byte'
		i = int(math.floor(math.log(size) / math.log(1024)))
		return "{0} {1}".format(round(size / math.pow(1024, i), 2), sizes[i])
	get_byte2size.short_description = _("Size")

	def get_dict(self):
		return {
			"pk": self.pk,
			"title": self.title,
			"is_active": self.is_active,
			"storage": self.get_storage_display(),
			"storage0": self.storage,
			"source": {"name": self.source.name, "url": self.source.url} if self.source else {"name": "", "url": ""},
			"size": self.size,
			"url": self.url,
			"src": self.src,
			"filetype": self.get_filetype_display(),
			"filetype0": self.filetype,
			"mimetype": self.mimetype,
			"extension": self.extension,
			"size_text": self.get_byte2size(),
		}

def get_byte2size(size):
	size = size if size else 0
	sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
	if size == 0:
		return '0 Byte'
	i = int(math.floor(math.log(size) / math.log(1024)))
	return "{0} {1}".format(round(size / math.pow(1024, i), 2), sizes[i])

