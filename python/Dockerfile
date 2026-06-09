############################
# ---- Build Stage ----
############################
FROM public.ecr.aws/docker/library/python:3.14.3-slim AS builder

# Prevent Python from writing .pyc outside our control
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Run on virtual env
ENV PATH="/venv/bin:$PATH"
RUN python -m venv /venv


# Copy the contents of the backend directory into the container at /app
COPY requirements.txt .

# Install dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source into builder
COPY app.py .

# Compile Python source to bytecode
RUN python -m compileall -b app.py

# Move only compiled file to artifact directory
RUN mkdir /artifact && \
    mv app.pyc /artifact/

############################
# ---- Production Stage ----
############################

# Use a slim Python image as the final base image
FROM public.ecr.aws/docker/library/python:3.14.3-slim AS runner

# Create non-root user (CIS Docker Benchmark compliant)
ARG APP_USER=appuser
ARG APP_UID=10001
ARG APP_GID=10001

RUN groupadd --gid ${APP_GID} ${APP_USER} && \
    useradd --uid ${APP_UID} --gid ${APP_GID} \
    --create-home --shell /usr/sbin/nologin ${APP_USER}

# Set the working directory to /app
WORKDIR /app

# Runtime environment
ENV PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# Copy the built dependencies from the virtual env in previous stage
COPY --from=builder /venv /venv

# Copy ONLY compiled artifact
COPY --from=builder /artifact/app.pyc /app/app.pyc

# Create directory
RUN mkdir -p /tmp/ready \
    # Set owner
    # && chown -R {APP_UID}:${APP_GID} /tmp/ready \
    # Set scope
    && chmod -R 550 /tmp/ready 

USER ${APP_USER}

# Expose port 8080 for the Flask application
EXPOSE 8080

# Define the default command to run the application
CMD ["python", "app.pyc"]
