from django.test import TestCase

# Create your tests here.
import os

credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
print(f"Google Credentials Path: {credentials_path}")

# Check if the file exists at the given path
if os.path.exists(credentials_path):
    print("The file exists.")
else:
    print("The file does not exist.")
