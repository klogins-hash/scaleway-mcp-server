#!/usr/bin/env python3
"""
Scaleway MCP Server
A Model Context Protocol server for managing Scaleway cloud infrastructure.
"""

import os
import sys
import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from scaleway import Client
from scaleway.instance.v1.api import InstanceV1API
from scaleway.vpc.v2.api import VpcV2API
from scaleway.k8s.v1.api import K8SV1API

# Configure logging to stderr only (NEVER use print() in STDIO-based MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("scaleway-mcp")

# Initialize FastMCP server
mcp = FastMCP("scaleway")

# Global Scaleway client
scaleway_client: Optional[Client] = None


def get_scaleway_client() -> Client:
    """Get or create Scaleway client with credentials from environment variables."""
    global scaleway_client
    
    if scaleway_client is not None:
        return scaleway_client
    
    # Load credentials from environment variables
    access_key = os.getenv("SCW_ACCESS_KEY")
    secret_key = os.getenv("SCW_SECRET_KEY")
    project_id = os.getenv("SCW_PROJECT_ID")
    organization_id = os.getenv("SCW_ORGANIZATION_ID")
    default_region = os.getenv("SCW_DEFAULT_REGION", "fr-par")
    default_zone = os.getenv("SCW_DEFAULT_ZONE", "fr-par-1")
    
    if not access_key or not secret_key or not project_id:
        error_msg = "Missing required Scaleway credentials. Please set SCW_ACCESS_KEY, SCW_SECRET_KEY, and SCW_PROJECT_ID environment variables."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Initializing Scaleway client with region={default_region}, zone={default_zone}")
    
    scaleway_client = Client(
        access_key=access_key,
        secret_key=secret_key,
        default_project_id=project_id,
        default_organization_id=organization_id,
        default_region=default_region,
        default_zone=default_zone,
    )
    
    return scaleway_client


