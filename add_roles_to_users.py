"""
Script to add role field to existing users in the database.
Run this after adding the role field to the User model.

Usage:
    python manage.py shell < add_roles_to_users.py
    
Or:
    python manage.py shell
    >>> exec(open('add_roles_to_users.py').read())
"""

from users.models import User

print("\n" + "="*60)
print("  Adding Role Field to Existing Users")
print("="*60 + "\n")

# Get all users
all_users = User.objects.all()
total_users = all_users.count()

print(f"Found {total_users} user(s) in database\n")

if total_users == 0:
    print("No users found. Database is empty.")
    print("\nDone!")
    exit()

# Update users without role or with empty role
users_to_update = User.objects.filter(role__in=['', None]) | User.objects.exclude(role__in=['user', 'admin'])
users_to_update_count = users_to_update.count()

if users_to_update_count == 0:
    print("✅ All users already have valid roles!")
    print("\nCurrent user roles:")
    for user in all_users:
        role_icon = "👑" if user.role == 'admin' else "👤"
        print(f"  {role_icon} {user.email}: {user.role}")
    print("\nDone!")
    exit()

print(f"Found {users_to_update_count} user(s) that need role update\n")
print("Users to update:")
for user in users_to_update:
    print(f"  - {user.email} (current role: '{user.role if user.role else 'None'}')")

print("\n" + "-"*60)
print("Updating users to 'user' role...")
print("-"*60 + "\n")

# Update users
updated_count = users_to_update.update(role='user')

print(f"✅ Successfully updated {updated_count} user(s) to 'user' role\n")

# Option to promote specific users to admin
print("-"*60)
print("Promote specific users to admin?")
print("-"*60 + "\n")

admin_emails_input = input("Enter email addresses separated by commas (or press Enter to skip):\n> ").strip()

if admin_emails_input:
    admin_emails = [email.strip() for email in admin_emails_input.split(',') if email.strip()]
    
    if admin_emails:
        print(f"\nPromoting {len(admin_emails)} user(s) to admin...")
        
        admin_users = User.objects.filter(email__in=admin_emails)
        promoted_count = admin_users.update(role='admin')
        
        if promoted_count > 0:
            print(f"✅ Successfully promoted {promoted_count} user(s) to admin role")
            for user in admin_users:
                print(f"  👑 {user.email} -> admin")
        else:
            print("⚠️ No users found with the provided email addresses")
else:
    print("Skipping admin promotion\n")

# Display final summary
print("\n" + "="*60)
print("  Final User Roles Summary")
print("="*60 + "\n")

admin_count = User.objects.filter(role='admin').count()
user_count = User.objects.filter(role='user').count()

print(f"👑 Admins: {admin_count}")
print(f"👤 Users:  {user_count}")
print(f"📊 Total:  {total_users}\n")

print("Current user list:")
for user in User.objects.all().order_by('-date_joined'):
    role_icon = "👑" if user.role == 'admin' else "👤"
    print(f"  {role_icon} {user.email}: {user.role}")

print("\n" + "="*60)
print("  Migration Complete!")
print("="*60 + "\n")

print("Next steps:")
print("1. ✅ Run migrations: python manage.py makemigrations && python manage.py migrate")
print("2. ✅ Restart Django server: python manage.py runserver")
print("3. ✅ Test API endpoints with role field")
print("\nSee ROLE_MIGRATION_GUIDE.md for more details\n")
