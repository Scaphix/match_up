from django.views import generic
from .models import Profile


class Home(generic.TemplateView):
    template_name = 'dating/index.html'


class ProfileList(generic.ListView):
    queryset = Profile.objects.all().order_by("-createdAt")
    template_name = 'dating/profile_list.html'
    context_object_name = 'profiles'


