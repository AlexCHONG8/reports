#!/usr/bin/env python3
"""
MinerU Automated PDF to Markdown Converter
Monitors input folder, uploads PDFs to MinerU Cloud API, downloads markdown

Updated with correct MinerU API v4 endpoints
API Documentation: https://mineru.net/apiManage/docs

Author: Auto-generated for MacBook i5 setup
Date: 2026-02-01
Version: 2.0
"""

import os
import sys
import time
import json
import shutil
import logging
import configparser
from pathlib import Path
from datetime import datetime
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============== CONFIGURATION ==============
def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"

    # Use script location as base folder (Desktop/PDF_Automation)
    base_folder = Path(__file__).parent

    if config_path.exists():
        config.read(config_path)
        return {
            "api_base": config.get("mineru", "api_base", fallback="https://mineru.net"),
            "api_key": config.get("mineru", "api_key", fallback=""),
            "watch_folder": base_folder / "input",
            "output_folder": base_folder / "output",
            "processing_folder": base_folder / "processing",
            "logs_folder": base_folder / "logs",
            "poll_interval": config.getint("settings", "poll_interval", fallback=5),
            "max_file_size": config.getint("settings", "max_file_size", fallback=52428800),
        }
    else:
        # Fallback to defaults
        return {
            "api_base": "https://mineru.net",
            "api_key": "",
            "watch_folder": base_folder / "input",
            "output_folder": base_folder / "output",
            "processing_folder": base_folder / "processing",
            "logs_folder": base_folder / "logs",
            "poll_interval": 5,
            "max_file_size": 50 * 1024 * 1024,
        }

CONFIG = load_config()

# ============== LOGGING SETUP ==============
def setup_logging():
    """Configure logging to file and console"""
    log_file = CONFIG["logs_folder"] / f"converter_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============== MINERU API CLIENT (v4) ==============
