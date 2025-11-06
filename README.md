# Diet Dashboard - Phase 2: Cloud Deployment

## Project Overview

This project is the Phase 2 implementation of a cloud-based nutritional insights dashboard. It consists of:
- **Backend**: Azure Functions (Python) for data processing and API endpoints
- **Frontend**: Interactive web dashboard with data visualizations
- **Storage**: Azure Blob Storage for dataset hosting

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Dashboard)   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Azure Static   │
│   Web App       │
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│ Azure Functions │
│  (Python 3.9)   │
└────────┬────────┘
         │ Reads Data
         ▼
┌─────────────────┐
│  Azure Blob     │
│    Storage      │
│ (All_Diets.csv) │
└─────────────────┘
```

## Features

### Backend API Endpoints

1. **GET /health** - Health check endpoint
2. **GET /nutritional-insights** - Average macronutrients by diet type
3. **GET /scatter-data** - Protein vs carbs data for scatter plot
4. **GET /heatmap-data** - Nutrient correlation matrix
5. **GET /pie-chart-data** - Recipe distribution by diet type
6. **GET /recipes** - Paginated recipe list with filters
7. **GET /clusters** - Recipe clusters based on macronutrient profiles
8. **GET /stats** - Overall dataset statistics

### Dashboard Features

- **4 Interactive Visualizations**:
  - Bar Chart: Average macronutrient content by diet type
  - Scatter Plot: Protein vs Carbs relationships
  - Heatmap: Nutrient correlations
  - Pie Chart: Recipe distribution by diet type

- **Interactive Controls**:
  - Diet type filter dropdown
  - Search by diet type
  - API interaction buttons
  - Pagination for recipe lists

- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Prerequisites

- Azure subscription (free tier works fine)
- Azure CLI installed
- Python 3.9 or higher
- Node.js (for local testing)
- Git

## Project Structure

```
diet-dashboard-phase2/
├── azure-function/
│   ├── function_app.py       # Main Azure Function code
│   ├── requirements.txt      # Python dependencies
│   ├── host.json            # Function configuration
│   └── local.settings.json  # Local configuration
├── dashboard/
│   ├── index.html           # Dashboard UI
│   ├── styles.css           # Styling
│   └── app.js               # Frontend JavaScript
├── deployment/
│   └── deploy.sh            # Automated deployment script
├── docs/
│   └── documentation.pdf    # Complete project documentation
└── README.md
```

## Installation & Deployment

### Option 1: Automated Deployment (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd diet-dashboard-phase2
   ```

2. **Prepare the dataset**:
   - Place `All_Diets.csv` in the project root or `data/` folder

3. **Run the deployment script**:
   ```bash
   cd deployment
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Update dashboard configuration**:
   - Open `dashboard/app.js`
   - Update `API_BASE_URL` with your Function App URL
   - The script will output your Function URL

5. **Deploy the dashboard**:
   - Option A: Azure Static Web Apps (recommended)
   - Option B: Azure App Service
   - Option C: GitHub Pages

### Option 2: Manual Deployment

#### Step 1: Create Azure Resources

```bash
# Login to Azure
az login

# Create Resource Group
az group create --name diet-analysis-rg --location eastus

# Create Storage Account
az storage account create \
    --name dietstorageacct$(date +%s) \
    --resource-group diet-analysis-rg \
    --location eastus \
    --sku Standard_LRS

# Get connection string
STORAGE_CONNECTION=$(az storage account show-connection-string \
    --name <your-storage-account> \
    --resource-group diet-analysis-rg \
    --query connectionString -o tsv)

# Create container
az storage container create \
    --name datasets \
    --connection-string "$STORAGE_CONNECTION"

# Upload CSV
az storage blob upload \
    --container-name datasets \
    --file All_Diets.csv \
    --name All_Diets.csv \
    --connection-string "$STORAGE_CONNECTION"
```

#### Step 2: Deploy Azure Function

```bash
# Create Function App
az functionapp create \
    --name diet-function-app-$(date +%s) \
    --storage-account <your-storage-account> \
    --resource-group diet-analysis-rg \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --os-type Linux

# Configure app settings
az functionapp config appsettings set \
    --name <your-function-app> \
    --resource-group diet-analysis-rg \
    --settings \
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION" \
    "CONTAINER_NAME=datasets" \
    "BLOB_NAME=All_Diets.csv"

