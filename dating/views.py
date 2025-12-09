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
    success_url = reverse_lazy('profile_form')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
