This contains the configs for the current version of airflow.
It is setup together with Jupyterlab and papermill dependencies to enable parameterized scheduling of notebooks.
DAGS, notebooks and scripts are located in a shared volume.

** On first time usage:**
´´´ docker-compose up airflow-init ´´´ to initialise the airflow database before docker-compose up
