# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Build argument to choose which nginx config to use
# Default is 'local' (for docker-compose), use 'azure' for Azure deployment
ARG DEPLOY_TARGET=local

# Copy the appropriate nginx config based on deploy target
COPY nginx.conf /tmp/nginx.local.conf
COPY nginx.azure.conf /tmp/nginx.azure.conf

# Use shell to conditionally copy the right config
RUN if [ "$DEPLOY_TARGET" = "azure" ]; then \
    cp /tmp/nginx.azure.conf /etc/nginx/conf.d/default.conf; \
    else \
    cp /tmp/nginx.local.conf /etc/nginx/conf.d/default.conf; \
    fi && \
    rm -rf /tmp/*.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
