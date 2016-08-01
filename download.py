# -*- coding: utf-8 -*-
import lxml.html
import requests
import re
from bs4 import BeautifulSoup
import sys
import os


# método para crear un directorio con el nombre de la serie.
def crear_directorio(ruta):
    try:
        os.makedirs(ruta)
    except OSError:
        pass
    # si no podemos crear la ruta dejamos que pase
    # si la operación resulto con éxito nos cambiamos al directorio
    os.chdir(ruta)

def main30():
    # constantes y variables
    hdtv = False
    hdtv_string = "hdtv"
    hd_ready = False
    hd_ready_string = "720"
    hd_extras = ""
    mTemporada = 0
    temps = []
    all_caps = []
    caps = []
    caps_codes = []
    url_pre = 'http://www.series-torrents.com'
    prefix = 'http://www.series-torrents.com/get_torrent.php?id='
    all_series_list = 'http://www.series-torrents.com/todas-las-series'
    search_part_one = 'http://www.series-torrents.com/buscar?searchword='
    search_part_two = '&ordering=&searchphrase=all&limit=100'
    str2 = 'get_torrent.php?id='

    # capturamos los argumentos de entrada
    arguments = sys.argv[1:]
    # comprobamos si existe petición HDReady o FullHD
    # activamos el centinela correspondiente y lo eliminamos de argumentos
    # [-1] es el último elemento de la lista.
    # .pop() elimina el último elemento de la lista.
    if arguments[-1] == 'fullhd':
        hd_extras = "hdtv"
        arguments.pop()
    elif arguments[-1] == '720p':
        hd_extras = "720p"
        arguments.pop()

    if arguments[-1].isdigit():
        mTemporada = arguments[-1]
        arguments.pop()

    serie_name = ""
    for word in arguments:
        # serie_name es el nombre de la serie que vamos a descargar
        serie_name += word + "-"
    # serie_name contendrá el nombre completo de la serie
    # eliminamos el último "-" -> por ejemplo: the-flah- ==> the-flash
    serie_name = serie_name[:len(serie_name) - 1]
    # si no hay opción HD activa, colocaremos el nombre de la propia serie
    # en la variable hd_extras para la posterior búsqueda.
    if not hd_extras:
        hd_extras = serie_name
    # capturamos todas las series de series-torrents.com
    result_one = requests.get(all_series_list)
    soup_one = BeautifulSoup(result_one.text, 'lxml')

    # y de entre todas las series, buscamos la que nos interesa descargar
    list_one = soup_one.find_all('a')
    for link in list_one:
        if link.has_attr('href'):
            link_detail = link['href']
            if link_detail.find(serie_name) != -1 :  # serie_name = "the-flash"
            # Si no hemos especificado temporada alguna ( mTem == 0) y si coincide
            # unicamente con la que hemos especificado, la añadimos para descarga.
                if mTemporada == 0 or mTemporada == link_detail[len(link_detail) - 1:len(link_detail)]:
                    temps.append(link_detail)  # temps contiene las temporadas de la serie a descargar
                    print "Temporada " + link_detail[len(link_detail) - 1:len(link_detail)] + " OK."
    # print temps

    # las temporadas se dividen en varias páginas HTML
    for new_temp in temps:
        sentinel = True
        value = 0
        while sentinel:
            caps = []
            # nueva página
            my_url = new_temp + '?start=' + str(value)
            # print my_url  # descomentar para ver la URL de descarga de varios caps
            result_one = requests.get(my_url)
            soup_one = BeautifulSoup(result_one.text, 'lxml')
            # capturamos todos los enlaces de cada capítulo
            list_one = soup_one.find_all('a')

            for link in list_one:
                if link.has_attr('href'):
                    link_detail = link['href']
                    if link_detail[0: 10] == '/torrents/' and link_detail.find(serie_name) != -1 and link_detail.find(hd_extras) != -1 and link_detail[10: 15] not in caps_codes:  # serie_name = "the-flash"
                        caps_codes.append(link_detail[10: 15])
                        # para no repetir capítulos, en caps_codes guardaremos el ID y comprobaremos que no se repita.
                        caps.append(link_detail)
            all_caps.extend(caps)  # all_caps contiene todos los enlaces a páginas de descargas de los torrents

            # si la página no contiene más capítulos, paramos de buscar enlaces.
            if not caps:
                sentinel = False
            value += 10
        # print all_caps  # descomentar para ver todos los caps que se descargarán.
    # creamos una carpeta con el nombre de la serie y guardamos en ella los archivos .torrent
    crear_directorio(serie_name)
    # para cada enlace torrent, componemos la URL completa de descarga.
    for my_cap in all_caps:
        # print my_cap[10:]
        print "descargando... " + my_cap[16:]
        my_full_cap = url_pre + my_cap
        result_cap = requests.get(my_full_cap)
        soup = BeautifulSoup(result_cap.text, 'lxml')
        columns = soup.find_all('a', attrs = {'rel' : 'nofollow'})
        # y extraemos el enlace torrent que deseamos
        url2 = url_pre + columns[1]['href']
        # y guardamos en id_torrent la URL completa de donde está el archivo .torrent
        # que nos interesa descargar ;)
        ses = requests.get(url2)
        soup2 = BeautifulSoup(ses.text, 'lxml')
        columns2 = soup2.find_all('script')
        start = columns2[8].text.find(str2)
        id_torrent = columns2[8].text[int(start) +19: int(start)+79]

        # y descargamos al ordenador cada archivo .torrent
        res = requests.get(prefix + id_torrent)
        res.raise_for_status()
        playFile = open(my_cap[16:] + '.torrent', 'wb')
        for chunk in res.iter_content(100000):
            playFile.write(chunk)
        playFile.close()

# inicio
if __name__ == "__main__":
    main30()
