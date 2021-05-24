from django.contrib import admin

from comment.models import Comment, MPTTComment
from mptt.admin import MPTTModelAdmin


admin.site.register(MPTTComment, MPTTModelAdmin)
admin.site.register(Comment)
# admin.site.register(MPTTComment)

# Register your models here.
