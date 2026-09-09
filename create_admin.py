import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayurvedic_products.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    username = 'admin'
    email = 'admin@herbacare.com'
    password = 'adminpassword123'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully with password '{password}'.")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Superuser '{username}' updated with password '{password}'.")

if __name__ == '__main__':
    create_admin()
