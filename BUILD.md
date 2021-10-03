## Build from source

1. clone this repo, hop into the src dir and tweak the codebase as required
2. remove any existing build artifacts

    ```bash
    rm -rf build/ dist/ airflow_xtended_api.egg-info/
    ```
3. build the codebase

    ```bash
    python3 setup.py sdist bdist_wheel
    ```
4. (optional) upload build artifacts to testpypi (may require some tweaks in [setup.py](setup.py))

    ```bash
    python3 -m twine upload --repository testpypi dist/*
    ```