#!/usr/bin/env python3
"""
Database Manager for LLM Calculator
===================================

This script provides direct access to the SQLite database file for:
- Viewing database information
- Exporting/importing configurations
- Creating backups
- Analyzing configuration statistics
- Direct database operations

Usage:
    python database_manager.py [command] [options]

Commands:
    info          - Show database information
    stats         - Show configuration statistics
    export        - Export configurations to JSON
    backup        - Create database backup
    list          - List all saved configurations
    search        - Search configurations by criteria
    clean         - Clean up old configurations
"""

import sys
import json
import argparse
from datetime import datetime
from database import DatabaseManager, GPUConfig, ModelConfig, DeploymentConfig

def print_database_info():
    """Print database file information."""
    db = DatabaseManager()
    info = db.get_database_info()
    
    print("=== Database Information ===")
    print(f"File Path: {info['file_path']}")
    print(f"Exists: {info['exists']}")
    print(f"File Size: {info['file_size']:,} bytes")
    print(f"Last Modified: {datetime.fromtimestamp(info['last_modified']).strftime('%Y-%m-%d %H:%M:%S') if info['last_modified'] else 'N/A'}")
    
    print("\n=== Table Counts ===")
    for table, count in info['table_counts'].items():
        print(f"{table}: {count:,} records")

def print_configuration_stats():
    """Print configuration statistics."""
    db = DatabaseManager()
    stats = db.get_configuration_stats()
    
    print("=== Configuration Statistics ===")
    print(f"Total Configurations: {stats.get('total_configurations', 0):,}")
    print(f"Profitable Configurations: {stats.get('profitable_configurations', 0):,}")
    print(f"Unprofitable Configurations: {stats.get('unprofitable_configurations', 0):,}")
    print(f"Average Daily Profit: ${stats.get('average_daily_profit', 0):,.2f}")
    print(f"Maximum Daily Profit: ${stats.get('maximum_daily_profit', 0):,.2f}")
    print(f"Minimum Daily Profit: ${stats.get('minimum_daily_profit', 0):,.2f}")
    print(f"Average ROI: {stats.get('average_roi_percentage', 0):.1f}%")
    
    print("\n=== GPU Usage Statistics ===")
    for gpu_stat in stats.get('gpu_usage_stats', []):
        print(f"{gpu_stat['gpu_count']}x GPU: {gpu_stat['usage_count']} configs, Avg Profit: ${gpu_stat['avg_profit']:,.2f}")

def export_configurations():
    """Export configurations to JSON file."""
    db = DatabaseManager()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"configurations_export_{timestamp}.json"
    
    success = db.export_configurations_to_json(file_path)
    
    if success:
        print(f"✅ Configurations exported to: {file_path}")
        
        # Show export summary
        info = db.get_database_info()
        print(f"📊 Export Summary:")
        print(f"   GPU Configurations: {info['table_counts'].get('gpu_configs', 0)}")
        print(f"   Model Configurations: {info['table_counts'].get('model_configs', 0)}")
        print(f"   Deployment Configurations: {info['table_counts'].get('deployment_configs', 0)}")
        print(f"   User Preferences: {info['table_counts'].get('user_preferences', 0)}")
    else:
        print("❌ Failed to export configurations")

def create_backup():
    """Create database backup."""
    db = DatabaseManager()
    backup_path = db.backup_database()
    
    if backup_path:
        print(f"✅ Database backed up to: {backup_path}")
        
        # Show backup info
        import os
        backup_size = os.path.getsize(backup_path)
        print(f"📊 Backup Size: {backup_size:,} bytes")
    else:
        print("❌ Failed to create backup")

def list_configurations():
    """List all saved configurations."""
    db = DatabaseManager()
    configs = db.get_deployment_configs()
    
    print("=== Saved Configurations ===")
    if not configs:
        print("No configurations found.")
        return
    
    for i, config in enumerate(configs, 1):
        print(f"\n{i}. {config.name}")
        print(f"   GPU Count: {config.gpu_count}")
        print(f"   Model: {config.model_name}")
        print(f"   TPS: {config.input_tps + config.output_tps:,}")
        print(f"   Daily Profit: ${config.profit_per_day:,.2f}")
        print(f"   ROI: {config.roi_percentage:.1f}%")
        print(f"   Created: {config.created_at}")
        if config.notes:
            print(f"   Notes: {config.notes}")

