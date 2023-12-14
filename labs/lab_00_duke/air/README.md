# Introduction

Apache Airflow is an open-source workflow management platform. It allows you to author, schedule and monitor workflows as directed acyclic graphs (DAGs).

Airflow requires several services to run - a database, message queue, scheduler, web server etc. Docker Compose allows you to quickly run all these services locally in containers.

Running Airflow with Docker Compose
Install Docker and Docker Compose on your machine if you haven't already.

Create a directory for the Airflow deployment.

Download the docker-compose.yaml file for Airflow:  
`curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.3.0/docker-compose.yaml'`

Start up the Airflow containers: docker-compose up


This will start containers for the Airflow scheduler, webserver, worker, triggerer and other services.

Access the Airflow UI at  http://localhost:8080 and login with username: airflow and password airflow.

Create a simple Python DAG and place it in the dags folder. Observe it getting picked up and running in the Airflow UI.

Tear down the deployment: `docker-compose down`

Reflection
In this reading, you deployed Apache Airflow locally using Docker Compose.

Challenge
In this reading, you deployed Apache Airflow locally using Docker Compose next, grab a Wikipedia page by using the  Airflow scheduler. Here is a good command to start with to grab a page:   

`curl https://simple.wikipedia.org/wiki/LeBron_James`