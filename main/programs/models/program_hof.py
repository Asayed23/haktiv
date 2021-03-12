# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models

from main.core.models import UniqueIdentityModel
from .program import Program

class ProgramHallOfFame(UniqueIdentityModel):
    """Hall of Fame Program"""
    class Meta:
        verbose_name = _("Program Hall Of Fame")
        verbose_name_plural = _("Program Hall Of Fame")
        ordering = ("-created",)

    is_top   = models.BooleanField(_("Is Top"), default=False)
    program  = models.ForeignKey(Program, verbose_name=_("Program"), null=True, blank=True,
                                related_name='program_hof', on_delete=models.SET_NULL)
    hacker   = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Program Hacker"),
                                 related_name='program_hof_hacker', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.program.title}" if self.program else str(_("Gost Program"))
