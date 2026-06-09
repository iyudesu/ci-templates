############################
# ---- Build Stage ----
############################
FROM public.ecr.aws/docker/library/node:23.11.0-alpine3.21 AS builder

# Set build arguments (can be overridden at build time)
ARG NODE_ENV=production
ARG VERSION=1.0.0
ARG COMMIT=unknown
ARG APP_HOME=/app

# Environment variables
ENV NODE_ENV=${NODE_ENV}

# Install required packages
RUN apk add --no-cache libc6-compat

WORKDIR ${APP_HOME}

# Copy only package files first (better layer caching)
COPY package*.json ./

# Install only production dependencies
RUN npm ci && \
    npm cache clean --force

# Copy application source
COPY . .

# Build application
RUN npm run build

# Remove dev dependencies after build
RUN npm prune --omit=dev

############################
# ---- Production Stage ----
############################
FROM public.ecr.aws/docker/library/node:23.11.0-alpine3.21 AS runner

# Set runtime argument variables
ARG NODE_ENV=production 
ARG PORT=8080 
ARG APP_HOME=/app

# Create non-root user and group
RUN addgroup nodegroup && \
    adduser -D nodeuser -G nodegroup

# Set working directory
WORKDIR ${APP_HOME}

# Copy ONLY required runtime artifacts
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

# Remove unnecessary files
RUN rm -rf \
    /root/.npm \
    /tmp/* \
    /var/cache/apk/*

# Create required directory with correct permissions
RUN mkdir -p /tmp/ready \
    # Set owner
    # && chown -R nodeuser:appgroup /tmp/ready \
    # Set scope
    && chmod -R 550 /tmp/ready 

# Switch to non-root user
USER nodeuser

# Expose application port
EXPOSE ${PORT}

# Use CMD instead of ENTRYPOINT for better override flexibility
CMD ["node", "dist/app.js"]