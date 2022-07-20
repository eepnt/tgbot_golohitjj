import functions_framework

# gcp cloud storage
from google.cloud import storage
storage_client = storage.Client()

@functions_framework.http
def hello_http(request):
    blobs = storage_client.list_blobs('golo_bucket')
    rt = ''
    for blob in blobs:
        rt += blob.path() + "\n"
    return rt
