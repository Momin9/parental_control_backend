from django.contrib import admin

from api.models import User, Child, BlockedURL

admin.site.register(User)
admin.site.register(Child)
admin.site.register(BlockedURL)
