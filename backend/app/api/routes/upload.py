"""File upload API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import structlog
from pathlib import Path
from datetime import datetime
from app.services.document_processor import process_and_upload_document

logger = structlog.get_logger()
router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx", ".md"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing.

    Supports: PDF, TXT, DOC, DOCX, MD files up to 10MB
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Read file content
        contents = await file.read()
        file_size = len(contents)

        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB",
            )

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(contents)

        # Process and index the file for RAG
        processing_status = "processing"
        processing_message = "File uploaded, processing for search..."

        try:
            # Process the document and add to vector store
            result = process_and_upload_document(str(file_path))
            processing_status = "indexed"
            processing_message = f"File processed successfully. Added {result.get('chunks', 0)} chunks to knowledge base."
            logger.info(
                "File processed and indexed", filename=file.filename, chunks=result.get("chunks", 0)
            )
        except Exception as proc_error:
            logger.warning(
                "File saved but processing failed", filename=file.filename, error=str(proc_error)
            )
            processing_status = "saved_not_indexed"
            processing_message = f"File saved but indexing failed: {str(proc_error)}"

        logger.info(
            "File upload completed",
            filename=file.filename,
            size=file_size,
            path=str(file_path),
            status=processing_status,
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": processing_message,
                "filename": file.filename,
                "size": file_size,
                "saved_as": safe_filename,
                "status": processing_status,
                "indexed": processing_status == "indexed",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("File upload failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/upload/multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files at once.

    Maximum 5 files per request.
    """
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed per request")

    results = []
    errors = []

    for file in files:
        try:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                errors.append({"filename": file.filename, "error": "File type not allowed"})
                continue

            # Read file content
            contents = await file.read()
            file_size = len(contents)

            # Validate file size
            if file_size > MAX_FILE_SIZE:
                errors.append(
                    {
                        "filename": file.filename,
                        "error": f"File too large (max {MAX_FILE_SIZE / (1024*1024):.0f}MB)",
                    }
                )
                continue

            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = UPLOAD_DIR / safe_filename

            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)

            # Process and index the file
            indexed = False
            chunks_added = 0
            try:
                result = process_and_upload_document(str(file_path))
                indexed = True
                chunks_added = result.get("chunks", 0)
                logger.info(
                    "File processed and indexed", filename=file.filename, chunks=chunks_added
                )
            except Exception as proc_error:
                logger.warning(
                    "File saved but processing failed",
                    filename=file.filename,
                    error=str(proc_error),
                )

            results.append(
                {
                    "filename": file.filename,
                    "size": file_size,
                    "saved_as": safe_filename,
                    "status": "success",
                    "indexed": indexed,
                    "chunks": chunks_added,
                }
            )

            logger.info("File uploaded successfully", filename=file.filename, size=file_size)

        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
            logger.error("File upload failed", error=str(e), filename=file.filename)

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Processed {len(files)} files",
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        },
    )


@router.get("/upload/status")
async def get_upload_status():
    """Get upload directory status and configuration."""
    try:
        total_files = len(list(UPLOAD_DIR.glob("*")))
        total_size = sum(f.stat().st_size for f in UPLOAD_DIR.glob("*") if f.is_file())

        return {
            "upload_directory": str(UPLOAD_DIR.absolute()),
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
            "allowed_extensions": list(ALLOWED_EXTENSIONS),
            "max_files_per_batch": 5,
        }
    except Exception as e:
        logger.error("Failed to get upload status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get upload status: {str(e)}")
