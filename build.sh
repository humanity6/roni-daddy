#!/bin/bash
# Build script for Hostinger Git integration - Mobile App

echo "🚀 Starting mobile app build..."

# Install dependencies
npm ci

# Build the mobile app
npm run build

echo "✅ Mobile app build completed!"
echo "📁 Built files are in ./dist/"