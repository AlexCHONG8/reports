# PDF Converter - Free Cloud Hosting

Automated PDF to Markdown conversion using MinerU API, deployed on Render.com (FREE tier).

## 🚀 Quick Start

### Deploy Your Own Cloud Service (5 minutes)

1. **Star this repo** ⭐

2. **Deploy to Render.com:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect this GitHub repository
   - Settings:
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python render_deploy.py`
   - Click "Deploy Web Service"

3. **Add Environment Variable:**
   - Go to your service → Settings → Environment
   - Add: `MINERU_API_KEY` = your MinerU API key
   - Get API key from: https://mineru.net

4. **Test your deployment:**
   ```bash
   curl -X POST -F "file=@document.pdf" https://your-app.onrender.com/convert
   ```

## 📁 Project Structure

```
├── render_deploy.py          # FastAPI web service (main cloud app)
├── mineru_auto_converter.py  # Local file watcher (for Mac)
├── requirements.txt          # Python dependencies
├── Dockerfile               # Render deployment config
├── cloud_solutions.md       # Cloud deployment guide
└── README.md               # This file
```

## 🔧 Usage

### Cloud API (Deployed on Render)

**Upload PDF for conversion:**
```bash
curl -X POST -F "file=@document.pdf" https://your-app.onrender.com/convert
```

**Check conversion status:**
```bash
curl https://your-app.onrender.com/status/TASK_ID
```

**Get markdown result:**
```bash
curl https://your-app.onrender.com/result/TASK_ID
```

**Convert and wait (all-in-one):**
```bash
curl -X POST -F "file=@document.pdf" \
  https://your-app.onrender.com/convert-and-wait
```

### Local File Watcher (Mac)

Run locally to monitor a folder:
```bash
pip3 install -r requirements.txt
python3 mineru_auto_converter.py
```

Drop PDFs into `input/` folder → get Markdown in `output/` folder.

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check (used by Render) |
| `/convert` | POST | Upload PDF, get task_id |
| `/status/{task_id}` | GET | Check conversion status |
| `/result/{task_id}` | GET | Get markdown result |
| `/convert-and-wait` | POST | Upload and wait for completion |

## 💡 Features

- ✅ **Zero local processing** - Everything runs in cloud
- ✅ **Free hosting** - Render.com free tier
- ✅ **Auto-scaling** - Handles multiple requests
- ✅ **SSL included** - Secure HTTPS
- ✅ **Accessible anywhere** - From any device
- ✅ **MinerU integration** - State-of-the-art PDF parsing

## 🎯 Why Cloud?

Your older MacBook (i5, 12GB RAM) doesn't need to run heavy models:
- **No local resources** used
- **No model downloads** required
- **Works from any device** with internet
- **Always available** (wakes in 30s)

## 📊 Free Tier Limits

| Resource | Limit |
|----------|-------|
| Hours/month | ~750 |
| RAM | 512MB |
| Sleep time | 15min inactivity |
| Wake-up time | ~30 seconds |

Perfect for personal PDF automation!

## 🔑 Get MinerU API Key

1. Go to https://mineru.net
2. Sign up for free account
3. Navigate to API Management
4. Create new API key
5. Add to Render environment variables

## 📖 Documentation

- [Cloud Solutions Guide](cloud_solutions.md) - Detailed deployment options
- [MinerU Documentation](https://mineru.net/apiManage/docs)
- [Render.com Documentation](https://render.com/docs)

## 🤝 Contributing

Feel free to fork, star, and improve!

## 📄 License

MIT License - Use freely for personal or commercial projects

---

**Made with ❤️ for older MacBooks everywhere**

**享受云端PDF转换的便利！** 🎉
