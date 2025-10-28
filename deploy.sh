#!/bin/bash
set -e

# Scaleway MCP Server Deployment Script
# This script builds and deploys the MCP server to Scaleway Serverless Containers

echo "==================================================================="
echo "Scaleway MCP Server - Deployment Script"
echo "==================================================================="

# Configuration
IMAGE_NAME="scaleway-mcp-server"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-docker.io}"
REGISTRY_NAMESPACE="${REGISTRY_NAMESPACE:-your-namespace}"
FULL_IMAGE_NAME="${REGISTRY}/${REGISTRY_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"

# Scaleway configuration
SCW_REGION="${SCW_REGION:-fr-par}"
SCW_NAMESPACE_NAME="${SCW_NAMESPACE_NAME:-scaleway-mcp}"
SCW_CONTAINER_NAME="${SCW_CONTAINER_NAME:-scaleway-mcp-server}"

echo ""
echo "Configuration:"
echo "  Image: ${FULL_IMAGE_NAME}"
echo "  Region: ${SCW_REGION}"
echo "  Namespace: ${SCW_NAMESPACE_NAME}"
echo "  Container: ${SCW_CONTAINER_NAME}"
echo ""

# Check if required environment variables are set
if [ -z "$SCW_ACCESS_KEY" ] || [ -z "$SCW_SECRET_KEY" ] || [ -z "$SCW_PROJECT_ID" ]; then
    echo "Error: Required environment variables not set!"
    echo "Please set: SCW_ACCESS_KEY, SCW_SECRET_KEY, SCW_PROJECT_ID"
    exit 1
fi

# Step 1: Build Docker image
echo "Step 1: Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
echo "✓ Docker image built successfully"

# Step 2: Tag image for registry
echo ""
echo "Step 2: Tagging image for registry..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}
echo "✓ Image tagged: ${FULL_IMAGE_NAME}"

# Step 3: Push to registry
echo ""
echo "Step 3: Pushing image to registry..."
echo "Note: Make sure you're logged in to your registry (docker login)"
read -p "Press Enter to continue or Ctrl+C to cancel..."
docker push ${FULL_IMAGE_NAME}
echo "✓ Image pushed to registry"

# Step 4: Deploy to Scaleway (using Scaleway CLI)
echo ""
echo "Step 4: Deploying to Scaleway Serverless Containers..."

# Check if namespace exists, create if not
echo "Checking if namespace exists..."
if ! scw container namespace get name=${SCW_NAMESPACE_NAME} region=${SCW_REGION} &>/dev/null; then
    echo "Creating namespace: ${SCW_NAMESPACE_NAME}"
    scw container namespace create \
        name=${SCW_NAMESPACE_NAME} \
        region=${SCW_REGION} \
        description="Scaleway MCP Server namespace"
    echo "✓ Namespace created"
else
    echo "✓ Namespace already exists"
fi

# Get namespace ID
NAMESPACE_ID=$(scw container namespace list region=${SCW_REGION} -o json | jq -r ".[] | select(.name==\"${SCW_NAMESPACE_NAME}\") | .id")
echo "Namespace ID: ${NAMESPACE_ID}"

# Deploy or update container
echo ""
echo "Deploying container..."
if scw container container get ${SCW_CONTAINER_NAME} region=${SCW_REGION} &>/dev/null; then
    echo "Updating existing container..."
    scw container container update ${SCW_CONTAINER_NAME} \
        region=${SCW_REGION} \
        registry-image=${FULL_IMAGE_NAME}
else
    echo "Creating new container..."
    scw container container create \
        name=${SCW_CONTAINER_NAME} \
        namespace-id=${NAMESPACE_ID} \
        region=${SCW_REGION} \
        registry-image=${FULL_IMAGE_NAME} \
        port=8080 \
        min-scale=0 \
        max-scale=5 \
        cpu-limit=1000 \
        memory-limit=2048 \
        environment-variables.SCALEWAY_ACCESS_KEY=${SCW_ACCESS_KEY} \
        environment-variables.SCALEWAY_SECRET_KEY=${SCW_SECRET_KEY} \
        environment-variables.SCALEWAY_PROJECT_ID=${SCW_PROJECT_ID} \
        environment-variables.SCALEWAY_ORGANIZATION_ID=${SCW_ORGANIZATION_ID} \
        environment-variables.SCALEWAY_DEFAULT_REGION=${SCW_REGION} \
        environment-variables.SCALEWAY_DEFAULT_ZONE=${SCW_REGION}-1
fi

echo "✓ Container deployed"

# Get container URL
echo ""
echo "Getting container URL..."
CONTAINER_URL=$(scw container container get ${SCW_CONTAINER_NAME} region=${SCW_REGION} -o json | jq -r '.domain_name')

echo ""
echo "==================================================================="
echo "Deployment Complete!"
echo "==================================================================="
echo ""
echo "Container URL: https://${CONTAINER_URL}"
echo "MCP Endpoint: https://${CONTAINER_URL}/mcp"
echo "Health Check: https://${CONTAINER_URL}/health"
echo ""
echo "Test the deployment:"
echo "  curl https://${CONTAINER_URL}/health"
echo ""
echo "==================================================================="
