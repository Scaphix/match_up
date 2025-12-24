from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.views import generic
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from .models import Profile


class Home(generic.TemplateView):
    template_name = 'dating/index.html'


class ProfileGetStarted(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_signup')
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        return redirect('profile_about')


class ProfileCreate(LoginRequiredMixin, generic.CreateView):
    model = Profile
    fields = ['age', 'gender', 'location', 'bio', 'interests', 'photo']
    template_name = 'dating/profile_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            with transaction.atomic():
                response = super().form_valid(form)
            # Add success message after profile is created
            messages.success(
                self.request,
                'Profile successfully created! '
                'You can now browse other profiles.'
            )
            return response
        except IntegrityError:
            self.request.user.refresh_from_db()
            # Show a friendly error on the page instead of a 400
            form.add_error(None, "You already have a profile.")
            return self.form_invalid(form)
        except ValidationError as e:
            # Handle validation errors
            if hasattr(e, 'error_dict'):
                for field, errors in e.error_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                error_msg = str(e)
                form.add_error(None, error_msg)
            return self.form_invalid(form)
        except Exception:
            form.add_error(
                None,
                "Something went wrong while saving your profile. "
                "Please try again."
            )
            return self.form_invalid(form)
    # Redirect to profile detail page after successful profile creation

    def get_success_url(self):
        # Use reverse instead of reverse_lazy since object is already saved
        return reverse('profile_detail', args=[self.object.pk])


class ProfileUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    fields = ['age', 'gender', 'location', 'bio', 'interests', 'photo']
    template_name = 'dating/profile_form.html'

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add success message after profile is updated
        messages.success(
            self.request,
            'Your profile has been successfully updated!'
        )
        return response

    def get_success_url(self):
        return reverse_lazy('profile_about')


class ProfileDelete(LoginRequiredMixin, generic.DeleteView):
    model = Profile
    template_name = 'dating/profile_delete.html'

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user.profile

    def post(self, request, *args, **kwargs):
        # Add success message BEFORE deletion and redirect
        messages.success(
            request,
            'Your profile has been successfully deleted.'
        )
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('home')


class ProfileDetail(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'dating/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = '/connections/discover/'

        next_url = self.request.GET.get('origin')
        if next_url and url_has_allowed_host_and_scheme(
                        url=next_url, allowed_hosts=self.request.get_host()):
            context['next_url'] = next_url

        return context


class ProfileAbout(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'dating/profile_detail.html'
    context_object_name = 'profile'

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user.profile


class AboutView(generic.TemplateView):
    template_name = 'dating/about.html'


class ContactView(generic.TemplateView):
    template_name = 'dating/contact.html'