# Enable CORS
az functionapp cors add \
    --name <your-function-app> \
    --resource-group diet-analysis-rg \
    --allowed-origins "*"

# Deploy code
cd azure-function
func azure functionapp publish <your-function-app>
```

#### Step 3: Deploy Dashboard

**Option A: Azure Static Web Apps**

```bash
# Install Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Deploy
cd dashboard
swa deploy --app-name diet-dashboard --resource-group diet-analysis-rg
```

**Option B: Azure App Service**

```bash
# Create App Service Plan
az appservice plan create \
    --name diet-dashboard-plan \
    --resource-group diet-analysis-rg \
    --sku F1 \
    --is-linux

# Create Web App
az webapp create \
    --name diet-dashboard-$(date +%s) \
    --resource-group diet-analysis-rg \
    --plan diet-dashboard-plan \
    --runtime "NODE|18-lts"

# Deploy files
az webapp deployment source config-zip \
    --name <your-webapp> \
    --resource-group diet-analysis-rg \
    --src dashboard.zip
```

## Testing

### Test Azure Function Endpoints

```bash
# Replace with your Function URL
FUNCTION_URL="https://your-function-app.azurewebsites.net/api"

# Health check
curl $FUNCTION_URL/health

# Get nutritional insights
curl $FUNCTION_URL/nutritional-insights

# Get scatter data
curl $FUNCTION_URL/scatter-data?limit=50

# Get heatmap data
curl $FUNCTION_URL/heatmap-data

# Get pie chart data
curl $FUNCTION_URL/pie-chart-data

# Get recipes with filters
curl "$FUNCTION_URL/recipes?diet_type=keto&page=1&limit=20"

# Get clusters
curl $FUNCTION_URL/clusters

# Get stats
curl $FUNCTION_URL/stats
```

### Test Dashboard Locally

```bash
cd dashboard

# Using Python HTTP server
python -m http.server 8000

# Or using Node.js
npx http-server -p 8000

# Open browser
open http://localhost:8000
```

## Configuration

### Azure Function Configuration

Edit `azure-function/local.settings.json` for local testing:

```json
{
  "Values": {
    "AZURE_STORAGE_CONNECTION_STRING": "your-connection-string",
    "CONTAINER_NAME": "datasets",
    "BLOB_NAME": "All_Diets.csv"
  }
}
```

### Dashboard Configuration

Edit `dashboard/app.js`:

```javascript
let API_BASE_URL = 'https://your-function-app.azurewebsites.net/api';
```

## Deliverables Checklist

- [x] Deployed Azure Function URL
- [x] Azure Static Web App / Frontend Deployment Link
- [x] GitHub Repository with code
- [x] Documentation PDF with architecture and screenshots

## Troubleshooting

### Common Issues

**Issue**: Function returns 500 error
- **Solution**: Check Azure Portal → Function App → Logs for detailed error messages
- Verify storage connection string is correct
- Ensure CSV file is uploaded to blob storage

**Issue**: CORS errors in dashboard
- **Solution**: Enable CORS in Function App:
  ```bash
  az functionapp cors add --name <app-name> --allowed-origins "*"
  ```

**Issue**: Charts not loading
- **Solution**: 
  - Open browser console (F12) to check for JavaScript errors
  - Verify API_BASE_URL is correct in app.js
  - Check network tab for failed API requests

**Issue**: CSV file not found
- **Solution**:
  - Verify file is uploaded: Azure Portal → Storage Account → Containers → datasets
  - Check file name is exactly "All_Diets.csv" (case-sensitive)

## Project Grading Rubric

| Category | Requirement | Status |
|----------|-------------|--------|
| **Deployment (20)** | Azure Function and Storage deployed | ✅ |
| **Frontend (20)** | Functional and clear dashboard UI | ✅ |
| **Visualization (20)** | 3+ distinct visualizations | ✅ (4 charts) |
| **Integration (20)** | Frontend fetches data from Azure Function | ✅ |
| **Cloud Practices (10)** | Proper Azure resource usage | ✅ |
| **Documentation (10)** | Clear architecture explanation | ✅ |

## Resources

- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Blob Storage Documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Azure Static Web Apps](https://docs.microsoft.com/en-us/azure/static-web-apps/)

## License

This project is for educational purposes as part of ITSC320 coursework.

## Author

Vijay - SAIT Student
Project Phase 2: Cloud Dashboard Development
