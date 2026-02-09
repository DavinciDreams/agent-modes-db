import database as db
import json

uploads = db.get_all_file_uploads()
print(f"Total uploads: {len(uploads)}")

if uploads:
    print(f"\nUpload fields: {list(uploads[0].keys())}")
    print(f"\nRecent uploads:")
    for u in uploads[-5:]:
        print(f"\nID: {u['id']}")
        print(f"File: {u['original_filename']}")
        print(f"Status: {u['upload_status']}")
