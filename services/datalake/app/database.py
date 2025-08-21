import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Connection pool
_pool = None

def get_pool():
    """Get or create connection pool"""
    global _pool
    if _pool is None:
        try:
            _pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    return _pool

@contextmanager
def get_db():
    """Context manager to get database connection"""
    pool = get_pool()
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            pool.putconn(conn)

def close_pool():
    """Close the connection pool"""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None
        logger.info("Database connection pool closed")

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results"""
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
            return cur.rowcount

def execute_many(query, params_list):
    """Execute a query with multiple parameter sets"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.executemany(query, params_list)
            conn.commit()
            return cur.rowcount

def create_tables():
    """Create database tables if they don't exist"""
    create_realtime_table = """
    CREATE TABLE IF NOT EXISTS realtime (
        equipment_data_id VARCHAR(10) PRIMARY KEY,
        equipment_id VARCHAR(10),
        facility_id VARCHAR(10),
        equipment_location VARCHAR(40),
        measured_at TIMESTAMP,
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        temperature DECIMAL(6,2),
        humidity DECIMAL(5,2),
        smoke_density DECIMAL(6,3),
        co_level DECIMAL(6,3),
        gas_level DECIMAL(6,3),
        version INTEGER DEFAULT 1
    );
    """
    
    create_alert_table = """
    CREATE TABLE IF NOT EXISTS alert (
        alert_id VARCHAR(10) PRIMARY KEY,
        equipment_id VARCHAR(10),
        facility_id VARCHAR(10),
        equipment_location VARCHAR(40),
        alert_type VARCHAR(20),
        severity VARCHAR(20),
        status VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        version INTEGER DEFAULT 1
    );
    """
    
    create_storage_metadata_table = """
    CREATE TABLE IF NOT EXISTS storage_metadata (
        metadata_id VARCHAR(36) PRIMARY KEY,
        flush_timestamp TIMESTAMP NOT NULL,
        data_start_time TIMESTAMP NOT NULL,
        data_end_time TIMESTAMP NOT NULL,
        record_count INTEGER NOT NULL,
        storage_path TEXT NOT NULL,
        storage_type VARCHAR(50) NOT NULL,
        file_size_bytes BIGINT,
        compression_ratio DECIMAL(5,4),
        processing_duration_ms INTEGER,
        error_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        additional_info TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        execute_query(create_realtime_table, fetch=False)
        execute_query(create_alert_table, fetch=False)
        execute_query(create_storage_metadata_table, fetch=False)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
