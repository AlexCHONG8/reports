#!/bin/bash
# Deploy to Render.com - Free Cloud Hosting
# Complete setup script

echo "🚀 Setting up your FREE cloud PDF converter on Render.com"
echo "======================================================"

# Step 1: Install dependencies
echo ""
echo "📦 Step 1: Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"

# Step 2: Test locally
echo ""
echo "🧪 Step 2: Testing locally (optional)..."
echo "Run this to test: python3 render_deploy.py"
echo "Then visit: http://localhost:10000"
echo ""
read -p "Test locally? (y/n): " test_local

if [ "$test_local" = "y" ]; then
    echo "Starting local test..."
    echo "Press Ctrl+C to stop"
    python3 render_deploy.py
fi

# Step 3: Git setup
echo ""
echo "📝 Step 3: Setting up Git repository..."
git init
git add .
git commit -m "Initial commit: PDF converter for Render"

# Step 4: GitHub setup
echo ""
echo "🌐 Step 4: Push to GitHub"
echo "You need to create a GitHub repository first"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Create a new repository (name it 'pdf-converter')"
echo "3. Run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/pdf-converter.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

# Step 5: Render setup
echo "======================================================"
echo "🎯 Step 5: Deploy to Render.com (FREE)"
echo "======================================================"
echo ""
echo "1. Go to: https://render.com"
echo "2. Sign up (free)"
echo "3. Click 'New +' button"
echo "4. Select 'Web Service'"
echo "5. Connect your GitHub repo"
echo "6. Configure:"
echo "   - Name: pdf-converter"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python render_deploy.py"
echo "7. Click 'Deploy Web Service'"
echo ""
echo "8. IMPORTANT: Add Environment Variable"
echo "   - Go to your service → Settings → Environment"
echo "   - Add: MINERU_API_KEY = your-api-key"
echo "   - (Use the key from your config.ini)"
echo ""
echo "9. Deploy takes ~2-3 minutes"
echo "10. You'll get a URL like: https://pdf-converter.onrender.com"
echo ""
echo "======================================================"
echo "✅ Setup complete!"
echo "======================================================"
echo ""
echo "Test your deployment:"
echo "curl -X POST -F 'file=@test.pdf' https://your-app.onrender.com/convert"
echo ""
echo "For full setup guide, see: cloud_solutions.md"
echo ""
