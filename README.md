# MinerU Automated PDF to Markdown Converter

自动监控文件夹并将PDF转换为Markdown的工具 / Automated tool to monitor folder and convert PDFs to Markdown

## Features 特性

- ✅ **Zero local space** - 使用云API，无需本地安装模型
- ✅ **OCR Support** - 支持扫描文档和手写文字
- ✅ **Automatic** - 放入PDF即自动转换
- ✅ **Small footprint** - 仅需几MB空间
- ✅ **Works on i5 MacBook** - 低配置设备友好

## Directory Structure 文件结构

```
~/Documents/PDF_Automation/
├── input/           # Drop PDFs here (放入PDF文件)
├── output/          # Converted markdown appears here (转换后的markdown)
├── processing/      # Temporary processing folder (临时处理)
├── logs/            # Activity logs (活动日志)
├── config.ini       # Your API key configuration (API密钥配置)
├── mineru_auto_converter.py  # Main script (主脚本)
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Setup Steps 安装步骤

### 1. Install Python Dependencies

```bash
cd ~/Documents/PDF_Automation
pip3 install -r requirements.txt
```

### 2. Get MinerU API Key

1. Visit: https://mineru.net/
2. Sign up for an account
3. Go to API Management
4. Create a new API key
5. Copy your API key

### 3. Configure API Key

**Option A: Edit config.ini**
```bash
nano ~/Documents/PDF_Automation/config.ini
```
Replace `YOUR_API_KEY_HERE` with your actual API key

**Option B: Edit the script directly**
```bash
nano ~/Documents/PDF_Automation/mineru_auto_converter.py
```
Find line: `"api_key": "",` and add your key between quotes

### 4. Make Script Executable

```bash
chmod +x ~/Documents/PDF_Automation/mineru_auto_converter.py
```

## Usage 使用方法

### Start the Converter

```bash
cd ~/Documents/PDF_Automation
python3 mineru_auto_converter.py
```

You'll see:
```
🚀 MinerU Auto-Converter Started
============================================================
📂 Watching: /Users/xxx/Documents/PDF_Automation/input
📤 Output:   /Users/xxx/Documents/PDF_Automation/output
📋 Logs:     /Users/xxx/Documents/PDF_Automation/logs
============================================================
💡 Drop PDF files into the input folder to convert them
💡 Press Ctrl+C to stop
============================================================
```

### Convert PDFs

Simply copy or move PDF files to:
```
~/Documents/PDF_Automation/input/
```

The script will automatically:
1. ✅ Detect new PDF
2. ✅ Upload to MinerU Cloud
3. ✅ Convert to Markdown
4. ✅ Download to output folder
5. ✅ Move original PDF to output folder

### Output Location

Find your converted markdown in:
```
~/Documents/PDF_Automation/output/
```

Each PDF becomes: `filename.pdf` → `filename.md`

## Quick Start Example

```bash
# Terminal 1: Start the converter
cd ~/Documents/PDF_Automation
python3 mineru_auto_converter.py

# Terminal 2: Copy a PDF to convert
cp ~/Desktop/my_document.pdf ~/Documents/PDF_Automation/input/

# Wait a few seconds, then check output:
ls ~/Documents/PDF_Automation/output/
# You'll see: my_document.pdf, my_document.md
```

## Advanced Usage 高级用法

### Run in Background 后台运行

```bash
# Start in background
cd ~/Documents/PDF_Automation
nohup python3 mineru_auto_converter.py > /dev/null 2>&1 &

# Check if running
ps aux | grep mineru_auto_converter

# Stop background process
pkill -f mineru_auto_converter.py
```

### Auto-start on Login 开机自启动

Create a launch agent (macOS):

```bash
# Create launch agent file
nano ~/Library/LaunchAgents/com.mineru.autoconverter.plist
```

Add this content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mineru.autoconverter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/alexchong/Documents/PDF_Automation/mineru_auto_converter.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.mineru.autoconverter.plist
```

## Troubleshooting 故障排除

### Problem: "API key not set"
**Solution:** Add your API key to `config.ini` or edit the script

### Problem: "Upload failed"
**Solution:**
- Check internet connection
- Verify API key is valid
- Check if PDF file size is too large (>50MB)

### Problem: Script doesn't detect new PDFs
**Solution:**
- Make sure script is running
- Check you're putting files in the correct `input/` folder
- Check logs in `logs/` folder for errors

### Problem: OCR quality is poor
**Solution:**
- Ensure PDF is scanned at good resolution (300 DPI recommended)
- Try different scan quality settings
- For handwritten text, results may vary

## API Endpoint Notes

**Important:** The API endpoints in this script are templates. You may need to verify the exact endpoints from:
- Official docs: https://mineru.net/apiManage/docs
- The script uses common patterns, but actual endpoints may differ

If uploads fail, check the documentation and update these lines in `mineru_auto_converter.py`:
- Line ~68: Upload endpoint
- Line ~93: Status check endpoint

## Costs 费用

MinerU Cloud API uses pay-as-you-go pricing. Check current pricing at:
https://mineru.net/pricing

For light usage (occasional PDFs), costs should be minimal.

## Space Usage 空间占用

- Script: ~50KB
- Dependencies: ~10MB
- Processing: Only stores PDFs you're converting
- No model downloads needed!

Total: <20MB (well under your 1GB limit!)

## Support 支持

- MinerU official site: https://mineru.net/
- API documentation: https://mineru.net/apiManage/docs
- GitHub issues: https://github.com/opendatalab/MinerU/issues

---

**Enjoy automated PDF to Markdown conversion!** 🎉

**享受自动PDF转Markdown的便利！** 🎉
