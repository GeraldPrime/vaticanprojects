import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import FormUpload

def test_form_upload_save():
    print("Attempting to save FormUpload...")
    try:
        # Create a dummy file
        dummy_file = SimpleUploadedFile("test_form.txt", b"dummy content")
        
        form = FormUpload(
            name="Test Form",
            description="Test Description",
            form_file=dummy_file
        )
        form.save()
        print(f"Success! Form saved with ID: {form.id}")
    except Exception as e:
        print(f"Failed to save form. Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_form_upload_save()
