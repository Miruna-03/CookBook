from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sqlite3
import json
from datetime import datetime
import math

# Initialize FastAPI app
app = FastAPI(
    title="Recipe API",
    description="A RESTful API for accessing recipe database",
    version="1.0.0"
)

# Add CORS middleware - IMPORTANT FOR FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database configuration
DATABASE = "recipes_clean2.db"

# ==================== Pydantic Models ====================

class Nutrient(BaseModel):
    """Nutrient model for validation."""
    calories: Optional[str] = None
    carbohydrateContent: Optional[str] = None
    cholesterolContent: Optional[str] = None
    fiberContent: Optional[str] = None
    proteinContent: Optional[str] = None
    saturatedFatContent: Optional[str] = None
    sodiumContent: Optional[str] = None
    sugarContent: Optional[str] = None
    fatContent: Optional[str] = None
    unsaturatedFatContent: Optional[str] = None

class RecipeResponse(BaseModel):
    """Response model for a single recipe."""
    cuisine: Optional[str] = None
    title: Optional[str] = None
    rating: Optional[float] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    description: Optional[str] = None
    nutrients: Optional[Nutrient] = None
    serves: Optional[str] = None

class PaginatedRecipesResponse(BaseModel):
    """Response model for paginated recipes."""
    success: bool = True
    data: List[RecipeResponse]
    pagination: Dict[str, Any]

# ==================== Database Utilities ====================

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def parse_nutrients(nutrients_str: str) -> Optional[Nutrient]:
    """Parse nutrients JSON string to Nutrient model."""
    if nutrients_str:
        try:
            nutrients_dict = json.loads(nutrients_str)
            return Nutrient(**nutrients_dict)
        except (json.JSONDecodeError, Exception):
            return None
    return None

def extract_calories(nutrients_str: str) -> Optional[float]:
    """Extract numeric calories value from nutrients JSON."""
    if nutrients_str:
        try:
            nutrients = json.loads(nutrients_str)
            calories_str = nutrients.get('calories', '')
            if calories_str:
                # Extract numbers from string like "389 kcal"
                import re
                numbers = re.findall(r'\d+', calories_str)
                if numbers:
                    return float(numbers[0])
        except:
            pass
    return None

# ==================== ENDPOINT 1: Get all recipes (paginated, sorted by rating) ====================

@app.get("/api/recipes", response_model=PaginatedRecipesResponse)
async def get_recipes(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page (max 100)")
):
    """
    Get all recipes with pagination, sorted by rating (descending).
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM recipe")
        total_count = cursor.fetchone()["total"]
        
        # Get paginated recipes sorted by rating (descending)
        cursor.execute("""
            SELECT cuisine, title, rating, prep_time, cook_time, total_time,
                   description, nutrients, serves
            FROM recipe
            WHERE title IS NOT NULL AND cuisine IS NOT NULL
            ORDER BY rating DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        
        recipes = []
        for row in cursor.fetchall():
            recipe_dict = dict(row)
            recipe_dict["nutrients"] = parse_nutrients(recipe_dict.get("nutrients", ""))
            recipes.append(RecipeResponse(**recipe_dict))
        
        conn.close()
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
        
        pagination_info = {
            "page": page,
            "per_page": per_page,
            "total_recipes": total_count,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
        
        return {
            "success": True,
            "data": recipes,
            "pagination": pagination_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINT 2: Search recipes (UPDATED for frontend) ====================

@app.get("/api/recipes/search", response_model=PaginatedRecipesResponse)
async def search_recipes(
    query: Optional[str] = Query(None, description="Search in recipe titles"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating (0-5)"),
    max_calories: Optional[float] = Query(None, ge=0, description="Maximum calories"),
    max_total_time: Optional[int] = Query(None, ge=0, description="Maximum total cooking time in minutes"),
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page (max 100)")
):
    """
    Search recipes with filters.
    """
    try:
        # Build WHERE clause dynamically
        conditions = ["title IS NOT NULL", "cuisine IS NOT NULL"]
        params = []
        
        if query and query.strip():
            conditions.append("LOWER(title) LIKE LOWER(?)")
            params.append(f"%{query}%")
        
        if min_rating is not None:
            conditions.append("rating >= ?")
            params.append(min_rating)
        
        if max_total_time is not None:
            conditions.append("(total_time <= ? OR total_time IS NULL)")
            params.append(max_total_time)
        
        where_clause = " AND ".join(conditions)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count with filters (excluding calories filter for now)
        count_query = f"SELECT COUNT(*) as total FROM recipe WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()["total"]
        
        # Apply pagination
        offset = (page - 1) * per_page
        limit_query = f"""
            SELECT cuisine, title, rating, prep_time, cook_time, total_time,
                   description, nutrients, serves
            FROM recipe
            WHERE {where_clause}
            ORDER BY rating DESC
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(limit_query, params + [per_page, offset])
        rows = cursor.fetchall()
        
        # Apply calories filter in Python (since calories is in JSON)
        filtered_recipes = []
        for row in rows:
            recipe_dict = dict(row)
            
            # Apply calories filter if specified
            if max_calories is not None:
                calories = extract_calories(recipe_dict.get("nutrients", ""))
                if calories is not None and calories > max_calories:
                    continue
            
            recipe_dict["nutrients"] = parse_nutrients(recipe_dict.get("nutrients", ""))
            filtered_recipes.append(RecipeResponse(**recipe_dict))
        
        conn.close()
        
        # Recalculate total after calories filter
        if max_calories is not None:
            total_count = len(filtered_recipes)
            # Re-paginate after filtering
            start_idx = offset
            end_idx = offset + per_page
            filtered_recipes = filtered_recipes[start_idx:end_idx]
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
        
        pagination_info = {
            "page": page,
            "per_page": per_page,
            "total_recipes": total_count,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
        
        return {
            "success": True,
            "data": filtered_recipes,
            "pagination": pagination_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Health Check Endpoint ====================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Recipe API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check with database connectivity."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recipe count
        cursor.execute("SELECT COUNT(*) as count FROM recipe")
        recipe_count = cursor.fetchone()["count"]
        
        # Get average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM recipe WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()["avg_rating"]
        
        # Get average time
        cursor.execute("SELECT AVG(total_time) as avg_time FROM recipe WHERE total_time IS NOT NULL")
        avg_time = cursor.fetchone()["avg_time"]
        
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_recipes": recipe_count,
            "avg_rating": round(avg_rating, 2) if avg_rating else 0,
            "avg_time": round(avg_time, 0) if avg_time else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ==================== New Endpoint for Frontend Stats ====================

@app.get("/api/stats")
async def get_stats():
    """Get database statistics for frontend."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recipe count
        cursor.execute("SELECT COUNT(*) as total FROM recipe")
        total_count = cursor.fetchone()["total"]
        
        # Get average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM recipe WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()["avg_rating"]
        
        # Get average total time
        cursor.execute("SELECT AVG(total_time) as avg_time FROM recipe WHERE total_time IS NOT NULL")
        avg_time = cursor.fetchone()["avg_time"]
        
        conn.close()
        
        return {
            "success": True,
            "total_recipes": total_count,
            "avg_rating": round(avg_rating, 2) if avg_rating else 0,
            "avg_time": round(avg_time, 0) if avg_time else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Run the application ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        
    )