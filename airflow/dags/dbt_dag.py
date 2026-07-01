from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/project/dbt"

default_args = {"owner":"airflow","retries":1,"retry_delay":timedelta(minutes=3)}

with DAG("ecommerce_dbt", default_args=default_args, schedule_interval="@daily",
         start_date=datetime(2024,1,1), catchup=False, tags=["ecommerce","dbt"]) as dag:

    dbt_run = BashOperator(task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir .")

    dbt_test = BashOperator(task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir .")

    dbt_docs = BashOperator(task_id="dbt_docs",
        bash_command=f"cd {DBT_DIR} && dbt docs generate --profiles-dir .")

    dbt_run >> dbt_test >> dbt_docs