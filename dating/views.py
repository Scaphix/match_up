from django.db import IntegrityError
from django.forms import ValidationError
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile, Preference
from .forms import PreferenceForm


class Home(generic.TemplateView):
    template_name = 'dating/index.html'


class ProfileGetStarted(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_signup')
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        return redirect('profile_about')


class ProfileList(LoginRequiredMixin, generic.ListView):
    """
    Redirect to connections discover view for better filtering.
    Kept for backward compatibility but redirects to discovery feed.
    """
    model = Profile
    template_name = 'dating/profile_list.html'
    context_object_name = 'profiles'

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.info(
                request,
                'You must create a profile to browse other profiles.'
            )
            return redirect('profile_create')
        # Redirect to connections discover view
        return redirect('connections:discover')


class ProfileCreate(LoginRequiredMixin, generic.CreateView):
    model = Profile
    fields = ['age', 'gender', 'location', 'bio', 'interests', 'photo']
    template_name = 'dating/profile_form.html'
    success_url = reverse_lazy('profile_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError:
            # Show a friendly error on the page instead of a 400
            form.add_error(None, "You already have a profile.")
            return self.form_invalid(form)
        except ValidationError as e:
            # Attach validation errors to the form and re-render
            error_msg = (
                e.message if hasattr(e, "message") else str(e)
            )
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
        return reverse_lazy('profile_detail', args=[self.object.pk])


class ProfileUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    fields = ['age', 'gender', 'location', 'bio', 'interests', 'photo']
    template_name = 'dating/profile_form.html'

    def get_object(self):
        return self.request.user.profile

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

    def get_success_url(self):
        return reverse_lazy('home')


class ProfileDetail(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'dating/profile_detail.html'
    context_object_name = 'profile'


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


class PreferenceCreate(LoginRequiredMixin, generic.CreateView):
    """
    Create user matching preferences.
    Should be created after profile creation.
    """
    model = Preference
    form_class = PreferenceForm
    template_name = 'dating/preference_form.html'

    def get(self, request, *args, **kwargs):
        """Check if user has a profile and doesn't already have preferences"""
        if not hasattr(request.user, 'profile'):
            messages.info(
                request,
                'You must create a profile before setting preferences.'
            )
            return redirect('profile_create')

        # Check if preferences already exist
        if hasattr(request.user, 'preference'):
            messages.info(
                request,
                'You already have preferences. You can edit them instead.'
            )
            return redirect('preference_update')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Set the user for the preference"""
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(
                None,
                "You already have preferences. Please edit them instead."
            )
            return self.form_invalid(form)

    def get_success_url(self):
        """Redirect to discovery after creating preferences"""
        messages.success(
            self.request,
            'Your preferences have been saved! Start discovering matches.'
        )
        return reverse_lazy('connections:discover')


class PreferenceUpdate(LoginRequiredMixin, generic.UpdateView):
    """
    Update existing user matching preferences.
    """
    model = Preference
    form_class = PreferenceForm
    template_name = 'dating/preference_form.html'

    def get(self, request, *args, **kwargs):
        """Check if user has a profile and preferences"""
        if not hasattr(request.user, 'profile'):
            messages.info(
                request,
                'You must create a profile before setting preferences.'
            )
            return redirect('profile_create')

        # Check if preferences exist, if not redirect to create
        if not hasattr(request.user, 'preference'):
            messages.info(
                request,
                'You don\'t have preferences yet. Create them first.'
            )
            return redirect('preference_create')

        return super().get(request, *args, **kwargs)

    def get_object(self):
        """Get the current user's preference"""
        return self.request.user.preference

    def get_success_url(self):
        """Redirect to profile about page after updating"""
        messages.success(self.request, 'Your preferences have been updated!')
        return reverse_lazy('profile_about')
