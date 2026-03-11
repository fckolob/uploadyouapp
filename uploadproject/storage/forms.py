from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserFile
import mimetypes
import hashlib

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    import pyclamd
    CLAMD_AVAILABLE = True
except ImportError:
    CLAMD_AVAILABLE = False

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
        
        # Read file content for MIME detection and virus scan
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Use python-magic for content-based MIME detection if available
        if MAGIC_AVAILABLE:
            mime = magic.from_buffer(file_content[:1024], mime=True)
        else:
            mime, _ = mimetypes.guess_type(file_name)
        
        if mime and mime not in self.ALLOWED_MIME_TYPES:
            raise forms.ValidationError("Invalid file type.")
        
        # Virus scan with ClamAV if available
        if CLAMD_AVAILABLE:
            try:
                cd = pyclamd.ClamdNetworkSocket(host='127.0.0.1', port=3310)
                result = cd.scan_stream(file_content)
                if result:
                    raise forms.ValidationError("File contains malware.")
            except Exception as e:
                # If ClamAV is not available or fails, log but don't block
                pass
        
        # Prevent double extension attacks (e.g., .php.jpg)
        base_name = file.name.rsplit('.', 1)[0]
        if '.' in base_name:
            raise forms.ValidationError(
                "Files with multiple dots in the name are not allowed."
            )
        
        return file
