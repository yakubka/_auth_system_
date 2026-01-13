import re

with open('auth_system/settings.py', 'r') as f:
    content = f.read()

new_content = re.sub(
    r"DATABASES = \{[\s\S]*?\}",
    '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}''',
    content
)

with open('auth_system/settings.py', 'w') as f:
    f.write(new_content)

print("Настройки базы данных обновлены на SQLite")
