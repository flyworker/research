#!/usr/bin/env python3
"""
Update GPU Costs Script
=======================

This script updates the existing GPU costs in the database to match
the user's specified pricing.
"""

from database import DatabaseManager, GPUConfig

def update_gpu_costs():
    """Update GPU costs in the database."""
    print("Updating GPU costs in database...")
    
    db = DatabaseManager()
    
    # Get existing GPU configurations
    gpus = db.get_gpu_configs(active_only=False)
    
    for gpu in gpus:
        if gpu.name == "NVIDIA A100 80GB":
            # Update A100 cost to $1.80/hour
            gpu.cost_per_hour = 1.8
            gpu.cost_per_month = 1.8 * 24 * 30  # 1296.0
            success = db.update_gpu_config(gpu)
            if success:
                print(f"✓ Updated {gpu.name} cost to ${gpu.cost_per_hour}/hour")
            else:
                print(f"✗ Failed to update {gpu.name}")
        
        elif gpu.name == "NVIDIA H100 80GB":
            # Ensure H100 cost is $2.00/hour
            if gpu.cost_per_hour != 2.0:
                gpu.cost_per_hour = 2.0
                gpu.cost_per_month = 2.0 * 24 * 30  # 1440.0
                success = db.update_gpu_config(gpu)
                if success:
                    print(f"✓ Updated {gpu.name} cost to ${gpu.cost_per_hour}/hour")
                else:
                    print(f"✗ Failed to update {gpu.name}")
            else:
                print(f"✓ {gpu.name} already has correct cost: ${gpu.cost_per_hour}/hour")
        
        elif gpu.name == "NVIDIA RTX 3080":
            # Ensure RTX 3080 cost is $0.55/hour
            if gpu.cost_per_hour != 0.55:
                gpu.cost_per_hour = 0.55
                gpu.cost_per_month = 0.55 * 24 * 30  # 396.0
                success = db.update_gpu_config(gpu)
                if success:
                    print(f"✓ Updated {gpu.name} cost to ${gpu.cost_per_hour}/hour")
                else:
                    print(f"✗ Failed to update {gpu.name}")
            else:
                print(f"✓ {gpu.name} already has correct cost: ${gpu.cost_per_hour}/hour")
        
        elif gpu.name == "NVIDIA RTX 3090":
            # Ensure RTX 3090 cost is $0.75/hour
            if gpu.cost_per_hour != 0.75:
                gpu.cost_per_hour = 0.75
                gpu.cost_per_month = 0.75 * 24 * 30  # 540.0
                success = db.update_gpu_config(gpu)
                if success:
                    print(f"✓ Updated {gpu.name} cost to ${gpu.cost_per_hour}/hour")
                else:
                    print(f"✗ Failed to update {gpu.name}")
            else:
                print(f"✓ {gpu.name} already has correct cost: ${gpu.cost_per_hour}/hour")
    
    print("\nGPU cost update complete!")
    
    # Show current GPU configurations
    print("\nCurrent GPU Configurations:")
    print("-" * 50)
    updated_gpus = db.get_gpu_configs()
    for gpu in updated_gpus:
        print(f"{gpu.name:<20} ${gpu.cost_per_hour:<6} {gpu.vram_gb}GB {gpu.gpu_type}")

if __name__ == "__main__":
    update_gpu_costs() 