# ============================================================================
# INSTANCE MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_instances(zone: Optional[str] = None) -> str:
    """List all compute instances in a Scaleway zone.
    
    Args:
        zone: Scaleway zone (e.g., fr-par-1, nl-ams-1). If not provided, uses default zone.
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Listing instances in zone: {target_zone}")
        
        response = instance_api.list_servers(zone=target_zone)
        servers = response.servers or []
        
        if not servers:
            return f"No instances found in zone {target_zone}."
        
        result = f"Found {len(servers)} instance(s) in zone {target_zone}:\n\n"
        for server in servers:
            result += f"- **{server.name}** (ID: {server.id})\n"
            result += f"  - State: {server.state}\n"
            result += f"  - Type: {server.commercial_type}\n"
            result += f"  - Public IP: {server.public_ip.address if server.public_ip else 'None'}\n"
            result += f"  - Private IP: {server.private_ip or 'None'}\n"
            result += f"  - Created: {server.creation_date}\n\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to list instances: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def get_instance(instance_id: str, zone: Optional[str] = None) -> str:
    """Get detailed information about a specific instance.
    
    Args:
        instance_id: The ID of the instance to retrieve
        zone: Scaleway zone (e.g., fr-par-1). If not provided, uses default zone.
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Getting instance {instance_id} in zone {target_zone}")
        
        server = instance_api.get_server(zone=target_zone, server_id=instance_id)
        s = server.server
        
        result = f"**Instance Details: {s.name}**\n\n"
        result += f"- ID: {s.id}\n"
        result += f"- State: {s.state}\n"
        result += f"- Type: {s.commercial_type}\n"
        result += f"- Architecture: {s.arch}\n"
        result += f"- Public IP: {s.public_ip.address if s.public_ip else 'None'}\n"
        result += f"- Private IP: {s.private_ip or 'None'}\n"
        result += f"- IPv6: {s.ipv6.address if s.ipv6 else 'None'}\n"
        result += f"- Bootscript: {s.bootscript.title if s.bootscript else 'None'}\n"
        result += f"- Protected: {s.protected}\n"
        result += f"- Created: {s.creation_date}\n"
        result += f"- Modified: {s.modification_date}\n"
        
        if s.volumes:
            result += f"\n**Volumes:**\n"
            for vol_key, vol in s.volumes.items():
                result += f"- {vol_key}: {vol.name} ({vol.size} bytes, {vol.volume_type})\n"
        
        if s.tags:
            result += f"\n**Tags:** {', '.join(s.tags)}\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to get instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def create_instance(
    name: str,
    instance_type: str,
    image_id: str,
    zone: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> str:
    """Create a new compute instance.
    
    Args:
        name: Name for the new instance
        instance_type: Instance type (e.g., DEV1-S, GP1-XS, PLAY2-NANO)
        image_id: Image ID to use for the instance
        zone: Scaleway zone (e.g., fr-par-1). If not provided, uses default zone.
        tags: Optional list of tags for the instance
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Creating instance {name} in zone {target_zone}")
        
        server = instance_api.create_server(
            zone=target_zone,
            name=name,
            commercial_type=instance_type,
            image=image_id,
            project=client.default_project_id,
            tags=tags or []
        )
        
        s = server.server
        result = f"✓ Instance created successfully!\n\n"
        result += f"- Name: {s.name}\n"
        result += f"- ID: {s.id}\n"
        result += f"- Type: {s.commercial_type}\n"
        result += f"- State: {s.state}\n"
        result += f"- Zone: {target_zone}\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to create instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def start_instance(instance_id: str, zone: Optional[str] = None) -> str:
    """Start a stopped instance.
    
    Args:
        instance_id: The ID of the instance to start
        zone: Scaleway zone (e.g., fr-par-1). If not provided, uses default zone.
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Starting instance {instance_id} in zone {target_zone}")
        
        instance_api.server_action(
            zone=target_zone,
            server_id=instance_id,
            action="poweron"
        )
        
        return f"✓ Instance {instance_id} is starting."
        
    except Exception as e:
        error_msg = f"Failed to start instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def stop_instance(instance_id: str, zone: Optional[str] = None) -> str:
    """Stop a running instance.
    
    Args:
        instance_id: The ID of the instance to stop
        zone: Scaleway zone (e.g., fr-par-1). If not provided, uses default zone.
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Stopping instance {instance_id} in zone {target_zone}")
        
        instance_api.server_action(
            zone=target_zone,
            server_id=instance_id,
            action="poweroff"
        )
        
        return f"✓ Instance {instance_id} is stopping."
        
    except Exception as e:
        error_msg = f"Failed to stop instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def delete_instance(instance_id: str, zone: Optional[str] = None) -> str:
    """Delete an instance.
    
    Args:
        instance_id: The ID of the instance to delete
        zone: Scaleway zone (e.g., fr-par-1). If not provided, uses default zone.
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Deleting instance {instance_id} in zone {target_zone}")
        
        instance_api.delete_server(
            zone=target_zone,
            server_id=instance_id
        )
        
        return f"✓ Instance {instance_id} has been deleted."
        
    except Exception as e:
        error_msg = f"Failed to delete instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


# ============================================================================
# NETWORK MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_private_networks(region: Optional[str] = None) -> str:
    """List all private networks in a Scaleway region.
    
    Args:
        region: Scaleway region (e.g., fr-par, nl-ams). If not provided, uses default region.
    """
    try:
        client = get_scaleway_client()
        vpc_api = VpcV2API(client)
        
        target_region = region or client.default_region
        logger.info(f"Listing private networks in region: {target_region}")
        
        response = vpc_api.list_private_networks(region=target_region)
        networks = response.private_networks or []
        
        if not networks:
            return f"No private networks found in region {target_region}."
        
        result = f"Found {len(networks)} private network(s) in region {target_region}:\n\n"
        for network in networks:
            result += f"- **{network.name}** (ID: {network.id})\n"
            result += f"  - Created: {network.created_at}\n"
            if network.tags:
                result += f"  - Tags: {', '.join(network.tags)}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to list private networks: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def create_private_network(name: str, region: Optional[str] = None, tags: Optional[list[str]] = None) -> str:
    """Create a new private network.
    
    Args:
        name: Name for the new private network
        region: Scaleway region (e.g., fr-par, nl-ams). If not provided, uses default region.
        tags: Optional list of tags for the network
    """
    try:
        client = get_scaleway_client()
        vpc_api = VpcV2API(client)
        
        target_region = region or client.default_region
        logger.info(f"Creating private network {name} in region {target_region}")
        
        network = vpc_api.create_private_network(
            region=target_region,
            name=name,
            project_id=client.default_project_id,
            tags=tags or []
        )
        
        result = f"✓ Private network created successfully!\n\n"
        result += f"- Name: {network.name}\n"
        result += f"- ID: {network.id}\n"
        result += f"- Region: {target_region}\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to create private network: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


