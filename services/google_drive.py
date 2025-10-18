"""
Google Drive integration for sharing wall inspection results
"""

import os
import json
import io
from datetime import datetime
from typing import Optional, Dict, Any
import streamlit as st

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.folder_id = None
        self.credentials = None
        
    def initialize_from_secrets(self):
        """Initialize Google Drive service using Streamlit secrets"""
        try:
            if not GOOGLE_DRIVE_AVAILABLE:
                st.warning("Google Drive integration not available. Install google-api-python-client to enable sharing.")
                return False
            
            # Try to get credentials from Streamlit secrets
            if "google_drive" in st.secrets:
                credentials_info = dict(st.secrets["google_drive"])
                self.credentials = Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
                
                self.service = build('drive', 'v3', credentials=self.credentials)
                self.folder_id = st.secrets.get("google_drive_folder_id", "root")
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Failed to initialize Google Drive: {str(e)}")
            return False
    
    def initialize_from_file(self, credentials_path: str, folder_id: str = "root"):
        """Initialize Google Drive service using credentials file"""
        try:
            if not GOOGLE_DRIVE_AVAILABLE:
                return False
                
            if not os.path.exists(credentials_path):
                return False
            
            self.credentials = Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            self.service = build('drive', 'v3', credentials=self.credentials)
            self.folder_id = folder_id
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize Google Drive: {str(e)}")
            return False
    
    def create_inspection_folder(self, wall_name: str) -> Optional[str]:
        """Create a folder for the inspection"""
        if not self.service:
            return None
        
        try:
            # Create folder name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"WallInspection_{wall_name.replace(' ', '_')}_{timestamp}"
            
            folder_metadata = {
                'name': folder_name,
                'parents': [self.folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(body=folder_metadata).execute()
            return folder.get('id')
            
        except Exception as e:
            st.error(f"Failed to create folder: {str(e)}")
            return None
    
    def upload_file(self, file_data: bytes, filename: str, folder_id: str, 
                   mime_type: str = 'application/octet-stream') -> Optional[Dict[str, Any]]:
        """Upload a file to Google Drive"""
        if not self.service:
            return None
        
        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_data),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            return file
            
        except Exception as e:
            st.error(f"Failed to upload file: {str(e)}")
            return None
    
    def make_file_public(self, file_id: str) -> bool:
        """Make a file publicly viewable"""
        if not self.service:
            return False
        
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to make file public: {str(e)}")
            return False
    
    def get_shareable_link(self, file_id: str) -> Optional[str]:
        """Get a shareable link for a file"""
        if not self.service:
            return None
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            return file.get('webViewLink')
            
        except Exception as e:
            st.error(f"Failed to get shareable link: {str(e)}")
            return None
    
    def upload_inspection_results(self, wall_name: str, original_image: bytes, 
                                annotated_image: bytes, report_data: Dict[str, Any]) -> Optional[str]:
        """Upload complete inspection results and return folder link"""
        if not self.service:
            return None
        
        try:
            # Create inspection folder
            folder_id = self.create_inspection_folder(wall_name)
            if not folder_id:
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{wall_name.replace(' ', '_')}_{timestamp}"
            
            # Upload original image
            original_file = self.upload_file(
                original_image,
                f"{base_filename}_original.png",
                folder_id,
                'image/png'
            )
            
            # Upload annotated image
            annotated_file = self.upload_file(
                annotated_image,
                f"{base_filename}_annotated.png",
                folder_id,
                'image/png'
            )
            
            # Upload report
            report_json = json.dumps(report_data, indent=2).encode('utf-8')
            report_file = self.upload_file(
                report_json,
                f"{base_filename}_report.json",
                folder_id,
                'application/json'
            )
            
            # Make files public
            if original_file:
                self.make_file_public(original_file['id'])
            if annotated_file:
                self.make_file_public(annotated_file['id'])
            if report_file:
                self.make_file_public(report_file['id'])
            
            # Get folder link
            folder_link = f"https://drive.google.com/drive/folders/{folder_id}"
            
            return folder_link
            
        except Exception as e:
            st.error(f"Failed to upload inspection results: {str(e)}")
            return None

# Global instance
drive_service = GoogleDriveService()

def get_drive_service() -> GoogleDriveService:
    """Get the global Google Drive service instance"""
    return drive_service

def is_drive_available() -> bool:
    """Check if Google Drive integration is available"""
    return GOOGLE_DRIVE_AVAILABLE and drive_service.service is not None
