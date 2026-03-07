from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserFile
import mimetypes

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UploadFileForm(forms.ModelForm):
    # Whitelist of allowed file extensions
    ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx', '.xlsx', '.pptx', 
                          '.jpg', '.jpeg', '.png', '.gif', '.zip']
    
    # Whitelist of allowed MIME types
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/zip',
    ]
    
    class Meta:
        model = UserFile
        fields = ['file']
    
    def clean_file(self):
        file = self.cleaned_data['file']
        
        # 10MB limit
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError(
                f"File too large. Maximum size is 10MB, but you uploaded {file.size / (1024*1024):.2f}MB"
            )
        
        # Check file extension
        file_name = file.name.lower()
        if not any(file_name.endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            allowed = ', '.join(self.ALLOWED_EXTENSIONS)
            raise forms.ValidationError(
                f"File type not allowed. Allowed types: {allowed}"
            )
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise forms.ValidationError(
                f"Invalid file format. MIME type {mime_type} is not allowed."
            )
        
        # Prevent double extension attacks (e.g., .php.jpg)
        base_name = file.name.rsplit('.', 1)[0]
        if '.' in base_name:
            raise forms.ValidationError(
                "Files with multiple dots in the name are not allowed."
            )
        
        return file
