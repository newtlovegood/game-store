from django.contrib import admin

from comment.models import MPTTComment
from mptt.admin import MPTTModelAdmin


admin.site.register(MPTTComment, MPTTModelAdmin)

