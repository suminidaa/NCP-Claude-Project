"""Naver Cloud Platform Object Storage client (S3-compatible)."""
import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

ENTRIES_PREFIX = "entries/"
PHOTOS_PREFIX = "photos/"


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

    # -------- entries (text + photo metadata) --------

    def entry_key(self, date: str) -> str:
        return f"{ENTRIES_PREFIX}{date}.json"

    def load_entry(self, date: str) -> dict[str, Any]:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self.entry_key(date))
            data = json.loads(obj["Body"].read())
            data.setdefault("mood", "")
            return data
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:
                return {"date": date, "text": "", "photos": [], "mood": "", "updated_at": None}
            raise

    def save_entry(self, date: str, text: str, photos: list[dict[str, Any]], mood: str = "") -> dict[str, Any]:
        payload = {
            "date": date,
            "text": text,
            "photos": photos,
            "mood": mood,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self.writer.put_object(
            Bucket=self.bucket,
            Key=self.entry_key(date),
            Body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
        )
        return payload

    def _fetch_mood(self, key: str) -> str:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(obj["Body"].read()).get("mood", "") or ""
        except Exception:
            return ""

    def list_entries(self) -> list[dict[str, Any]]:
        paginator = self.client.get_paginator("list_objects_v2")
        items: list[dict[str, Any]] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=ENTRIES_PREFIX):
            for item in page.get("Contents", []):
                if item["Key"].endswith(".json"):
                    items.append(item)

        moods: dict[str, str] = {}
        if items:
            with ThreadPoolExecutor(max_workers=8) as ex:
                fetched = list(ex.map(self._fetch_mood, [it["Key"] for it in items]))
            moods = {PurePosixPath(it["Key"]).stem: m for it, m in zip(items, fetched)}

        by_date: dict[str, dict[str, Any]] = {}
        for it in items:
            date = PurePosixPath(it["Key"]).stem
            by_date[date] = {
                "date": date,
                "size": it["Size"],
                "last_modified": it["LastModified"].isoformat(),
                "has_text": it["Size"] > 110,
                "has_photos": False,
                "mood": moods.get(date, ""),
            }
        for page in paginator.paginate(Bucket=self.bucket, Prefix=PHOTOS_PREFIX):
            for item in page.get("Contents", []):
                parts = item["Key"].split("/")
                if len(parts) >= 3 and parts[1] in by_date:
                    by_date[parts[1]]["has_photos"] = True
        results = list(by_date.values())
        results.sort(key=lambda r: r["date"], reverse=True)
        return results

    # -------- photos --------

    def upload_photo(self, date: str, filename: str, content_type: str, data: bytes) -> dict[str, Any]:
        ext = PurePosixPath(filename).suffix.lower() or ""
        photo_id = uuid.uuid4().hex
        key = f"{PHOTOS_PREFIX}{date}/{photo_id}{ext}"
        self.writer.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type or "application/octet-stream",
        )
        return {
            "id": photo_id,
            "key": key,
            "filename": filename,
            "content_type": content_type,
            "size": len(data),
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
        }

    def delete_photo(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
