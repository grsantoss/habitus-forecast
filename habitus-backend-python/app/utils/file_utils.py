import os
import uuid
import shutil
from pathlib import Path
from typing import Union
from fastapi import UploadFile, HTTPException, status


async def save_upload_file(
    upload_file: UploadFile, destination: Union[str, Path]
) -> Path:
    """
    Save an uploaded file to the specified destination
    
    Args:
        upload_file: The uploaded file
        destination: Directory to save the file to
        
    Returns:
        Path object for the saved file
    """
    # Ensure destination is a Path object
    if isinstance(destination, str):
        destination = Path(destination)
    
    # Ensure destination directory exists
    os.makedirs(destination, exist_ok=True)
    
    # Generate a unique filename
    file_extension = upload_file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Create full destination path
    file_path = destination / unique_filename
    
    try:
        # Write the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        # Reset file pointer
        await upload_file.seek(0)
    
    return file_path


def delete_file(file_path: Union[str, Path]) -> bool:
    """
    Delete a file from the filesystem
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if the file was deleted, False otherwise
    """
    try:
        os.remove(file_path)
        return True
    except Exception:
        return False
    
    
def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting file size: {str(e)}"
        ) 