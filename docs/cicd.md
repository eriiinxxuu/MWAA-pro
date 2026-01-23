# CI/CD Pipeline with GitHub Actions
GitHub Actions automatically discovers workflows defined under the `.github/workflows/` directory. \
The deployment workflow is triggered on pushes to the `main` branch, ensuring that only finalized and reviewed code is promoted to the MWAA runtime environment.

The GitHub Actions workflow performs the following steps:

- Source Checkout \
The repository is checked out to retrieve the latest DAG code and configuration files.

- DAG Synchronization to S3 \
All DAG files under the `dags/` directory are synchronized to the MWAA S3 bucket using `AWS S3 sync`. In my project, only codes in `dags` folder and `requirements.txt` included. \
![AWS_S3](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/aws_S3.png)

- Dependency Configuration Update \
The `requirements.txt` file is uploaded to Amazon S3, allowing MWAA to install and manage Python dependencies required by the DAGs.

Once the synchronization is complete, MWAA automatically detects changes in the S3 bucket and refreshes DAG definitions accordingly, enabling continuous delivery without manual intervention.