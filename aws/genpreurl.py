import boto3

# -----------------------------
# CONFIGURATION
# -----------------------------
bucket_name = "bucket-name"
object_key = "object-key-name"  # S3 object name
region_name = "region-west-2" # Region of the bucket
expires_in = 3600  # seconds

# -----------------------------
# GENERATE PRESIGNED URL
# -----------------------------
# Force the S3 client to use the regional endpoint
s3 = boto3.client(
    "s3",
    region_name=region_name,
    endpoint_url=f"https://s3.{region_name}.amazonaws.com"
)

presigned_url = s3.generate_presigned_url(
    ClientMethod="put_object",
    Params={"Bucket": bucket_name, "Key": object_key},
    ExpiresIn=expires_in
)

print("Presigned URL (valid for 1 hour):")
print(presigned_url)
