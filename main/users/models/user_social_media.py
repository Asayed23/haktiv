from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models

from main.core.models import UniqueIdentityModel

class UserSocialMedia(UniqueIdentityModel):
    class Meta:
        verbose_name = _("User Social Media")
        verbose_name_plural = _("User Social Medias")
        ordering = ("user",)
        unique_together = ("user", "social",)

    FACEBOOK = "facebook"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    GITHUB = "github"
    GITLAB = "gitlab"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    WEBSITE = "website"
    OTHER = "other"
    SOCIALS = (
        (FACEBOOK, _("Facebook")),
        (TWITTER, _("Twitter")),
        (INSTAGRAM, _("Instagram")),
        (YOUTUBE, _("Youtube")),
        (GITHUB, _("Github")),
        (GITLAB, _("Gitlab")),
        (LINKEDIN, _("LinkedIn")),
        (TWITCH, _("Twitch")),
        (WEBSITE, _("Website")),
        (OTHER, _("Other")),
    )
    # Social Media
    social = models.CharField(_("Social Media"), max_length=24, choices=SOCIALS, default=OTHER)
    link = models.URLField(_("link"), blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.social} {self.user.get_short_name()}"
