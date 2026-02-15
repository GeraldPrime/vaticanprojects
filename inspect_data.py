import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import FormUpload

def inspect_data():
    print("Inspecting FormUpload data...")
    all_forms = FormUpload.objects.all()
    print(f"Total forms: {all_forms.count()}")
    for form in all_forms:
        print(f"ID: {form.id}, Name: {form.name}, File: {form.form_file}")
        if form.id is None:
            print("WARNING: FOUND FORM WITH ID NONE!")

if __name__ == "__main__":
    inspect_data()
