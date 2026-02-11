# Technical SEO Audit Tool

A navigation-based SEO audit tool that crawls website navigation links and identifies technical SEO issues. Built with FastAPI (Python) backend and vanilla JavaScript frontend.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the Application](#running-the-application-using-Docker)
- [Testing Locally](#testing-locally-without-docker)
- [Features](#features)
- [SEO Checks Performed](#seo-checks-performed)
- [Navigation Detection Strategy](#navigation-link-detection-strategy)
- [Architecture Overview](#architecture-overview)
- [API Documentation](#api-examples)
- [Common Problems and Solutions](#common-problems-and-solutions)
- [Important Commands](#important-commands)
- [Trade-offs and Limitations](#trade-offs--limitations)
- [Evolution Roadmap](#evolution-to-full-seo-crawler)
- [Technologies Used](#technologies-used)

---

## Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0 or higher

### Three Steps to Run

```bash
# 1. Clone the repository
git clone <repository-url>
cd seo-audit-tool

# 2. Start the application
docker compose up --build

# 3. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

---

## Installation

### Step 1: Install Docker

#### Windows

1. Visit: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Run the installer
4. Restart your computer after installation
5. Open Docker Desktop and ensure it is running

#### Mac

1. Visit: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Mac
3. Install the application
4. Open Docker Desktop and make sure it is running

#### Linux

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker

# Optional: Add user to docker group to run without sudo
sudo usermod -aG docker $USER
# Log out and log back in for changes to take effect
```

### Step 2: Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker info
```

If all commands execute without errors, Docker is properly installed.

---

## Running the Application

### Start the Application

```bash
docker compose up --build
```

**First run will take 3-5 minutes** as Docker downloads and builds the required images.

### Access the Application

Once the application is running, you can access:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Stop the Application

To stop all running containers:

```bash
docker compose down
```

This will stop and remove the containers and network.

### Alternative Stop Options

**Option 1: Stop without removing containers**
```bash
docker compose stop
```

**Option 2: If running in foreground**
```bash
Press: Ctrl + C
```

**Option 3: Stop and remove containers, networks, and images**
```bash
docker compose down --rmi all
```

### Remove Everything (Full Cleanup)

To stop containers and delete associated volumes:
```bash
docker compose down -v
```

To remove all unused Docker data (containers, images, networks, cache):
```bash
docker system prune -a
```

**Note:** This will remove all unused Docker resources from your system.

---

## Testing Locally (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000

### Frontend Setup

Simply open `frontend/index.html` in a browser, or use a local server:

```bash
cd frontend
python -m http.server 3000
```

The frontend will be available at http://localhost:3000

---

## Features

### Backend (FastAPI)

- **POST /audit** - Start a new SEO audit
- **GET /audit/{audit_id}** - Retrieve audit results
- **GET /health** - Health check endpoint

### Frontend

- Simple, functional UI to trigger audits
- Real-time status updates with polling
- Expandable page details
- Summary metrics dashboard

---

## SEO Checks Performed

The tool performs the following SEO checks on each crawled page:

### 1. Title Tag

- Missing title
- Title too short (< 30 chars)
- Title too long (> 60 chars)

### 2. Meta Description

- Missing meta description
- Description too short (< 120 chars)
- Description too long (> 160 chars)

### 3. H1 Tags

- Missing H1
- Multiple H1 tags

### 4. Canonical URL

- Missing canonical tag

### 5. Indexability

- Noindex directive present

### 6. HTTP Status

- Non-200 status codes

### 7. Page Metrics

- Page size (KB)
- Internal links count

---

## Navigation Link Detection Strategy

The crawler identifies main navigation links using the following multi-strategy approach:

### Strategy Priority (in order)

#### 1. Primary Strategy: `<nav>` Elements

- Searches for semantic `<nav>` HTML5 tags
- Most reliable indicator of navigation structure

#### 2. Secondary Strategy: `<header>` Elements

- If no `<nav>` found, searches within `<header>` tags
- Common pattern for top-level navigation

#### 3. Tertiary Strategy: Class/ID-based Detection

- Searches for elements with navigation-related classes/IDs
- Matches: `nav`, `menu`, `header`, `navigation`
- Searches within `<div>` and `<ul>` elements

#### 4. Fallback Strategy: First `<ul>`

- If all else fails, uses the first unordered list
- Assumes it's likely the main menu

### Link Filtering Rules

The crawler applies the following filters:

- **Include:** Same-domain links only
- **Include:** Converts relative URLs to absolute
- **Include:** Deduplicates URLs
- **Exclude:** External domains
- **Exclude:** Footer links
- **Exclude:** Sidebar links
- **Exclude:** In-content links
- **Exclude:** URL fragments (#)

### Documentation Note

The assumption is that the **first matching element** from the strategies above represents the main navigation. This works well for most standard website layouts but may need refinement for complex sites with multiple navigation menus.

---

## Architecture Overview

### Backend Architecture

```
backend/
├── main.py              # FastAPI application & endpoints
├── crawler.py           # Navigation crawler logic
├── seo_analyzer.py      # SEO analysis engine
├── database.py          # In-memory data storage
├── requirements.txt     # Python dependencies
└── Dockerfile           # Backend container config
```

#### Request Flow

1. Client sends POST request to `/audit` with URL
2. Server creates audit record and returns `audit_id`
3. Background task starts:
   - Fetches homepage
   - Extracts navigation links
   - Crawls each link asynchronously
   - Analyzes SEO metrics
   - Stores results
4. Client polls GET `/audit/{audit_id}` until status = "completed"
5. Results returned with summary and page details

### Frontend Architecture

```
frontend/
├── index.html          # Single-page application
├── style.css           # CSS styling
├── script.js           # JavaScript logic
└── Dockerfile          # Nginx container config
```

**Technologies:**

- Vanilla JavaScript (no framework)
- Fetch API for HTTP requests
- CSS Grid/Flexbox for layout
- Polling mechanism for async updates

### Docker Architecture

```
docker-compose.yml      # Service orchestration
├── backend service     # Port 8000
└── frontend service    # Port 3000 (Nginx)
```

### Data Flow

```
User Input (URL)
    ↓
Frontend (POST /audit)
    ↓
Backend API (Create Audit)
    ↓
Background Task
    ↓
Crawler (Fetch + Parse Navigation)
    ↓
SEO Analyzer (Check Issues)
    ↓
Database (Store Results)
    ↓
Frontend (Poll GET /audit/{id})
    ↓
Display Results
```

---

## API Examples

### Start an Audit

**Endpoint:** POST /audit

**Request:**
```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "message": "Audit started successfully"
}
```

### Get Audit Results

**Endpoint:** GET /audit/{audit_id}

**Request:**
```bash
curl http://localhost:8000/audit/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "url": "https://example.com",
  "status": "completed",
  "results": {
    "url": "https://example.com",
    "pages_crawled": 5,
    "summary": {
      "missing_title": 0,
      "missing_meta_description": 1,
      "multiple_h1": 0,
      "noindex_pages": 0,
      "non_200_pages": 0
    },
    "pages": [
      {
        "url": "https://example.com",
        "status_code": 200,
        "title": "Example Domain",
        "title_length": 14,
        "meta_description": "",
        "meta_description_length": 0,
        "h1_count": 1,
        "canonical_present": false,
        "noindex": false,
        "page_size_kb": 1.23,
        "internal_links": 1,
        "issues": [
          "MISSING_META_DESCRIPTION",
          "MISSING_CANONICAL"
        ]
      }
    ]
  }
}
```

---

## Common Problems and Solutions

### 1. Port 3000 already in use

**Problem:** Another application is using port 3000

**Solution:**
```bash
# Stop any application that is using port 3000
# Or change the port in docker-compose.yml
ports:
  - "3001:80"  # Use 3001 instead of 3000
```

### 2. Docker daemon not running

**Problem:** Docker service is not started

**Solution:**

- Open the Docker Desktop application
- Wait until Docker finishes starting
- Ensure the Docker (whale) icon shows that Docker is running

### 3. Cannot connect to backend

**Problem:** Frontend cannot reach the backend API

**Solution:**
```bash
# Check if the backend container is running
docker compose ps

# View backend logs for errors
docker compose logs backend
```

### 4. Permission denied (Linux)

**Problem:** User doesn't have permission to access Docker

**Solution:**
```bash
sudo usermod -aG docker $USER
# Log out and log back in for the changes to take effect
```

### 5. Frontend not loading

**Problem:** Frontend page not displaying correctly

**Solution:**
```bash
# Clear the browser cache
# Or open the application in Incognito/Private mode
# Rebuild and recreate containers
docker compose up --build --force-recreate
```

---

## Important Commands

### Starting and Stopping

```bash
# Start the application
docker compose up

# Start in background (detached mode)
docker compose up -d

# Stop and remove containers
docker compose down

# Rebuild and start
docker compose up --build
```

### Viewing Logs

```bash
# View logs (live)
docker compose logs -f

# View logs for a specific service
docker compose logs backend
docker compose logs frontend
```

### Container Management

```bash
# List running containers
docker compose ps

# Access a container (for debugging)
docker compose exec backend bash
docker compose exec frontend sh
```

---

## Trade-offs & Limitations

### Current Limitations

#### 1. In-Memory Storage

**Limitation:**
- Data lost on restart
- No persistence between sessions
- Not suitable for production

**Solution:**
- Use PostgreSQL/MongoDB with SQLAlchemy/Motor

#### 2. Navigation Detection

**Limitation:**
- Heuristic-based approach
- May not work for all website structures
- Single navigation assumption

**Solution:**
- ML-based navigation detection or user-configurable selectors

#### 3. No JavaScript Rendering

**Limitation:**
- Only crawls static HTML
- Misses SPAs and dynamic content

**Solution:**
- Integrate Playwright/Selenium for JS rendering

#### 4. Synchronous Blocking

**Limitation:**
- Background tasks use asyncio but still run in-process
- Heavy crawls could impact API responsiveness

**Solution:**
- Use Celery with Redis/RabbitMQ for distributed task queue

#### 5. No Rate Limiting

**Limitation:**
- Could overwhelm target servers
- No respect for robots.txt

**Solution:**
- Implement rate limiting and robots.txt parsing

#### 6. Single Audit at a Time

**Limitation:**
- No concurrency control

**Solution:**
- Implement job queue with worker pools

#### 7. Basic Error Handling

**Limitation:**
- Minimal retry logic
- No timeout configuration

**Solution:**
- Exponential backoff, configurable timeouts

#### 8. Security

**Limitation:**
- No authentication
- Open CORS policy

**Solution:**
- Add JWT auth, API keys, rate limiting

---

## Evolution to Full SEO Crawler

### Phase 1: Core Infrastructure

- [ ] Replace in-memory DB with PostgreSQL
- [ ] Implement Celery task queue
- [ ] Add Redis for caching
- [ ] User authentication system

### Phase 2: Enhanced Crawling

- [ ] JavaScript rendering (Playwright)
- [ ] Sitemap.xml parsing
- [ ] Robots.txt compliance
- [ ] Configurable crawl depth
- [ ] Custom CSS selectors for navigation

### Phase 3: Advanced SEO Checks

- [ ] Mobile-friendliness check
- [ ] Page speed metrics (Core Web Vitals)
- [ ] Structured data validation
- [ ] Image optimization checks
- [ ] Internal linking analysis
- [ ] Broken link detection
- [ ] Redirect chain detection

### Phase 4: Reporting & Analytics

- [ ] PDF report generation
- [ ] Historical trend tracking
- [ ] Competitor comparison
- [ ] Custom dashboards
- [ ] Email alerts for issues
- [ ] Scheduled recurring audits

### Phase 5: Scalability

- [ ] Kubernetes deployment
- [ ] Distributed crawling
- [ ] CDN integration
- [ ] Multi-region support
- [ ] Auto-scaling workers

### Phase 6: Additional Features

- [ ] Chrome extension
- [ ] Slack/Discord integrations
- [ ] API client libraries (Python, Node.js)
- [ ] Webhook notifications
- [ ] White-label support

---

## Technologies Used

### Backend

- **FastAPI** - Modern, fast web framework
- **httpx** - Async HTTP client
- **BeautifulSoup4** - HTML parsing
- **lxml** - Fast XML/HTML processor
- **Pydantic** - Data validation

### Frontend

- **Vanilla JavaScript** - No framework overhead
- **Nginx** - Production-grade web server

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

---

**Created by Kunal Pandey**
