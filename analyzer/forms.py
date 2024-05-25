from django import forms
from .models import UploadedImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
        labels = {
            'image': '', 
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={'style': 'border: 1px solid #ccc; padding: 5px; border-radius:10px'})
        }
