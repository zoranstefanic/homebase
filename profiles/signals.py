from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        profile = Profile(user=user)
        profile.save()

