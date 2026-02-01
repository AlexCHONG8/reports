"""
FastAPI Web Service for Render.com Deployment
Converts PDFs using MinerU API - Free Cloud Hosting!

Requirements:
pip install fastapi uvicorn python-multipart requests
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import requests
import os
from typing import Optional
import time

app = FastAPI(title="MinerU PDF Converter", version="1.0")

# Configuration
MINERU_API_KEY = os.getenv("MINERU_API_KEY", "")
MINERU_API_BASE = "https://mineru.net"

# Health check endpoint (Render uses this)
@app.get("/health")
async def health_check():
    """Render calls this to keep your service alive"""
    return {"status": "healthy", "service": "mineru-converter"}

@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "MinerU PDF Converter",
        "status": "running",
        "endpoints": {
            "POST /convert": "Upload PDF and get task_id",
            "GET /status/{task_id}": "Check conversion status",
            "GET /result/{task_id}": "Get markdown result",
            "POST /convert-and-wait": "Upload and wait for completion"
        }
    }

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """
    Upload PDF to MinerU and return task ID

    Usage:
    curl -X POST -F "file=@document.pdf" https://your-app.onrender.com/convert
    """
    if not MINERU_API_KEY:
        raise HTTPException(status_code=500, detail="MINERU_API_KEY not configured")

    try:
        # Read file
        pdf_content = await file.read()

        # Check file size (Render free tier limit)
        if len(pdf_content) > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")

        # Upload to MinerU
        response = requests.post(
            f"{MINERU_API_BASE}/api/v4/extract/task",
            files={'file': (file.filename, pdf_content, 'application/pdf')},
            headers={'Authorization': f'Bearer {MINERU_API_KEY}'},
            timeout=120
        )

        if response.status_code in [200, 201]:
            result = response.json()
            task_id = (
                result.get('task_id') or
                result.get('data', {}).get('task_id') or
                result.get('id') or
                result.get('data', {}).get('id')
            )

            if task_id:
                return {
                    "success": True,
                    "task_id": task_id,
                    "filename": file.filename,
                    "message": "PDF uploaded successfully. Use /status/{task_id} to check progress."
                }

        raise HTTPException(status_code=500, detail="Upload failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def check_status(task_id: str):
    """
    Check conversion status

    Usage:
    curl https://your-app.onrender.com/status/TASK_ID
    """
    if not MINERU_API_KEY:
        raise HTTPException(status_code=500, detail="MINERU_API_KEY not configured")

    try:
        response = requests.get(
            f"{MINERU_API_BASE}/api/v1/tasks/{task_id}",
            headers={'Authorization': f'Bearer {MINERU_API_KEY}'},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            status = (
                data.get('status') or
                data.get('data', {}).get('status') or
                'unknown'
            )

            return {
                "task_id": task_id,
                "status": status,
                "complete": status in ['completed', 'succeeded']
            }

        return {"task_id": task_id, "status": "not_found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """
    Get markdown result

    Usage:
    curl https://your-app.onrender.com/result/TASK_ID
    """
    if not MINERU_API_KEY:
        raise HTTPException(status_code=500, detail="MINERU_API_KEY not configured")

    try:
        response = requests.get(
            f"{MINERU_API_BASE}/api/v4/extract/{task_id}",
            headers={'Authorization': f'Bearer {MINERU_API_KEY}'},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            md_content = (
                data.get('md_content') or
                data.get('md') or
                data.get('data', {}).get('md_content') or
                data.get('data', {}).get('md') or
                data.get('result', {}).get('md_content')
            )

            if md_content:
                return PlainTextResponse(content=md_content)

        raise HTTPException(status_code=404, detail="Result not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-and-wait")
async def convert_and_wait(file: UploadFile = File(...), max_wait: int = 180):
    """
    Upload PDF and wait for conversion to complete

    Usage:
    curl -X POST -F "file=@document.pdf" https://your-app.onrender.com/convert-and-wait
    """
    if not MINERU_API_KEY:
        raise HTTPException(status_code=500, detail="MINERU_API_KEY not configured")

    try:
        # Step 1: Upload
        pdf_content = await file.read()
        upload_response = requests.post(
            f"{MINERU_API_BASE}/api/v4/extract/task",
            files={'file': (file.filename, pdf_content, 'application/pdf')},
            headers={'Authorization': f'Bearer {MINERU_API_KEY}'},
            timeout=120
        )

        if upload_response.status_code not in [200, 201]:
            raise HTTPException(status_code=500, detail="Upload failed")

        result = upload_response.json()
        task_id = (
            result.get('task_id') or
            result.get('data', {}).get('task_id') or
            result.get('id') or
            result.get('data', {}).get('id')
        )

        if not task_id:
            raise HTTPException(status_code=500, detail="No task_id returned")

        # Step 2: Poll for completion
        for attempt in range(max_wait):
            time.sleep(5)  # Wait 5 seconds between checks

            status_response = requests.get(
                f"{MINERU_API_BASE}/api/v1/tasks/{task_id}",
                headers={'Authorization': f'Bearer {MINERU_API_KEY}'},
                timeout=30
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                status = (
                    status_data.get('status') or
                    status_data.get('data', {}).get('status') or
                    'unknown'
                )

                if status in ['completed', 'succeeded']:
                    # Step 3: Get result
                    result_response = requests.get(
                        f"{MINERU_API_BASE}/api/v4/extract/{task_id}",
                        headers={'Authorization': f'Bearer {MINERU_API_KEY}'},
                        timeout=60
                    )

                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        md_content = (
                            result_data.get('md_content') or
                            result_data.get('md') or
                            result_data.get('data', {}).get('md_content') or
                            result_data.get('data', {}).get('md') or
                            result_data.get('result', {}).get('md_content')
                        )

                        if md_content:
                            return {
                                "success": True,
                                "task_id": task_id,
                                "filename": file.filename,
                                "markdown": md_content
                            }

        raise HTTPException(status_code=408, detail="Conversion timeout")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
