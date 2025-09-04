from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Contact
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages
from .forms import ContactForm, FeedbackForm, SignupForm

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.email:  # only if email is provided
                body = (
                    f"Hello {user.username},\n\n"
                    "Welcome to Contact Book! \n\n"
                    "Your registration was successful. You can now log in and start adding contacts.\n\n"
                    "Thanks,\n"
                    "Contact Book Team"
                )
                msg = EmailMessage(
                    subject="Registration Successful - Contact Book",
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,  # your Gmail
                    to=[user.email],  # send directly to the registered user
                )
                msg.send()
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def home(request):
    contacts = Contact.objects.filter(user=request.user).order_by("-created_at")
    # templates in app: contacts/templates/contacts/home.html
    return render(request, "contacts/home.html", {"contacts": contacts})

from django.core.mail import EmailMessage

@login_required
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()

            # Email admin with reply-to pointing to the signed-in user's email
            body = (
                f"User: {request.user.username} ({request.user.email or 'no email'})\n"
                f"Added Contact: {contact.name}\n"
                f"Email: {contact.email}\n"
                f"Phone: {contact.phone or '-'}\n"
                f"Notes: {contact.notes or '-'}\n"
            )

            msg = EmailMessage(
                subject="New Contact Added",
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,              
                to=[settings.EMAIL_HOST_USER],                     
                reply_to=[request.user.email] if request.user.email else None,
            )
            msg.send(fail_silently=False)

            messages.success(request, "Contact saved and admin notified.")
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

