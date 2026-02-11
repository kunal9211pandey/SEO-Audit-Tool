from typing import Dict, Optional
from datetime import datetime
import threading


class AuditDatabase:
    # Simple in-memory database for storing audit results.
    
    def __init__(self):
        self.audits = {}
        self.lock = threading.Lock()
    
    def create_audit(self, audit_id: str, url: str):
        # Create a new audit record.
        
        with self.lock:
            self.audits[audit_id] = {
                "audit_id": audit_id,
                "url": url,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "results": None,
                "error": None
            }
    
    def update_status(self, audit_id: str, status: str):
        # Update audit status.
        with self.lock:
            if audit_id in self.audits:
                self.audits[audit_id]["status"] = status
                self.audits[audit_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def save_results(self, audit_id: str, results: Dict):
        # Save audit results.
        with self.lock:
            if audit_id in self.audits:
                self.audits[audit_id]["results"] = results
                self.audits[audit_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def save_error(self, audit_id: str, error: str):
        # Save error message.
        with self.lock:
            if audit_id in self.audits:
                self.audits[audit_id]["error"] = error
                self.audits[audit_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def get_audit(self, audit_id: str) -> Optional[Dict]:
        # Retrieve audit by ID.
        with self.lock:
            return self.audits.get(audit_id)
