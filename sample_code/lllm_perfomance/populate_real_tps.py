#!/usr/bin/env python3
"""
Populate Real TPS Data
======================

This script populates sample real TPS (Tokens Per Second) data for models
to demonstrate the real vs theoretical performance comparison.
"""

import sqlite3
from database import DatabaseManager

def populate_real_tps_data():
    """Populate sample real TPS data for demonstration."""
    
    # Sample real TPS data based on typical benchmarks
    real_tps_data = [
        # Model Name, Real Input TPS, Real Output TPS
        ("Stheno 8B", 150, 350),
        ("TheSpice 8B", 140, 320),
        ("Lyra 12B V4", 120, 280),
        ("Mixtral 8×7B", 100, 250),
        ("SpicedQ3 A3B 30B", 80, 200),
        ("DeepSeek-Coder-33B", 60, 150),
        ("Llama-3-8B", 180, 400),
        ("Mistral-7B", 160, 380),
        ("Gemma-7B", 170, 390),
        ("DeepSeek-V3-0324", 40, 100),
        ("Llama-3-70B", 30, 80),
        ("DeepSeek-V3-0324-AWQ", 50, 120),
    ]
    
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        updated_count = 0
        for model_name, real_input_tps, real_output_tps in real_tps_data:
            cursor.execute("""
                UPDATE model_configs 
                SET real_input_tps_per_gpu = ?, real_output_tps_per_gpu = ?
                WHERE name = ?
            """, (real_input_tps, real_output_tps, model_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✓ Updated {model_name}: Input {real_input_tps} TPS, Output {real_output_tps} TPS")
            else:
                print(f"✗ Model not found: {model_name}")
        
        conn.commit()
        print(f"\nUpdated {updated_count} models with real TPS data")

if __name__ == "__main__":
    print("Populating Real TPS Data...")
    populate_real_tps_data()
    print("Done!") 