"""
Synapse Package Registry Service
Centralized package management for quantum algorithms and libraries
"""

import hashlib
import json
import os
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import aioredis
import asyncpg
import boto3
import toml
import yaml
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Synapse Package Registry",
    description="Package management for quantum algorithms and libraries",
    version="1.0.0"
)

# Database and storage connections
postgres_pool = None
redis_client = None
s3_client = None

# Configuration
PACKAGE_STORAGE_PATH = os.getenv("PACKAGE_STORAGE_PATH", "/app/packages")
S3_BUCKET = os.getenv("S3_BUCKET", "synapse-packages")
MAX_PACKAGE_SIZE = 100 * 1024 * 1024  # 100MB

# --- Models ---

class PackageMetadata(BaseModel):
    name: str = Field(..., pattern="^[a-z0-9-]+$")
    version: str
    description: str
    author: str
    author_email: str | None = None
    license: str = "MIT"
    homepage: str | None = None
    repository: str | None = None
    keywords: list[str] = []
    classifiers: list[str] = []
    dependencies: list[str] = []
    quantum_requirements: dict[str, Any] = {}

class Package(BaseModel):
    id: str
    name: str
    version: str
    description: str
    author: str
    author_email: str | None
    license: str
    homepage: str | None
    repository: str | None
    keywords: list[str]
    classifiers: list[str]
    dependencies: list[str]
    quantum_requirements: dict[str, Any]
    downloads: int
    stars: int
    created_at: datetime
    updated_at: datetime
    published_by: str
    size_bytes: int
    checksum: str
    verified: bool = False
    deprecated: bool = False

class PackageSearch(BaseModel):
    query: str
    category: str | None = None
    tags: list[str] = []
    min_qubits: int | None = None
    max_qubits: int | None = None
    hardware_compatible: str | None = None
    limit: int = 20
    offset: int = 0

class PackageStats(BaseModel):
    daily_downloads: list[dict[str, Any]]
    total_downloads: int
    unique_users: int
    average_rating: float
    version_history: list[dict[str, Any]]

# --- Startup/Shutdown ---

