import azure.functions as func
import logging
import json
import datetime as dt
from shared.blob_utils import load_dataset

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="getNutritionalInsights", methods=["GET"])
def get_nutritional_insights(req: func.HttpRequest) -> func.HttpResponse:
    """Get average nutritional data by diet type"""
    logging.info('getNutritionalInsights called')
    
    try:
        df = load_dataset()
        
        # Optional filter by diet type
        diet = req.params.get("dietType")
        if diet and diet.lower() != 'all':
            df = df[df["diet_type"].str.lower() == diet.lower()]
        
        # Calculate averages by diet type
        agg = df.groupby("diet_type")[["protein", "carbs", "fat", "calories"]].mean().reset_index()
        
        result = {
            "meta": {
                "generatedAt": dt.datetime.utcnow().isoformat() + "Z",
                "totalRecipes": int(df.shape[0])
            },
            "barChart": agg.to_dict(orient="records")
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logging.error(f"Error in getNutritionalInsights: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.route(route="getRecipes", methods=["GET"])
def get_recipes(req: func.HttpRequest) -> func.HttpResponse:
    """Get paginated list of recipes"""
    logging.info('getRecipes called')
    
    try:
        df = load_dataset()
        
        # Filters
        diet = req.params.get("dietType")
        page = int(req.params.get("page", 1))
        size = int(req.params.get("pageSize", 20))
        
        if diet and diet.lower() != 'all':
            df = df[df["diet_type"].str.lower() == diet.lower()]
        
        # Pagination
        total = int(df.shape[0])
        start = (page - 1) * size
        end = start + size
        
        cols = ["recipe", "diet_type", "calories", "protein", "carbs", "fat"]
        items = df[cols].iloc[start:end].to_dict(orient="records")
        
        result = {
            "meta": {
                "generatedAt": dt.datetime.utcnow().isoformat() + "Z",
                "total": total,
                "page": page,
                "pageSize": size,
                "totalPages": (total + size - 1) // size
            },
            "recipes": items
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logging.error(f"Error in getRecipes: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.route(route="getClusters", methods=["GET"])
def get_clusters(req: func.HttpRequest) -> func.HttpResponse:
    """Get recipe scatter data for protein vs carbs"""
    logging.info('getClusters called')
    
    try:
        df = load_dataset()
        
        # Get a sample of recipes for scatter plot
        sample_size = min(100, len(df))
        sample = df.sample(n=sample_size, random_state=42)
        
        result = {
            "meta": {
                "generatedAt": dt.datetime.utcnow().isoformat() + "Z",
                "totalRecipes": int(df.shape[0])
            },
            "clusters": [
                {
                    "recipe": row['recipe'],
                    "protein": float(row['protein']),
                    "carbs": float(row['carbs']),
                    "fat": float(row['fat']),
                    "diet_type": row['diet_type']
                }
                for _, row in sample.iterrows()
            ]
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logging.error(f"Error in getClusters: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.route(route="getStats", methods=["GET"])
def get_stats(req: func.HttpRequest) -> func.HttpResponse:
    """Get overall dataset statistics"""
    logging.info('getStats called')
    
    try:
        df = load_dataset()
        
        result = {
            "meta": {
                "generatedAt": dt.datetime.utcnow().isoformat() + "Z"
            },
            "stats": {
                "totalRecipes": int(df.shape[0]),
                "dietTypes": int(df['diet_type'].nunique()),
                "avgProtein": round(float(df['protein'].mean()), 2),
                "avgCarbs": round(float(df['carbs'].mean()), 2),
                "avgFat": round(float(df['fat'].mean()), 2),
                "avgCalories": round(float(df['calories'].mean()), 2)
            }
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logging.error(f"Error in getStats: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )