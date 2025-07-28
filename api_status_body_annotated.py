from enum import Enum
from fastapi import FastAPI, Query, Path, Body, status, Response
from pydantic import BaseModel, Field
from typing import Annotated, Any
from random import random

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
async def add_movie(movie : MovieIn) -> Any:
    
    new_movie_id = max(movies.keys()) + 1 if movies else 1
    movies[new_movie_id] = movie.dict()
    return {"id" : new_movie_id, **movies[new_movie_id]}

@app.get('/movies/{movie_id}', status_code=status.HTTP_200_OK)
async def get_movie(movie_id : Annotated[int, Path(ge=1)]):
    
    movie = movies.get(movie_id)
    if movie:    
        return {"id" : movie_id, **movie[movie_id]}
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
@app.get('/movies/', response_model=list[Movie])
async def filter_movies(min_rating : Annotated[float | None, Query(ge=0, le=10.0)] = None, max_year : int | None = None) -> Any:
    
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
async def get_top_rated(limit : Annotated[int, Query(ge=1, lt=10)] = 3) -> Any:

    sorted_movies = sorted(movies.items(), key=lambda item: item[1]['rating'], reverse=True)
    
    top_list = []
    for movie_id, m in sorted_movies[:limit]:
        top_list.append({"id" : movie_id, **m})
    return top_list