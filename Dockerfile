# Taken from https://github.com/astral-sh/uv-docker-example
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory in the container
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project 

# Install Quarto
RUN apt-get update && apt-get install -y wget gnupg ca-certificates \
    && wget -qO quarto.deb "https://github.com/quarto-dev/quarto-cli/releases/download/v1.5.0/quarto-1.5.0-linux-amd64.deb" \
    && apt-get install -y ./quarto.deb \
    && rm -f quarto.deb \
    && rm -rf /var/lib/apt/lists/*

# Add the rest of the project source code
COPY . .

EXPOSE 8080

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Start dagster webserver 
CMD uv run dagster dev --host 0.0.0.0 --port 8080
