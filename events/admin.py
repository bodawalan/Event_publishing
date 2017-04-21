from django.contrib import admin
from .models import User, Article, Group, Slide, Event

class ArticleAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('title',)}

class GroupAdmin(ArticleAdmin):
	pass

class EventAdmin(ArticleAdmin):
	pass

admin.site.register(User)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Slide)
admin.site.register(Event, EventAdmin)