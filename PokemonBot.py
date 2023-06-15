import random
import pypokedex
import tweepy
import schedule
import time
import requests
import os
import cv2
import sys
from decouple import config

api_key = config('API_KEY')
api_secret = config('API_SECRET')

bearer_token = config('BEARER_TOKEN')

access_token = config('ACCESS_TOKEN')
access_token_secret = config('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuth1UserHandler(
    api_key,
    api_secret,
    access_token,
    access_token_secret
)

#API V1.1 (Para subir fotos)
api = tweepy.API(auth)

#API V2 (Para subir el tweet)
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

def leer_fichero_as_list(fichero):
    with open(fichero, "r") as f:
        lineas = [linea.split(",") for linea in f]
    return lineas

def escribir_fichero(fichero, id, nombre, tipos, peso, altura, imagenNormal, imagenShiny):
    with open(fichero, "a") as f:
        f.write(str(id)+","+nombre+","+str(tipos)+","+str(peso/10)+","+str(altura/10)+","+imagenNormal+","+imagenShiny+"\n")
        f.close()

def escribir_fichero_vistos(fichero, id, nombre, tipos, peso, altura, imagenNormal, imagenShiny):
    with open(fichero, "a") as f:
        f.write(str(id)+","+nombre+","+tipos+","+str(peso)+","+str(altura)+","+imagenNormal+","+imagenShiny)
        f.close()

def elegir_pokemon(listaPokemon, listaPokemonVistos):
    random.shuffle(listaPokemon)
    for pokemon in listaPokemon:
        if pokemon not in listaPokemonVistos:
            break
    listaPokemonVistos.append(pokemon)
    escribir_fichero_vistos("PokemonVistos.txt", pokemon[0], pokemon[1], pokemon[2], pokemon[3], pokemon[4], pokemon[5], pokemon[6])
    return pokemon

def cargarPokemon(id, fichero="Pokemon.txt"):
    #Hacer una llamada a la api para obtener todos los pokemon hasta que llegue un id que devuelva error
    while True:
        try:
            pokemon = pypokedex.get(dex=id)
            imagen = pokemon.sprites.front.get("default")
            imagenShiny = pokemon.sprites.front.get("shiny")
            if(imagen is not None and imagenShiny is not None):
                tipos=str(pokemon.types)
                characters = "'[]"
                for x in range(len(characters)):
                    tipos = tipos.replace(characters[x],"")
                tipos = tipos.replace(",",";")
                nombre = limpiar_nombre(pokemon.name)
                escribir_fichero(fichero,pokemon.dex,nombre,tipos,pokemon.weight,pokemon.height,imagen,imagenShiny)
            else:
                break
            id += 1
        except:
            break

def limpiar_nombre(nombre):
    nombres=["ho-oh","porygon-z","jangmo-o","hakamo-o","kommo-o"]
    if("-" in nombre):
        if(nombre not in nombres):
            nombreLimpio=nombre.split("-")[0]
            return nombreLimpio
        else:
            return nombre
    else:
        return nombre

def descargar_imagen(url, nombre):
    img_data = requests.get(url).content
    jpg=nombre+".jpg"
    with open(jpg, 'wb') as handler:
        handler.write(img_data)

def elimnar_fotos():
    try:
        os.remove("Normal.jpg")
    except:
        pass
    try:
        os.remove("Shiny.jpg")
    except:
        pass

def redimensionar_imagen(imagen, ancho, alto):
    res=cv2.resize(imagen,(ancho,alto))
    cv2.imwrite("Shiny.jpg",res)

def tweet(pokemon):
    id=pokemon[0]
    nombre=pokemon[1].title()
    tipos=pokemon[2].title().replace(";",", ")
    peso=pokemon[3]
    altura=pokemon[4]
    foto=pokemon[5]
    fotoShiny=pokemon[6].replace("\n","")
    texto="The pokemon of the day is "+nombre+"\n"+"Pokedex nº: "+str(id)+"\n"+"Types: "+tipos+"\n"+"Weight: "+str(peso)+" Kg"+"\n"+ "Height: "+str(altura)+" m"

    descargar_imagen(foto, "Normal")
    descargar_imagen(fotoShiny, "Shiny")
    media1 = api.media_upload("Normal.jpg")
    media2 = api.media_upload("Shiny.jpg")

    client.create_tweet(text=texto, media_ids=[media1.media_id_string, media2.media_id_string])
    elimnar_fotos()

def pokemon_tweet():
    inicio = time.time()
    listaPokemon = leer_fichero_as_list("Pokemon.txt")
    listaPokemonVistos = leer_fichero_as_list("PokemonVistos.txt")
    if(len(listaPokemonVistos) != len(listaPokemon)):
        pokemon=elegir_pokemon(listaPokemon, listaPokemonVistos)
        tweet(pokemon)
        numeroPokemon=len(listaPokemon)
        cargarPokemon(numeroPokemon+1)
        print("Pokemon vistos ",len(listaPokemonVistos))
    time.sleep(1)
    fin = time.time()
    print("Tiempo de ejecución ", fin-inicio)
    sys.exit()

def main():
    #id=1
    #cargarPokemon(id)

    schedule.every().day.at('20:00').do(pokemon_tweet)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()