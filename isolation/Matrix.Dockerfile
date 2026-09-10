ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /work
COPY synapse_lang-*.whl /opt/
RUN pip install --no-cache-dir /opt/synapse_lang-*.whl pytest pytest-cov pyyaml numba
COPY . /work
CMD ["sh", "-c", "python -m pytest tests/ -o addopts='' -q --junitxml=/work/linux-results.xml && cd /tmp && python -I /work/scripts/wheel_smoke.py"]
