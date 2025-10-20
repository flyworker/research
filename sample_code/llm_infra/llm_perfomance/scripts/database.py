"""
Database Management System for LLM Calculator
============================================

This module provides database functionality for storing and managing:
- GPU configurations and pricing
- Model deployment settings
- User preferences and saved configurations
- Historical calculations and results
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import os

@dataclass
class GPUConfig:
    """GPU configuration data."""
    id: Optional[int] = None
    name: str = ""
    gpu_type: str = ""
    vram_gb: int = 0
    cost_per_hour: float = 0.0
    cost_per_month: float = 0.0
    power_watts: int = 0
    memory_bandwidth_gbps: int = 0
    fp16_performance_tflops: float = 0.0
    fp8_performance_tflops: float = 0.0
    description: str = ""
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class DeploymentConfig:
    """Deployment configuration data."""
    id: Optional[int] = None
    name: str = ""
    gpu_config_id: int = 0
    gpu_count: int = 0
    gpu_cost_per_hour: float = 0.0
    model_name: str = ""
    input_tps: int = 0
    output_tps: int = 0
    input_price_per_m: float = 0.0
    output_price_per_m: float = 0.0
    real_input_tps_per_gpu: int = 0  # Real tested input TPS per GPU
    real_output_tps_per_gpu: int = 0  # Real tested output TPS per GPU
    profit_per_day: float = 0.0
    roi_percentage: float = 0.0
    notes: str = ""
    is_favorite: bool = False
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class ModelConfig:
    """Model configuration data."""
    id: Optional[int] = None
    name: str = ""
    slug: str = ""
    parameters_b: float = 0.0
    context_window: str = ""
    precision: str = ""
    typical_gpu: str = ""
    input_price_per_m: float = 0.0
    output_price_per_m: float = 0.0
    tokens_per_gpu_tps: int = 0
    real_input_tps_per_gpu: int = 0  # Real tested input TPS per GPU
    real_output_tps_per_gpu: int = 0  # Real tested output TPS per GPU
    openrouter_link: str = ""
    description: str = ""
    is_free: bool = False
    is_moe: bool = False
    is_awq: bool = False
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DatabaseManager:
    """Database manager for LLM calculator data."""
    
    def __init__(self, db_path: str = "llm_calculator.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # GPU Configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gpu_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    gpu_type TEXT NOT NULL,
                    vram_gb INTEGER NOT NULL,
                    cost_per_hour REAL NOT NULL,
                    cost_per_month REAL NOT NULL,
                    power_watts INTEGER NOT NULL,
                    memory_bandwidth_gbps INTEGER NOT NULL,
                    fp16_performance_tflops REAL NOT NULL,
                    fp8_performance_tflops REAL NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Model Configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    parameters_b REAL NOT NULL,
                    context_window TEXT NOT NULL,
                    precision TEXT NOT NULL,
                    typical_gpu TEXT NOT NULL,
                    input_price_per_m REAL NOT NULL,
                    output_price_per_m REAL NOT NULL,
                    tokens_per_gpu_tps INTEGER NOT NULL,
                    real_input_tps_per_gpu INTEGER DEFAULT 0,
                    real_output_tps_per_gpu INTEGER DEFAULT 0,
                    openrouter_link TEXT,
                    description TEXT,
                    is_free BOOLEAN DEFAULT 0,
                    is_moe BOOLEAN DEFAULT 0,
                    is_awq BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Deployment Configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployment_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    gpu_config_id INTEGER NOT NULL,
                    gpu_count INTEGER NOT NULL,
                    gpu_cost_per_hour REAL NOT NULL,
                    model_name TEXT NOT NULL,
                    input_tps INTEGER NOT NULL,
                    output_tps INTEGER NOT NULL,
                    input_price_per_m REAL NOT NULL,
                    output_price_per_m REAL NOT NULL,
                    real_input_tps_per_gpu INTEGER DEFAULT 0,
                    real_output_tps_per_gpu INTEGER DEFAULT 0,
                    profit_per_day REAL NOT NULL,
                    roi_percentage REAL NOT NULL,
                    notes TEXT,
                    is_favorite BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gpu_config_id) REFERENCES gpu_configs (id)
                )
            """)
            
            # User Preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Calculation History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deployment_config_id INTEGER,
                    gpu_cost_per_hour REAL NOT NULL,
                    gpu_count INTEGER NOT NULL,
                    input_tps INTEGER NOT NULL,
                    output_tps INTEGER NOT NULL,
                    input_price_per_m REAL NOT NULL,
                    output_price_per_m REAL NOT NULL,
                    profit_per_day REAL NOT NULL,
                    roi_percentage REAL NOT NULL,
                    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deployment_config_id) REFERENCES deployment_configs (id)
                )
            """)
            
            conn.commit()
    
    def insert_gpu_config(self, gpu_config: GPUConfig) -> int:
        """Insert a new GPU configuration."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO gpu_configs (
                    name, gpu_type, vram_gb, cost_per_hour, cost_per_month,
                    power_watts, memory_bandwidth_gbps, fp16_performance_tflops,
                    fp8_performance_tflops, description, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gpu_config.name, gpu_config.gpu_type, gpu_config.vram_gb,
                gpu_config.cost_per_hour, gpu_config.cost_per_month,
                gpu_config.power_watts, gpu_config.memory_bandwidth_gbps,
                gpu_config.fp16_performance_tflops, gpu_config.fp8_performance_tflops,
                gpu_config.description, gpu_config.is_active
            ))
            return cursor.lastrowid
    
    def get_gpu_configs(self, active_only: bool = True) -> List[GPUConfig]:
        """Get all GPU configurations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM gpu_configs"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY name"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            return [GPUConfig(**dict(row)) for row in rows]
    
    def get_gpu_config_by_id(self, gpu_id: int) -> Optional[GPUConfig]:
        """Get GPU configuration by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpu_configs WHERE id = ?", (gpu_id,))
            row = cursor.fetchone()
            return GPUConfig(**dict(row)) if row else None
    
    def update_gpu_config(self, gpu_config: GPUConfig) -> bool:
        """Update GPU configuration."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE gpu_configs SET
                    name = ?, gpu_type = ?, vram_gb = ?, cost_per_hour = ?,
                    cost_per_month = ?, power_watts = ?, memory_bandwidth_gbps = ?,
                    fp16_performance_tflops = ?, fp8_performance_tflops = ?,
                    description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                gpu_config.name, gpu_config.gpu_type, gpu_config.vram_gb,
                gpu_config.cost_per_hour, gpu_config.cost_per_month,
                gpu_config.power_watts, gpu_config.memory_bandwidth_gbps,
                gpu_config.fp16_performance_tflops, gpu_config.fp8_performance_tflops,
                gpu_config.description, gpu_config.is_active, gpu_config.id
            ))
            return cursor.rowcount > 0
    
    def insert_model_config(self, model_config: ModelConfig) -> int:
        """Insert a new model configuration."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO model_configs (
                    name, slug, parameters_b, context_window, precision,
                    typical_gpu, input_price_per_m, output_price_per_m,
                    tokens_per_gpu_tps, real_input_tps_per_gpu, real_output_tps_per_gpu,
                    openrouter_link, description, is_free, is_moe, is_awq, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_config.name, model_config.slug, model_config.parameters_b,
                model_config.context_window, model_config.precision,
                model_config.typical_gpu, model_config.input_price_per_m,
                model_config.output_price_per_m, model_config.tokens_per_gpu_tps,
                model_config.real_input_tps_per_gpu, model_config.real_output_tps_per_gpu,
                model_config.openrouter_link, model_config.description,
                model_config.is_free, model_config.is_moe, model_config.is_awq,
                model_config.is_active
            ))
            return cursor.lastrowid
    
    def get_model_configs(self, active_only: bool = True) -> List[ModelConfig]:
        """Get all model configurations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM model_configs"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY name"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            return [ModelConfig(**dict(row)) for row in rows]
    
    def get_model_config_by_name(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM model_configs WHERE name = ?", (name,))
            row = cursor.fetchone()
            return ModelConfig(**dict(row)) if row else None
    
    def update_model_config(self, model_config: ModelConfig) -> bool:
        """Update model configuration."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE model_configs SET
                        slug = ?, parameters_b = ?, context_window = ?, precision = ?,
                        typical_gpu = ?, input_price_per_m = ?, output_price_per_m = ?,
                        tokens_per_gpu_tps = ?, real_input_tps_per_gpu = ?, real_output_tps_per_gpu = ?,
                        openrouter_link = ?, description = ?, is_free = ?, is_moe = ?, is_awq = ?, 
                        is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    model_config.slug, model_config.parameters_b, model_config.context_window,
                    model_config.precision, model_config.typical_gpu, model_config.input_price_per_m,
                    model_config.output_price_per_m, model_config.tokens_per_gpu_tps,
                    model_config.real_input_tps_per_gpu, model_config.real_output_tps_per_gpu,
                    model_config.openrouter_link, model_config.description, model_config.is_free,
                    model_config.is_moe, model_config.is_awq, model_config.is_active, model_config.id
                ))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating model config: {e}")
            return False
    
    def insert_deployment_config(self, deployment_config: DeploymentConfig) -> int:
        """Insert a new deployment configuration."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO deployment_configs (
                    name, gpu_config_id, gpu_count, gpu_cost_per_hour, model_name, input_tps,
                    output_tps, input_price_per_m, output_price_per_m, real_input_tps_per_gpu,
                    real_output_tps_per_gpu, profit_per_day, roi_percentage, notes, is_favorite, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment_config.name, deployment_config.gpu_config_id,
                deployment_config.gpu_count, deployment_config.gpu_cost_per_hour,
                deployment_config.model_name, deployment_config.input_tps, deployment_config.output_tps,
                deployment_config.input_price_per_m, deployment_config.output_price_per_m,
                deployment_config.real_input_tps_per_gpu, deployment_config.real_output_tps_per_gpu,
                deployment_config.profit_per_day, deployment_config.roi_percentage,
                deployment_config.notes, deployment_config.is_favorite,
                deployment_config.is_active
            ))
            return cursor.lastrowid
    
    def get_deployment_configs(self, favorites_only: bool = False, active_only: bool = True) -> List[DeploymentConfig]:
        """Get deployment configurations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM deployment_configs"
            conditions = []
            
            if favorites_only:
                conditions.append("is_favorite = 1")
            
            if active_only:
                conditions.append("is_active = 1")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            configs = []
            for row in rows:
                config = DeploymentConfig(**dict(row))
                print(f"Debug: Loaded config {config.id}, gpu_cost_per_hour: {config.gpu_cost_per_hour}")  # Debug log
                configs.append(config)
            return configs
    
    def update_deployment_config(self, deployment_config: DeploymentConfig) -> bool:
        """Update deployment configuration."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE deployment_configs SET
                        name = ?, gpu_config_id = ?, gpu_count = ?, gpu_cost_per_hour = ?, model_name = ?,
                        input_tps = ?, output_tps = ?, input_price_per_m = ?,
                        output_price_per_m = ?, real_input_tps_per_gpu = ?, real_output_tps_per_gpu = ?,
                        profit_per_day = ?, roi_percentage = ?,
                        notes = ?, is_favorite = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    deployment_config.name, deployment_config.gpu_config_id,
                    deployment_config.gpu_count, deployment_config.gpu_cost_per_hour,
                    deployment_config.model_name, deployment_config.input_tps, deployment_config.output_tps,
                    deployment_config.input_price_per_m, deployment_config.output_price_per_m,
                    deployment_config.real_input_tps_per_gpu, deployment_config.real_output_tps_per_gpu,
                    deployment_config.profit_per_day, deployment_config.roi_percentage,
                    deployment_config.notes, deployment_config.is_favorite,
                    deployment_config.is_active, deployment_config.id
                ))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating deployment config: {e}")
            return False
    
    def save_calculation_history(self, deployment_config_id: Optional[int], 
                               gpu_cost_per_hour: float, gpu_count: int,
                               input_tps: int, output_tps: int,
                               input_price_per_m: float, output_price_per_m: float,
                               profit_per_day: float, roi_percentage: float):
        """Save calculation to history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calculation_history (
                    deployment_config_id, gpu_cost_per_hour, gpu_count,
                    input_tps, output_tps, input_price_per_m, output_price_per_m,
                    profit_per_day, roi_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment_config_id, gpu_cost_per_hour, gpu_count,
                input_tps, output_tps, input_price_per_m, output_price_per_m,
                profit_per_day, roi_percentage
            ))
    
    def get_calculation_history(self, limit: int = 50) -> List[Dict]:
        """Get recent calculation history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ch.*, dc.name as deployment_name, gc.name as gpu_name
                FROM calculation_history ch
                LEFT JOIN deployment_configs dc ON ch.deployment_config_id = dc.id
                LEFT JOIN gpu_configs gc ON dc.gpu_config_id = gc.id
                ORDER BY ch.calculation_date DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def set_user_preference(self, key: str, value: str, description: str = ""):
        """Set user preference."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (key, value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, description))
    
    def get_user_preference(self, key: str, default: str = "") -> str:
        """Get user preference."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
    
    def populate_default_data(self):
        """Populate database with default GPU configurations."""
        default_gpus = [
            GPUConfig(
                name="NVIDIA H100 80GB",
                gpu_type="Data Center",
                vram_gb=80,
                cost_per_hour=2.0,
                cost_per_month=1440.0,
                power_watts=700,
                memory_bandwidth_gbps=3350,
                fp16_performance_tflops=989.0,
                fp8_performance_tflops=1979.0,
                description="NVIDIA's flagship data center GPU for AI workloads"
            ),
            GPUConfig(
                name="NVIDIA A100 80GB",
                gpu_type="Data Center",
                vram_gb=80,
                cost_per_hour=1.8,
                cost_per_month=1296.0,
                power_watts=400,
                memory_bandwidth_gbps=2039,
                fp16_performance_tflops=312.0,
                fp8_performance_tflops=624.0,
                description="NVIDIA A100 for data center AI workloads"
            ),
            GPUConfig(
                name="NVIDIA RTX 3090",
                gpu_type="Consumer",
                vram_gb=24,
                cost_per_hour=0.75,
                cost_per_month=540.0,
                power_watts=350,
                memory_bandwidth_gbps=936,
                fp16_performance_tflops=35.6,
                fp8_performance_tflops=71.2,
                description="High-end consumer GPU for AI development"
            ),
            GPUConfig(
                name="NVIDIA RTX 3080",
                gpu_type="Consumer",
                vram_gb=10,
                cost_per_hour=0.55,
                cost_per_month=396.0,
                power_watts=320,
                memory_bandwidth_gbps=760,
                fp16_performance_tflops=29.8,
                fp8_performance_tflops=59.6,
                description="Mid-range consumer GPU for AI workloads"
            )
        ]
        
        for gpu in default_gpus:
            self.insert_gpu_config(gpu)
        
        # Set default preferences
        self.set_user_preference("default_gpu_cost", "2.0", "Default GPU cost per hour")
        self.set_user_preference("default_gpu_count", "8", "Default number of GPUs")
        self.set_user_preference("currency", "USD", "Preferred currency")

    def get_database_info(self) -> Dict[str, Any]:
        """Get database file information."""
        import os
        import sqlite3
        
        db_info = {
            "file_path": self.db_path,
            "file_size": 0,
            "exists": False,
            "table_counts": {},
            "last_modified": None
        }
        
        if os.path.exists(self.db_path):
            db_info["exists"] = True
            db_info["file_size"] = os.path.getsize(self.db_path)
            db_info["last_modified"] = os.path.getmtime(self.db_path)
            
            # Get table counts
            with self.get_connection() as conn:
                cursor = conn.cursor()
                tables = ["gpu_configs", "model_configs", "deployment_configs", "user_preferences", "calculation_history"]
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                        result = cursor.fetchone()
                        db_info["table_counts"][table] = result['count'] if result else 0
                    except sqlite3.OperationalError:
                        db_info["table_counts"][table] = 0
        
        return db_info
    
    def export_configurations_to_json(self, file_path: str = "configurations_backup.json") -> bool:
        """Export all configurations to a JSON file."""
        try:
            import json
            from datetime import datetime
            
            # Get all data
            gpu_configs = self.get_gpu_configs(active_only=False)
            model_configs = self.get_model_configs(active_only=False)
            deployment_configs = self.get_deployment_configs(favorites_only=False)
            user_preferences = []
            
            # Get user preferences
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_preferences")
                rows = cursor.fetchall()
                user_preferences = [dict(row) for row in rows]
            
            # Prepare export data
            export_data = {
                "export_date": datetime.now().isoformat(),
                "database_info": self.get_database_info(),
                "gpu_configs": [asdict(gpu) for gpu in gpu_configs],
                "model_configs": [asdict(model) for model in model_configs],
                "deployment_configs": [asdict(deployment) for deployment in deployment_configs],
                "user_preferences": user_preferences
            }
            
            # Write to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting configurations: {e}")
            return False
    
    def import_configurations_from_json(self, file_path: str) -> Dict[str, Any]:
        """Import configurations from a JSON file."""
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            results = {
                "success": True,
                "imported": {
                    "gpu_configs": 0,
                    "model_configs": 0,
                    "deployment_configs": 0,
                    "user_preferences": 0
                },
                "errors": []
            }
            
            # Import GPU configurations
            if "gpu_configs" in import_data:
                for gpu_data in import_data["gpu_configs"]:
                    try:
                        gpu_config = GPUConfig(**gpu_data)
                        self.insert_gpu_config(gpu_config)
                        results["imported"]["gpu_configs"] += 1
                    except Exception as e:
                        results["errors"].append(f"GPU config error: {e}")
            
            # Import model configurations
            if "model_configs" in import_data:
                for model_data in import_data["model_configs"]:
                    try:
                        model_config = ModelConfig(**model_data)
                        self.insert_model_config(model_config)
                        results["imported"]["model_configs"] += 1
                    except Exception as e:
                        results["errors"].append(f"Model config error: {e}")
            
            # Import deployment configurations
            if "deployment_configs" in import_data:
                for deployment_data in import_data["deployment_configs"]:
                    try:
                        deployment_config = DeploymentConfig(**deployment_data)
                        self.insert_deployment_config(deployment_config)
                        results["imported"]["deployment_configs"] += 1
                    except Exception as e:
                        results["errors"].append(f"Deployment config error: {e}")
            
            # Import user preferences
            if "user_preferences" in import_data:
                for pref_data in import_data["user_preferences"]:
                    try:
                        self.set_user_preference(
                            pref_data["key"],
                            pref_data["value"],
                            pref_data.get("description", "")
                        )
                        results["imported"]["user_preferences"] += 1
                    except Exception as e:
                        results["errors"].append(f"User preference error: {e}")
            
            if results["errors"]:
                results["success"] = False
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "imported": {"gpu_configs": 0, "model_configs": 0, "deployment_configs": 0, "user_preferences": 0},
                "errors": [f"Import error: {e}"]
            }
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database file."""
        import shutil
        import os
        from datetime import datetime
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"llm_calculator_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""
    
    def get_configuration_stats(self) -> Dict[str, Any]:
        """Get statistics about saved configurations."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get deployment config stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_configs,
                        COUNT(CASE WHEN profit_per_day > 0 THEN 1 END) as profitable_configs,
                        COUNT(CASE WHEN profit_per_day <= 0 THEN 1 END) as unprofitable_configs,
                        AVG(profit_per_day) as avg_profit,
                        MAX(profit_per_day) as max_profit,
                        MIN(profit_per_day) as min_profit,
                        AVG(roi_percentage) as avg_roi
                    FROM deployment_configs
                """)
                stats = dict(cursor.fetchone())
                
                # Get GPU usage stats
                cursor.execute("""
                    SELECT 
                        gpu_count,
                        COUNT(*) as usage_count,
                        AVG(profit_per_day) as avg_profit
                    FROM deployment_configs 
                    GROUP BY gpu_count 
                    ORDER BY gpu_count
                """)
                gpu_stats = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total_configurations": stats["total_configs"],
                    "profitable_configurations": stats["profitable_configs"],
                    "unprofitable_configurations": stats["unprofitable_configs"],
                    "average_daily_profit": stats["avg_profit"],
                    "maximum_daily_profit": stats["max_profit"],
                    "minimum_daily_profit": stats["min_profit"],
                    "average_roi_percentage": stats["avg_roi"],
                    "gpu_usage_stats": gpu_stats
                }
                
        except Exception as e:
            print(f"Error getting configuration stats: {e}")
            return {}

# Global database instance
db = DatabaseManager()

def get_db() -> DatabaseManager:
    """Get database instance."""
    return db 