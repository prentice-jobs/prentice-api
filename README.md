# prentice-api
This repository contains the source code for the API of the Prentice project, a one stop platform for undergraduates to research about their dream internship.

## Structure
The `prentice-api` codebase is structured as a monolith with 4 distinct services, namely `Account`, `Review`, `Company`, and `Salary` services. It boasts 15+ API endpoints to provide services for the frontend client. The services in detail: 

### Account
The `Account` service provides the APIs to interact with user account logic. For example, registering a new user, saving user preferences, and checking if a user exists. 

### Review
The `Review` service provides the APIs to interact with company reviews within the app. Clients can create and fetch company reviews, upload offer letters as proof, create review comment, like or unlike a comment, and more.

### Company
The `Company` service provides the APIs to interact with the company objects. This is designated for Prentice Admin users only and will utilize RBAC in the future. Here clients can create new companies, fetch companies, and perform other CRUD operations.

### Salary
The `Salary` service provides the APIs to interact with salary related logic, such as comparing salary between two companies.

## Running the app locally
1. Clone this repository using `git clone`
2. Create virtual environments using `python -m venv .venv`
3. Activate venv `source .venv/bin/activate`
4. Install all dependencies through `pip install -r requirements.txt`
4. Ensure you have the correct environment variables in your `.env` file located at the root of the project
5. Run `make dev` and the app should run on your local machine

## Containerizing the app using Docker
1. Clone this repository using `git clone`
2. Ensure you have Docker Engine and Docker Daemon installed on your machine
3. Build Docker Image using `docker build . --file ./Dockerfile --tag prentice-api`
4. Run container from image using Docker Desktop or on CLI: `docker run -it prentice-api`
5. Your app should be up and running!
