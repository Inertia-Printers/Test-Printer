import os

def implicit():
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\jrmuy\Documents\Code\Inertia\inertia-printers-project-1af0a447d855.json"

print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

implicit()