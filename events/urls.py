from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name = 'home'),
    url(r'^events/invite_user_success/(?P<slug>[\w-]+)/$', views.InviteUserSuccessView.as_view(), name = 'invite_user_success'),
    url(r'^events/join_event/(?P<slug>[\w-]+)/$', views.JoinEventView.as_view(), name = 'join_event'),
    url(r'^events/leave_event/(?P<slug>[\w-]+)/$', views.LeaveEventView.as_view(), name = 'leave_event'),
    url(r'^events/$', views.EventsView.as_view(), name = 'events'),
    url(r'^events/(?P<slug>[\w-]+)/$', views.EventView.as_view(), name='event'),
    url(r'^news/$', views.NewsView.as_view(), name = 'news'),
    url(r'^news/(?P<slug>[\w-]+)/$', views.ArticleView.as_view(), name='article'),
    url(r'^about/$', views.AboutView.as_view(), name = 'about'),
    url(r'^register/$', views.RegisterView.as_view(), name = 'register'),
    url(r'^login/$', views.LoginView.as_view(), name = 'login'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^logout/$', views.LogoutView.as_view(), name = 'logout'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name = 'dashboard'),
    url(r'^dashboard/event_create/$', views.EventCreateView.as_view(), name = 'event_create'),
    url(r'^dashboard/event_edit/(?P<slug>[\w-]+)/$', views.EventEditView.as_view(), name = 'event_edit'),
    url(r'^dashboard/event_delete/(?P<slug>[\w-]+)/$', views.EventDeleteView.as_view(), name = 'event_delete'),
    url(r'^dashboard/profile/$', views.ProfileView.as_view(), name = 'profile'),
    url(r'^dashboard/password_change/$', views.PasswordChangeView.as_view(), name = 'password_change'),
    url(r'^notification_delete/(?P<pk>\d+)/$', views.NotificationDeleteView.as_view(), name = 'notification_delete'),
]
