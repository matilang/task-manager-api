from enum import Enum
from fastapi import FastAPI, Query, Path, Body, status, Response
from pydantic import BaseModel, Field
from typing import Annotated, Any
from random import random

"""
Task: Simple API for Managing Movies

Description:
Create an API that stores a list of movies in memory.

Each movie has:
- id: int
- title: str
- year: int
- rating: float (0.0–10.0)

Initial data:
movies = []

Endpoints to implement:

1. POST /movies/ – Add a new movie
   Body:
      MovieIn(BaseModel) with: title, year, rating
   Validations:
      year: 1900 <= year <= 2100
      rating: 0.0 <= rating <= 10.0
   Behavior:
      - API assigns id automatically
      - Return 201 Created
      - response_model = Movie (Movie includes id)

2. GET /movies/{movie_id}
   - Path parameter: movie_id >= 1
   - Return 200 OK with movie if found
   - Return 404 if not found

3. GET /movies/
   - Optional query parameters:
       min_rating (0.0–10.0)
       max_year
   - Filter movies if parameters are provided
   - Return list of movies (response_model = list[Movie])

4. DELETE /movies/{movie_id}
   - If exists: remove and return 204 No Content
   - Else: return 404 Not Found

5. GET /movies/top/
   - Query: limit (default 3, 1 <= limit <= 10)
   - Sort by rating descending
   - Return top `limit` movies

Additional requirements:
- Use a separate MovieOut for responses
- Inside functions, use object attributes (movie.title) instead of class-level references
- Handle status codes explicitly: 201, 204, 404, 400
"""

app = FastAPI()

movies = {
    1: {"title": "Matrix", "year": 1999, "rating": 8.7},
    2: {"title": "Inception", "year": 2010, "rating": 9.0},
}   

class Movie(BaseModel):
    title : str
    year : int = Field(gt=1900, lt=2100)
    rating : float = Field(gt=0.0, lt=10.0)

class MovieIn(Movie):
    pass

class MovieOut(Movie):
    id : int
    
@app.post('/movies/', response_model=MovieOut, status_code=status.HTTP_201_CREATED)
async def add_movie(movie : MovieIn):
    
    new_movie_id = max(movies.keys()) + 1 if movies else 1
    movies[new_movie_id] = movie.dict()
    return {"id" : new_movie_id, **movies[new_movie_id]}

@app.get('/movies/{movie_id}', status_code=status.HTTP_200_OK)
async def get_movie(movie_id : Annotated[int, Path(ge=1)]):
    
    movie = movies.get(movie_id)
    if movie:    
        return {"id" : movie_id, **movie}
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
@app.get('/movies/', response_model=list[Movie])
async def filter_movies(min_rating : Annotated[float | None, Query(ge=0, le=10.0)] = None, max_year : int | None = None):
    
    movie_list = []
    for movie_id , m in movies.items():
        if (min_rating is None or m['rating'] >= min_rating) and (max_year is None or m['year'] <= max_year):
            movie_list.append({"id" : movie_id, **m})
                
    return movie_list

@app.delete('/movies/{movie_id}')
async def delete_movie(movie_id : Annotated[int, Path()]):
    
    deleted_movie = movies.pop(movie_id, None)
    if deleted_movie is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get('/movies/top/', response_model=list[Movie])
async def get_top_rated(limit : Annotated[int, Query(ge=1, lt=10)] = 3):

    sorted_movies = sorted(movies.items(), key=lambda item: item[1]['rating'], reverse=True)
    
    top_list = []
    for movie_id, m in sorted_movies[:limit]:
        top_list.append({"id" : movie_id, **m})
    return top_list