"""PostgreSQL integration for job logging."""

import os
from typing import Optional
from datetime import datetime
import uuid


# Check if psycopg is available
try:
    import psycopg
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False


class JobLogger:
    """Logs TTS generation jobs to PostgreSQL."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize logger with database connection."""
        self.database_url = database_url
        self.enabled = PSYCOPG_AVAILABLE and database_url and database_url.strip()
        
        if self.enabled:
            self._ensure_table()
    
    def _ensure_table(self):
        """Create jobs table if it doesn't exist."""
        if not self.enabled:
            return
        
        try:
            # Set a short connection timeout
            conn_string = self.database_url
            if '?' not in conn_string:
                conn_string += '?connect_timeout=3'
            else:
                conn_string += '&connect_timeout=3'
                
            with psycopg.connect(conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS jobs (
                            id UUID PRIMARY KEY,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            lang TEXT,
                            voice TEXT,
                            input_chars INT,
                            est_duration_sec NUMERIC,
                            out_mp3_path TEXT,
                            status TEXT
                        )
                    """)
                    conn.commit()
        except Exception as e:
            print(f"Warning: Could not create jobs table: {e}")
            self.enabled = False
    
    def log_job(
        self,
        lang: str,
        voice: str,
        input_chars: int,
        est_duration_sec: float,
        out_mp3_path: str,
        status: str = "ok"
    ) -> Optional[str]:
        """
        Log a completed job to the database.
        
        Returns:
            Job ID (UUID string) if successful, None otherwise
        """
        if not self.enabled:
            return None
        
        job_id = str(uuid.uuid4())
        
        try:
            with psycopg.connect(self.database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO jobs (id, lang, voice, input_chars, est_duration_sec, out_mp3_path, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (job_id, lang, voice, input_chars, est_duration_sec, out_mp3_path, status))
                    conn.commit()
            
            return job_id
        except Exception as e:
            print(f"Warning: Could not log job to database: {e}")
            return None


def create_logger(database_url: Optional[str] = None) -> JobLogger:
    """Factory function to create a job logger."""
    return JobLogger(database_url)
