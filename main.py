import pandas as pd
import numpy as np
import re
import ast

from fastapi import FastAPI

app = FastAPI()

@app.get('/peliculas_idioma')
def peliculas_idioma(Idioma):
    ## Abro el archivo y creo una lista con los valores de los idiomas
    DF = pd.read_csv("movies_dataset_modificado.csv")
    list_lang = list(DF.spoken_languages.values)
    
    cantidad = sum(1 for item in list_lang if re.search(Idioma, str(item)))
    return {'Se produjeron la cantidad de':cantidad , 'películas en el idioma':Idioma }

@app.get('/peliculas_duracion')
def peliculas_duracion(Pelicula):
    DF = pd.read_csv("movies_dataset_modificado.csv")
    DF_title = DF.set_index("title")
    
    duracion = DF_title.loc[Pelicula , "runtime"].item()
    year = DF_title.loc[Pelicula , "release_year"].item()
    return {'La pelicula': Pelicula, 'tiene una duración de': duracion , 'Año': year}

@app.get('/franquicia')

def franquicia(Franquicia):
    ## Abro el archivo y aplico groupby para tener los df de donde tomare la info que me solicitan
    DF = pd.read_csv("movies_dataset_modificado.csv")
    DF_SUM = DF.groupby(["belongs_to_collection"]).sum()
    DF_PROM = DF.groupby(["belongs_to_collection"]).mean()
    DF_COUNT = DF.groupby(["belongs_to_collection"]).count()
    lista_collection = list(DF.belongs_to_collection)
    
    ## Verifico que el valor sea valido     
    ## Ubico los valores de la franquicia a traves de la funcion loc

    if Franquicia not in lista_collection:
        return {'Franquicia': "Valor incorrecto", 'cantidad': "Error", 'ganancia_total': "Error", 'ganancia_promedio': "Error"}

    if Franquicia not in DF_COUNT.index:
        return {'Franquicia': "Valor incorrecto", 'cantidad': "Error", 'ganancia_total': "Error", 'ganancia_promedio': "Error"}

    resp_cant = DF_COUNT.loc[Franquicia, 'revenue'].item()
    resp_gan_tot = DF_SUM.loc[Franquicia, 'revenue'].item()
    resp_gan_prom = DF_PROM.loc[Franquicia, 'revenue'].item()

    return {'La franquicia': Franquicia, 'posee la siguiente cantidad de peliculas': resp_cant, 'con ganancia total': resp_gan_tot, 'y una ganancia promedio': resp_gan_prom}

    

@app.get('/peliculas_pais')

def peliculas_pais(Pais):
    ## Abro el archivo y genero una lista con los valores de los paises
    DF = pd.read_csv("movies_dataset_modificado.csv")
    list_countries = list(DF.production_countries.values)
    
    ## Cuento cada vez que se nombra un país ya que la list_countries es una lista de listas, de esta forma puedo contar al país aún cuando aparece en una lista con otro país
    cantidad = sum(1 for item in list_countries if re.search(Pais, str(item)))
    return {'Se produjeron la siguiente cantidad':cantidad , 'de películas en el país':Pais }


@app.get('/productoras_exitosas')

def productoras_exitosas(Productora):
    DF = pd.read_csv("movies_dataset_modificado.csv")
    list_companies = list(DF.production_companies.values)
    
    # Convertir la columna 'production_companies' en una lista de listas de strings
    DF['production_companies'] = DF['production_companies'].apply(ast.literal_eval)
    
    # Filtrar el DataFrame por la productora especificada
    companie_movies = DF[DF['production_companies'].apply(lambda x: any(Productora.lower() in item.lower() for item in x))]
    
    
    
    sum_revenue = companie_movies['revenue'].sum()
    cantidad = sum(1 for item in list_companies if re.search(Productora, str(item)))
    
    return {'La productora': Productora, 'realizó peliculas por la cantidad de': cantidad, 'revenue total': sum_revenue}

@app.get('/get_director')

def get_director(nombre_director):
    DF = pd.read_csv("movies_dataset_modificado.csv")

    director_movies = DF[DF['crew'] == nombre_director]
    sum_return = director_movies['return'].sum()

    movies_data = director_movies[['title', 'release_date', 'budget', 'revenue', 'return']].values.tolist()

    return {'Director': nombre_director, 'Retorno total': sum_return, 'Pelicula, fecha de lanzamiento, costo, retorno individual, ganancia': movies_data}

@app.get('/recomendacion')

def recomendacion(titulo):
    DF = pd.read_csv("movies_dataset_modificado.csv")
    Recomendaciones = []
    other_movies = DF[DF['title'] == titulo]

    belongs_to_collection_value = other_movies['belongs_to_collection'].values[0]
    max_vote_average_movie = DF[(DF['belongs_to_collection'] == belongs_to_collection_value)].sort_values('vote_average', ascending=False).iloc[0]

    if max_vote_average_movie['title'] == titulo:
        next_movie = DF[(DF['belongs_to_collection'] == belongs_to_collection_value) & (DF['title'] != titulo)].sort_values('vote_average', ascending=False).iloc[0]
        Recomendaciones.append(next_movie['title'])
    else:
        Recomendaciones.append(max_vote_average_movie['title'])

    genres_value = other_movies['genres'].values[0]
    max_vote_average_genre_movie = DF[(DF['genres'] == genres_value)].sort_values('vote_average', ascending=False).iloc[0]

    if max_vote_average_genre_movie['title'] != titulo:
        Recomendaciones.append(max_vote_average_genre_movie['title'])

    crew_value = other_movies['crew'].values[0]
    max_vote_average_crew_movie = DF[(DF['crew'] == crew_value)].sort_values('vote_average', ascending=False).iloc[0]

    if max_vote_average_crew_movie['title'] != titulo:
        Recomendaciones.append(max_vote_average_crew_movie['title'])

    production_companies_value = other_movies['production_companies'].values[0]
    max_vote_average_production_companies_movie = DF[(DF['production_companies'] == production_companies_value)].sort_values('vote_average', ascending=False).iloc[0]

    if max_vote_average_production_companies_movie['title'] != titulo:
        Recomendaciones.append(max_vote_average_production_companies_movie['title'])

    production_countries_value = other_movies['production_countries'].values[0]
    max_vote_average_production_countries_movie = DF[(DF['production_countries'] == production_countries_value)].sort_values('vote_average', ascending=False).iloc[0]

    if max_vote_average_production_countries_movie['title'] != titulo:
        Recomendaciones.append(max_vote_average_production_countries_movie['title'])

    num_recommendations = len(Recomendaciones)
    while num_recommendations < 5:
        random_movie = DF.sample(n=1)
        random_title = random_movie['title'].values[0]
        if random_title not in Recomendaciones:
            Recomendaciones.append(random_title)
            num_recommendations += 1

    return {'Pelicula': titulo, 'Sugerencias': Recomendaciones}

