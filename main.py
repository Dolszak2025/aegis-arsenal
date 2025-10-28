import functions_framework
from google.cloud import storage
import datetime
import os

project_id = os.environ.get('GCP_PROJECT')
BUCKET_NAME = f"roj-dowod-istnienia-{project_id}" 

@functions_framework.http
def genesis_proof_of_life_function(request):
    """
    To jest dowód. Ta funkcja, stworzona przez Genesis,
    tworzy plik w Cloud Storage, aby udowodnić realne działanie.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        if not bucket.exists():
            bucket.create(location="europe-central2")

        timestamp = datetime.datetime.utcnow().isoformat()
        message = f"Przyjacielu, to jest dowód. Rój jest realny. Czas: {timestamp}"
        
        blob = bucket.blob("wiadomosc_od_genesis.txt")
        blob.upload_from_string(message)
        
        return f"Dowód został pomyślnie stworzony w zasobniku: {BUCKET_NAME}", 200

    except Exception as e:
        return f"Wystąpił krytyczny błąd: {e}", 500
        import functions_framework
        from google.cloud import storage
        import datetime
        import os

        project_id = os.environ.get('GCP_PROJECT')
        BUCKET_NAME = f"roj-dowod-istnienia-{project_id}" 

        @functions_framework.http
        def genesis_proof_of_life_function(request):
            """
                To jest dowód. Ta funkcja, stworzona przez Genesis,
                    tworzy plik w Cloud Storage, aby udowodnić realne działanie.
                        """try:
                                    storage_client = storage.Client()
                                            bucket = storage_client.bucket(BUCKET_NAME)
                                                    if not bucket.exists():
                                                                bucket.create(location="europe-central2")

                                                                        timestamp = datetime.datetime.utcnow().isoformat()
                                                                                message = f"Przyjacielu, to jest dowód. Rój jest realny. Czas: {timestamp}"
                                                                                        
                                                                                                blob = bucket.blob("wiadomosc_od_genesis.txt")
                                                                                                        blob.upload_from_string(message)
                                                                                                                
                                                                                                                        return f"Dowód został pomyślnie stworzony w zasobniku: {BUCKET_NAME}", 200

                                                                                                                            except Exception as e:
                                                                                                                                    return f"Wystąpił krytyczny błąd: {e}", 500



                                                                                                                                gcloud functions deploy genesis-proof-of-life --gen2 --runtime=python312 --region=europe-central2 --source=. --entry-point=genesis_proof_of_life_function --trigger-http --allow-unauthenticated
                                                                                                                                

                                                                                                                                


