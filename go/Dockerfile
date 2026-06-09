############################
# ---- Build Stage ----
############################
FROM public.ecr.aws/docker/library/golang:1.26-alpine3.23 AS builder

# ---- Build arguments ----
ARG APP_NAME=healthcheck
ARG VERSION=1.0.0
ARG COMMIT=unknown

# ---- Environment variables ----
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

# Install certificates (for HTTPS calls if needed)
RUN apk add --no-cache ca-certificates

WORKDIR /app

# Copy go module files first (better caching)
# COPY go.mod go.sum ./
COPY go.mod ./
RUN go mod download

# Copy application source
COPY . .

# Build binary with security flags
RUN go build \
    -ldflags="-s -w -X main.version=${VERSION} -X main.commit=${COMMIT}" \
    -o /${APP_NAME}

# Optional: Run tests
FROM builder AS run-test
RUN go test -v ./...

############################
# ---- Production Stage ----
############################
FROM public.ecr.aws/docker/library/alpine:3.23.3

# ---- Runtime arguments ----
ARG APP_NAME=healthcheck

# ---- Runtime environment ----
ENV APP_ENV=production \
    APP_PORT=8080 \
    TZ=UTC

# Install minimal required packages only
RUN apk add --no-cache ca-certificates tzdata \
    && addgroup appgroup \
    && adduser -D appuser -G appgroup

WORKDIR /app

# Copy binary from builder
COPY --from=builder /${APP_NAME} /usr/local/bin/${APP_NAME}

# Create necessary directories with correct ownership
RUN mkdir -p /tmp/ready \
    # Set owner
    # && chown -R appuser:appgroup /tmp/ready \
    # Set scope
    && chmod -R 550 /tmp/ready 

# Use non-root user
USER appuser

EXPOSE 8080

# Run as non-root
ENTRYPOINT ["/usr/local/bin/healthcheck"]