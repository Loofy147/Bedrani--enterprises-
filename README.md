# PropTech Platform

This repository contains the source code for a multi-tenant PropTech platform.

## Architecture

The platform is built on a microservices architecture and orchestrated using Docker Compose. The main components are:

- **Backend API:** A Python-based API built with FastAPI.
- **Frontend Applications:** Multiple frontend applications built with Next.js and TypeScript, one for each tenant (e.g., "Maamur", "Djelali").
- **Database:** A PostgreSQL database with the PostGIS extension for geospatial data.
- **Reverse Proxy:** Traefik is used as a reverse proxy in the production environment to manage routing and SSL certificates.

## Development Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Getting Started

1.  **Configure Backend Environment Variables:**

    Create a `.env` file in the root directory by copying the example file:

    ```bash
    cp .env.example .env
    ```

    Update the `.env` file with your desired database credentials.

2.  **Configure Frontend Environment Variables:**

    Create a `.env.local` file in the `frontend-djelali` directory:

    ```bash
    touch frontend-djelali/.env.local
    ```

    Add the following line to the file, pointing to the API's URL:

    ```
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

3.  **Launch the Application:**

    Start the development environment using Docker Compose:

    ```bash
    docker-compose up -d --build
    ```

4.  **Access the Services:**

    -   **`frontend-djelali`:** [http://localhost:3000](http://localhost:3000)
    -   **API:** [http://localhost:8000](http://localhost:8000)
