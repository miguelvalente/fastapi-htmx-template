FROM ghcr.io/astral-sh/uv:0.7-python3.12-bookworm-slim
LABEL org.opencontainers.image.source=https://github.com/cyberaci/minerva-test-suite

# Install curl and postgresql-client for psql
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl postgresql-client wget gnupg && \
    # Install GitHub CLI
    mkdir -p -m 755 /etc/apt/keyrings && \
    wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    # Clean up apt cache
    rm -rf /var/lib/apt/lists/*


# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 80

RUN curl -fsSL https://raw.githubusercontent.com/pressly/goose/master/install.sh | sh 

ENV GOOSE_DRIVER=postgres
ENV GOOSE_MIGRATION_DIR="migrations"

CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0"]