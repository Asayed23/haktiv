# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json

from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer
from main.notify.utils import get_user_channel


channel_layer = get_channel_layer()

def send_to_notfiy_ws(user, **kwargs):
	"""[Send Notification To WS]

	Args:
		user ([UserObject]): [User Object]
	"""
	session_group_name = "session_%s" % get_user_channel(user)
	AsyncToSync(channel_layer.group_send)(session_group_name, dict(
		type="data_handller",
		data=json.dumps(dict(
			**kwargs,
		))
	))
