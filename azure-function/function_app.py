import azure.functions as func
import logging
import pandas as pd
import io
import json
import os
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Global variables for caching
_df_cache = None
_cache_timestamp = None

def get_dataframe():
    """Load and cache the dataset from Azure Blob Storage"""
    global _df_cache, _cache_timestamp
    
    # Return cached data if available (cache for 5 minutes)
    import time
    if _df_cache is not None and _cache_timestamp is not None:
        if time.time() - _cache_timestamp < 300:
            logging.info("Using cached dataframe")
            return _df_cache
    
    try:
        # Get connection string from environment variable
        connect_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        
        if not connect_str:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set")
        
        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = os.environ.get('CONTAINER_NAME', 'datasets')
        blob_name = os.environ.get('BLOB_NAME', 'All_Diets.csv')
        
        # Download the CSV from blob storage
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        stream = blob_client.download_blob().readall()
        df = pd.read_csv(io.BytesIO(stream))
        
        # Data cleaning (from Phase 1)
        df.fillna(df.mean(numeric_only=True), inplace=True)
        
        # Add calculated ratios
        df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)'].replace(0, 1)
        df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / df['Fat(g)'].replace(0, 1)
        
        # Cache the dataframe
        _df_cache = df
        _cache_timestamp = time.time()
        
        logging.info(f"Successfully loaded dataset with {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info('Health check endpoint called')
    
    return func.HttpResponse(
        json.dumps({"status": "healthy", "message": "Azure Function is running"}),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="nutritional-insights", methods=["GET"])
def nutritional_insights(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get average macronutrients by diet type (for Bar Chart)
    Query params: diet_type (optional filter)
    """
    logging.info('Nutritional insights endpoint called')
    
    try:
        df = get_dataframe()
        
        # Get optional diet_type filter
        diet_filter = req.params.get('diet_type')
        
        if diet_filter and diet_filter.lower() != 'all':
            df = df[df['Diet_type'].str.lower() == diet_filter.lower()]
        
        # Calculate average macros by diet type
        avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
        
        # Format for chart
        result = {
            'diet_types': avg_macros.index.tolist(),
            'protein': avg_macros['Protein(g)'].round(2).tolist(),
            'carbs': avg_macros['Carbs(g)'].round(2).tolist(),
            'fat': avg_macros['Fat(g)'].round(2).tolist(),
            'total_recipes': len(df)
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in nutritional_insights: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route(route="scatter-data", methods=["GET"])
def scatter_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get protein vs carbs data for scatter plot
    Query params: diet_type (optional), limit (default 100)
    """
    logging.info('Scatter data endpoint called')
    
    try:
        df = get_dataframe()
        
        diet_filter = req.params.get('diet_type')
        limit = int(req.params.get('limit', 100))
        
        if diet_filter and diet_filter.lower() != 'all':
            df = df[df['Diet_type'].str.lower() == diet_filter.lower()]
        
        # Get top protein recipes
        top_recipes = df.nlargest(limit, 'Protein(g)')
        
        result = {
            'data': [
                {
                    'recipe_name': row['Recipe_name'],
                    'protein': round(row['Protein(g)'], 2),
                    'carbs': round(row['Carbs(g)'], 2),
                    'fat': round(row['Fat(g)'], 2),
                    'diet_type': row['Diet_type'],
                    'cuisine_type': row['Cuisine_type']
                }
                for _, row in top_recipes.iterrows()
            ],
            'total_count': len(top_recipes)
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in scatter_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route(route="heatmap-data", methods=["GET"])
def heatmap_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get correlation matrix for nutrients (for Heatmap)
    """
    logging.info('Heatmap data endpoint called')
    
    try:
        df = get_dataframe()
        
        # Calculate correlation matrix
        nutrients = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
        correlation = df[nutrients].corr()
        
        result = {
            'labels': nutrients,
            'data': correlation.values.tolist()
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in heatmap_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route(route="pie-chart-data", methods=["GET"])
def pie_chart_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get recipe distribution by diet type (for Pie Chart)
    """
    logging.info('Pie chart data endpoint called')
    
    try:
        df = get_dataframe()
        
        # Count recipes by diet type
        recipe_counts = df['Diet_type'].value_counts()
        
        result = {
            'labels': recipe_counts.index.tolist(),
            'values': recipe_counts.values.tolist(),
            'total': len(df)
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in pie_chart_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route(route="recipes", methods=["GET"])
def get_recipes(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get recipes with filters
    Query params: diet_type, cuisine_type, page, limit
    """
    logging.info('Recipes endpoint called')
    
    try:
        df = get_dataframe()
        
        # Apply filters
        diet_filter = req.params.get('diet_type')
        cuisine_filter = req.params.get('cuisine_type')
        page = int(req.params.get('page', 1))
        limit = int(req.params.get('limit', 20))
        
        if diet_filter and diet_filter.lower() != 'all':
            df = df[df['Diet_type'].str.lower() == diet_filter.lower()]
        
        if cuisine_filter and cuisine_filter.lower() != 'all':
            df = df[df['Cuisine_type'].str.lower() == cuisine_filter.lower()]
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        paginated_df = df.iloc[start_idx:end_idx]
        
        result = {
            'recipes': [
                {
                    'recipe_name': row['Recipe_name'],
                    'diet_type': row['Diet_type'],
                    'cuisine_type': row['Cuisine_type'],
                    'protein': round(row['Protein(g)'], 2),
                    'carbs': round(row['Carbs(g)'], 2),
                    'fat': round(row['Fat(g)'], 2)
                }
                for _, row in paginated_df.iterrows()
            ],
            'page': page,
            'total_pages': (len(df) + limit - 1) // limit,
            'total_recipes': len(df)
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in recipes: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route(route="clusters", methods=["GET"])
def get_clusters(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get recipe clusters based on macronutrient profiles
    Uses simple k-means-like grouping
    """
    logging.info('Clusters endpoint called')
    
    try:
        df = get_dataframe()
        
        # Create simple clusters based on dominant macronutrient
        def classify_recipe(row):
            protein = row['Protein(g)']
            carbs = row['Carbs(g)']
            fat = row['Fat(g)']
            
            total = protein + carbs + fat
            if total == 0:
                return 'Balanced'
            
            protein_pct = (protein * 4 / total) * 100
            carbs_pct = (carbs * 4 / total) * 100
            fat_pct = (fat * 9 / total) * 100
            
            if protein_pct > 40:
                return 'High Protein'
            elif carbs_pct > 50:
                return 'High Carb'
            elif fat_pct > 40:
                return 'High Fat'
            else:
                return 'Balanced'
        
        df['Cluster'] = df.apply(classify_recipe, axis=1)
        
        cluster_counts = df['Cluster'].value_counts()
        
        result = {
            'clusters': [
                {
                    'name': cluster,
                    'count': int(count),
                    'percentage': round((count / len(df)) * 100, 2)
                }
                for cluster, count in cluster_counts.items()
            ],
            'total_recipes': len(df)
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in clusters: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route(route="stats", methods=["GET"])
def get_stats(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get overall dataset statistics
    """
    logging.info('Stats endpoint called')
    
    try:
        df = get_dataframe()
        
        result = {
            'total_recipes': len(df),
            'diet_types': df['Diet_type'].nunique(),
            'cuisine_types': df['Cuisine_type'].nunique(),
            'avg_protein': round(df['Protein(g)'].mean(), 2),
            'avg_carbs': round(df['Carbs(g)'].mean(), 2),
            'avg_fat': round(df['Fat(g)'].mean(), 2),
            'diet_distribution': df['Diet_type'].value_counts().to_dict()
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f"Error in stats: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )
