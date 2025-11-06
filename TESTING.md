# Testing Guide - Diet Dashboard Phase 2

## API Endpoint Testing

### 1. Health Check
**Purpose**: Verify Function App is running

```bash
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "message": "Azure Function is running"
}
```

---

### 2. Nutritional Insights
**Purpose**: Get average macronutrients by diet type

```bash
# All diets
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/nutritional-insights

# Filter by diet type
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/nutritional-insights?diet_type=keto
```

**Expected Response**:
```json
{
  "diet_types": ["dash", "keto", "mediterranean", "paleo", "vegan"],
  "protein": [63.42, 89.15, 71.28, 65.33, 42.17],
  "carbs": [112.45, 45.23, 98.76, 87.54, 145.67],
  "fat": [45.78, 123.45, 67.89, 78.90, 34.56],
  "total_recipes": 7806
}
```

---

### 3. Scatter Data
**Purpose**: Get protein vs carbs data

```bash
# Top 100 recipes
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/scatter-data?limit=100

# Filter by diet
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/scatter-data?diet_type=paleo&limit=50
```

**Expected Response**:
```json
{
  "data": [
    {
      "recipe_name": "High Protein Chicken",
      "protein": 150.5,
      "carbs": 25.3,
      "fat": 45.2,
      "diet_type": "paleo",
      "cuisine_type": "american"
    }
  ],
  "total_count": 100
}
```

---

### 4. Heatmap Data
**Purpose**: Get nutrient correlation matrix

```bash
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/heatmap-data
```

**Expected Response**:
```json
{
  "labels": ["Protein(g)", "Carbs(g)", "Fat(g)"],
  "data": [
    [1.0, 0.45, 0.67],
    [0.45, 1.0, 0.23],
    [0.67, 0.23, 1.0]
  ]
}
```

---

### 5. Pie Chart Data
**Purpose**: Get recipe distribution

```bash
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/pie-chart-data
```

**Expected Response**:
```json
{
  "labels": ["mediterranean", "dash", "vegan", "keto", "paleo"],
  "values": [1753, 1745, 1522, 1512, 1274],
  "total": 7806
}
```

---

### 6. Recipes
**Purpose**: Get paginated recipe list

```bash
# First page
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/recipes?page=1&limit=20

# Filter by diet
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/recipes?diet_type=vegan&page=1&limit=10
```

**Expected Response**:
```json
{
  "recipes": [
    {
      "recipe_name": "Vegan Buddha Bowl",
      "diet_type": "vegan",
      "cuisine_type": "asian",
      "protein": 15.2,
      "carbs": 65.3,
      "fat": 12.4
    }
  ],
  "page": 1,
  "total_pages": 391,
  "total_recipes": 7806
}
```

---

### 7. Clusters
**Purpose**: Get macronutrient-based clusters

```bash
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/clusters
```

**Expected Response**:
```json
{
  "clusters": [
    {
      "name": "High Carb",
      "count": 3245,
      "percentage": 41.57
    },
    {
      "name": "High Protein",
      "count": 2156,
      "percentage": 27.62
    }
  ],
  "total_recipes": 7806
}
```

---

### 8. Statistics
**Purpose**: Get overall dataset stats

```bash
curl https://YOUR-FUNCTION-APP.azurewebsites.net/api/stats
```

**Expected Response**:
```json
{
  "total_recipes": 7806,
  "diet_types": 5,
  "cuisine_types": 15,
  "avg_protein": 66.27,
  "avg_carbs": 97.79,
  "avg_fat": 68.02,
  "diet_distribution": {
    "mediterranean": 1753,
    "dash": 1745,
    "vegan": 1522,
    "keto": 1512,
    "paleo": 1274
  }
}
```

---

## Dashboard Testing Checklist

### Visual Testing
- [ ] **Bar Chart**: Shows 5 diet types with 3 bars each (protein, carbs, fat)
- [ ] **Scatter Plot**: Shows colored points distributed across the chart
- [ ] **Heatmap**: Shows bubble chart with 9 bubbles (3x3 matrix)
- [ ] **Pie Chart**: Shows 5 colored sections representing diet types

### Interaction Testing
- [ ] **Diet Filter**: Selecting a diet updates bar and scatter charts
- [ ] **Search Box**: Typing "keto" filters to keto diet
- [ ] **Get Nutritional Insights**: Shows JSON response below
- [ ] **Get Recipes**: Shows recipe table with 20 rows
- [ ] **Get Clusters**: Shows JSON with cluster data
- [ ] **Pagination**: Previous/Next buttons work correctly

### Responsiveness Testing
- [ ] **Desktop** (1920x1080): All charts fit in 2x2 grid
- [ ] **Tablet** (768px): Charts stack in 1 column
- [ ] **Mobile** (375px): All elements are accessible

### Performance Testing
- [ ] Initial page load: < 3 seconds
- [ ] Chart render time: < 1 second
- [ ] API response time: < 500ms (first call), < 100ms (cached)

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Automated Testing Script

Save as `test-api.sh`:

```bash
#!/bin/bash

# Replace with your Function URL
FUNCTION_URL="https://YOUR-FUNCTION-APP.azurewebsites.net/api"

echo "Testing Diet Dashboard API Endpoints..."
echo "========================================"

# Test health
echo -e "\n1. Testing /health"
curl -s "$FUNCTION_URL/health" | jq '.'

# Test nutritional insights
echo -e "\n2. Testing /nutritional-insights"
curl -s "$FUNCTION_URL/nutritional-insights" | jq '.diet_types, .total_recipes'

# Test scatter data
echo -e "\n3. Testing /scatter-data"
curl -s "$FUNCTION_URL/scatter-data?limit=5" | jq '.total_count'

# Test heatmap
echo -e "\n4. Testing /heatmap-data"
curl -s "$FUNCTION_URL/heatmap-data" | jq '.labels'

# Test pie chart
echo -e "\n5. Testing /pie-chart-data"
curl -s "$FUNCTION_URL/pie-chart-data" | jq '.total'

# Test recipes
echo -e "\n6. Testing /recipes"
curl -s "$FUNCTION_URL/recipes?page=1&limit=5" | jq '.total_recipes'

# Test clusters
echo -e "\n7. Testing /clusters"
curl -s "$FUNCTION_URL/clusters" | jq '.total_recipes'

# Test stats
echo -e "\n8. Testing /stats"
curl -s "$FUNCTION_URL/stats" | jq '.total_recipes, .diet_types'

echo -e "\n========================================"
echo "All tests complete!"
```

**Run**: `chmod +x test-api.sh && ./test-api.sh`

---

## Troubleshooting

### API Returns 500 Error
1. Check Azure Portal → Function App → Logs
2. Verify CSV file is uploaded to Blob Storage
3. Check connection string in Function App settings

### CORS Errors
```bash
az functionapp cors add \
  --name YOUR-FUNCTION-APP \
  --resource-group diet-analysis-rg \
  --allowed-origins "*"
```

### Charts Not Rendering
1. Open browser console (F12)
2. Look for JavaScript errors
3. Verify Chart.js library loaded
4. Check API responses in Network tab

### Slow Response Times
- **First call**: Normal (loading CSV)
- **Subsequent calls**: Should be fast (cached)
- If all calls are slow, check Function App logs

---

## Performance Benchmarks

| Endpoint | First Call | Cached Call | Data Size |
|----------|-----------|-------------|-----------|
| /health | 50ms | 10ms | <100 bytes |
| /nutritional-insights | 800ms | 50ms | ~500 bytes |
| /scatter-data | 900ms | 60ms | ~15KB |
| /heatmap-data | 850ms | 55ms | ~300 bytes |
| /pie-chart-data | 800ms | 50ms | ~200 bytes |
| /recipes | 850ms | 80ms | ~5KB |
| /clusters | 900ms | 70ms | ~400 bytes |
| /stats | 800ms | 50ms | ~400 bytes |

*Tested from eastus region on 2.5GB RAM consumption plan*

---

## Screenshot Locations

For documentation, capture:
1. Azure Portal showing all resources
2. Function App overview page
3. Blob Storage with CSV file
4. Dashboard with all 4 charts
5. Browser console showing successful API calls
6. Network tab showing response times
7. Mobile view of dashboard

Save screenshots as:
- `screenshots/01-azure-resources.png`
- `screenshots/02-function-app.png`
- `screenshots/03-blob-storage.png`
- `screenshots/04-dashboard-desktop.png`
- `screenshots/05-dashboard-mobile.png`
- `screenshots/06-api-responses.png`
