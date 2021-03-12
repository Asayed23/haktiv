# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.utils.timesince import timesince


class TimeStampedModel(models.Model):
	"""
	Abstract base class that provides self-updating 'created' and 'modified' fields.
	"""
	created = models.DateTimeField(auto_now_add=True, editable=False)
	modified = models.DateTimeField(auto_now=True)

	ORDER_BY = (
		("created", _("Created Ascendant"),),
		("-created", _("Created Descendant"),),
		("modified", _("Modified Ascendant"),),
		("-modified", _("Modified Descendant"),),
	)
	ORDER_BY_DEFAULT = "-modified"

	class Meta:
		abstract = True
	def get_dict(self):
		from main.core.utils import readabledateformat
		return {
			"created": timezone.localtime(self.created).isoformat() if self.created else None,
			"createdf": readabledateformat(timezone.localtime(self.created)) if self.created else None,
			"createds": timesince(self.created) if self.created else None,
			"modified": timezone.localtime( self.modified).isoformat() if self.modified else None,
			"modifiedf": readabledateformat(timezone.localtime(self.modified)) if self.modified else None,
			"modifieds": timesince(self.modified) if self.modified else None,
			"is_edited": self.is_edited,
		}
	@property
	def is_edited(self):
		return False if self.created.strftime('%Y-%m-%d %H:%M:%S') == self.modified.strftime('%Y-%m-%d %H:%M:%S') else True

class UniqueIdentityModel(TimeStampedModel):
	class Meta:
		abstract = True
	guid = models.UUIDField(unique=True, default=uuid4, editable=False, verbose_name=_("Unique ID"),
		help_text=_("This field is automatically determined by the system, do not interfere.")
	)