@app.on_event("startup")
async def startup():
    global postgres_pool, redis_client, s3_client

    # PostgreSQL for package metadata
    postgres_pool = await asyncpg.create_pool(
        "postgresql://synapse:synapse@postgres:5432/packages"
    )

    # Redis for caching and search
    redis_client = await aioredis.create_redis_pool("redis://redis:6379")

    # S3 for package storage
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )

    # Create tables if not exist
    await create_tables()

    # Ensure storage directory exists
    Path(PACKAGE_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

@app.on_event("shutdown")
async def shutdown():
    await postgres_pool.close()
    redis_client.close()
    await redis_client.wait_closed()

async def create_tables():
    """Create database tables"""
    async with postgres_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                version VARCHAR(50) NOT NULL,
                description TEXT,
                author VARCHAR(255),
                author_email VARCHAR(255),
                license VARCHAR(100),
                homepage VARCHAR(500),
                repository VARCHAR(500),
                keywords TEXT[],
                classifiers TEXT[],
                dependencies TEXT[],
                quantum_requirements JSONB,
                downloads INTEGER DEFAULT 0,
                stars INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                published_by VARCHAR(255),
                size_bytes BIGINT,
                checksum VARCHAR(64),
                verified BOOLEAN DEFAULT FALSE,
                deprecated BOOLEAN DEFAULT FALSE,
                UNIQUE(name, version)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS package_versions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                package_name VARCHAR(255),
                version VARCHAR(50),
                release_notes TEXT,
                breaking_changes BOOLEAN DEFAULT FALSE,
                released_at TIMESTAMP DEFAULT NOW(),
                yanked BOOLEAN DEFAULT FALSE
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS package_reviews (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                package_name VARCHAR(255),
                user_id VARCHAR(255),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                review TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Create indices
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_package_name ON packages(name)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_package_keywords ON packages USING GIN(keywords)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_package_downloads ON packages(downloads DESC)")

# --- Package Upload ---

@app.post("/api/v1/packages/upload")
async def upload_package(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload a new package to the registry"""

    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_PACKAGE_SIZE:
        raise HTTPException(400, f"Package size exceeds {MAX_PACKAGE_SIZE} bytes")

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Extract and validate package
        metadata = await extract_package_metadata(tmp_path)

        # Check if version already exists
        existing = await get_package(metadata.name, metadata.version)
        if existing:
            raise HTTPException(400, f"Package {metadata.name}@{metadata.version} already exists")

        # Calculate checksum
        checksum = hashlib.sha256(contents).hexdigest()

        # Store package file
        await store_package_file(
            metadata.name,
            metadata.version,
            contents,
            checksum
        )

        # Create database entry
        package_id = await create_package_entry(
            metadata,
            len(contents),
            checksum,
            "user_id"  # Would come from auth
        )

        # Background tasks
        background_tasks.add_task(scan_package_security, package_id)
        background_tasks.add_task(build_search_index, metadata.name)
        background_tasks.add_task(notify_subscribers, metadata.name, metadata.version)

        return {
            "package_id": package_id,
            "name": metadata.name,
            "version": metadata.version,
            "checksum": checksum,
            "status": "published"
        }

    finally:
        os.unlink(tmp_path)

async def extract_package_metadata(package_path: str) -> PackageMetadata:
    """Extract metadata from package archive"""

    with tarfile.open(package_path, "r:gz") as tar:
        # Look for package.yaml or package.json
        for member in tar.getmembers():
            if member.name.endswith("package.yaml"):
                f = tar.extractfile(member)
                data = yaml.safe_load(f.read())
                return PackageMetadata(**data)
            elif member.name.endswith("package.json"):
                f = tar.extractfile(member)
                data = json.loads(f.read())
                return PackageMetadata(**data)
            elif member.name.endswith("pyproject.toml"):
                f = tar.extractfile(member)
                data = toml.loads(f.read().decode())
                # Extract from pyproject.toml format
                project = data.get("project", {})
                return PackageMetadata(
                    name=project.get("name"),
                    version=project.get("version"),
                    description=project.get("description", ""),
                    author=project.get("authors", [{}])[0].get("name", "Unknown"),
                    dependencies=project.get("dependencies", [])
                )

    raise HTTPException(400, "No package metadata found")

async def store_package_file(name: str, version: str, contents: bytes, checksum: str) -> str:
    """Store package file in S3 or local storage"""

    filename = f"{name}-{version}.tar.gz"

    if s3_client:
        # Store in S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=f"packages/{name}/{version}/{filename}",
            Body=contents,
            Metadata={
                "checksum": checksum,
                "content-type": "application/gzip"
            }
        )
        return f"s3://{S3_BUCKET}/packages/{name}/{version}/{filename}"
    else:
        # Store locally
        package_dir = Path(PACKAGE_STORAGE_PATH) / name / version
        package_dir.mkdir(parents=True, exist_ok=True)

        package_file = package_dir / filename
        package_file.write_bytes(contents)

        return str(package_file)

async def create_package_entry(
    metadata: PackageMetadata,
    size_bytes: int,
    checksum: str,
    published_by: str
) -> str:
    """Create package entry in database"""

    async with postgres_pool.acquire() as conn:
        result = await conn.fetchrow("""
            INSERT INTO packages (
                name, version, description, author, author_email,
                license, homepage, repository, keywords, classifiers,
                dependencies, quantum_requirements, size_bytes, checksum,
                published_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            RETURNING id
        """,
            metadata.name, metadata.version, metadata.description,
            metadata.author, metadata.author_email, metadata.license,
            metadata.homepage, metadata.repository, metadata.keywords,
            metadata.classifiers, metadata.dependencies,
            json.dumps(metadata.quantum_requirements),
            size_bytes, checksum, published_by
        )

        return str(result["id"])

# --- Package Search ---

@app.post("/api/v1/packages/search")
async def search_packages(search: PackageSearch):
    """Search for packages with advanced filters"""

    # Build query
    query = """
        SELECT * FROM packages
        WHERE deprecated = FALSE
    """
    params = []
    param_count = 0

    # Text search
    if search.query:
        param_count += 1
        query += f" AND (name ILIKE ${param_count} OR description ILIKE ${param_count})"
        params.append(f"%{search.query}%")

    # Category filter
    if search.category:
        param_count += 1
        query += f" AND ${param_count} = ANY(classifiers)"
        params.append(search.category)

    # Tag filter
    if search.tags:
        param_count += 1
        query += f" AND keywords && ${param_count}"
        params.append(search.tags)

    # Quantum requirements
    if search.min_qubits:
        param_count += 1
        query += f" AND (quantum_requirements->>'min_qubits')::int >= ${param_count}"
        params.append(search.min_qubits)

    if search.max_qubits:
        param_count += 1
        query += f" AND (quantum_requirements->>'max_qubits')::int <= ${param_count}"
        params.append(search.max_qubits)

    # Order and pagination
    query += " ORDER BY downloads DESC, stars DESC"
    param_count += 1
    query += f" LIMIT ${param_count}"
    params.append(search.limit)

    param_count += 1
    query += f" OFFSET ${param_count}"
    params.append(search.offset)

    # Execute search
    async with postgres_pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

        packages = [
            Package(
                id=str(row["id"]),
                name=row["name"],
                version=row["version"],
                description=row["description"],
                author=row["author"],
                author_email=row["author_email"],
                license=row["license"],
                homepage=row["homepage"],
                repository=row["repository"],
                keywords=row["keywords"],
                classifiers=row["classifiers"],
                dependencies=row["dependencies"],
                quantum_requirements=json.loads(row["quantum_requirements"]),
                downloads=row["downloads"],
                stars=row["stars"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                published_by=row["published_by"],
                size_bytes=row["size_bytes"],
                checksum=row["checksum"],
                verified=row["verified"],
                deprecated=row["deprecated"]
            )
            for row in rows
        ]

        # Get total count
        count_query = "SELECT COUNT(*) FROM packages WHERE deprecated = FALSE"
        if search.query:
            count_query += " AND (name ILIKE $1 OR description ILIKE $1)"
            total = await conn.fetchval(count_query, f"%{search.query}%")
        else:
            total = await conn.fetchval(count_query)

        return {
            "results": packages,
            "total": total,
            "page": search.offset // search.limit + 1,
            "pages": (total + search.limit - 1) // search.limit
        }

# --- Package Download ---

@app.get("/api/v1/packages/{name}/{version}/download")
async def download_package(name: str, version: str):
    """Download a package"""

    # Get package info
    package = await get_package(name, version)
    if not package:
        raise HTTPException(404, f"Package {name}@{version} not found")

    # Increment download counter
    await increment_downloads(name, version)

    # Get file path
    filename = f"{name}-{version}.tar.gz"

    if s3_client:
        # Download from S3
        try:
            response = s3_client.get_object(
                Bucket=S3_BUCKET,
                Key=f"packages/{name}/{version}/{filename}"
            )
            return StreamingResponse(
                response["Body"],
                media_type="application/gzip",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        except Exception as e:
            raise HTTPException(500, f"Failed to download package: {e}")
    else:
        # Serve from local storage
        file_path = Path(PACKAGE_STORAGE_PATH) / name / version / filename
        if not file_path.exists():
            raise HTTPException(404, "Package file not found")

        return FileResponse(
            file_path,
            media_type="application/gzip",
            filename=filename
        )

@app.get("/api/v1/packages/{name}/{version}")
async def get_package_info(name: str, version: str = "latest"):
    """Get package information"""

    # Resolve version
    if version == "latest":
        version = await get_latest_version(name)
        if not version:
            raise HTTPException(404, f"Package {name} not found")

    package = await get_package(name, version)
    if not package:
        raise HTTPException(404, f"Package {name}@{version} not found")

    return package

@app.get("/api/v1/packages/{name}/versions")
async def list_package_versions(name: str):
    """List all versions of a package"""

    async with postgres_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT version, created_at, size_bytes, downloads
            FROM packages
            WHERE name = $1
            ORDER BY created_at DESC
        """, name)

        if not rows:
            raise HTTPException(404, f"Package {name} not found")

        versions = [
            {
                "version": row["version"],
                "created_at": row["created_at"],
                "size_bytes": row["size_bytes"],
                "downloads": row["downloads"]
            }
            for row in rows
        ]

        return {
            "name": name,
            "versions": versions,
            "latest": versions[0]["version"] if versions else None
        }

# --- Package Statistics ---

@app.get("/api/v1/packages/{name}/stats")
async def get_package_stats(name: str) -> PackageStats:
    """Get package statistics"""

    async with postgres_pool.acquire() as conn:
        # Get download history
        downloads = await conn.fetch("""
            SELECT DATE(created_at) as date, COUNT(*) as downloads
            FROM package_downloads
            WHERE package_name = $1
            AND created_at > NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """, name)

        # Get total downloads
        total = await conn.fetchval("""
            SELECT SUM(downloads) FROM packages WHERE name = $1
        """, name)

        # Get unique users
        unique_users = await conn.fetchval("""
            SELECT COUNT(DISTINCT user_id)
            FROM package_downloads
            WHERE package_name = $1
        """, name)

        # Get average rating
        avg_rating = await conn.fetchval("""
            SELECT AVG(rating) FROM package_reviews WHERE package_name = $1
        """, name)

        # Get version history
        versions = await conn.fetch("""
            SELECT version, created_at, downloads
            FROM packages
            WHERE name = $1
            ORDER BY created_at DESC
        """, name)

        return PackageStats(
            daily_downloads=[
                {"date": str(row["date"]), "downloads": row["downloads"]}
                for row in downloads
            ],
            total_downloads=total or 0,
            unique_users=unique_users or 0,
            average_rating=float(avg_rating) if avg_rating else 0.0,
            version_history=[
                {
                    "version": row["version"],
                    "released": row["created_at"],
                    "downloads": row["downloads"]
                }
                for row in versions
            ]
        )

# --- Helper Functions ---

async def get_package(name: str, version: str) -> Package | None:
    """Get package from database"""

    async with postgres_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM packages
            WHERE name = $1 AND version = $2
        """, name, version)

        if not row:
            return None

        return Package(
            id=str(row["id"]),
            name=row["name"],
            version=row["version"],
            description=row["description"],
            author=row["author"],
            author_email=row["author_email"],
            license=row["license"],
            homepage=row["homepage"],
            repository=row["repository"],
            keywords=row["keywords"],
            classifiers=row["classifiers"],
            dependencies=row["dependencies"],
            quantum_requirements=json.loads(row["quantum_requirements"]),
            downloads=row["downloads"],
            stars=row["stars"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            published_by=row["published_by"],
            size_bytes=row["size_bytes"],
            checksum=row["checksum"],
            verified=row["verified"],
            deprecated=row["deprecated"]
        )

async def get_latest_version(name: str) -> str | None:
    """Get latest version of a package"""

    async with postgres_pool.acquire() as conn:
        version = await conn.fetchval("""
            SELECT version FROM packages
            WHERE name = $1
            ORDER BY created_at DESC
            LIMIT 1
        """, name)

        return version

async def increment_downloads(name: str, version: str):
    """Increment download counter"""

    async with postgres_pool.acquire() as conn:
        await conn.execute("""
            UPDATE packages
            SET downloads = downloads + 1
            WHERE name = $1 AND version = $2
        """, name, version)

        # Also track in downloads table for analytics
        await conn.execute("""
            INSERT INTO package_downloads (package_name, version, user_id, created_at)
            VALUES ($1, $2, $3, NOW())
        """, name, version, "anonymous")  # Would use actual user_id

async def scan_package_security(package_id: str):
    """Scan package for security issues"""
    # Implement security scanning
    pass

async def build_search_index(package_name: str):
    """Build search index for package"""
    # Update search index in Redis/Elasticsearch
    pass

async def notify_subscribers(package_name: str, version: str):
    """Notify subscribers of new package version"""
    # Send notifications
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
