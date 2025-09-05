from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3, os, uuid

router = APIRouter(prefix="/media", tags=["media"])

class InitUpload(BaseModel):
    page_id: str
    filename: str

@router.post("/upload/init")
async def init_upload(body: InitUpload):
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        region_name=os.getenv("S3_REGION", "us-east-1"),
    )
    bucket = os.getenv("S3_BUCKET", "qr-media")
    key = f"pages/{body.page_id}/{uuid.uuid4()}_{body.filename}"
    presigned = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        ExpiresIn=600,
        Conditions=[["content-length-range", 0, 104857600]]
    )
    return {"s3_key": key, "presigned": presigned}
