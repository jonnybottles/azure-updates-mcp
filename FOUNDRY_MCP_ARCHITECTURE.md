# Azure AI Foundry MCP Server Architecture - Findings & Restructuring Plan

## Executive Summary

**Key Discovery:** "Local MCP Server" in Azure AI Foundry catalog is misleading terminology. It means "custom/third-party MCP server," NOT "running on localhost." All MCP servers for Azure AI Foundry must be deployed to cloud-accessible endpoints.

---

## Table of Contents

1. [Original Misunderstanding](#original-misunderstanding)
2. [What We Discovered](#what-we-discovered)
3. [Actual Architecture](#actual-architecture)
4. [End Goal](#end-goal)
5. [Current State](#current-state)
6. [Required Restructuring](#required-restructuring)
7. [Reference Implementation](#reference-implementation)
8. [Next Steps](#next-steps)

---

## Original Misunderstanding

### What We Thought
- "Local MCP Server" = MCP server running on `localhost` (developer's machine)
- Azure AI Foundry agents could somehow connect to `localhost:8000`
- Could run `uvx azure-updates-mcp` locally and have cloud agents use it
- Architecture we attempted:
  ```
  Azure AI Foundry Agent (cloud)
      ↓ HTTP to localhost ❌
  azure-updates-mcp (localhost:8000)
  ```

### The Problem
```
openai.BadRequestError: Error code: 400 - {'error': {'message':
'Error encountered while enumerating tools from remote server:
http://localhost:8000/mcp. Details: Connection refused (localhost:8000)'}}
```

**Root Cause:** Azure AI Foundry is a cloud service. It cannot connect to `localhost` on a developer's machine without tunneling (ngrok, cloudflared, etc.).

---

## What We Discovered

### Investigation of Microsoft's Example

We examined the **Azure PostgreSQL MCP Server** from the official Foundry catalog:
- **Catalog Entry:** Listed as "local MCP server"
- **Repository:** https://github.com/Azure-Samples/azure-postgres-mcp-demo
- **Actual Implementation:** Deployed to Azure Container Apps (ACA), NOT running locally

### Key Findings

1. **"Local" is Misleading Terminology**
   - "Local MCP Server" = Custom/third-party/community MCP server
   - Does NOT mean "running on localhost"
   - Means "not Microsoft's official built-in tools"

2. **All MCP Servers Must Be Cloud-Accessible**
   - Deployed to Azure Container Apps, Azure App Service, or similar
   - Must have a publicly accessible HTTPS endpoint (or Azure-internal endpoint)
   - Must support Microsoft Entra ID authentication

3. **Authentication is Required**
   - Uses Managed Identity (Entra ID)
   - Foundry agent's Managed Identity authenticates to MCP server
   - MCP server may use its own Managed Identity for downstream resources

---

## Actual Architecture

### Azure PostgreSQL MCP Example Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Azure AI Foundry Agent (Cloud)                              │
│ - Has Managed Identity (MI)                                 │
│ - Configured with MCPTool pointing to Container Apps URL    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTPS + Entra ID Auth
                      │ (Foundry MI authenticates to MCP server)
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ Azure Container Apps (Cloud)                                │
│ - Runs the MCP server code                                  │
│ - Has its own Managed Identity                              │
│ - Accepts requests from Foundry MI                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Database connection using ACA MI
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ Azure Database for PostgreSQL (Cloud)                       │
│ - Entra ID authentication enabled                           │
│ - Grants access to ACA Managed Identity                     │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

| Component | Location | Authentication | Purpose |
|-----------|----------|----------------|---------|
| Foundry Agent | Azure AI Foundry (Cloud) | Uses Project MI | Client that calls MCP tools |
| MCP Server | Azure Container Apps (Cloud) | Accepts Foundry MI | Executes tool logic |
| Backend Resource | Azure (PostgreSQL, etc.) | Accepts ACA MI | Data source for MCP tools |

### Deployment Process (PostgreSQL Example)

1. **Developer runs:** `azd up`
2. **Azure Developer CLI deploys:**
   - Azure Container Apps instance
   - Entra ID App Registration
   - Role assignments for Managed Identities
   - PostgreSQL database (if needed)
3. **Output:** Container Apps URL (e.g., `https://mcp-server.azurecontainerapps.io`)
4. **Developer configures Foundry agent:**
   ```python
   tool = MCPTool(
       server_label="postgres_mcp",
       server_url="https://mcp-server.azurecontainerapps.io/mcp",
       require_approval="never"
   )
   ```

---

## End Goal

### Primary Objective
**Publish `azure-updates-mcp` to Microsoft's official Azure AI Foundry Tool Catalog** as a community/third-party MCP server.

### Success Criteria

1. ✅ **Cloud-Deployed Architecture**
   - MCP server runs in Azure Container Apps (or equivalent)
   - Accessible via HTTPS endpoint
   - No localhost dependencies

2. ✅ **Authentication & Security**
   - Supports Microsoft Entra ID authentication
   - Uses Managed Identity for secure access
   - No hardcoded credentials

3. ✅ **Easy Deployment**
   - Provide `azd` templates for one-command deployment
   - Infrastructure-as-code (Bicep/Terraform)
   - Clear documentation

4. ✅ **Foundry Integration**
   - Works seamlessly with Azure AI Foundry agents
   - Proper MCP protocol implementation
   - Tools discoverable and callable from agents

5. ✅ **Documentation & Examples**
   - Setup guide matching Microsoft's patterns
   - Sample agent configurations
   - Use case examples

### Target User Experience

```bash
# User clones the repo
git clone https://github.com/your-org/azure-updates-mcp

cd azure-updates-mcp

# One command deployment
azd up

# Output provides Container Apps URL
# User adds to Foundry agent configuration

# Agent can now search Azure updates!
```

---

## Current State

### What Works
- ✅ MCP server code (`azure-updates-mcp`) functional
- ✅ Supports HTTP transport via FastMCP
- ✅ Can run locally with `uvx azure-updates-mcp`
- ✅ Tool implementation works (searches Azure updates)

### What Doesn't Work for Foundry
- ❌ Running on localhost (Foundry can't reach it)
- ❌ No authentication layer (needs Entra ID)
- ❌ No Azure deployment templates
- ❌ Not packaged for cloud deployment
- ❌ No Managed Identity support

### Current Server Structure
```
azure-updates-mcp/
├── server code (FastMCP-based)
├── Tool: azure_updates_search
├── Transport: stdio OR http (localhost only)
└── Authentication: None
```

---

## Required Restructuring

### Architecture Changes Needed

#### 1. Add Entra ID Authentication
**Current:** No authentication
```python
mcp.run(transport="http", host="0.0.0.0", port=port)
```

**Required:** Entra ID token validation
```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Entra ID token from Foundry agent"""
    token = credentials.credentials
    # Validate token audience, issuer, etc.
    # Return validated identity
    pass

# Apply to MCP endpoints
```

#### 2. Container Apps Deployment
**Create containerization:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Run in HTTP mode for cloud deployment
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Infrastructure as Code (Bicep/Terraform)
**Create `infra/` directory:**
```
infra/
├── main.bicep                 # Main deployment template
├── containerapp.bicep         # Container Apps definition
├── managed-identity.bicep     # MI configuration
└── entra-app.bicep           # App registration
```

**Or use `azd` templates:**
```yaml
# azure.yaml
name: azure-updates-mcp
services:
  mcp-server:
    project: ./src
    language: python
    host: containerapp
```

#### 4. Update MCP Server Code
**Add authentication middleware:**
```python
# New: auth.py
from azure.identity import DefaultAzureCredential
from fastapi import Request, HTTPException
import jwt

class EntraIDAuth:
    def __init__(self, tenant_id: str, client_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.credential = DefaultAzureCredential()

    async def validate_token(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.replace("Bearer ", "")
        # Validate JWT token
        # Check audience, issuer, expiration
        return True
```

**Update main server file:**
```python
# main.py
from auth import EntraIDAuth
import os

# Initialize auth
auth = EntraIDAuth(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID")
)

# Apply to MCP endpoints
@app.middleware("http")
async def authenticate_requests(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        await auth.validate_token(request)
    return await call_next(request)
```

#### 5. Configuration Management
**Environment variables for cloud deployment:**
```bash
# Required for Azure Container Apps
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<app-registration-client-id>
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8000

# Optional: if MCP server needs downstream auth
AZURE_SUBSCRIPTION_ID=<subscription-id>
```

#### 6. Deployment Scripts
**Create deployment automation:**
```bash
# deploy.sh
#!/bin/bash
set -e

echo "Deploying Azure Updates MCP Server..."

# Deploy infrastructure
azd up

# Get Container Apps URL
CONTAINER_APP_URL=$(azd env get-values | grep CONTAINER_APP_URL | cut -d'=' -f2)

echo "MCP Server deployed to: $CONTAINER_APP_URL"
echo "Use this URL in your Foundry agent configuration:"
echo "  server_url=\"$CONTAINER_APP_URL/mcp\""
```

---

## Reference Implementation

### Azure PostgreSQL MCP Server
**Repository:** https://github.com/Azure-Samples/azure-postgres-mcp-demo

**Key Files to Study:**
1. **`infra/`** - Bicep templates for Container Apps deployment
2. **`azure.yaml`** - Azure Developer CLI configuration
3. **Authentication code** - How they handle Entra ID tokens
4. **README.md** - Deployment instructions pattern

**Deployment Command:**
```bash
azd up
```

**Output Example:**
```
✅ Container App created: mcp-server-app
✅ Entra App registered: mcp-server-auth
✅ Managed Identity assigned
📋 MCP Endpoint: https://mcp-server-xxxxxxx.azurecontainerapps.io/mcp
```

---

## Next Steps

### Phase 1: Research & Planning
- [ ] Clone and study Azure PostgreSQL MCP demo repo
- [ ] Document authentication flow in detail
- [ ] Map current `azure-updates-mcp` code to required structure
- [ ] Identify reusable components from PostgreSQL example

### Phase 2: Add Authentication
- [ ] Add FastAPI authentication middleware
- [ ] Implement Entra ID token validation
- [ ] Test authentication locally (using Azure CLI tokens)
- [ ] Add error handling for auth failures

### Phase 3: Containerization
- [ ] Create Dockerfile
- [ ] Test container locally
- [ ] Push to Azure Container Registry
- [ ] Verify container runs in Azure Container Apps

### Phase 4: Infrastructure as Code
- [ ] Create Bicep templates (or use `azd` templates)
- [ ] Define Container Apps resource
- [ ] Configure Managed Identity
- [ ] Set up Entra ID App Registration
- [ ] Add role assignments

### Phase 5: Deployment & Testing
- [ ] Deploy to Azure using `azd up`
- [ ] Verify MCP endpoint is accessible
- [ ] Test authentication with Foundry agent
- [ ] Run 5+ test queries
- [ ] Validate tool execution

### Phase 6: Documentation
- [ ] Create comprehensive README
- [ ] Add deployment guide
- [ ] Document architecture diagrams
- [ ] Provide troubleshooting guide
- [ ] Create example Foundry agent configurations

### Phase 7: Submission to Catalog
- [ ] Follow Microsoft's submission process
- [ ] Provide required metadata
- [ ] Submit for review
- [ ] Address feedback
- [ ] Publish to catalog

---

## Technical Debt & Considerations

### Current Limitations
1. **No caching** - Every query hits the search service
2. **No rate limiting** - Could be abused
3. **No logging/telemetry** - Hard to debug issues
4. **No health checks** - Container Apps needs health endpoints

### Recommended Additions
```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "azure-updates-mcp"}

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return {
        "requests_total": request_counter,
        "errors_total": error_counter,
        "uptime_seconds": get_uptime()
    }

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/mcp/tools/call")
@limiter.limit("10/minute")
async def call_tool(request: Request):
    # Tool execution
    pass
```

---

## Questions to Answer

1. **Authentication Scope:**
   - Should we allow unauthenticated requests for public access?
   - Or require Entra ID for all requests?
   - **Recommendation:** Start with Entra ID required, add public mode later

2. **Deployment Options:**
   - Container Apps only?
   - Also support Azure App Service?
   - Azure Functions?
   - **Recommendation:** Start with Container Apps (matches Microsoft's pattern)

3. **Pricing & Cost:**
   - Container Apps has free tier (limited)
   - Need to document expected costs
   - **Recommendation:** Provide cost calculator in README

4. **Multi-Tenancy:**
   - Should one deployment support multiple Foundry projects?
   - Or one deployment per project?
   - **Recommendation:** Start single-tenant, add multi-tenant later

---

## Resources

### Microsoft Documentation
- [Azure AI Foundry MCP Tools](https://learn.microsoft.com/azure/ai-foundry/tools/mcp)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [Managed Identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

### Example Implementations
- [Azure PostgreSQL MCP](https://github.com/Azure-Samples/azure-postgres-mcp-demo)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

### Tools Needed
- Azure Developer CLI (`azd`)
- Azure CLI (`az`)
- Docker (for local testing)
- Python 3.11+

---

## Conclusion

**Key Takeaway:** To publish `azure-updates-mcp` to the Azure AI Foundry catalog, we must restructure from a localhost-only tool to a cloud-deployed service with authentication. This requires significant architectural changes but follows a well-established pattern from Microsoft's examples.

**Estimated Effort:**
- Authentication layer: 2-4 hours
- Containerization: 1-2 hours
- Infrastructure as Code: 4-8 hours
- Testing & debugging: 4-8 hours
- Documentation: 2-4 hours
- **Total: ~2-3 days of focused development**

**Value Proposition:**
Once deployed, any Azure AI Foundry user can add the `azure-updates-mcp` tool to their agents with a single configuration change, enabling AI-powered discovery of Azure service updates and announcements.

---

**Document Version:** 1.0
**Last Updated:** 2026-02-02
**Author:** Implementation findings from Azure AI Foundry MCP integration testing
