#!/bin/sh
# Docker entrypoint script for frontend
# Generates nginx.conf from template with environment variables

set -e

# Default values - EXPORT to make available for envsubst
export BACKEND_INTERNAL_PORT=${BACKEND_INTERNAL_PORT:-8000}

echo "🔧 Configuring Nginx with BACKEND_INTERNAL_PORT=${BACKEND_INTERNAL_PORT}"

# Generate nginx.conf from template
envsubst '${BACKEND_INTERNAL_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "✅ Nginx configuration generated successfully"
cat /etc/nginx/conf.d/default.conf

# Start Nginx
echo "🚀 Starting Nginx..."
exec nginx -g 'daemon off;'
