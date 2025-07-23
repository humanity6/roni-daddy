#!/bin/bash
# Script to create a deployment branch with built files

echo "🚀 Building and deploying to Hostinger..."

# Build mobile app
echo "📱 Building mobile app..."
npm ci
npm run build

# Build admin dashboard
echo "🔧 Building admin dashboard..."
cd admin-dashboard
npm ci
npm run build
cd ..

# Create deployment branch
echo "📤 Creating deployment branch..."
git checkout -b hostinger-deploy 2>/dev/null || git checkout hostinger-deploy

# Copy built files to root for Hostinger
echo "📁 Preparing files for Hostinger..."
cp -r dist/* .
mkdir -p admin
cp -r admin-dashboard/dist/* admin/

# Commit built files
git add .
git commit -m "Deploy built files to Hostinger"
git push origin hostinger-deploy --force

echo "✅ Deployment branch created!"
echo "📋 Now configure Hostinger Git to use 'hostinger-deploy' branch"

# Switch back to main
git checkout main