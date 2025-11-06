#!/bin/bash

# Azure Deployment Script for Diet Dashboard Phase 2
# This script deploys all necessary Azure resources

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Diet Dashboard - Azure Deployment${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Configuration
RESOURCE_GROUP="diet-analysis-rg"
LOCATION="westus2"
STORAGE_ACCOUNT="dietstorageacct$(date +%s)"
CONTAINER_NAME="datasets"
FUNCTION_APP="diet-function-app-$(date +%s)"
STATIC_WEB_APP="diet-dashboard-$(date +%s)"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    echo "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo -e "${YELLOW}Step 1: Azure Login${NC}"
az login

# Create Resource Group
echo -e "${YELLOW}Step 2: Creating Resource Group${NC}"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Resource Group created: $RESOURCE_GROUP${NC}"
else
    echo -e "${RED}✗ Failed to create Resource Group${NC}"
    exit 1
fi

# Create Storage Account
echo -e "${YELLOW}Step 3: Creating Storage Account${NC}"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Storage Account created: $STORAGE_ACCOUNT${NC}"
else
    echo -e "${RED}✗ Failed to create Storage Account${NC}"
    exit 1
fi

# Get Storage Connection String
echo -e "${YELLOW}Step 4: Getting Storage Connection String${NC}"
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query connectionString \
    --output tsv)

echo -e "${GREEN}✓ Storage Connection String retrieved${NC}"

# Create Blob Container
echo -e "${YELLOW}Step 5: Creating Blob Container${NC}"
az storage container create \
    --name $CONTAINER_NAME \
    --connection-string "$STORAGE_CONNECTION_STRING" \
    --public-access blob

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Blob Container created: $CONTAINER_NAME${NC}"
else
    echo -e "${RED}✗ Failed to create Blob Container${NC}"
    exit 1
fi

# Upload CSV file to Blob Storage
echo -e "${YELLOW}Step 6: Uploading All_Diets.csv to Blob Storage${NC}"
if [ -f "../data/All_Diets.csv" ]; then
    az storage blob upload \
        --container-name $CONTAINER_NAME \
        --file ../data/All_Diets.csv \
        --name All_Diets.csv \
        --connection-string "$STORAGE_CONNECTION_STRING"
    
    echo -e "${GREEN}✓ CSV file uploaded successfully${NC}"
else
    echo -e "${RED}✗ All_Diets.csv not found in ../data/ directory${NC}"
    echo -e "${YELLOW}Please ensure the CSV file is in the correct location${NC}"
fi

# Create Function App
echo -e "${YELLOW}Step 7: Creating Function App${NC}"
az functionapp create \
    --name $FUNCTION_APP \
    --storage-account $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location $LOCATION \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --os-type Linux

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Function App created: $FUNCTION_APP${NC}"
else
    echo -e "${RED}✗ Failed to create Function App${NC}"
    exit 1
fi

# Configure Function App Settings
echo -e "${YELLOW}Step 8: Configuring Function App Settings${NC}"
az functionapp config appsettings set \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --settings \
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" \
    "CONTAINER_NAME=$CONTAINER_NAME" \
    "BLOB_NAME=All_Diets.csv"

echo -e "${GREEN}✓ Function App settings configured${NC}"

# Enable CORS for Function App
echo -e "${YELLOW}Step 9: Enabling CORS for Function App${NC}"
az functionapp cors add \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --allowed-origins "*"

echo -e "${GREEN}✓ CORS enabled${NC}"

# Deploy Function App Code
echo -e "${YELLOW}Step 10: Deploying Function App Code${NC}"
cd ../azure-function

# Create deployment package
echo "Creating deployment package..."
zip -r function-deployment.zip . -x "*.pyc" -x "__pycache__/*" -x "local.settings.json"

# Deploy using zip
az functionapp deployment source config-zip \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --src function-deployment.zip

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Function App code deployed${NC}"
    rm function-deployment.zip
else
    echo -e "${RED}✗ Failed to deploy Function App code${NC}"
    exit 1
fi

cd ../deployment

# Get Function App URL
FUNCTION_URL="https://${FUNCTION_APP}.azurewebsites.net/api"

# Create Static Web App
echo -e "${YELLOW}Step 11: Creating Static Web App (Alternative: Manual Upload)${NC}"
echo -e "${YELLOW}Note: You can manually deploy the dashboard to Azure Static Web Apps or App Service${NC}"

# Save deployment info
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${YELLOW}Important Information:${NC}"
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Function App: $FUNCTION_APP"
echo "Function URL: $FUNCTION_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update your dashboard/app.js with the Function URL:"
echo "   API_BASE_URL = '$FUNCTION_URL'"
echo ""
echo "2. Test your function endpoints:"
echo "   $FUNCTION_URL/health"
echo "   $FUNCTION_URL/nutritional-insights"
echo ""
echo "3. Deploy your dashboard:"
echo "   - Option A: Azure Static Web Apps"
echo "   - Option B: Azure App Service"
echo "   - Option C: GitHub Pages"
echo ""
echo -e "${GREEN}Deployment details saved to: deployment-info.txt${NC}"

# Save to file
cat > deployment-info.txt << EOF
Azure Deployment Information
=============================

Resource Group: $RESOURCE_GROUP
Location: $LOCATION
Storage Account: $STORAGE_ACCOUNT
Blob Container: $CONTAINER_NAME
Function App: $FUNCTION_APP
Function URL: $FUNCTION_URL

Storage Connection String:
$STORAGE_CONNECTION_STRING

Deployment Date: $(date)

Next Steps:
1. Update dashboard/app.js with Function URL
2. Test endpoints
3. Deploy dashboard frontend
EOF

echo ""
echo -e "${GREEN}All done! 🎉${NC}"