def search_configurations():
    """Search configurations by criteria."""
    db = DatabaseManager()
    configs = db.get_deployment_configs()
    
    print("=== Search Configurations ===")
    print("Available search criteria:")
    print("1. By profitability (profitable/unprofitable)")
    print("2. By GPU count")
    print("3. By model name")
    print("4. By minimum profit")
    
    choice = input("\nEnter search choice (1-4): ").strip()
    
    if choice == "1":
        profitable = input("Show profitable configs? (y/n): ").lower() == 'y'
        filtered = [c for c in configs if (c.profit_per_day > 0) == profitable]
        print(f"\nFound {len(filtered)} {'profitable' if profitable else 'unprofitable'} configurations:")
        
    elif choice == "2":
        gpu_count = int(input("Enter GPU count: "))
        filtered = [c for c in configs if c.gpu_count == gpu_count]
        print(f"\nFound {len(filtered)} configurations with {gpu_count} GPUs:")
        
    elif choice == "3":
        model_name = input("Enter model name (partial match): ").lower()
        filtered = [c for c in configs if model_name in c.model_name.lower()]
        print(f"\nFound {len(filtered)} configurations matching '{model_name}':")
        
    elif choice == "4":
        min_profit = float(input("Enter minimum daily profit: "))
        filtered = [c for c in configs if c.profit_per_day >= min_profit]
        print(f"\nFound {len(filtered)} configurations with profit >= ${min_profit:,.2f}:")
        
    else:
        print("Invalid choice")
        return
    
    # Display results
    for i, config in enumerate(filtered, 1):
        print(f"\n{i}. {config.name}")
        print(f"   Daily Profit: ${config.profit_per_day:,.2f}")
        print(f"   ROI: {config.roi_percentage:.1f}%")
        print(f"   GPU Count: {config.gpu_count}")
        print(f"   Model: {config.model_name}")

def clean_configurations():
    """Clean up old or unprofitable configurations."""
    db = DatabaseManager()
    configs = db.get_deployment_configs()
    
    print("=== Clean Configurations ===")
    print("1. Delete unprofitable configurations")
    print("2. Delete configurations older than X days")
    print("3. Delete configurations with low ROI")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        unprofitable = [c for c in configs if c.profit_per_day <= 0]
        if unprofitable:
            print(f"\nFound {len(unprofitable)} unprofitable configurations:")
            for config in unprofitable:
                print(f"  - {config.name}: ${config.profit_per_day:,.2f}")
            
            confirm = input("\nDelete these configurations? (y/n): ").lower() == 'y'
            if confirm:
                deleted = 0
                for config in unprofitable:
                    config.is_favorite = False  # Mark as inactive
                    if db.update_deployment_config(config):
                        deleted += 1
                print(f"✅ Deleted {deleted} configurations")
        else:
            print("No unprofitable configurations found")
    
    elif choice == "2":
        days = int(input("Delete configurations older than how many days? "))
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        
        old_configs = []
        for config in configs:
            if config.created_at:
                try:
                    created_timestamp = datetime.fromisoformat(config.created_at.replace('Z', '+00:00')).timestamp()
                    if created_timestamp < cutoff_date:
                        old_configs.append(config)
                except:
                    pass
        
        if old_configs:
            print(f"\nFound {len(old_configs)} configurations older than {days} days:")
            for config in old_configs:
                print(f"  - {config.name}: {config.created_at}")
            
            confirm = input("\nDelete these configurations? (y/n): ").lower() == 'y'
            if confirm:
                deleted = 0
                for config in old_configs:
                    config.is_favorite = False
                    if db.update_deployment_config(config):
                        deleted += 1
                print(f"✅ Deleted {deleted} configurations")
        else:
            print(f"No configurations older than {days} days found")
    
    elif choice == "3":
        min_roi = float(input("Delete configurations with ROI below: "))
        low_roi_configs = [c for c in configs if c.roi_percentage < min_roi]
        
        if low_roi_configs:
            print(f"\nFound {len(low_roi_configs)} configurations with ROI < {min_roi}%:")
            for config in low_roi_configs:
                print(f"  - {config.name}: {config.roi_percentage:.1f}%")
            
            confirm = input("\nDelete these configurations? (y/n): ").lower() == 'y'
            if confirm:
                deleted = 0
                for config in low_roi_configs:
                    config.is_favorite = False
                    if db.update_deployment_config(config):
                        deleted += 1
                print(f"✅ Deleted {deleted} configurations")
        else:
            print(f"No configurations with ROI < {min_roi}% found")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Database Manager for LLM Calculator")
    parser.add_argument("command", choices=["info", "stats", "export", "backup", "list", "search", "clean"],
                       help="Command to execute")
    
    args = parser.parse_args()
    
    try:
        if args.command == "info":
            print_database_info()
        elif args.command == "stats":
            print_configuration_stats()
        elif args.command == "export":
            export_configurations()
        elif args.command == "backup":
            create_backup()
        elif args.command == "list":
            list_configurations()
        elif args.command == "search":
            search_configurations()
        elif args.command == "clean":
            clean_configurations()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(1)
    main() 