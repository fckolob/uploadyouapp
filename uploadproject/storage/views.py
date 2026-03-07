from django.shortcuts import render


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import FileResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .forms import RegisterForm, UploadFileForm
from .models import UserFile
import logging
from datetime import timedelta
from django.utils import timezone
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

# Rate limiting decorator
def rate_limit_uploads(uploads_per_hour=10):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Check uploads in the last hour
                one_hour_ago = timezone.now() - timedelta(hours=1)
                recent_uploads = UserFile.objects.filter(
                    user=request.user,
                    uploaded_at__gte=one_hour_ago
                ).count()
                
                if recent_uploads >= uploads_per_hour:
                    logger.warning(f"Rate limit exceeded for user {request.user.username}")
                    return HttpResponseForbidden(
                        "Too many uploads. Maximum 10 uploads per hour."
                    )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Register
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f"New user registered: {user.username}")
                login(request, user)
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                form.add_error(None, "Registration failed. Please try again.")
    else:
        form = RegisterForm()
    return render(request, 'storage/register.html', {'form': form})


# Dashboard
@login_required
@require_http_methods(["GET"])
def dashboard(request):
    files = UserFile.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'storage/dashboard.html', {'files': files})


# Upload with rate limiting
@login_required
@rate_limit_uploads(uploads_per_hour=10)
@require_http_methods(["GET", "POST"])
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file_instance = form.save(commit=False)
                file_instance.user = request.user
                file_instance.original_name = request.FILES['file'].name
                file_instance.save()
                logger.info(f"File uploaded by {request.user.username}: {file_instance.original_name}")
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"File upload error for user {request.user.username}: {str(e)}")
                form.add_error('file', 'File upload failed. Please try again.')
        else:
            logger.warning(f"Invalid form submission from {request.user.username}: {form.errors}")
    else:
        form = UploadFileForm()
    return render(request, 'storage/upload.html', {'form': form})


# Download with access control
@login_required
@require_http_methods(["GET"])
def download_file(request, file_id):
    try:
        file = get_object_or_404(UserFile, id=file_id, user=request.user)
        logger.info(f"File downloaded by {request.user.username}: {file.original_name}")
        return FileResponse(file.file.open(), as_attachment=True)
    except Exception as e:
        logger.error(f"Download error for user {request.user.username}: {str(e)}")
        return HttpResponseForbidden("Access denied")


# Delete with access control
@login_required
@require_http_methods(["POST"])
def delete_file(request, file_id):
    try:
        file = get_object_or_404(UserFile, id=file_id, user=request.user)
        file_name = file.original_name
        file.file.delete()
        file.delete()
        logger.info(f"File deleted by {request.user.username}: {file_name}")
        return redirect('dashboard')
    except Exception as e:
        logger.error(f"Delete error for user {request.user.username}: {str(e)}")
        return HttpResponseForbidden("Access denied")


# Login
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}")
            # Redirect to the 'next' parameter or dashboard
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            logger.warning("Failed login attempt")
    else:
        form = AuthenticationForm()
    
    # Pass the 'next' parameter to the template
    next_param = request.GET.get('next', '')
    return render(request, 'storage/login.html', {'form': form, 'next': next_param})


# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

