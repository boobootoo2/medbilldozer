#!/bin/bash
# Script to configure CORS for Google Cloud Storage buckets

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up CORS for GCS buckets...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get the bucket name from environment or use default
BUCKET_NAME="${GCS_BUCKET_DOCUMENTS:-medbilldozer-documents}"

echo -e "${YELLOW}Bucket name: ${BUCKET_NAME}${NC}"

# Apply CORS configuration
echo -e "${YELLOW}Applying CORS configuration...${NC}"
gcloud storage buckets update "gs://${BUCKET_NAME}" \
    --cors-file=config/gcs-cors.json

echo -e "${GREEN}✅ CORS configuration applied successfully!${NC}"

# Verify the configuration
echo -e "${YELLOW}Current CORS configuration:${NC}"
gcloud storage buckets describe "gs://${BUCKET_NAME}" --format="json(cors_config)"

echo ""
echo -e "${GREEN}Done! Your bucket is now configured to accept uploads from:${NC}"
echo "  - Local development servers (localhost:5173-5176)"
echo "  - Vercel preview deployments"
echo "  - Production domain (medbilldozer.com)"
