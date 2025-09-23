from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import UserProfile


@login_required
def profile_view(request):
    """View the user's profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)

    return render(request, "user_profile/profile.html", {"profile": profile})


@login_required
def profile_edit(request):
    """Edit the user's profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile:profile_view")
    else:
        form = UserProfileForm(instance=profile)

    return render(
        request, "user_profile/profile_edit.html", {"form": form, "profile": profile}
    )
