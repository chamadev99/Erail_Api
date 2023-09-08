import boto3
import os
from dotenv import load_dotenv

load_dotenv()


# AWS S3 credentials and bucket name
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')
bucket_name = os.environ.get('S3_BUCKET_NAME')


s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)


def get_images(location_list):
    try:
        # print(f"location_list:{location_list}")
        # print(f"location_list:{type(location_list)}")
        # List all objects (images) in the S3 bucket
        response = s3.list_objects(Bucket=bucket_name,)

        image_urls = []
        key_list = []
        img_dict = {}

        for obj in response.get('Contents', []):

            # Generate a pre-signed URL for each image
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': obj['Key']},
                ExpiresIn=3600
            )
            image_urls.append(url)
            _key = str(obj['Key']).split('/')[0].lower().strip().replace(" ", "_")
            # print(f"_key:{_key}")
            if _key in location_list:
                # print(f"_key:{_key}")
                if _key not in key_list:
                    img_dict[f"{_key}"] = []
                    img_dict.get(_key).append(url)
                else:
                    img_dict.get(_key).append(url)

        # print(f"img_dict:{img_dict}")
        return img_dict

    except Exception as e:
        print(f'e:{e}')
        return []


# get_images([])
