# sql-app

SQL-APP is a simple RESTful API built using Python's FastAPI library to demonstrate Vault's Public Key Infrastructure (PKI) and Database secrets engine capabilities. The app retrieves an SSL certificate on startup and uses database credentials managed by Vault for backend database requests. Usage metrics are exposed to Prometheus for usage and availability monitoring.

## Getting Started
A fully configured HashiCorp Vault server is required for this application. See my Vault_DB_Engine project (linked at the end) for more information.

## How It's Made:

**Tech used:** Python, FastAPI, Docker

Initially built as a demo script retrieving database credentials from Vault in a loop, SQL-APP became a great launching off point for practice in building and deploying containers and container orchestration using Docker Compose. It also serves as an example of how to secure traffic being sent and received by the application using SSL certificates issued by Vault's PKI secrets engine. Short lived certificates and credentials in an application are essential to modern application security where security requirements are increasingly strict.

## Lessons Learned:

This project has been instrumental in my goal of learning Python and Vault beyond a simple Key/Value static secrets storage solution. Adopting dynamic, short lived credentials and certificates in a lab environment provides the perfect foundation for implementing secure solutions in the future.

As applications are onboarded to Vault, it is important to consider a couple of factors to ensure Vault is used in a healthy way:

1. Token Type:
    Determining which type of token to use depends a lot on how the application behaves. Does your application process batches in short bursts? Maybe consider batch tokens. Is your application long-lived? Is maximum control over the token's lifecycle important? In that case service tokens would serve well. Misunderstanding Vault's token system is sure to cause problems down the road as your needs grow.

2. Monitoring:
    Monitoring of Vault as well as client applications such as SQL-APP is crucial to the health of your infrastructure. Rogue applications requesting thousands of Vault tokens can quickly cripple your Vault cluster leading to downtime. Monitoring as well as appropriately tuned rate limits on requests to Vault can mitigate these issues, however ensuring your application only requests resources from Vault as needed is equally as important. 

3. Available client libraries:
    Client libraries such as Python's HVAC make interacting with Vault more intuitive, providing guidance and a fast way to get started for developers. Vault also has a fully featured API which is the core of how users and applications interact with Vault. This is perfect for shell scripts, or other languages where a client library is not available. 

Implementing a CI/CD pipeline using GitHub Actions into the project was also a huge benefit. This allowed me to simply commit my changes to the repository, allow the build to complete, push the image to GitHub Packages, then pull and run the image via Docker Compose. The images are tagged with the branch name as well as the SHA-256 image digest, making it easy to get started with the latest version or ensure the same image is pulled every time.

This project was also my first exposure to Prometheus. Coming from an infrastructure background, deciding what metrics to track was an interesting change of pace. I would like to build this out further in the future by adding more metrics and introducing artificial variations in things like database latency to track in Prometheus.

## Links: 
Check out my Vault_DB_Engine project for specifics on my Vault implementation and container orchestration using Docker Compose:

https://github.com/igallion/Vault_DB_Engine