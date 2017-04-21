from __future__ import unicode_literals

from django.db import models
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    name = models.CharField(_('last name'), max_length=30, blank=True)
    student_id = models.CharField(max_length=10, blank=True)
    is_organization = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    avatar = models.ImageField(upload_to = 'user/', null=True, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the display name.
        '''
        return self.name

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_notifications(self):
        return Notification.objects.filter(user = self.id).exclude(viewed = True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length = 200)
    slug = models.SlugField(unique = True)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to = 'article/', null = True, blank = True)
    updated = models.DateTimeField(auto_now = True, auto_now_add = False)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ["-timestamp"]

class Article(Post):
    user = models.ForeignKey(User, on_delete = models.CASCADE)

class Group(Post):
    user = models.ForeignKey(User, on_delete = models.CASCADE)

class Event(Post):
    users = models.ManyToManyField(User)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank = True, null=True)
    created_by = models.ForeignKey(User, on_delete = models.CASCADE,
        related_name="created_by")

class Slide(models.Model):
    headline =  models.CharField(max_length = 200, blank = True, help_text = 'Optional')
    text = models.TextField(blank = True, help_text = 'Optional')
    image = models.ImageField(upload_to = 'slides/', null = True)
    link_title = models.CharField(_('link title'), max_length = 100, blank = True, help_text = 'Optional')
    link = models.URLField(blank = True, help_text = 'Optional')

    def __str__(self):
        return str(self.id)

class Notification(models.Model):
    message = models.CharField(max_length = 255, blank = True)
    link = models.URLField()
    viewed = models.BooleanField(default=False)
    user =  models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-id"]

def SendEmails(subject, text_content, html_content):
    recievers = []
    for user in User.objects.all():
        recievers.append(user.email)
    email = EmailMultiAlternatives(subject, text_content, "admin@eventsfbu.com", recievers)
    email.attach_alternative(html_content, "text/html")
    email.send()

def InviteUser(subject, to, text_content, html_content):
    email = EmailMultiAlternatives(subject, text_content, "admin@eventsfbu.com", [to,])
    email.attach_alternative(html_content, "text/html")
    email.send()

def NotifyAll(message, link):
    notifications = []
    for user in User.objects.all():
        notifications.append(Notification(user=user, message=message, link=link))
    Notification.objects.bulk_create(notifications)

def NotifyUser(user, message, link):
    Notification.objects.create(user=user, message=message, link=link)