class MinerUClient:
    """Client for MinerU Cloud API v4"""

    # API v4 Endpoints
    ENDPOINTS = {
        "extract": "/api/v4/extract/task",      # Upload and extract
        "status": "/api/v1/tasks/{}",            # Check status
        "result": "/api/v4/extract/{}",          # Get result
    }

    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.session = requests.Session()
        # Set default auth header
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })

    def upload_pdf(self, pdf_path):
        """
        Upload PDF to MinerU for conversion
        Endpoint: POST /api/v4/extract/task
        """
        try:
            # Check file size
            file_size = os.path.getsize(pdf_path)
            if file_size > CONFIG["max_file_size"]:
                raise ValueError(f"File too large: {file_size / 1024 / 1024:.1f}MB")

            logger.info(f"📤 Uploading {pdf_path.name} ({file_size / 1024 / 1024:.1f}MB)...")

            url = f"{self.api_base}{self.ENDPOINTS['extract']}"

            # Prepare multipart form data
            with open(pdf_path, 'rb') as f:
                files = {
                    'file': (pdf_path.name, f, 'application/pdf')
                }

                # Don't set Content-Type for multipart - let requests handle it
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }

                response = requests.post(
                    url,
                    files=files,
                    headers=headers,
                    timeout=120
                )

            logger.debug(f"Upload response status: {response.status_code}")
            logger.debug(f"Upload response: {response.text[:500]}")

            if response.status_code in [200, 201]:
                result = response.json()

                # Try different possible response structures
                task_id = (
                    result.get('task_id') or
                    result.get('data', {}).get('task_id') or
                    result.get('id') or
                    result.get('data', {}).get('id')
                )

                if task_id:
                    logger.info(f"✅ Upload successful. Task ID: {task_id}")
                    return task_id
                else:
                    logger.error(f"❌ No task_id in response: {result}")
                    return None
            else:
                logger.error(f"❌ Upload failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def check_status(self, task_id):
        """
        Check conversion status
        Endpoint: GET /api/v1/tasks/{task_id}
        """
        try:
            url = f"{self.api_base}{self.ENDPOINTS['status'].format(task_id)}"

            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                status = (
                    data.get('status') or
                    data.get('data', {}).get('status') or
                    'unknown'
                )

                logger.debug(f"Task {task_id} status: {status}")

                if status == 'completed' or status == 'succeeded':
                    # Return task_id for result retrieval
                    return True, task_id
                elif status in ['failed', 'error']:
                    error_msg = (
                        data.get('error') or
                        data.get('data', {}).get('error') or
                        data.get('message') or
                        'Unknown error'
                    )
                    logger.error(f"❌ Conversion failed: {error_msg}")
                    return False, None
                else:
                    # Still processing
                    return False, None

            elif response.status_code == 404:
                logger.warning(f"⚠️  Task not found: {task_id}")
                return False, None

            logger.debug(f"Status check: {response.status_code}")
            return False, None

        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return False, None

    def get_result(self, task_id):
        """
        Get conversion result (markdown content)
        Endpoint: GET /api/v4/extract/{task_id}
        """
        try:
            url = f"{self.api_base}{self.ENDPOINTS['result'].format(task_id)}"

            response = self.session.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Try different possible response structures
                md_content = (
                    data.get('md_content') or
                    data.get('md') or
                    data.get('data', {}).get('md_content') or
                    data.get('data', {}).get('md') or
                    data.get('result', {}).get('md_content')
                )

                if md_content:
                    return True, md_content
                else:
                    logger.error(f"❌ No markdown content in response")
                    logger.debug(f"Response keys: {data.keys()}")
                    return False, None
            else:
                logger.error(f"❌ Get result failed: {response.status_code}")
                logger.debug(f"Response: {response.text[:500]}")
                return False, None

        except Exception as e:
            logger.error(f"❌ Get result error: {e}")
            return False, None

    def download_markdown(self, md_content, output_path):
        """Save markdown content to file"""
        try:
            logger.info(f"💾 Saving markdown to {output_path.name}...")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            logger.info(f"✅ Saved: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Save error: {e}")
            return False

# ============== FILE WATCHER ==============
class PDFHandler(FileSystemEventHandler):
    """Handles new PDF files in watch folder"""

    def __init__(self, client):
        self.client = client
        self.processing = set()

    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Only process PDF files
        if path.suffix.lower() != '.pdf':
            return

        # Skip if already processing
        if path.name in self.processing:
            return

        # Wait for file to be fully written
        time.sleep(2)

        if not path.exists():
            return

        logger.info(f"🔔 New PDF detected: {path.name}")
        self.process_pdf(path)

    def on_moved(self, event):
        """Called when a file is moved into watch folder"""
        if event.is_directory:
            return

        path = Path(event.dest_path)

        # Only process PDF files
        if path.suffix.lower() != '.pdf':
            return

        # Skip if already processing
        if path.name in self.processing:
            return

        logger.info(f"🔔 PDF moved to folder: {path.name}")
        self.process_pdf(path)

    def process_pdf(self, pdf_path):
        """Process a single PDF file"""
        self.processing.add(pdf_path.name)

        try:
            # Move to processing folder
            processing_path = CONFIG["processing_folder"] / pdf_path.name
            shutil.move(str(pdf_path), str(processing_path))

            logger.info(f"📋 Processing: {pdf_path.name}")
            logger.info("=" * 50)

            # Upload to MinerU
            task_id = self.client.upload_pdf(processing_path)

            if not task_id:
                logger.error(f"❌ Failed to upload {pdf_path.name}")
                # Move back to input for retry
                shutil.move(str(processing_path), str(pdf_path))
                return

            # Poll for completion
            max_attempts = 180  # 15 minutes max (180 * 5s)
            logger.info(f"⏳ Waiting for conversion...")

            for attempt in range(max_attempts):
                time.sleep(CONFIG["poll_interval"])

                is_complete, result = self.client.check_status(task_id)

                if is_complete and result:
                    # Get markdown content
                    success, md_content = self.client.get_result(result)

                    if success and md_content:
                        # Save markdown
                        output_filename = pdf_path.stem + ".md"
                        output_path = CONFIG["output_folder"] / output_filename

                        if self.client.download_markdown(md_content, output_path):
                            # Success - move original PDF to output folder
                            final_pdf = CONFIG["output_folder"] / pdf_path.name
                            shutil.move(str(processing_path), str(final_pdf))
                            logger.info("=" * 50)
                            logger.info(f"✅ Conversion complete: {output_filename}")
                            logger.info(f"📁 Location: {output_path}")
                            logger.info("=" * 50)
                            break
                    else:
                        logger.error("❌ Failed to get result")
                        break

                # Show progress every 30 seconds
                if (attempt + 1) % 6 == 0:
                    elapsed = (attempt + 1) * CONFIG["poll_interval"]
                    logger.info(f"⏳ Still processing... ({elapsed}s elapsed)")

            else:
                logger.error(f"❌ Timeout waiting for conversion: {pdf_path.name}")
                # Move back to input for retry
                shutil.move(str(processing_path), str(pdf_path))

        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # Try to move back to input
            processing_path = CONFIG["processing_folder"] / pdf_path.name
            if processing_path.exists():
                shutil.move(str(processing_path), str(pdf_path))
        finally:
            self.processing.discard(pdf_path.name)

# ============== MAIN ==============
def main():
    """Main entry point"""
    # Reload config to get API key
    global CONFIG
    CONFIG = load_config()

    # Check API key
    if not CONFIG["api_key"] or CONFIG["api_key"] == "YOUR_API_KEY_HERE":
        logger.error("=" * 60)
        logger.error("❌ API key not configured!")
        logger.error("=" * 60)
        logger.info("📝 Get your API key from: https://mineru.net/")
        logger.info("📝 Then add it to config.ini:")
        logger.info("   [mineru]")
        logger.info("   api_key = YOUR_ACTUAL_API_KEY")
        logger.info("")
        return

    # Create directories
    for folder in [CONFIG["watch_folder"], CONFIG["output_folder"],
                   CONFIG["processing_folder"], CONFIG["logs_folder"]]:
        folder.mkdir(parents=True, exist_ok=True)

    # Initialize client
    client = MinerUClient(CONFIG["api_key"], CONFIG["api_base"])

    # Setup file watcher
    event_handler = PDFHandler(client)
    observer = Observer()
    observer.schedule(event_handler, str(CONFIG["watch_folder"]), recursive=False)
    observer.start()

    logger.info("")
    logger.info("=" * 60)
    logger.info("🚀 MinerU Auto-Converter v2.0 Started")
    logger.info("=" * 60)
    logger.info(f"📂 Watching: {CONFIG['watch_folder']}")
    logger.info(f"📤 Output:   {CONFIG['output_folder']}")
    logger.info(f"📋 Logs:     {CONFIG['logs_folder']}")
    logger.info("=" * 60)
    logger.info("💡 Drop PDF files into the input folder to convert them")
    logger.info("💡 Press Ctrl+C to stop")
    logger.info("=" * 60)
    logger.info("")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("")
        logger.info("=" * 60)
        logger.info("👋 Stopped by user")
        logger.info("=" * 60)

    observer.join()

if __name__ == "__main__":
    main()
