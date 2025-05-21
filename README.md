# Research Repository

A collection of research, experiments, and sample implementations in AI/ML agents and decentralized computing.

## Research Focus Areas

### AI/ML Agents
- Autonomous agent architectures
- Agent-based system design
- Multi-agent collaboration
- Agent learning and adaptation
- Natural language processing for agents

### Decentralized Computing
- Distributed systems architecture
- Blockchain integration
- IPFS storage solutions
- Decentralized identity and authentication
- Smart contract implementations

## Project Structure

```
.
├── agent/                     # AI agent research and documentation
│   ├── AI_Billing_Agent_Pipeline.md    # Implementation pipeline for AI billing agents
│   └── Future_of_AI_Billing_Agent.md   # Future research directions
├── sample_code/              # Example implementations
│   ├── webhook/             # Webhook integration samples
│   ├── nebula_block_storage/ # Nebula Block storage example
│   ├── mcp_nebula_block/     # MCP server for Nebula Block GPU resources
│   └── team_billing/         # FastAPI team billing example
├── venv/                    # Python virtual environment
├── .gitignore              # Git ignore file
├── LICENSE                  # Project license
└── README.md               # Project documentation
```

## Code Architecture

### Webhook Server (`sample_code/webhook/`)
- **FastAPI Application**: Provides verification endpoints
- **Key Endpoints**:
  - `/webhook/verify-user`: User quest verification
  - `/webhook/developer/verify`: Enhanced developer verification
  - `/webhook/status/{verification_id}`: Verification status check
  - `/webhook/health`: Health check
- **Authentication**: Bearer token verification
- **Models**:
  - `VerificationRequest/Response`: Basic verification
  - `DeveloperVerificationRequest/Response`: Extended verification

### Team Billing API (`sample_code/team_billing/`)
- **FastAPI Application**: Team management and billing
- **SQLModel ORM**: Database operations
- **Key Models**:
  - `Team`: Team information
  - `TeamMember`: Team members
  - `UsageRecord`: Resource usage tracking
  - `Invoice`: Billing invoices
- **Key Endpoints**:
  - `/teams/create`: Team creation
  - `/teams/invite`: Member invitations
  - `/billing/invoice/generate`: Invoice generation
  - `/usage/log`: Usage tracking

### Nebula Block Storage (`sample_code/nebula_block_storage/`)
- **S3 Client**: boto3-based storage operations
- **Key Functions**:
  - `upload_file`: File upload
  - `download_file`: File download
  - `list_objects`: Bucket contents listing
  - `generate_presigned_url`: Temporary access URLs
- **Configuration**: Environment-based setup

### MCP Server (`sample_code/mcp_nebula_block/`)
- **FastMCP Server**: GPU resource management
- **GPUInstance Model**: GPU resource details
- **NebulaGPUClient**: Nebula Block API integration
- **MCP Tools**:
  - `get_all_gpu_instances`: All available GPUs
  - `get_gpu_instances_by_region`: Region-specific GPUs
  - `get_gpu_instances_by_type`: GPU type filtering

## Research Samples

This repository contains various research samples and implementations, including:

1. **AI Billing Agent Pipeline**
   - Implementation of decentralized billing systems
   - Integration of AI agents with blockchain technology
   - Secure payment processing using cryptographic verification

2. **Webhook Integration**
   - Sample implementations for agent communication
   - Event-driven architecture examples
   - API integration patterns

3. **Nebula Block Storage**
   - Example implementation for Nebula Block object storage
   - S3-compatible API usage
   - File upload, download, and management operations
   - Based on [Nebula Block Object Storage Documentation](https://docs.nebulablock.com/object-storage/tutorials/linuxmac)

4. **Team Billing API**
   - FastAPI application for managing teams, tracking usage, and generating invoices.
   - Uses SQLModel for database interactions (SQLite default).
   - Includes team creation, member invites, usage logging, and invoice generation/payment endpoints.
   - See `sample_code/team_billing/` for details.

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/flyworker/research.git
   cd research
   ```

2. Set up the Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Documentation

- [AI Billing Agent Pipeline](agent/AI_Billing_Agent_Pipeline.md) - Detailed implementation guide
- [Future of AI Billing Agent](agent/Future_of_AI_Billing_Agent.md) - Research roadmap
- [Nebula Block Storage Example](sample_code/nebula_block_storage/README.md) - Storage implementation guide

## Research Goals

This repository serves as a platform for:
- Exploring cutting-edge AI/ML agent architectures
- Developing decentralized computing solutions
- Sharing research findings and implementations
- Collaborating on innovative approaches to AI agent development

## Contributing

Contributions are welcome! This is a research-focused repository, and we encourage:
- Sharing new research findings
- Contributing sample implementations
- Discussing and improving existing approaches
- Collaborating on new research directions

## License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.
