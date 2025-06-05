# migration_script.py
# Run this to migrate data from Railway to AWS RDS

import os
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def migrate_database():
    """
    Script to migrate from Railway to AWS RDS
    """
    
    print("🚀 Starting database migration...")
    
    # Step 1: Backup current data
    print("📦 Creating data backup...")
    try:
        execute_from_command_line(['manage.py', 'dumpdata', '--output=railway_backup.json'])
        print("✅ Backup created: railway_backup.json")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return
    
    # Step 2: Update settings to point to RDS
    print("🔧 Updating database settings...")
    # (You'll need to manually update settings.py or environment variables)
    
    # Step 3: Run migrations on RDS
    print("🏗️  Running migrations on RDS...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return
    
    # Step 4: Load data into RDS
    print("📥 Loading data into RDS...")
    try:
        execute_from_command_line(['manage.py', 'loaddata', 'railway_backup.json'])
        print("✅ Data loaded successfully")
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return
    
    # Step 5: Create superuser (optional)
    print("👤 Creating superuser...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
    except Exception as e:
        print(f"⚠️  Superuser creation skipped: {e}")
    
    print("🎉 Migration completed successfully!")
    print("📋 Next steps:")
    print("   1. Update your Render environment variables")
    print("   2. Test your application")
    print("   3. Remove Railway database when confirmed working")


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
    django.setup()
    migrate_database()