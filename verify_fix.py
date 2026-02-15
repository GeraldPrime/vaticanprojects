import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import FormUpload

def test_form_upload_save_robust():
    print("Testing robust FormUpload save...")
    try:
        # Create a dummy file
        dummy_file = SimpleUploadedFile("robust_test.txt", b"robust content")
        
        form = FormUpload(
            name="Robust Test Form",
            description="Testing manual ID assignment",
            form_file=dummy_file
        )
        form.save()
        print(f"Success! Form saved with ID: {form.id}")
        
        # Verify it actually exists in DB
        fetched = FormUpload.objects.get(id=form.id)
        print(f"Verified! Fetched from DB: {fetched.name} (ID: {fetched.id})")
        
    except Exception as e:
        print(f"Failed to save form. Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_form_upload_save_robust()
