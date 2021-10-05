from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views import generic
from django.urls import reverse_lazy
from .forms import LoginForm, SignupForm, PasswordResetForm, PasswordResetConfirmForm, ProfileForm
from django.shortcuts import render

User = get_user_model()


# Login
class Login(LoginView):
    form_class = LoginForm
    template_name = ''


# Signup
class Signup(generic.CreateView):
    template_name = ''
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        subject = render_to_string('email/account_activation_confirm_subject.txt', context).strip()
        message = render_to_string('email/account_activation_confirm_message.txt', context)
        print(subject)
        print(message)
        user.email_user(subject, message)
        return redirect('accounts:signup_activation_confirm')


class SignupActivationConfirm(generic.TemplateView):
    template_name = 'pages/signup_activation_confirm.html'
    pass

   
# Password Reset
class PasswordReset(PasswordResetView):
    pass


class PasswordResetDone(PasswordResetDoneView):
    
    template_name = ''
    pass


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = ''


class PasswordResetComplete(PasswordResetCompleteView):
    
    template_name = ''


@login_required
def profile(request):
    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect("/accounts/profile")
    else:
        profile_form = ProfileForm(instance=request.user)
    return render(request, "", context={"form": profile_form})