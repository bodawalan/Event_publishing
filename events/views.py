from django.shortcuts import render, redirect, reverse
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, password_validation, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import View
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views import generic

from django.template import Context
from django.template.loader import get_template

from datetime import date
from .models import User, Article, Group, Slide, Event, SendEmails, InviteUser, NotifyAll, NotifyUser, Notification
from .forms import UserForm, ProfileForm

class HomeView(View):
	groups = Group.objects.all()
	slides = Slide.objects.all()
	template_name = 'events/home.html'
	context = {
	'groups': groups,
	'slides': slides
	}

	def get(self, request):
		return render(request, self.template_name, self.context)

class EventsView(generic.ListView):
	template_name = 'events/events.html'

	def get_queryset(self):
		event_list = Event.objects.all()
		paginator = Paginator(event_list, 10)

		page = self.request.GET.get('page')
		try:
			events = paginator.page(page)
		except PageNotAnInteger:
       # If page is not an integer, deliver first page.
			events = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			events = paginator.page(paginator.num_pages)

		return events

class EventView(generic.DetailView):
	model = Event
	template_name = 'events/event.html'

class NewsView(generic.ListView):
	template_name = 'events/news.html'

	def get_queryset(self):
		article_list = Article.objects.all()
		paginator = Paginator(article_list, 10)

		page = self.request.GET.get('page')
		try:
			news = paginator.page(page)
		except PageNotAnInteger:
       # If page is not an integer, deliver first page.
			news = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			news = paginator.page(paginator.num_pages)

		return news

class ArticleView(generic.DetailView):
	model = Article
	template_name = 'events/article.html'

class AboutView(View):
	template_name = 'events/about.html'

	def get(self, request):
		return render(request, self.template_name, {})

class ResetView(View):
	template_name = 'events/resetpassword.html'

	def get(self, request):
		return render(request, self.template_name, {})

class DashboardView(LoginRequiredMixin, View):
	redirect_field_name = ''
	template_name = 'user/dashboard.html'

	def get(self, request):
		event_list = Event.objects.all()
		paginator = Paginator(event_list, 10)

		page = self.request.GET.get('page')
		try:
			events = paginator.page(page)
		except PageNotAnInteger:
       # If page is not an integer, deliver first page.
			events = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			events = paginator.page(paginator.num_pages)

		return render(request, self.template_name, {'object_list': events})

class EventCreateView(LoginRequiredMixin, CreateView):
	redirect_field_name = ''
	model = Event
	fields = ['title', 'slug', 'content', 'thumbnail','start_date', 'end_date']
	template_name = 'user/event_edit.html'
	success_url = '/dashboard/'

	def form_valid(self, form):
	    form.instance.created_by = self.request.user
	    subject = "New event on EventsFBU"
	    text = get_template('events/notification_email.txt')
	    html = get_template('events/notification_email.html')
	    text_content = text.render({'event': form.instance})
	    html_content = html.render({'event': form.instance})
	    SendEmails(subject, text_content, html_content)

	    message = "You have been invited to " + form.instance.title
	    link = form.instance.slug.split("/")[-1]
	    NotifyAll(message, link)
	    return super(EventCreateView, self).form_valid(form)

class EventEditView(LoginRequiredMixin, UpdateView):
	redirect_field_name = ''
	model = Event
	fields = ['title', 'slug', 'content', 'thumbnail','start_date', 'end_date']
	template_name = 'user/event_edit.html'
	template_name_suffix = '_update_form'
	success_url = '/dashboard/'

	def get_queryset(self):
	    base_qs = super(EventEditView, self).get_queryset()
	    return base_qs.filter(created_by=self.request.user)

class EventDeleteView(LoginRequiredMixin, DeleteView):
	redirect_field_name = ''
	model = Event
	success_url = '/dashboard/'

	def get_object(self, queryset=None):
		obj = super(EventDeleteView, self).get_object()
		if not obj.created_by == self.request.user:
			raise Http404
		return obj

