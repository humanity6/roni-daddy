#!/bin/bash
# Build script for Hostinger Git integration - Admin Dashboard

echo "🚀 Starting admin dashboard build..."

# Install dependencies
npm ci

# Build the admin dashboard
npm run build

echo "✅ Admin dashboard build completed!"
echo "📁 Built files are in ./dist/"