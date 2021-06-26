import os
import logging
from concurrent import futures

import boto3

import airflow_xtended_api.config as config
from airflow_xtended_api.exceptions import (
    S3BucketDoesNotExistsError,
    S3ObjDownloadError,
    S3GenericError,
    OSFileHandlingError,
)

CONTENTS = "Contents"
KEY = "Key"
MAX_DOWNLOAD_THREADS = 5
s3 = None


def init_client(access_key, secret_key, s3_region):
    global s3
    if not s3:
        s3 = boto3.client(
            "s3",
            region_name=s3_region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )


def sync_specific_objects_from_bucket(
    bucket_name, object_keys, sync_dir, ext=config.VALID_DAG_FILE_EXT
):
    global s3
    try:
        s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    except Exception as e:
        # boto3.S3.Client.exceptions.NoSuchBucket
        if "NoSuchBucket".lower() in repr(e).lower():
            raise S3BucketDoesNotExistsError(f"{bucket_name} does not exists!")
        raise S3GenericError(f"error retriving {bucket_name} bucket contents!", repr(e))

    match = lambda obj: obj.split(".")[-1] in ext

    sync_status = {"synced": [], "failed": []}

    for obj_key in object_keys:
        if not match(obj_key):
            logging.info(f"skipping s3 object: {obj_key}")
            continue
        logging.info(f"downloading s3 object: {obj_key}")
        obj_path = os.path.join(sync_dir, obj_key)
        try:
            obj_base_dir = os.path.dirname(obj_path)
            if not os.path.exists(obj_base_dir):
                os.makedirs(obj_base_dir, exist_ok=True)
        except OSError as e:
            logging.exception(f"error during io operation: {obj_path}")
            sync_status["failed"].append(f"{obj_path}: {repr(e)}")
            continue

        try:
            s3.download_file(Filename=obj_path, Bucket=bucket_name, Key=obj_key)
        except Exception as e:
            logging.exception(f"error downloading s3 object: {obj_path}")
            sync_status["failed"].append(f"{obj_path}: {repr(e)}")
            continue

        sync_status["synced"].append(obj_key)

    logging.info(sync_status)
    return sync_status


def sync_files_from_bucket(
    bucket_name, sync_dir, prefix="", ext=config.VALID_DAG_FILE_EXT
):
    global s3
    page_iterator = None
    objects = []
    try:
        paginator = s3.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(
            Bucket=bucket_name, Prefix=prefix, PaginationConfig={"PageSize": 100}
        )
        for page in page_iterator:
            for obj in page[CONTENTS]:
                objects.append(obj)
    except Exception as e:
        # boto3.S3.Client.exceptions.NoSuchBucket
        if "NoSuchBucket".lower() in repr(e).lower():
            raise S3BucketDoesNotExistsError(f"{bucket_name} does not exists!")
        raise S3GenericError(f"error retriving {bucket_name} bucket contents!", repr(e))

    condition = lambda obj: obj[KEY].split(".")[-1] in ext
    required_objects = filter(condition, objects)

    sync_status = {"synced": [], "failed": []}
    for filename, download_result in fetch_bucket(
        required_objects, bucket_name, sync_dir
    ):
        if type(download_result) is bool:
            sync_status["synced"].append(filename)
        else:
            sync_status["failed"].append(f"{filename}: {repr(download_result)}")
    logging.info(sync_status)
    return sync_status


def fetch_object(obj_key, bucket_name, sync_dir):
    obj_path = os.path.join(sync_dir, obj_key)
    try:
        obj_base_dir = os.path.dirname(obj_path)
        if not os.path.exists(obj_base_dir):
            os.makedirs(obj_base_dir, exist_ok=True)
    except OSError as e:
        raise OSFileHandlingError(f"error during io operation: {obj_path}", repr(e))

    try:
        s3.download_file(Filename=obj_path, Bucket=bucket_name, Key=obj_key)
    except Exception as e:
        raise S3ObjDownloadError(f"error downloading s3 object: {obj_key}", repr(e))

    return True


def fetch_bucket(obj_list, bucket_name, sync_dir):
    with futures.ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_THREADS) as executor:
        # dict of future, filename
        future_2_filename_map = {
            executor.submit(fetch_object, obj[KEY], bucket_name, sync_dir): obj[KEY]
            for obj in obj_list
        }

        for future in futures.as_completed(future_2_filename_map):
            filename = future_2_filename_map[future]
            exception = future.exception()
            if not exception:
                yield filename, future.result()
            else:
                yield filename, exception