class ProfileView(View):
	update_profile_form = ProfileForm
	template_name = 'user/profile.html'

	def get(self, request):
		if request.user.is_authenticated():
			form = self.update_profile_form(instance = request.user)
			return render(request, self.template_name, {'form': form})
		else:
			return redirect('home')

	def post(self, request):
		if request.user.is_authenticated():
			form = self.update_profile_form(request.POST, request.FILES, instance = request.user)
			if form.is_valid():
				form.save()
				messages.success(request, 'Your profile was successfully updated!')
				return redirect('profile')
		else:
			return redirect('home')

		return render(request, self.template_name, {'form': form})

class PasswordChangeView(View):
	change_password_form = PasswordChangeForm
	template_name = 'user/password_change.html'

	def get(self, request):
		if request.user.is_authenticated():
			form = self.change_password_form(request.user)
			return render(request, self.template_name, {'form': form})
		else:
			return redirect('home')

	def post(self, request):
		if request.user.is_authenticated():
	 		form = self.change_password_form(request.user, request.POST)
	 		if form.is_valid():
	 			user = form.save()
	 			update_session_auth_hash(request, user)
	 			messages.success(request, 'Your password was successfully updated!')
	 			return redirect('password_change')
		else:
	 		return redirect('home')

		return render(request, self.template_name, {'form': form})

class LoginView(View):
	template_name = 'user/login.html'

	def get(self, request):
		return render(request, self.template_name, {})

	def post(self, request):
		errors = []
		email = request.POST['email']
		password = request.POST['password']
		
		user = authenticate(email=email, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('dashboard')
			else:
				errors.append('User is inactive.')
		else:
			errors.append('Wrong password or email.')

		return render(request, self.template_name, {'errors': errors})

class LogoutView(View):
	def get(self, request):
		logout(request)

		return redirect('home');

class RegisterView(View):
	form_class = UserForm
	template_name = 'user/register.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = self.form_class(request.POST)
		errors = []

		if form.is_valid():
			try:
				user = form.save(commit=False)

				email = form.cleaned_data['email']
				password = form.cleaned_data['password']
				cpassword = request.POST['password_confirmation']

				if password != cpassword:
				 	errors.append("The two password fields didn't match.")
				 	return render(request, self.template_name, {'form': form, 'errors': errors})
				
				password_validation.validate_password(password)

				user.set_password(password)
				user.save()

				user = authenticate(email=email, password=password)

				if user is not None:
					if user.is_active:
						login(request, user)
						return redirect('dashboard')
			except Exception:
				errors.append('Something went wrong!')
		else:
			er = form.errors
			for i in er:
				errors.append(er[i][0])

		return render(request, self.template_name, {'form': form, 'errors': errors})

class InviteUserSuccessView(View):
	template_name = 'events/invite_user_success.html'

	def get(self, request, slug):
		return render(request, self.template_name)

	def post(self, request, slug):
		event = Event.objects.get(slug=slug)
		try:
			email = request.POST['email']
			subject ="You are invited"
			text = get_template('events/notification_email.txt')
			html = get_template('events/notification_email.html')
			text_content = text.render({'event': event})
			html_content = html.render({'event': event})
			InviteUser(subject, email, text_content, html_content)
			messages.success(request, 'Invite sent successfully.')

			user = User.objects.get(email=email)
			if user:
				message = "You have been invited to " + event.title
				link = event.slug
				NotifyUser(user, message, link)

			return redirect('invite_user_success',slug=slug)

		except Exception:
			pass
		
		return redirect('invite_user_success', slug=slug)

class JoinEventView(View):
	def get(self, request, slug):
		return redirect('event',slug=slug)

	def post(self, request, slug):
		if request.user:
			if request.user.is_authenticated():
				event = Event.objects.get(slug=slug)
				event.users.add(request.user)
				return redirect('event',slug=slug)
		return redirect('home')

class LeaveEventView(View):
	def get(self, request, slug):
		return redirect('event',slug=slug)

	def post(self, request, slug):
		if request.user:
			if request.user.is_authenticated():
				event = Event.objects.get(slug=slug)
				event.users.remove(request.user)
				return redirect('event',slug=slug)
		return redirect('home')

class NotificationDeleteView(LoginRequiredMixin, View):
	redirect_field_name = ''

	def post(sel, request, pk):
		try:
			notification = Notification.objects.get(pk=pk)
			if notification.user == request.user:
				notification.delete()
		except Exception:
			pass

		return HttpResponse('OK')