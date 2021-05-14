from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.views.generic.edit import FormMixin


from .forms import ProfileUpdateForm, CustomUserChangeForm


@login_required
def profile_update(request):

    if request.method == 'POST':
        form_user = CustomUserChangeForm(request.POST, instance=request.user)
        form_profile = ProfileUpdateForm(request.POST,
                                         request.FILES,
                                         instance=request.user.profile)
        if form_user.is_valid() and form_profile.is_valid():
            form_user.save()
            form_profile.save()
            return redirect('profile')
    else:
        form_user = CustomUserChangeForm(instance=request.user)
        form_profile = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'form_user': form_user,
        'form_profile': form_profile
    }

    return render(request, 'account/profile.html', context)


class ProfileUpdate(View):

    template_name = 'account/profile.html'

    def get(self, request, *args, **kwargs):
        form_user = CustomUserChangeForm(instance=request.user)
        form_profile = ProfileUpdateForm(instance=request.user.profile)
        context = {'form_user': form_user, 'form_profile': form_profile}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        form_user = CustomUserChangeForm(request.POST, instance=request.user)
        form_profile = ProfileUpdateForm(request.POST,
                                         request.FILES,
                                         instance=request.user.profile)
        if form_user.is_valid() and form_profile.is_valid():
            form_user.save()
            form_profile.save()
            return redirect('profile')

        context = {'form_user': form_user, 'form_profile': form_profile}
        render(request, self.template_name, context)


