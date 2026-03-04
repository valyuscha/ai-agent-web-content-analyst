#!/bin/bash

echo "🔧 Fixing Frontend Setup..."
echo ""

cd "$(dirname "$0")"

# Clean
echo "Cleaning build artifacts..."
rm -rf .next node_modules package-lock.json

# Install
echo "Installing dependencies..."
npm install

# Verify
echo ""
echo "✅ Setup complete!"
echo ""
echo "Now run:"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000"
