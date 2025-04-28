# server.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import requests
import sys
from mcp.server.fastmcp import FastMCP

@dataclass
class GPUInstance:
    id: str
    dc_id: int
    product_type: str
    region: str
    price_per_hour: float
    cpu: Optional[int]
    ram: int
    gpu: str
    gpu_type: str
    gpu_count: int
    disk_size: int
    ephemeral: Optional[int]
    stock: int
    cycle: str
    is_available: bool

class NebulaGPUClient:
    def __init__(self, api_url: str = "https://api.nebulablock.com/api/v1/computing/products"):
        self.api_url = api_url

    def get_gpu_instances(self) -> Dict[str, Dict[str, List[GPUInstance]]]:
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "success":
                raise Exception("Failed to fetch GPU instances")
            
            # Process the data into a more structured format
            processed_data = {}
            for region, gpu_types in data["data"].items():
                processed_data[region] = {}
                for gpu_type, instances in gpu_types.items():
                    processed_data[region][gpu_type] = [
                        GPUInstance(**instance) for instance in instances
                    ]
            
            return processed_data
        except requests.RequestException as e:
            raise Exception(f"Error fetching GPU instances: {str(e)}")

# Create FastMCP instance
mcp = FastMCP("nebula-block")

@mcp.tool()
def get_all_gpu_instances() -> Dict[str, Dict[str, List[GPUInstance]]]:
    """Get all available GPU instances from Nebula Block"""
    client = NebulaGPUClient()
    return client.get_gpu_instances()

@mcp.tool()
def get_gpu_instances_by_region(region: str) -> Dict[str, List[GPUInstance]]:
    """Get GPU instances for a specific region"""
    client = NebulaGPUClient()
    instances = client.get_gpu_instances()
    if region not in instances:
        raise Exception(f"Region {region} not found")
    return instances[region]

@mcp.tool()
def get_gpu_instances_by_type(region: str, gpu_type: str) -> List[GPUInstance]:
    """Get GPU instances for a specific region and GPU type"""
    client = NebulaGPUClient()
    instances = client.get_gpu_instances()
    if region not in instances:
        raise Exception(f"Region {region} not found")
    if gpu_type not in instances[region]:
        raise Exception(f"GPU type {gpu_type} not found in region {region}")
    return instances[region][gpu_type]

def wrapper():
    """Entry point for the MCP server"""
    print("Nebula Block MCP Server is running...", file=sys.stderr)
    return mcp.run()

if __name__ == "__main__":
    wrapper()