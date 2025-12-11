# EspoCRM Docker Compose Setup

This directory contains a `docker-compose.yml` file to quickly set up a local instance of EspoCRM, a powerful open-source CRM application.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

Follow these steps to configure and launch your EspoCRM instance:

### 1. Configure Environment Variables

First, create a `.env` file by copying the provided example file. This file will store your sensitive credentials and configuration settings.

```bash
cp .env.example .env
```

Next, open the `.env` file in a text editor and replace the placeholder values with your own secure credentials for the database and EspoCRM admin user.

```
# .env

# MariaDB settings
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=espocrm
MYSQL_USER=espocrm_user
MYSQL_PASSWORD=your_secure_user_password

# EspoCRM settings
ESPO_ADMIN_USERNAME=admin
ESPO_ADMIN_PASSWORD=your_secure_admin_password
ESPO_SITE_URL=http://localhost:8080
```

**Note:** Do not commit the `.env` file to version control if it contains sensitive information.

### 2. Launch the Application

Once you have configured your `.env` file, you can start the EspoCRM application using Docker Compose. Run the following command in your terminal from the same directory as the `docker-compose.yml` file:

```bash
docker-compose up -d
```

This command will download the necessary Docker images and start the EspoCRM application and its database in the background (`-d` flag).

### 3. Access EspoCRM

After the containers have started, you can access your EspoCRM instance by opening your web browser and navigating to the `ESPO_SITE_URL` you configured in your `.env` file. By default, this is:

[http://localhost:8080](http://localhost:8080)

You can log in with the admin username and password you set in the `.env` file.

### 4. Stopping the Application

To stop the EspoCRM application and its containers, run the following command:

```bash
docker-compose down
```

This will stop and remove the containers. The data stored in the database will be preserved in a Docker volume, so you can start the application again with `docker-compose up -d` without losing your data.
