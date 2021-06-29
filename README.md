# Airflow Xtended API - Plugin

Apache Airflow plugin that exposes xtended secure API endpoints similar to the official [Airflow API (Stable) (1.0.0)](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html), providing richer capabilities to support more powerful DAG and job management. Apache Airflow version 2.1.0 or higher is necessary.

## Requirements

- [apache-airflow](https://github.com/apache/airflow)
- [pymongo](https://github.com/mongodb/mongo-python-driver)
- [boto3](https://github.com/boto/boto3)
- [requests](https://github.com/psf/requests)

## Installation

```python
python3 -m pip install airflow-xtended-api
```

## Screenshots

![screen1](https://raw.githubusercontent.com/anr007/airflow-xtended-api/main/grabs/screen1.jpg)
![screen2](https://raw.githubusercontent.com/anr007/airflow-xtended-api/main/grabs/screen2.jpg)
![screen3](https://raw.githubusercontent.com/anr007/airflow-xtended-api/main/grabs/screen3.jpg)

## Authentication

Airflow Xtended API plugin uses the same auth mechanism as [Airflow API (Stable) (1.0.0)](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#section/Trying-the-API). So, by default APIs exposed via this plugin respect the auth mechanism used by your Airflow webserver and also complies with the existing RBAC policies. Note that you will need to pass credentials data as part of the request. Here is a snippet from the official docs when basic authorization is used:

```bash
curl -X POST 'http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/dags/{dag_id}?update_mask=is_paused' \
-H 'Content-Type: application/json' \
--user "username:password" \
-d '{
    "is_paused": true
}'
```

## Using the Custom API

After installing the plugin python package and restarting your airflow webserver, You can see a link under the 'Xtended API' tab called 'Reference Docs' on the airflow webserver homepage. All the necessary documentation for the supported API endpoints resides on that page. You can also directly navigate to that page using below link.

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/xtended_api/
```

All the supported endpoints are exposed in the below format:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/{ENDPOINT_NAME}
```

Following are the names of endpoints which are currently supported.

- [deploy_dag](#deploy_dag)
- [create_dag](#create_dag)
- [s3_sync](#s3_sync)
- [mongo_sync](#mongo_sync)
- [scan_dags](#scan_dags)
- [purge_dags](#purge_dags)
- [refresh_all_dags](#refresh_all_dags)
- [delete_dag](#delete_dag)
- [upload_file](#upload_file)
- [restart_failed_task](#restart_failed_task)
- [kill_running_tasks](#kill_running_tasks)
- [run_task_instance](#run_task_instance)
- [skip_task_instance](#skip_task_instance)

### **_<span id="deploy_dag">deploy_dag</span>_**

##### Description:

- Deploy a new DAG File to the DAGs directory.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/deploy_dag
```

##### Method:

- POST

##### POST request Arguments:

- dag_file - file - Upload & Deploy a DAG from .py or .zip files
- force (optional) - boolean - Force uploading the file if it already exists
- unpause (optional) - boolean - The DAG will be unpaused on creation (Works only when uploading .py files)
- otf_sync (optional) - boolean - Check for newly created DAGs On The Fly!

##### Examples:

```bash
curl -X POST -H 'Content-Type: multipart/form-data' \
 --user "username:password" \
 -F 'dag_file=@test_dag.py' \
 -F 'force=y' \
 -F 'unpause=y' \
 http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/deploy_dag
```

##### response:

```json
{
  "message": "DAG File [<module '{MODULE_NAME}' from '/{DAG_FOLDER}/exam.py'>] has been uploaded",
  "status": "success"
}
```

##### Method:

- GET

##### Get request Arguments:

- dag_file_url - file - A valid url for fetching .py, .pyc or .zip DAG files
- filename - string - A valid filename ending with .py, .pyc or .zip
- force (optional) - boolean - Force uploading the file if it already exists.
- unpause (optional) - boolean - The DAG will be unpaused on creation (Works only when uploading .py files)
- otf_sync (optional) - boolean - Check for newly created DAGs On The Fly!

##### Examples:

```bash
curl -X GET --user "username:password" \
'http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/deploy_dag?dag_file_url={DAG_FILE_URL}&filename=test_dag.py&force=on&unpause=on'

```

##### response:

```json
{
  "message": "DAG File [<module '{MODULE_NAME}' from '/{DAG_FOLDER}/exam.py'>] has been uploaded",
  "status": "success"
}
```

### **_<span id="create_dag">create_dag</span>_**

##### Description:

- Create a new DAG File in the DAGs directory.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/create_dag
```

##### Method:

- POST

##### POST request Arguments:

- filename - string - Name of the python DAG file
- dag_code - string(multiline) - Python code of the DAG file
- force (optional) - boolean - Force uploading the file if it already exists
- unpause (optional) - boolean - The DAG will be unpaused on creation (Works only when uploading .py files)
- otf_sync (optional) - boolean - Check for newly created DAGs On The Fly!

### **_<span id="s3_sync">s3_sync</span>_**

##### Description:

- Sync DAG files from an S3 bucket.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/s3_sync
```

##### Method:

- POST

##### POST request Arguments:

- s3_bucket_name - string - S3 bucket name where DAG files exist
- s3_region - string - S3 region name where the specified bucket exists
- s3_access_key - string - IAM access key having atleast S3 bucket read access
- s3_secret_key - string - IAM secret key for the specifed access key
- s3_object_prefix (optional) - string - Filter results by object prefix
- s3_object_keys (optional) - string - Sync DAG files specifed by the object keys. Multiple object keys are seperated by comma (,)
- skip_purge (optional) - boolean - Skip emptying DAGs directory
- otf_sync (optional) - boolean - Check for newly created DAGs On The Fly!

##### Examples:

```bash
curl -X POST -H 'Content-Type: multipart/form-data' \
 --user "username:password" \
 -F 's3_bucket_name=test-bucket' \
 -F 's3_region=us-east-1' \
 -F 's3_access_key={IAM_ACCESS_KEY}' \
 -F 's3_secret_key={IAM_SECRET_KEY}' \
 -F 'skip_purge=y' \
 http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/s3_sync
```

##### response:

```json
{
  "message": "dag files synced from s3",
  "sync_status": {
    "synced": ["test_dag0.py", "test_dag1.py", "test_dag2.py"],
    "failed": []
  },
  "status": "success"
}
```

### **_<span id="mongo_sync">mongo_sync</span>_**

##### Description:

- Sync DAG files from a mongo db collection

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/mongo_sync
```

##### Method:

- POST

##### POST request Arguments:

- connection_string - string - Source mongo server connection string
- db_name - string - Source mongo database name
- collection_name - string - Collection name where DAG data exists in the specified db
- field_filename - string - DAGs are named using value of this document field from the specified collection
- field_dag_source - string - A document field referring the Python source for the yet-to-be created DAGs
- query_filter (optional) - string - JSON query string to filter required documents
- skip_purge (optional) - boolean - Skip emptying DAGs directory
- otf_sync (optional) - boolean - Check for newly created DAGs On The Fly!

##### Examples:

```bash
curl -X POST -H 'Content-Type: multipart/form-data' \
 --user "username:password" \
 -F 'connection_string={MONGO_SERVER_CONNECTION_STRING}' \
 -F 'db_name=test_db' \
 -F 'collection_name=test_collection' \
 -F 'field_dag_source=dag_source' \
 -F 'field_filename=dag_filename' \
 -F 'skip_purge=y' \
 http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/mongo_sync
```

##### response:

```json
{
  "message": "dag files synced from mongo",
  "sync_status": {
    "synced": ["test_dag0.py", "test_dag1.py", "test_dag2.py"],
    "failed": []
  },
  "status": "success"
}
```

### **_<span id="refresh_all_dags">refresh_all_dags</span>_**

##### Description:

- Refresh all DAGs in the webserver.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/refresh_all_dags
```

##### Method:

- GET

##### GET request Arguments:

- None

##### Examples:

```bash
curl -X GET --user "username:password" \
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/refresh_all_dags
```

##### response:

```json
{
  "message": "All DAGs are now up-to-date!!",
  "status": "success"
}
```

### **_<span id="scan_dags">scan_dags</span>_**

##### Description:

- Check for newly created DAGs.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/scan_dags
```

##### Method:

- GET

##### GET request Arguments:

- otf_sync (optional) - boolean - Check for newly created DAGs On The Fly!

##### Examples:

```bash
curl -X GET --user "username:password" \
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/scan_dags
```

##### response:

```json
{
  "message": "Ondemand DAG scan complete!!",
  "status": "success"
}
```

### **_<span id="purge_dags">purge_dags</span>_**

##### Description:

- Empty DAG directory.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/purge_dags
```

##### Method:

- GET

##### GET request Arguments:

- None

##### Examples:

```bash
curl -X GET --user "username:password" \
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/purge_dags
```

##### response:

```json
{
  "message": "DAG directory purged!!",
  "status": "success"
}
```

### **_<span id="delete_dag">delete_dag</span>_**

##### Description:

- Delete a DAG in the web server from Airflow database and filesystem.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/delete_dag
```

##### Method:

- GET

##### GET request Arguments:

- dag_id (optional)- string - DAG id
- filename (optional) - string - Name of the DAG file that needs to be deleted
- Note: Atleast one of args 'dag_id' or 'filename' should be specified

##### Examples:

```bash
curl -X GET --user "username:password" \
'http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/delete_dag?dag_id=test_dag&filename=test_dag.py'
```

##### response:

```json
{
  "message": "DAG [dag_test] deleted",
  "status": "success"
}
```

### **_<span id="upload_file">upload_file</span>_**

##### Description:

- Upload a new File to the specified directory.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/upload_file
```

##### Method:

- POST

##### POST request Arguments:

- file - file - File to be uploaded
- force (optional) - boolean - Force uploading the file if it already exists
- path (optional) - string - Location where the file is to be uploaded (Default is the DAGs directory)

##### Examples:

```bash
curl -X POST -H 'Content-Type: multipart/form-data' \
 --user "username:password" \
 -F 'file=@test_file.py' \
 -F 'force=y' \
 http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/upload_file
```

##### response:

```json
{
  "message": "File [/{DAG_FOLDER}/dag_test.txt] has been uploaded",
  "status": "success"
}
```

### **_<span id="restart_failed_task">restart_failed_task</span>_**

##### Description:

- Restart failed tasks with downstream.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/restart_failed_task
```

##### Method:

- GET

##### GET request Arguments:

- dag_id - string - DAG id
- run_id - string - DagRun id

##### Examples:

```bash
curl -X GET --user "username:password" \
'http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/restart_failed_task?dag_id=test_dag&run_id=test_run'
```

##### response:

```json
{
  "message": {
    "failed_task_count": 1,
    "clear_task_count": 7
  },
  "status": "success"
}
```

### **_<span id="kill_running_tasks">kill_running_tasks</span>_**

##### Description:

- Kill running tasks having status in ['none', 'running'].

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/kill_running_tasks
```

##### Method:

- GET

##### GET request Arguments:

- dag_id - string - DAG id
- run_id - string - DagRun id
- task_id - string - If task_id is none, kill all tasks, else kill the specified task.

##### Examples:

```bash
curl -X GET --user "username:password" \
'http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/kill_running_tasks?dag_id=test_dag&run_id=test_run&task_id=test_task'
```

##### response:

```json
{
  "message": "tasks in test_run killed!!",
  "status": "success"
}
```

### **_<span id="run_task_instance">run_task_instance</span>_**

##### Description:

- Create DagRun, run the specified tasks, and skip the rest.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/run_task_instance
```

##### Method:

- POST

##### POST request Arguments:

- dag_id - string - DAG id
- run_id - string - DagRun id
- tasks - string - task id(s), Multiple tasks are separated by comma (,)
- conf (optional)- string - Optional configuartion for creating DagRun.

##### Examples:

```bash
curl -X POST -H 'Content-Type: multipart/form-data' \
 --user "username:password" \
 -F 'dag_id=test_dag' \
 -F 'run_id=test_run' \
 -F 'tasks=test_task' \
 http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/run_task_instance
```

##### response:

```json
{
  "execution_date": "2021-06-21T05:50:19.740803+0000",
  "status": "success"
}
```

### **_<span id="skip_task_instance">skip_task_instance</span>_**

##### Description:

- Skip one task instance.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/skip_task_instance
```

##### Method:

- GET

##### GET request Arguments:

- dag_id - string - DAG id
- run_id - string - DagRun id
- task_id - string - task id

##### Examples:

```bash
curl -X GET http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/xtended/skip_task_instance?dag_id=test_dag&run_id=test_run&task_id=test_task
```

##### response:

```json
{
  "message": "<TaskInstance: test_dag.test_task 2021-06-21 19:59:34.638794+00:00 [skipped]> skipped!!",
  "status": "success"
}
```

## Acknowledgements

Huge shout out to these awesome plugins that contributed to the growth of Airflow ecosystem, which also inspired this plugin.

- [airflow-rest-api-plugin](https://github.com/teamclairvoyant/airflow-rest-api-plugin)
- [airflow-rest-api-plugin](https://github.com/eBay/airflow-rest-api-plugin)
- [simple-dag-editor](https://github.com/ohadmata/simple-dag-editor)
- [airflow-code-editor](https://github.com/andreax79/airflow-code-editor)
