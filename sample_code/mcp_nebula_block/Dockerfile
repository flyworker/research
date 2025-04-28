FROM python:3.10-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies and the package
RUN pip install --no-cache-dir -e .

# Set the entrypoint
ENTRYPOINT ["mcp-server-nebula-block"] 