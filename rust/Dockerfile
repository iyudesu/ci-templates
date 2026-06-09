# Use rust base image
FROM public.ecr.aws/docker/library/rust:1.86-alpine3.20 AS builder

# Set build arguments (can be overridden at build time)
ARG APP_NAME=rust
ARG VERSION=1.0.0
ARG COMMIT=unknown

# Set the working directory
WORKDIR /app

# Install libraries
RUN apk add libc-dev 

# Copy the entire project
COPY . .

# Build the application
RUN cargo build --release

# Second stage for a smaller image
FROM public.ecr.aws/docker/library/alpine:3.23.3

ARG APP_NAME=rust
ARG APP_UID=10001
ARG APP_GID=10001

ENV APP_HOME=/app \
    RUST_LOG=info

# Set the working directory
WORKDIR /app

# Update libraries
RUN apk update \
    && apk add --no-cache ca-certificates \
    && addgroup appgroup \
    && adduser -D appuser -G appgroup

# Copy the built binary from the builder stage, binary name check when test build on local
COPY --from=builder /app/target/release/rust .

# Create directory
RUN mkdir -p /tmp/ready \
    # set owner
    # chown -R ${APP_UID}:${APP_GID} /tmp/ready
    # Set scope
    && chmod -R 550 /tmp/ready 

# Use non-root user
USER appuser

# Expose port
EXPOSE 8080

# Set the entrypoint to the Rust app
CMD ["./rust"]
