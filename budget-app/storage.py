"""NCP Object Storage client for the budget app."""
import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import PurePosixPath
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

RECEIPTS_PREFIX = "receipts/"
IMAGES_PREFIX = "receipt-images/"
BUDGETS_PREFIX = "budgets/"


class ObjectStorage:
    def __init__(self) -> None:
        self.bucket = os.environ["NCP_BUCKET"]
        self.endpoint = os.environ["NCP_ENDPOINT"]
        common = dict(
            endpoint_url=self.endpoint,
            aws_access_key_id=os.environ["NCP_ACCESS_KEY"],
            aws_secret_access_key=os.environ["NCP_SECRET_KEY"],
            region_name=os.environ.get("NCP_REGION", "kr-standard"),
        )
        # NCP quirk: PutObject only accepts SigV2, list/get/etc. require SigV4.
        self.client = boto3.client("s3", **common, config=Config(signature_version="s3v4"))
        self.writer = boto3.client("s3", **common, config=Config(signature_version="s3"))

    # ---------- Receipts (metadata JSON) ----------

    def receipt_key(self, date: str, receipt_id: str) -> str:
        return f"{RECEIPTS_PREFIX}{date}/{receipt_id}.json"

    def save_receipt(self, receipt: dict[str, Any]) -> None:
        self.writer.put_object(
            Bucket=self.bucket,
            Key=self.receipt_key(receipt["date"], receipt["id"]),
            Body=json.dumps(receipt, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
        )

    def load_receipt(self, date: str, receipt_id: str) -> dict[str, Any] | None:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self.receipt_key(date, receipt_id))
            return json.loads(obj["Body"].read())
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:
                return None
            raise

    def delete_receipt(self, receipt: dict[str, Any]) -> None:
        self.writer.delete_object(Bucket=self.bucket, Key=self.receipt_key(receipt["date"], receipt["id"]))
        if receipt.get("image_key"):
            self.writer.delete_object(Bucket=self.bucket, Key=receipt["image_key"])

    def _read_body_json(self, key: str) -> dict[str, Any]:
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return json.loads(obj["Body"].read())

    def list_receipts_for_month(self, ym: str) -> list[dict[str, Any]]:
        paginator = self.client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=f"{RECEIPTS_PREFIX}{ym}-"):
            for item in page.get("Contents", []):
                if item["Key"].endswith(".json"):
                    keys.append(item["Key"])
        if not keys:
            return []
        with ThreadPoolExecutor(max_workers=8) as ex:
            receipts = list(ex.map(self._read_body_json, keys))
        receipts.sort(key=lambda r: (r["date"], r.get("uploaded_at", "")), reverse=True)
        return receipts

    def list_receipts_for_date(self, date: str) -> list[dict[str, Any]]:
        paginator = self.client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=f"{RECEIPTS_PREFIX}{date}/"):
            for item in page.get("Contents", []):
                if item["Key"].endswith(".json"):
                    keys.append(item["Key"])
        if not keys:
            return []
        with ThreadPoolExecutor(max_workers=8) as ex:
            receipts = list(ex.map(self._read_body_json, keys))
        receipts.sort(key=lambda r: r.get("uploaded_at", ""), reverse=True)
        return receipts

    # ---------- Receipt images ----------

    def upload_image(self, date: str, filename: str, content_type: str, data: bytes) -> dict[str, Any]:
        ext = PurePosixPath(filename).suffix.lower() or ".jpg"
        image_id = uuid.uuid4().hex
        key = f"{IMAGES_PREFIX}{date}/{image_id}{ext}"
        self.writer.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type or "image/jpeg",
        )
        return {"key": key, "filename": filename, "content_type": content_type, "size": len(data)}

    def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    # ---------- Monthly budget ----------

    def budget_key(self, ym: str) -> str:
        return f"{BUDGETS_PREFIX}{ym}.json"

    def save_budget(self, ym: str, amount: int) -> None:
        self.writer.put_object(
            Bucket=self.bucket,
            Key=self.budget_key(ym),
            Body=json.dumps({"month": ym, "amount": int(amount)}, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
        )

    def get_budget(self, ym: str) -> int:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self.budget_key(ym))
            return int(json.loads(obj["Body"].read()).get("amount", 0))
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:
                return 0
            raise
