# 🐳 Docker Publishing Instructions for v2.3.2

## Quick Commands to Run

Open **PowerShell** or **Command Prompt** on Windows and navigate to your project:

```powershell
cd C:\Users\micha\synapse-lang
```

Then run:

```powershell
.\docker_publish.bat
```

## Manual Steps (if script doesn't work)

### 1. Build the Docker Image

```bash
docker build -t michaelcrowe11/synapse-lang:2.3.2 -t michaelcrowe11/synapse-lang:latest .
```

### 2. Test the Image

```bash
docker run --rm michaelcrowe11/synapse-lang:2.3.2 python -c "import synapse_lang; print(synapse_lang.__version__)"
```

Expected output: `2.3.2`

### 3. Push to Docker Hub

```bash
# Push version tag
docker push michaelcrowe11/synapse-lang:2.3.2

# Push latest tag
docker push michaelcrowe11/synapse-lang:latest
```

## What's New in v2.3.2

- **PEP 625 Compliance**: Package naming now uses underscore (synapse_lang)
- **Updated Dependencies**: Installs from PyPI v2.3.2
- **Author Email**: Updated to michael@crowelogic.com
- **All Features**: Still includes all 8 major enhancements

## Verification

After pushing, verify at:
- https://hub.docker.com/r/michaelcrowe11/synapse-lang/tags

You should see:
- `2.3.2` tag
- `latest` tag (pointing to 2.3.2)
- `2.3.1` tag (previous version)
- `2.3.0` tag (older version)

## Complete Docker Commands

```bash
# Pull the new version
docker pull michaelcrowe11/synapse-lang:2.3.2

# Run interactive shell
docker run -it michaelcrowe11/synapse-lang:2.3.2

# Run Jupyter notebook
docker run -p 8888:8888 michaelcrowe11/synapse-lang:2.3.2 jupyter notebook --ip=0.0.0.0 --allow-root

# Run with volume mount
docker run -it -v $(pwd):/workspace michaelcrowe11/synapse-lang:2.3.2

# Run demo
docker run michaelcrowe11/synapse-lang:2.3.2 python /app/examples/demo_all_features.py
```

## Docker Compose Update

Update your docker-compose.yml to use v2.3.2:

```yaml
version: '3.8'

services:
  synapse-dev:
    image: michaelcrowe11/synapse-lang:2.3.2
    volumes:
      - ./workspace:/workspace
    ports:
      - "8888:8888"
    command: jupyter lab --ip=0.0.0.0 --allow-root --no-browser
```

## Status

- ✅ Dockerfile updated to v2.3.2
- ✅ Installs from PyPI v2.3.2 (PEP 625 compliant)
- ✅ Publishing script updated
- ⏳ Awaiting Docker Desktop to build and push

---

**Ready to publish!** Just run `.\docker_publish.bat` in PowerShell when Docker Desktop is running.