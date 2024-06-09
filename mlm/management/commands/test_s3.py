from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Test S3 connection by uploading and retrieving a file'

    def handle(self, *args, **kwargs):
        # Test file name and content
        test_file_name = 'test_s3_connection.txt'
        test_content = 'This is a test file for S3 connection.'

        # Upload the file
        file = ContentFile(test_content)
        file_name = default_storage.save(test_file_name, file)

        # Retrieve the file
        retrieved_content = default_storage.open(file_name).read().decode('utf-8')

        # Check if the content matches
        if retrieved_content == test_content:
            self.stdout.write(self.style.SUCCESS('S3 connection is working correctly.'))
        else:
            self.stdout.write(self.style.ERROR('S3 connection test failed.'))

        # Clean up the test file
        default_storage.delete(file_name)