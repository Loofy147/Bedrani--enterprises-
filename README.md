# EspoCRM Docker Compose Setup

This repository contains Docker Compose configurations for setting up EspoCRM for both local development and production environments.

-   **Local Development:** A simple setup using the base `docker-compose.yml` file for quick local testing.
-   **Production:** A robust, secure setup using `docker-compose.prod.yml` which includes a reverse proxy (Nginx), SSL certificate management (Certbot), a PostGIS database, and an S3-compatible file store (MinIO).

## Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Configure Environment Variables

Create a `.env` file by copying the provided example. This file stores credentials and configuration for both environments.

```bash
cp .env.example .env
```

Open `.env` in a text editor and fill in the required values.

### 2. Local Development Setup

For local development, the setup uses a MariaDB database and exposes the application on port 8080.

#### Launch

```bash
docker-compose up -d
```

#### Access

-   **EspoCRM:** [http://localhost:8080](http://localhost:8080)
-   **Login:** Use the `ESPO_ADMIN_USERNAME` and `ESPO_ADMIN_PASSWORD` from your `.env` file.

#### Stop

```bash
docker-compose down
```

---

### 3. Production Deployment

The production setup is designed for a public-facing server and includes:

-   **Nginx:** Reverse proxy to handle incoming traffic.
-   **Certbot:** Automated SSL certificate generation and renewal with Let's Encrypt for HTTPS.
-   **PostgreSQL + PostGIS:** A more powerful database with spatial data support.
-   **MinIO:** An S3-compatible object storage for robust file management.

#### Prerequisites for Production

-   A server with a public IP address.
-   A registered domain name (e.g., `your-domain.com`) with a DNS A record pointing to your server's IP (e.g., `crm.your-domain.com -> YOUR_SERVER_IP`).

#### Step 1: Configure Production Settings

Before deploying, update the following files with your actual domain and email address:

1.  **`.env` file:**
    -   Set `ESPO_SITE_URL` to your full domain (e.g., `https://crm.your-domain.com`).
    -   Fill in strong passwords for `POSTGRES_PASSWORD` and `MINIO_ROOT_PASSWORD`.

2.  **`docker-compose.prod.yml`:**
    -   In the `certbot` service, update the `command` to include your email and domain:
        `--email your-email@example.com -d crm.your-domain.com`

3.  **`deploy/nginx/conf.d/app.conf`:**
    -   Replace all instances of `crm.your-domain.com` with your actual domain.

4.  **`deploy/init-letsencrypt.sh`:**
    -   Update the `DOMAINS` and `EMAIL` variables at the top of the script.

#### Step 2: Obtain SSL Certificate

This step provisions the initial SSL certificate required by Nginx.

```bash
bash deploy/init-letsencrypt.sh
```

This script will:
1.  Temporarily start Nginx with a dummy certificate.
2.  Use Certbot to request a real certificate from Let's Encrypt.
3.  Reload Nginx with the new certificate.

#### Step 3: Launch Production Stack

Now you can launch the full production stack.

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Access Production Services

-   **EspoCRM:** `https://crm.your-domain.com`
-   **MinIO Console:** `http://<your_server_ip>:9001` (Login with `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD`)

#### Stopping the Production Stack

```bash
docker-compose -f docker-compose.prod.yml down
```

The data for all services is stored in Docker volumes, so it will be preserved.
