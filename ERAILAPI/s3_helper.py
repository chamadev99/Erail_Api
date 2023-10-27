import os
import boto3
from dotenv import load_dotenv


load_dotenv()

# AWS S3 credentials and bucket name
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')
bucket_name = os.environ.get('S3_BUCKET_NAME')

s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)


def get_media_files(location_list):
    try:
        media_dict = {}

        # Get a list of all objects (images and videos) in the S3 bucket
        response = s3.list_objects(Bucket=bucket_name)

        for obj in response.get('Contents', []):
            key = obj['Key']
            # Split the key to obtain the first part (subfolder or key prefix)
            key_parts = key.split('/')
            if key_parts:
                first_part = key_parts[0].lower().strip().replace(" ", "_")

                if first_part in location_list:
                    # Determine if the object is an image or video based on the file extension
                    extension = key.split('.')[-1].lower()
                    if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                        media_type = 'image'
                    elif extension in ['mp4', 'mov', 'avi', 'mkv']:
                        media_type = 'video'
                    else:
                        # Unsupported file type, skip
                        continue

                    # Generate a pre-signed URL for the matching media file
                    url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': key},
                        ExpiresIn=3600  # URL expiration time in seconds (adjust as needed)
                    )

                    # Organize URLs based on media type
                    if first_part not in media_dict:
                        media_dict[first_part] = {'images': [], 'videos': []}
                    media_dict[first_part][media_type + 's'].append(url)

        return media_dict

    except Exception as e:
        print(f'Error: {e}')
        return {}


if __name__ == "__main__":
    location_list = ["pattipola", "idalgashinna", "ohiya", "ella", "haputhale", "demodara", "bandarawela", "badulla"]
    result = get_media_files(location_list)
    print(result)
