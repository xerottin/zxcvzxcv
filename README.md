# 🛒 Delivery Service API

## 📌 Description

**Delivery Service API** is a backend service for automating delivery operations.
Core functionality:

1. **Companies** — create and manage companies.
2. **Branches** — each branch is linked to a company and has its own product list.
3. **Products** — add, edit, and delete products.
4. **Orders** — users can place orders for products from branches.
5. **Automatic User Cleanup** — if a user hasn’t logged in for more than **2 days**, the system removes them.

---

## 🚀 Features

* 🏢 **Multi-company support** — manage multiple companies and branches.
* 📦 **Product catalog** — flexible product management.
* 🛍 **Orders** — create and track orders.
* 🔒 **JWT authentication** — secure API access.
* 🧹 **Automatic cleanup** — remove inactive users every 24 hours.
* 📜 **Swagger UI** — ready-to-use API documentation.

---

## 🛠 Tech Stack

| Technology               | Purpose                      |
| ------------------------ | ---------------------------- |
| Python 3.12              | Programming language         |
| **FastAPI**              | REST API framework           |
| **PostgreSQL**           | Database                     |
| **SQLAlchemy + Alembic** | ORM + migrations             |
| **Celery + Rabbitmq**    | Tasks                        |
| **Redis**                | Caching and background tasks |
| **Docker & Compose**     | Containerization             |
| **Gunicorn + Uvicorn**   | Application server           |

---

## 🖥 Running the Project Locally

### 1. Clone the Repository

```bash
git clone https://github.com/xerottin/cafeteria.git
```

### 2. Ensure Docker is Installed

Install Docker from the official site if necessary: [Docker](https://www.docker.com/).

### 3. Create a Docker Network

```bash
docker network create cafeteria-network
```

### 4. Build and Run Docker Containers

```bash
docker compose up --build
```

### 5 Open API Documentation

Once the server is running, you can explore the interactive Swagger UI documentation here:

👉 **http://0.0.0.0:8000/docs#/**

---

## 🎉 Conclusion

Your local development environment is now ready!
You can customize the Docker setup and database configurations as needed.

---

