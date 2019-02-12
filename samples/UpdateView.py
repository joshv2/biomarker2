from django.views.generic import UpdateView

class EditUserProfileView(UpdateView) #Note that we are using UpdateView and not FormView
    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/user_profile.html"

    def get_object(self, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['pk'])

        # We can also get user object using self.request.user  but that doesnt work
        # for other models.

        return user.userprofile

    def get_success_url(self, *args, **kwargs):
        return reverse("some url name")