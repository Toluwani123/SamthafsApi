from django.contrib import admin
from .models import *
from django.utils.html import format_html

# Register your models here.
admin.site.register(HomePage)
admin.site.register(TeamMember)
admin.site.register(Project)
admin.site.register(Challenge)
admin.site.register(Phase)
admin.site.register(ProjectGallery)

