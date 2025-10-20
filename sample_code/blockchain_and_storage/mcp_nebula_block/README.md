# Nebula Block MCP Server

## Overview
A Model Context Protocol (MCP) server implementation that provides access to Nebula Block GPU resources. This server enables querying GPU instances across different regions, filtering by GPU type, and retrieving detailed information about available resources.

## Components

### Resources
The server exposes the following dynamic resources:
- `gpu://`: Returns all GPU instances across all regions
- `gpu://{region}`: Returns GPU instances for a specific region
- `gpu://{region}/{gpu_type}`: Returns GPU instances for a specific region and GPU type

### Tools
The server provides the following core functionality:

#### Query Tools
- `get_all_gpu_instances`
   - Retrieve all GPU instances across all regions
   - Returns: Dictionary of regions and their GPU instances

- `get_gpu_instances_by_region`
   - Get GPU instances for a specific region
   - Input:
     - `region` (string): The region to query (e.g., "us-east-1")
   - Returns: Dictionary of GPU types and their instances in the specified region

- `get_gpu_instances_by_type`
   - Get GPU instances for a specific region and GPU type
   - Input:
     - `region` (string): The region to query
     - `gpu_type` (string): The GPU type to filter by (e.g., "RTX 4090")
   - Returns: List of GPU instances matching the criteria

### Response Format

The server returns GPU instances in the following format:

```python
@dataclass
class GPUInstance:
    id: str                  # Unique identifier
    dc_id: int               # Data center ID
    product_type: str        # Type of product (Container/Virtual Machine)
    region: str              # Region where the instance is located
    price_per_hour: float    # Price per hour in USD
    cpu: Optional[int]       # Number of CPU cores
    ram: int                 # RAM in GB
    gpu: str                 # GPU model name
    gpu_type: str            # GPU type (H100, A100, L40, RTX)
    gpu_count: int           # Number of GPUs
    disk_size: int           # Disk size in GB
    ephemeral: Optional[int] # Ephemeral storage in GB
    stock: int               # Available stock
    cycle: str               # Billing cycle
    is_available: bool       # Whether the instance is available
```

## Usage with Claude Desktop

### uv

```bash
# Add the server to your claude_desktop_config.json
"mcpServers": {
  "nebula": {
    "command": "uv",
    "args": [
      "--directory",
      "parent_of_servers_repo/mcp_nebula_block",
      "run",
      "mcp-server-nebula-block"
    ]
  }
}
```

### Docker

```json
# Add the server to your claude_desktop_config.json
"mcpServers": {
  "nebula": {
    "command": "docker",
    "args": [
      "run",
      "--rm",
      "-i",
      "mcp/nebula-block"
    ]
  }
}
```

## Usage with VS Code

For quick installation, click the installation buttons below:

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=nebula&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-nebula-block%22%5D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=nebula&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-nebula-block%22%5D%7D&quality=insiders)

[![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Docker-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=nebula&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22mcp%2Fnebula-block%22%5D%7D) [![Install with Docker in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Docker-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=nebula&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22mcp%2Fnebula-block%22%5D%7D&quality=insiders)

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> Note that the `mcp` key is needed when using the `mcp.json` file.

### uv

```json
{
  "mcp": {
    "servers": {
      "nebula": {
        "command": "uvx",
        "args": [
          "mcp-server-nebula-block"
        ]
      }
    }
  }
}
```

### Docker

```json
{
  "mcp": {
    "servers": {
      "nebula": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "mcp/nebula-block"
        ]
      }
    }
  }
}
```

## Building

Docker:

```bash
docker build -t mcp/nebula-block .
```

## Test with MCP inspector

```bash
uv add "mcp[cli]"
mcp dev src/mcp_server_nebula_block/server.py:wrapper
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
