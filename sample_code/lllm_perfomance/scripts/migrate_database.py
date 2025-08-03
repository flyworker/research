#!/usr/bin/env python3
"""
Database migration script for LLM Calculator.
This script updates existing databases to include new schema changes.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database(db_path: str = "llm_calculator.db"):
    """Migrate database to latest schema."""
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Creating new database...")
        return
    
    print(f"Migrating database: {db_path}")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if deployment_configs table has is_active column
        cursor.execute("PRAGMA table_info(deployment_configs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_active' not in columns:
            print("Adding is_active column to deployment_configs table...")
            cursor.execute("ALTER TABLE deployment_configs ADD COLUMN is_active BOOLEAN DEFAULT 1")
            
            # Set all existing records as active
            cursor.execute("UPDATE deployment_configs SET is_active = 1 WHERE is_active IS NULL")
        
        if 'gpu_cost_per_hour' not in columns:
            print("Adding gpu_cost_per_hour column to deployment_configs table...")
            cursor.execute("ALTER TABLE deployment_configs ADD COLUMN gpu_cost_per_hour REAL NOT NULL DEFAULT 0.0")
            
            # Set default value for existing records
            cursor.execute("UPDATE deployment_configs SET gpu_cost_per_hour = 2.0 WHERE gpu_cost_per_hour = 0.0")
        
        # Check if model_configs table has real TPS columns
        cursor.execute("PRAGMA table_info(model_configs)")
        model_columns = [column[1] for column in cursor.fetchall()]
        
        if 'real_input_tps_per_gpu' not in model_columns:
            print("Adding real_input_tps_per_gpu column to model_configs table...")
            cursor.execute("ALTER TABLE model_configs ADD COLUMN real_input_tps_per_gpu INTEGER DEFAULT 0")
        
        if 'real_output_tps_per_gpu' not in model_columns:
            print("Adding real_output_tps_per_gpu column to model_configs table...")
            cursor.execute("ALTER TABLE model_configs ADD COLUMN real_output_tps_per_gpu INTEGER DEFAULT 0")
        
        # Check if deployment_configs table has real TPS columns
        cursor.execute("PRAGMA table_info(deployment_configs)")
        deployment_columns = [column[1] for column in cursor.fetchall()]
        
        if 'real_input_tps_per_gpu' not in deployment_columns:
            print("Adding real_input_tps_per_gpu column to deployment_configs table...")
            cursor.execute("ALTER TABLE deployment_configs ADD COLUMN real_input_tps_per_gpu INTEGER DEFAULT 0")
        
        if 'real_output_tps_per_gpu' not in deployment_columns:
            print("Adding real_output_tps_per_gpu column to deployment_configs table...")
            cursor.execute("ALTER TABLE deployment_configs ADD COLUMN real_output_tps_per_gpu INTEGER DEFAULT 0")
        
        conn.commit()
        print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database() 