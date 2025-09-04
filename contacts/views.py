from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import ContactForm, FeedbackForm
from .models import Contact
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = UserCreationForm()

    # If your template is inside the app:
    return render(request, "contacts/registration/signup.html", {"form": form})
    # If you kept it at project-level `templates/registration/`, use this instead:
    # return render(request, "registration/signup.html", {"form": form})

@login_required
def home(request):
    contacts = Contact.objects.filter(user=request.user).order_by("-created_at")
    # templates in app: contacts/templates/contacts/home.html
    return render(request, "contacts/home.html", {"contacts": contacts})

@login_required
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()

            # Notify admin (safe)
            try:
                send_mail(
                    subject="New Contact Added",
                    message=f"{request.user.username} added {contact.name} ({contact.email})",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception as e:
                messages.warning(request, f"Could not send email: {e}")

            messages.success(request, "Contact saved successfully.")
            return redirect("home")
    else:
        form = ContactForm()
    return render(request, "contacts/add_contact.html", {"form": form})

@login_required
def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            try:
                send_mail(
                    subject=f"Feedback from {request.user.username}: {subject}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, "Feedback sent. Thank you!")
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception as e:
                messages.warning(request, f"Could not send email: {e}")

            return redirect("home")
    else:
        form = FeedbackForm()
    return render(request, "contacts/feedback.html", {"form": form})



@login_required
def logout_then_redirect(request):
    logout(request)
    return redirect("login")