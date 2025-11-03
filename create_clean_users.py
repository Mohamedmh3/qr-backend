import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
import django
django.setup()

from users.models import User

def main():
    # Create admin
    a = User.objects.create_user(email='admin@example.com', name='Admin User', password='AdminPass123!', role='admin')
    a.is_staff = True
    a.is_superuser = True
    a.save()
    print(f"admin created: id={a.pk}, email={a.email}")

    # Create user
    u = User.objects.create_user(email='player1@example.com', name='Player One', password='TestPass123!', role='user')
    print(f"user created: id={u.pk}, email={u.email}")

if __name__ == '__main__':
    main()





