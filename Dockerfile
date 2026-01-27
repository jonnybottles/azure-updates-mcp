FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Expose MCP server port
EXPOSE 8000

# Set environment defaults
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Run the server
CMD ["python", "-m", "azure_updates_mcp.server"]
