"""
Metadata that defines a single API:
{
    "name": "{string}",                     # Name of the API
    "description": "{string}",              # Description of the API
    "http_method": "{string}",              # HTTP method to use when calling the function.
    "form_enctype": "{string}",             # Optional encoding type
    "arguments": [                          # List of arguments that can be provided to the API
        {
            "arg1": "val1",    
        }
    ],
    "post_arguments": [                     # List of arguments that can be provided in the POST body to the API
        {
            "arg1": "val1",
        }
    ]
},
"""

api_metadata = [
    {
        "name": "deploy_dag",
        "description": "Deploy a new DAG File to the DAGs directory",
        "http_method": "POST",
        "form_enctype": "multipart/form-data",
        "arguments": [],
        "post_arguments": [
            {
                "name": "dag_file",
                "description": "Upload & Deploy a DAG from .py or .zip files",
                "form_input_type": "file",
                "required": True,
            },
            {
                "name": "force",
                "description": "Force uploading the file if it already exists",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "unpause",
                "description": "The DAG will be unpaused on creation (Works only when uploading .py files)",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "otf_sync",
                "description": "Check for newly created DAGs On The Fly!",
                "form_input_type": "checkbox",
                "required": False,
            },
        ],
        "footnotes": "",
    },
    {
        "name": "deploy_dag",
        "description": "Fetch & Deploy a new DAG File to the DAGs directory",
        "http_method": "GET",
        "arguments": [
            {
                "name": "dag_file_url",
                "description": "A valid url for fetching .py, .pyc or .zip DAG files",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "filename",
                "description": "A valid filename ending with .py, .pyc or .zip",
                "form_input_type": "text",
                "required": False,
            },
            {
                "name": "force",
                "description": "Force uploading the file if it already exists",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "unpause",
                "description": "The DAG will be unpaused on creation (Works only for .py files)",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "otf_sync",
                "description": "Check for newly created DAGs On The Fly!",
                "form_input_type": "checkbox",
                "required": False,
            },
        ],
        "post_arguments": [],
        "footnotes": "",
    },
    {
        "name": "create_dag",
        "description": "Create a new DAG File in the DAGs directory",
        "http_method": "POST",
        "form_enctype": "multipart/form-data",
        "arguments": [],
        "post_arguments": [
            {
                "name": "filename",
                "description": "Name of the python DAG file",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "dag_code",
                "description": "Python code of the DAG file",
                "form_input_type": "textarea",
                "required": True,
            },
            {
                "name": "force",
                "description": "Force uploading the file if it already exists",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "unpause",
                "description": "The DAG will be unpaused on creation",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "otf_sync",
                "description": "Check for newly created DAGs On The Fly!",
                "form_input_type": "checkbox",
                "required": False,
            },
        ],
    },
    {
        "name": "s3_sync",
        "description": "Sync DAG files from an S3 bucket",
        "http_method": "POST",
        "form_enctype": "multipart/form-data",
        "arguments": [],
        "post_arguments": [
            {
                "name": "s3_bucket_name",
                "description": "S3 bucket name where the DAG files exist",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "s3_region",
                "description": "S3 region name where the specified bucket exists",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "s3_access_key",
                "description": "IAM entity access key having atleast S3 bucket read access",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "s3_secret_key",
                "description": "IAM secret key for the specifed access key",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "s3_object_prefix",
                "description": "Filter results by object prefix",
                "form_input_type": "text",
                "required": False,
            },
            {
                "name": "s3_object_keys",
                "description": "Sync DAG files specifed by the object keys. Multiple object keys are seperated by comma (,)",
                "form_input_type": "text",
                "required": False,
            },
            {
                "name": "skip_purge",
                "description": "Skip emptying DAGs directory",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "otf_sync",
                "description": "Check for newly created DAGs On The Fly!",
                "form_input_type": "checkbox",
                "required": False,
            },
        ],
    },
    {
        "name": "mongo_sync",
        "description": "Sync DAG files from a mongo db collection",
        "http_method": "POST",
        "form_enctype": "multipart/form-data",
        "arguments": [],
        "post_arguments": [
            {
                "name": "connection_string",
                "description": "Source mongo server connection string",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "db_name",
                "description": "Source mongo database name",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "collection_name",
                "description": "Collection name where DAG data exists in the specified db",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "field_filename",
                "description": "DAGs are named using value of this document field from the specified collection",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "field_dag_source",
                "description": "A document field referring the Python source for the yet-to-be created DAGs",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "query_filter",
                "description": "JSON query string to filter required documents",
                "form_input_type": "text",
                "required": False,
            },
            {
                "name": "skip_purge",
                "description": "Skip emptying DAGs directory",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "otf_sync",
                "description": "Check for newly created DAGs On The Fly!.",
                "form_input_type": "checkbox",
                "required": False,
            },
        ],
    },
    {
        "name": "refresh_all_dags",
        "description": "Refresh all DAGs in the Web Server",
        "http_method": "GET",
        "arguments": [],
    },
    {
        "name": "scan_dags",
        "description": "Check for newly created DAGs",
        "http_method": "GET",
        "arguments": [
            {
                "name": "otf_sync",
                "description": "Check for newly created DAGs On The Fly!",
                "form_input_type": "checkbox",
                "required": False,
            }
        ],
    },
    {
        "name": "purge_dags",
        "description": "Empty DAG directory",
        "http_method": "GET",
        "arguments": [],
    },
    {
        "name": "delete_dag",
        "description": "Delete a DAG in the web server from Airflow database and filesystem",
        "http_method": "GET",
        "arguments": [
            {
                "name": "dag_id",
                "description": "DAG id",
                "form_input_type": "text",
                "required": False,
            },
            {
                "name": "filename",
                "description": "Name of the DAG file that needs to be deleted",
                "form_input_type": "text",
                "required": False,
            },
        ],
        "footnotes": "Atleast one of args 'dag_id' or 'filename' should be specified",
    },
    {
        "name": "upload_file",
        "description": "Upload a new file to the specified directory",
        "http_method": "POST",
        "form_enctype": "multipart/form-data",
        "arguments": [],
        "post_arguments": [
            {
                "name": "file",
                "description": "File to be uploaded",
                "form_input_type": "file",
                "required": True,
            },
            {
                "name": "force",
                "description": "Force uploading the file if it already exists",
                "form_input_type": "checkbox",
                "required": False,
            },
            {
                "name": "path",
                "description": "Location where the file is to be uploaded (Default is the DAGs directory)",
                "form_input_type": "text",
                "required": False,
            },
        ],
    },
    {
        "name": "restart_failed_task",
        "description": "Restart failed tasks with downstream",
        "http_method": "GET",
        "arguments": [
            {
                "name": "dag_id",
                "description": "DAG id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "run_id",
                "description": "DagRun id",
                "form_input_type": "text",
                "required": True,
            },
        ],
    },
    {
        "name": "kill_running_tasks",
        "description": "Kill running tasks having status in ['none', 'running']",
        "http_method": "GET",
        "arguments": [
            {
                "name": "dag_id",
                "description": "DAG id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "run_id",
                "description": "DagRun id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "task_id",
                "description": "If task_id is none, kill all tasks, else kill the specified task",
                "form_input_type": "text",
                "required": False,
            },
        ],
    },
    {
        "name": "run_task_instance",
        "description": "Create DagRun, run the specified tasks, and skip the rest",
        "http_method": "POST",
        "form_enctype": "multipart/form-data",
        "arguments": [],
        "post_arguments": [
            {
                "name": "dag_id",
                "description": "DAG id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "run_id",
                "description": "DagRun id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "tasks",
                "description": "task id(s), Multiple tasks are separated by comma (,)",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "conf",
                "description": "Optional configuartion for creating DagRun",
                "form_input_type": "text",
                "required": False,
            },
        ],
    },
    {
        "name": "skip_task_instance",
        "description": "Skip one task instance",
        "http_method": "GET",
        "arguments": [
            {
                "name": "dag_id",
                "description": "DAG id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "run_id",
                "description": "DagRun id",
                "form_input_type": "text",
                "required": True,
            },
            {
                "name": "task_id",
                "description": "task id",
                "form_input_type": "text",
                "required": True,
            },
        ],
    },
]
