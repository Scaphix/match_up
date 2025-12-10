from django.db import IntegrityError
from django.forms import ValidationError
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile


class Home(generic.TemplateView):
    template_name = 'dating/index.html'


class ProfileList(LoginRequiredMixin, generic.ListView):
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
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Profile.objects.all().order_by("-createdAt")
        # Exclude current user's profile if they have one
        if hasattr(self.request.user, 'profile'):
            queryset = queryset.exclude(user=self.request.user)
        return queryset


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