# ============================================================================
# KUBERNETES MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_k8s_clusters(region: Optional[str] = None) -> str:
    """List all Kubernetes clusters in a Scaleway region.
    
    Args:
        region: Scaleway region (e.g., fr-par, nl-ams). If not provided, uses default region.
    """
    try:
        client = get_scaleway_client()
        k8s_api = K8SV1API(client)
        
        target_region = region or client.default_region
        logger.info(f"Listing Kubernetes clusters in region: {target_region}")
        
        response = k8s_api.list_clusters(region=target_region)
        clusters = response.clusters or []
        
        if not clusters:
            return f"No Kubernetes clusters found in region {target_region}."
        
        result = f"Found {len(clusters)} Kubernetes cluster(s) in region {target_region}:\n\n"
        for cluster in clusters:
            result += f"- **{cluster.name}** (ID: {cluster.id})\n"
            result += f"  - Status: {cluster.status}\n"
            result += f"  - Version: {cluster.version}\n"
            result += f"  - CNI: {cluster.cni}\n"
            result += f"  - Created: {cluster.created_at}\n"
            if cluster.tags:
                result += f"  - Tags: {', '.join(cluster.tags)}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to list Kubernetes clusters: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@mcp.tool()
async def get_k8s_cluster(cluster_id: str, region: Optional[str] = None) -> str:
    """Get detailed information about a Kubernetes cluster.
    
    Args:
        cluster_id: The ID of the cluster to retrieve
        region: Scaleway region (e.g., fr-par, nl-ams). If not provided, uses default region.
    """
    try:
        client = get_scaleway_client()
        k8s_api = K8SV1API(client)
        
        target_region = region or client.default_region
        logger.info(f"Getting Kubernetes cluster {cluster_id} in region {target_region}")
        
        cluster = k8s_api.get_cluster(region=target_region, cluster_id=cluster_id)
        
        result = f"**Kubernetes Cluster Details: {cluster.name}**\n\n"
        result += f"- ID: {cluster.id}\n"
        result += f"- Status: {cluster.status}\n"
        result += f"- Version: {cluster.version}\n"
        result += f"- CNI: {cluster.cni}\n"
        result += f"- Type: {cluster.type_}\n"
        result += f"- Description: {cluster.description or 'None'}\n"
        result += f"- Dashboard URL: {cluster.dashboard_url or 'None'}\n"
        result += f"- Created: {cluster.created_at}\n"
        result += f"- Updated: {cluster.updated_at}\n"
        
        if cluster.tags:
            result += f"\n**Tags:** {', '.join(cluster.tags)}\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to get Kubernetes cluster: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


# ============================================================================
# IMAGE MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_images(zone: Optional[str] = None, arch: Optional[str] = None) -> str:
    """List available instance images.
    
    Args:
        zone: Scaleway zone (e.g., fr-par-1). If not provided, uses default zone.
        arch: Filter by architecture (x86_64 or arm64). If not provided, shows all.
    """
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Listing images in zone: {target_zone}")
        
        response = instance_api.list_images(zone=target_zone, arch=arch)
        images = response.images or []
        
        if not images:
            return f"No images found in zone {target_zone}."
        
        result = f"Found {len(images)} image(s) in zone {target_zone}:\n\n"
        for image in images[:20]:  # Limit to first 20 to avoid overwhelming output
            result += f"- **{image.name}** (ID: {image.id})\n"
            result += f"  - Arch: {image.arch}\n"
            result += f"  - Public: {image.public}\n"
            if image.creation_date:
                result += f"  - Created: {image.creation_date}\n"
            result += "\n"
        
        if len(images) > 20:
            result += f"\n... and {len(images) - 20} more images.\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to list images: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


# ============================================================================
# SERVER MAIN
# ============================================================================

def main():
    """Initialize and run the Scaleway MCP server."""
    logger.info("Starting Scaleway MCP server...")
    
    try:
        # Validate credentials on startup
        get_scaleway_client()
        logger.info("Scaleway client initialized successfully")
    except ValueError as e:
        logger.error(f"Failed to initialize Scaleway client: {e}")
        sys.exit(1)
    
    # Run the MCP server with STDIO transport
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
