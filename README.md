# StockFlow MVP – SaaS Inventory Management System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#how-to-execute-tests)
[![Tests](https://img.shields.io/badge/pytest-73%20passed-success.svg)](#how-to-execute-tests)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.165.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react)](https://react.dev)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?logo=mysql)](https://www.mysql.com)

StockFlow is a cloud-native, multi-tenant B2B SaaS Inventory Management System designed to help modern businesses track warehouse stock levels, prevent inventory stockouts, automate reorder alerts, and analyze total asset valuations in real time.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Solution](#3-solution)
4. [Features](#4-features)
5. [Technology Stack](#5-technology-stack)
6. [Project Architecture](#6-project-architecture)
7. [Folder Structure](#7-folder-structure)
8. [Database Design](#8-database-design)
9. [API Endpoints](#9-api-endpoints)
10. [Prerequisites](#10-prerequisites)
11. [Backend Installation](#11-backend-installation)
12. [Frontend Installation](#12-frontend-installation)
13. [Environment Variable Configuration](#13-environment-variable-configuration)
14. [How to Run the Application](#14-how-to-run-the-application)
15. [How to Execute Tests](#15-how-to-execute-tests)
16. [Production Deployment Instructions](#16-production-deployment-instructions)

---

## 1. Project Overview

StockFlow MVP delivers a full-stack inventory lifecycle platform. Built with a high-performance Python (FastAPI) backend and a React (Vite) frontend, StockFlow supports multi-organization data isolation, strict SKU uniqueness per tenant, atomic concurrent stock deductions, low-stock threshold triggers, and real-time executive dashboard KPIs.

---

## 2. Problem Statement

Growing supply chain and retail businesses face critical operational bottlenecks:
- **Stockouts and Overselling**: Lack of atomic decrement operations causes overselling during concurrent purchase requests.
- **Data Cross-Contamination**: Shared database architectures without strict tenancy filters expose sensitive enterprise stock counts and margins across competitors.
- **Delayed Visibility**: Manual spreadsheets fail to provide aggregated inventory valuation and real-time low-stock alerts.
- **Complex Setups**: Traditional ERPs are bloated, expensive, and take months to deploy.

---

## 3. Solution

StockFlow solves these challenges by providing:
- **Multi-Tenant Isolation**: Every database query is scoped strictly to the authenticated user's `organization_id` using JWT tokens.
- **Safe Concurrency & Underflow Protection**: Pessimistic database locking (`with_for_update()`) and conditional decrement clauses prevent inventory from falling below zero under high concurrency.
- **Real-Time Analytics Engine**: Dynamic aggregation endpoints return live inventory metrics, out-of-stock counts, and total monetary valuation without precision loss.
- **Intuitive SaaS User Interface**: A modern React dashboard providing instant catalog filtering, one-click stock adjustments, and organization settings.

---

## 4. Features

### Multi-Tenant Authentication & Access Control
- Organization-level registration (creates tenant organization and admin user simultaneously).
- Secure JWT (JSON Web Token) authentication with configurable expiration.
- Argon2 / PBKDF2 password hashing with timing attack resistance.

### Product Catalog Management
- Full CRUD capabilities for products (SKU, Name, Description, Price, Initial Quantity, Low-Stock Threshold).
- SKU uniqueness enforced per organization (different organizations can reuse the same internal SKUs without collisions).
- Server-side search by Product Name and SKU with limit/offset pagination.

### Stock Operations
- **Increase Stock**: Concurrency-safe addition with audit trails (tracks previous quantity, updated quantity, and delta).
- **Decrease Stock**: Safe stock deduction verifying sufficient balance; rejects negative balance and concurrent race conditions.
- **Low-Stock Detection**: Real-time identification of products where `quantity <= low_stock_threshold`.

### Executive Dashboard & Analytics
- Live KPI cards: Total Products, Total In-Stock Units, Total Monetary Valuation ($), Low-Stock Items, Out-of-Stock Items.
- High-priority Low-Stock alerts table with direct one-click restock modals.
- Numeric-safe valuation calculations avoiding floating-point rounding discrepancies.

### Organization Profile & Settings
- Tenant profile management (Organization Name, Contact Email, Contact Phone, Default Low-Stock Threshold).
- Strict validation rules (international phone numbers, RFC-compliant email, threshold $\ge 0$).

---

## 5. Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11+) | Async-ready, OpenAPI documentation, dependency injection |
| **Database ORM** | SQLAlchemy 2.0 | Declarative mapping, session management, pessimistic row locks |
| **Database Driver** | PyMySQL | Pure-Python MySQL client with connection pooling |
| **Data Validation** | Pydantic v2 | High-performance schema validation, custom field validators |
| **Authentication** | Python-JOSE + Pwdlib | JWT verification, Argon2 password hashing |
| **Testing** | Pytest + AnyIO | 73 automated unit and integration tests |
| **Frontend Framework** | React 18 + Vite 6 | Fast HMR, optimized production build |
| **Routing** | React Router DOM v6 | Protected layouts, SPA client-side routing |
| **HTTP Client** | Axios | Request/Response interceptors, JWT Bearer attachment |
| **Icons & UI** | Lucide React | Modern SVG icons and clean SaaS design system |

---

## 6. Project Architecture

```mermaid
flowchart TD
    Client["React Frontend (Vite)"] -->|HTTPS / REST API| FastAPI["FastAPI Application"]
    FastAPI --> AuthMiddleware["JWT Auth Dependency (get_current_user)"]
    AuthMiddleware --> TenancyFilter["Org Isolation (organization_id)"]
    TenancyFilter --> Routes["API Routers: Auth, Products, Stock, Dashboard, Org"]
    Routes --> ORM["SQLAlchemy ORM (SessionLocal)"]
    ORM --> DB[("MySQL Database (stockflow_db)")]
```

---

## 7. Folder Structure

```text
StockFlow MVP/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic BaseSettings (DB, JWT, CORS)
│   │   │   └── security.py           # Password hashing & JWT generation/decoding
│   │   ├── database.py               # Engine, SessionLocal, declarative Base, get_db
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── organization.py       # Organization ORM model
│   │   │   ├── user.py               # User ORM model
│   │   │   └── product.py            # Product ORM model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Login, Signup, UserProfile schemas
│   │   │   ├── product.py            # ProductCreate, ProductUpdate, ProductResponse
│   │   │   ├── stock.py              # StockAdjustmentRequest, StockAdjustmentResponse
│   │   │   ├── dashboard.py          # DashboardSummaryResponse, InventoryValueResponse
│   │   │   └── organization.py       # OrganizationSettingsResponse, Update schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # /auth/signup, /auth/login, /auth/me
│   │   │   ├── products.py           # CRUD /products/
│   │   │   ├── stock.py              # /products/{id}/stock/increase, decrease, low-stock
│   │   │   ├── dashboard.py          # /dashboard/summary, low-stock, inventory-value
│   │   │   └── organization.py       # /organization/settings
│   │   └── main.py                   # FastAPI instantiation, CORS, router mounts, /health
│   ├── tests/
│   │   ├── test_mysql_connection.py
│   │   ├── test_phase2.py            # Auth & JWT verification tests
│   │   ├── test_phase3.py            # Product schema & CRUD tests
│   │   ├── test_products.py          # Organization isolation product tests
│   │   ├── test_stock.py             # Stock increase, decrease & concurrency tests
│   │   ├── test_dashboard.py         # Summary & inventory valuation tests
│   │   └── test_organization.py      # Organization settings tests
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/               # ProtectedRoute, Modal, Toast, LoadingSpinner
│   │   │   ├── layout/               # AppLayout, Sidebar, TopNav
│   │   │   └── stock/                # StockModal
│   │   ├── context/
│   │   │   └── AuthContext.jsx       # Global auth provider & token manager
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Products.jsx
│   │   │   ├── Stock.jsx
│   │   │   ├── Settings.jsx
│   │   │   └── NotFound.jsx
│   │   ├── services/
│   │   │   └── api.js                # Centralized Axios with Bearer token interceptor
│   │   ├── App.jsx                   # React Router route tree
│   │   ├── index.css                 # SaaS custom CSS system
│   │   └── main.jsx
│   ├── .env.example
│   ├── package.json
│   ├── vercel.json                   # Vercel SPA routing rewrite rules
│   └── vite.config.js
├── render.yaml                       # Render backend infrastructure as code
└── README.md
```

---

## 8. Database Design

### Entity Relationship Diagram
```mermaid
erDiagram
    ORGANIZATIONS ||--o{ USERS : "employs"
    ORGANIZATIONS ||--o{ PRODUCTS : "owns"

    ORGANIZATIONS {
        int id PK "auto_increment"
        varchar name "NOT NULL"
        varchar contact_email "NULL"
        varchar contact_phone "NULL"
        int default_low_stock_threshold "DEFAULT 5"
        datetime created_at
        datetime updated_at
    }

    USERS {
        int id PK "auto_increment"
        varchar name "NOT NULL"
        varchar email "UNIQUE, NOT NULL"
        varchar password_hash "NOT NULL"
        int organization_id FK "NOT NULL"
        datetime created_at
    }

    PRODUCTS {
        int id PK "auto_increment"
        varchar name "NOT NULL"
        varchar sku "NOT NULL"
        text description "NULL"
        numeric price "10,2 NOT NULL"
        int quantity "NOT NULL DEFAULT 0"
        int low_stock_threshold "NOT NULL DEFAULT 5"
        int organization_id FK "NOT NULL"
        datetime created_at
        datetime updated_at
    }
```

### Constraints & Indexes
- **Compound Unique Index**: `products(organization_id, sku)` guarantees SKU uniqueness within a tenant, while permitting distinct tenants to utilize matching SKUs.
- **Foreign Keys**: `users.organization_id -> organizations.id` and `products.organization_id -> organizations.id` with referential integrity.
- **Optimized Filters**: Indexed `organization_id` ensures lightning-fast queries even as tenant data scales to millions of rows.

---

## 9. API Endpoints

### Authentication & Profiles
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Register new organization & administrator account | No |
| `POST` | `/auth/login` | Authenticate user & issue JWT bearer access token | No |
| `GET` | `/auth/me` | Fetch authenticated user profile and organization ID | Bearer JWT |

### Product Management
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/products/` | Create a new product in the user's organization | Bearer JWT |
| `GET` | `/products/?skip=0&limit=10&search=` | List & search organization products with pagination | Bearer JWT |
| `GET` | `/products/{product_id}` | Retrieve details for a specific product by ID | Bearer JWT |
| `PUT` | `/products/{product_id}` | Update product information (name, price, SKU, etc.) | Bearer JWT |
| `DELETE`| `/products/{product_id}` | Delete a product from inventory permanently | Bearer JWT |

### Stock Operations
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/products/{id}/stock/increase` | Atomically increment product inventory quantity | Bearer JWT |
| `POST` | `/products/{id}/stock/decrease` | Atomically decrement stock with underflow check | Bearer JWT |
| `GET` | `/products/low-stock` | List items where `quantity <= low_stock_threshold` | Bearer JWT |

### Dashboard & Analytics
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/summary` | Aggregate counts, stock units & inventory value | Bearer JWT |
| `GET` | `/dashboard/low-stock` | Filtered list of low-stock products for dashboard | Bearer JWT |
| `GET` | `/dashboard/inventory-value` | Monetary valuation and total quantities | Bearer JWT |

### Organization Settings
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/organization/settings` | Retrieve company profile & low-stock default threshold | Bearer JWT |
| `PUT` | `/organization/settings` | Update company name, phone, email & threshold | Bearer JWT |

### System & Health
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Application health and status verification | No |
| `GET` | `/` | API root welcoming message | No |

---

## 10. Prerequisites

Before installing, ensure the following are installed on your machine:
- **Python**: Version `3.10` or higher (`python --version`)
- **Node.js**: Version `18.0` or higher (`node -v`)
- **npm**: Version `9.0` or higher (`npm -v`)
- **MySQL Server**: Version `8.0` or higher running locally or accessible in the cloud

---

## 11. Backend Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
3. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your local environment:
   ```bash
   cp .env.example .env
   ```
   *(Update `.env` with your local MySQL credentials).*

---

## 12. Frontend Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Configure frontend environment:
   ```bash
   cp .env.example .env
   ```
   Ensure `VITE_API_BASE_URL` points to `http://127.0.0.1:8000`.

---

## 13. Environment Variable Configuration

### Backend (`backend/.env`)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `APP_NAME` | Application title | `StockFlow MVP` |
| `DEBUG` | Enable debug logs (`True` or `False`) | `False` |
| `DATABASE_URL` | Cloud MySQL connection string (Optional) | `mysql+pymysql://user:pass@host:3306/db` |
| `DATABASE_HOST` | MySQL hostname | `localhost` |
| `DATABASE_PORT` | MySQL port | `3306` |
| `DATABASE_NAME` | Database schema name | `stockflow_db` |
| `DATABASE_USER` | Database user account | `root` |
| `DATABASE_PASSWORD`| Database user password | `your_secure_password` |
| `SECRET_KEY` | 64-char random string for JWT signing | `c9f37...8a1` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token validity window | `60` |
| `CORS_ORIGINS` | Allowed frontend domains (comma-separated or `*`)| `http://localhost:5173,https://app.vercel.app` |

### Frontend (`frontend/.env`)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Root URL for the FastAPI backend | `http://127.0.0.1:8000` |

---

## 14. How to Run the Application

Open two separate terminal windows:

### Terminal 1: Start Backend (FastAPI)
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API will be live at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger OpenAPI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Terminal 2: Start Frontend (React + Vite)
```powershell
cd frontend
npm run dev
```
- Web Application will be live at: [http://localhost:5173](http://localhost:5173)

---

## 15. How to Execute Tests

### Run Backend Pytest Suite
From the `backend` directory:
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v
```
Expected output:
```text
tests/test_dashboard.py ...........                                      [ 15%]
tests/test_mysql_connection.py .                                         [ 16%]
tests/test_organization.py .........                                     [ 28%]
tests/test_phase2.py ..................                                  [ 53%]
tests/test_phase3.py .....                                               [ 60%]
tests/test_products.py ..............                                    [ 80%]
tests/test_stock.py ..............                                       [100%]

============================= 73 passed in 2.10s ==============================
```

### Verify Frontend Production Build
From the `frontend` directory:
```bash
cd frontend
npm run build
```
Expected output:
```text
✓ 1656 modules transformed.
dist/index.html                   0.79 kB │ gzip:  0.45 kB
dist/assets/index-B1jjsd6g.css   11.32 kB │ gzip:  2.91 kB
dist/assets/index-BApiCqRQ.js   286.20 kB │ gzip: 89.59 kB
✓ built in 2.33s
```

---

## 16. Production Deployment Instructions

### 1. Database Deployment (Managed Cloud MySQL)
1. Provision a MySQL database instance on a cloud provider such as:
   - **Aiven MySQL** (Free tier available)
   - **PlanetScale**
   - **Amazon RDS**
   - **Railway**
2. Obtain your secure connection string:
   ```text
   mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>?ssl_ca=/path/to/ca.pem
   ```
3. Ensure the database user has `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `INDEX`, and `ALTER` privileges. Tables are automatically initialized on startup via `Base.metadata.create_all()`.

---

### 2. Backend Deployment on Render
1. Push your repository to GitHub.
2. Sign in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Web Service** and connect your GitHub repository (`stockflow-mvp`).
4. Configure service settings:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, define:
   - `DATABASE_URL`: Cloud MySQL connection URI.
   - `SECRET_KEY`: A secure 64-character random string (`openssl rand -hex 32`).
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g. `https://stockflow.vercel.app`).
   - `DEBUG`: `False`
6. Click **Create Web Service**. Your backend will be deployed at `https://stockflow-backend.onrender.com`.

*(Alternatively, connect using the included `render.yaml` Blueprint).*

---

### 3. Frontend Deployment on Vercel
1. Sign in to [Vercel](https://vercel.com).
2. Click **Add New** -> **Project** and select your `stockflow-mvp` repository.
3. In the project setup screen:
   - **Root Directory**: Set to `frontend`.
   - **Framework Preset**: `Vite` (automatically detected).
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add the following **Environment Variable**:
   - `VITE_API_BASE_URL`: Your live Render backend URL (e.g. `https://stockflow-backend.onrender.com`).
5. Click **Deploy**.
6. The included `frontend/vercel.json` ensures that deep-linking and browser refreshes on routes like `/dashboard`, `/products`, and `/stock` resolve cleanly to `index.html`.

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
