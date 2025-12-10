from django.db import IntegrityError
from django.forms import ValidationError
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Profile


class Home(generic.TemplateView):
    template_name = 'dating/index.html'


class ProfileList(generic.ListView):
    queryset = Profile.objects.all().order_by("-createdAt")
    template_name = 'dating/profile_list.html'
    context_object_name = 'profiles'


class ProfileCreate(LoginRequiredMixin, generic.CreateView):
    model = Profile
    fields = ['age', 'gender', 'location', 'bio', 'interests', 'photo']
    template_name = 'dating/profile_form.html'
    success_url = reverse_lazy('profile_list')

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
            form.add_error(None, e.message if hasattr(e, "message") else str(e))
            return self.form_invalid(form)
        except Exception:
            form.add_error(None, "Something went wrong while saving your profile. Please try again.")
            return self.form_invalid(form)
    # Redirect to profile detail page after successful profile creation

    def get_success_url(self):
        return reverse_lazy('profile_detail', args=[self.object.pk])


class ProfileDetail(generic.DetailView):
    model = Profile
    template_name = 'dating/profile_detail.html'
    context_object_name = 'profile'
