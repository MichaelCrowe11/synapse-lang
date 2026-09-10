# Build context must be release-dist/, never the repository or home directory.
FROM python:3.12-slim@sha256:09f7da3bc104798d0afb40bc08d23ab2da20a76130cec1f2ef170848f5d85217
COPY synapse_lang-*.whl /opt/
RUN pip install --no-cache-dir /opt/synapse_lang-*.whl
USER 65534:65534
WORKDIR /tmp
CMD ["python", "-I", "-m", "synapse_lang._container_worker"]
