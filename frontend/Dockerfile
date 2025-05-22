# Frontend Dockerfile - React + Tailwind Dashboard
# Multi-stage build for both development and production

# ---- Base Stage ----
FROM node:23-alpine AS base
WORKDIR /app
# Add package files for more efficient caching
COPY package.json package-lock.json* ./

# ---- Development Stage ----
FROM base AS development
# Install dependencies (including dev dependencies)
RUN npm ci
# Copy the rest of the code
COPY . .
# Expose port
EXPOSE 3000
# Start the development server
CMD ["npm", "run", "dev"]

# ---- Build Stage ----
FROM base AS builder
# Install dependencies
RUN npm ci
# Copy the rest of the code
COPY . .
# Build the application
RUN npm run build

# ---- Production Stage ----
FROM nginx:23-alpine AS production
# Copy built artifacts from build stage
COPY --from=builder /app/out /usr/share/nginx/html
# Copy custom nginx configuration if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port
EXPOSE 80
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]