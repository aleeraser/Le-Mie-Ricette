# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from flask import Flask, render_template, request, redirect, send_file, send_from_directory
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from weasyprint import HTML, CSS

reload(sys)
sys.setdefaultencoding('utf8')

UPLOAD_FOLDER = './static/img/uploaded'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'bmp', 'gif'])

app = Flask(__name__)
app.secret_key = '\xeb9\xb9}_\x83\xcb\xafp\xf1P\xcb@\x83\x0b\xb4L"\xc9\x91\xbd\xf0\xaa\xac'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL configuration
mysql = MySQL()

if "/alessandro/" or "/pi/" in os.path.dirname(os.path.abspath(__file__)):
    app.config["MYSQL_USER"] = "chef"
    app.config["MYSQL_PASSWORD"] = "ricette&preparazioni"
    app.config["MYSQL_DB"] = "ricette_db"
    app.config["MYSQL_HOST"] = "localhost"
else:
    app.config["MYSQL_USER"] = "my1606"
    app.config["MYSQL_PASSWORD"] = "azaitaiv"
    app.config["MYSQL_DB"] = "my1606"
    app.config["MYSQL_HOST"] = "golem"

app.config["MYSQL_USE_UNICODE"] = True

site_name = "Le mie ricette"

mysql.init_app(app)

page_head = """<meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1.0 user-scalable=0' />
  <title>""" + site_name + """</title>

  <!-- Favicon declarations -->
  <link rel='apple-touch-icon' sizes='57x57' href='/static/img/favicons_old/apple-touch-icon-57x57.png'>
  <link rel='apple-touch-icon' sizes='60x60' href='/static/img/favicons_old/apple-touch-icon-60x60.png'>
  <link rel='apple-touch-icon' sizes='72x72' href='/static/img/favicons_old/apple-touch-icon-72x72.png'>
  <link rel='apple-touch-icon' sizes='76x76' href='/static/img/favicons_old/apple-touch-icon-76x76.png'>
  <link rel='apple-touch-icon' sizes='114x114' href='/static/img/favicons_old/apple-touch-icon-114x114.png'>
  <link rel='apple-touch-icon' sizes='120x120' href='/static/img/favicons_old/apple-touch-icon-120x120.png'>
  <link rel='apple-touch-icon' sizes='144x144' href='/static/img/favicons_old/apple-touch-icon-144x144.png'>
  <link rel='apple-touch-icon' sizes='152x152' href='/static/img/favicons_old/apple-touch-icon-152x152.png'>
  <link rel='apple-touch-icon' sizes='180x180' href='/static/img/favicons_old/apple-touch-icon-180x180.png'>
  <link rel='icon' type='image/png' sizes='32x32' href='/static/img/favicons_old/favicon-32x32.png'>
  <link rel='icon' type='image/png' sizes='194x194' href='/static/img/favicons_old/favicon-194x194.png'>
  <link rel='icon' type='image/png' sizes='192x192' href='/static/img/favicons_old/android-chrome-192x192.png'>
  <link rel='icon' type='image/png' sizes='16x16' href='/static/img/favicons_old/favicon-16x16.png'>
  <link rel='manifest' href='/static/img/favicons_old/manifest.json'>
  <link rel='mask-icon' href='/static/img/favicons_old/safari-pinned-tab.svg' color='#da532c'>
  <!-- <link rel='shortcut icon' href='/static/img/favicons_old/favicon.ico'> -->
  <!-- <link rel='shortcut icon' href='{{ url_for('static', filename='img/favicons_old/favicon.ico') }}'> -->
  <meta name='msapplication-TileColor' content='#da532c'>
  <meta name='msapplication-TileImage' content='/static/img/favicons_old/mstile-144x144.png'>
  <meta name='msapplication-config' content='/static/img/favicons_old/browserconfig.xml'>
  <meta name='theme-color' content='#6e3603'>

  <!-- CSS -->
  <link href='/static/css/googleapis_material_icons.css' rel='stylesheet'>
  <link href='/static/css/materialize.custom.css' type='text/css' rel='stylesheet' media='screen,projection' />
  <link href='/static/css/style.css' type='text/css' rel='stylesheet' media='screen,projection' />

  <!-- Materialize icons include -->
  <!-- <link href='/static/css/googleapis_material_icons.css' rel='stylesheet'> -->

  <!-- jQuery -->
  <script src='/static/js/jquery-3.0.0.min.js'></script>

  <!-- jQuery UI -->
  <script src='/static/js/jquery_ui_1.12.1.min.js'></script>
  
  <!-- jQuery validate -->
  <script src='/static/js/jquery_validate_1.15.0.min.js'></script>"""

options = {
    "home": "<li><a href='/'>Home</a></li>",
    "ricette": "<li><a href='/ricette'>Ricette</a></li>",
    "preparazioni": "<li><a href='/preparazioni'>Preparazioni</a></li>",
    "ingredienti": "<li><a href='/ingredienti'>Ingredienti</a></li>",
    "metodi": "<li><a href='/metodi'>Metodi</a></li>",
    "menu": "<li><a href='/menu'>Menu</a></li>",
    "ricerca": "<li><a href='/cerca'><i class='material-icons'>search</i></a></li>"
}

menu_options = options["home"] + options["ricette"] + options["preparazioni"] + \
        options["ingredienti"] + options["metodi"] + \
        options["menu"] + options["ricerca"]

navbar = "<div id='logo-wrapper'><a id='logo-container' href='/' class='brand-logo'><img src='../static/img/logo.png' alt='logo'></a></div>"

footer = "<footer class='page-footer orange'><div class='container'><div class='col s12'><p class='grey-text text-lighten-4'>'" + site_name + \
    "' è stato sviluppato da <a href='mailto:alezini94@hotmail.it?Subject=In merito al sito: \"" + site_name + "\"' target='_top'>Alessandro Zini</a>.<br/>&copy; 2017 - Alessandro Zini</p></div></div></footer>"

# UTILITY
months_map = {
    1 : "Gennaio",
    2 : "Febbraio",
    3 : "Marzo",
    4 : "Aprile",
    5 : "Maggio",
    6 : "Giugno",
    7 : "Luglio",
    8 : "Agosto",
    9 : "Settembre",
    10 : "Ottobre",
    11 : "Novembre",
    12 : "Dicembre"
}
months_map_inverse = {
    "Gennaio" : 1,
    "Febbraio" : 2,
    "Marzo" : 3,
    "Aprile" : 4,
    "Maggio" : 5,
    "Giugno" : 6,
    "Luglio" : 7,
    "Agosto" : 8,
    "Settembre" : 9,
    "Ottobre" : 10,
    "Novembre" : 11,
    "Dicembre" : 12
}
def dish_type_map(v, javascriptFormat=False):
    if v == 1:
        if javascriptFormat:
            return "entree"
        return "Entrée"
    elif v == 2:
        if javascriptFormat:
            return "antipasti"
        return "Antipasto"
    elif v == 3:
        if javascriptFormat:
            return "primi"
        return "Primo"
    elif v == 4:
        if javascriptFormat:
            return "secondi"
        return "Secondo"
    elif v == 5:
        if javascriptFormat:
            return "dessert"
        return "Dessert"
def difficulty_map(v):
    if v == 1:
        return "Elementare"
    elif v == 2:
        return "Semplice"
    elif v == 3:
        return "Medio"
    elif v == 4:
        return "Avanzato"
    elif v == 5:
        return "Esperto"
def unit_map(v):
    if v == 1:
        return "gr"
    elif v == 2:
        return "kg"
    elif v == 3:
        return "lt"
    elif v == 4:
        return "ml"
    elif v == 5:
        return "q.b."
    elif v == 6:
        return "pezzi"
def normalize(s):
    return s.replace(' ', '_').replace('\'', '__single_quote__').replace('"', '__double_quotes__')
def reverse_normalize(s):
    return s.replace('__single_quote__', '\'').replace('__double_quotes__', '"').replace('_', ' ')
def upper_first(s):
    ret = ""
    try:
        ret = s[0].upper() + s[1:]
    except IndexError:
        pass

    return ret
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# LISTE
@app.route("/ricette", methods=["GET"])
def ricette():
    cur = mysql.connection.cursor()

    # Get stored recipes
    cur.execute("SELECT nome FROM ricetta;")
    recipes = cur.fetchall()
    if cur.rowcount == 0:
        recipes = None

    recipe_names = ""
    saved_recipes = "<div class='row mobile_row center'><br/><div class='container'><p>Non hai ancora inserito alcuna ricetta! <a href='/aggiungi_ricetta'>Inserisci una nuova ricetta</a>.</p></div></div>"
    if recipes is not None:
        for name in recipes:
            recipe_names += "<a href='/ricette/" + normalize(name[0]) + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + name[0] + "</a>"
        saved_recipes = "<div class='collection'>" + recipe_names + "</div>"

    return template_lista_elementi("Ricette salvate", "aggiungi_ricetta", saved_recipes, menu_options)
@app.route("/preparazioni", methods=["GET"])
def preparazioni():
    cur = mysql.connection.cursor()

    # Get stored preparations
    cur.execute("SELECT nome FROM preparazione;")
    preparations = cur.fetchall()
    if cur.rowcount == 0:
        preparations = None

    preparations_names = ""
    saved_preparations = "<div class='row mobile_row center'><br/><div class='container'><p>Non hai ancora inserito alcuna preparazione! <a href='/aggiungi_preparazione'>Inserisci una nuova preparazione</a>.</p></div></div>"
    if preparations is not None:
        for name in preparations:
            preparations_names += "<a href='/preparazioni/" + normalize(name[0]) + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + name[0] + "</a>"
        saved_preparations = "<div class='collection'>" + preparations_names + "</div>"

    return template_lista_elementi("Preparazioni salvate", "aggiungi_preparazione", saved_preparations, menu_options)
@app.route("/ingredienti", methods=["GET"])
def ingredienti():
    cur = mysql.connection.cursor()

    # Get stored ingredients
    cur.execute("SELECT nome FROM ingrediente;")
    ingredients = cur.fetchall()
    if cur.rowcount == 0:
        ingredients = None

    ingredients_names = ""
    saved_ingredients = "<div class='row mobile_row center'><br/><div class='container'><p>Non hai ancora inserito alcun ingrediente! <a href='/aggiungi_ingrediente'>Inserisci un nuovo ingrediente</a>.</p></div></div>"
    if ingredients is not None:
        for name in ingredients:
            ingredients_names += "<a href='/ingredienti/" + normalize(name[0]) + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + name[0] + "</a>"
        saved_ingredients = "<div class='collection'>" + ingredients_names + "</div>"

    return template_lista_elementi("Ingredienti salvati", "aggiungi_ingrediente", saved_ingredients, menu_options)
@app.route("/metodi", methods=["GET"])
def metodi():
    cur = mysql.connection.cursor()

    # Get stored methods
    cur.execute("SELECT nome FROM metodo;")
    methods = cur.fetchall()
    if cur.rowcount == 0:
        methods = None

    methods_names = ""
    saved_methods = "<div class='row mobile_row center'><br/><div class='container'><p>Non hai ancora inserito alcun metodo! <a href='/aggiungi_metodo'>Inserisci un nuovo metodo</a>.</p></div></div>"
    if methods is not None:
        for name in methods:
            methods_names += "<a href='/metodi/" + normalize(name[0]) + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + name[0] + "</a>"
        saved_methods = "<div class='collection'>" + methods_names + "</div>"

    return template_lista_elementi("Metodi salvati", "aggiungi_metodo", saved_methods, menu_options)
@app.route("/menu", methods=["GET"])
def menu():
    cur = mysql.connection.cursor()

    # Get stored menu
    cur.execute("SELECT DISTINCT nome FROM menu_ricetta;")
    menues = cur.fetchall()

    if cur.rowcount == 0:
        menues = None

    menu_names = ""
    saved_menu = "<div class='row mobile_row center'><br/><div class='container'><p>Non hai ancora inserito alcun menu! <a href='/aggiungi_menu'>Inserisci un nuovo menu</a>.</p></div></div>"
    if menues is not None:
        for name in menues:
            menu_names += "<a href='/menu/" + normalize(name[0]) + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + name[0].split("-")[0] + " " + months_map[int(name[0].split("-")[1])] + " " + name[0].split("-")[2] + "</a>"
        saved_menu = "<div class='collection'>" + menu_names + "</div>"

    return template_lista_elementi("Menu salvati", "aggiungi_menu", saved_menu, menu_options)
def template_lista_elementi(element_category, element_new_link, element_list, menu_opt):
    return render_template("template_lista_elementi.html", page_head=page_head, navbar=navbar, menu_options=menu_opt, element_category=element_category, element_new_link=element_new_link, element_list=element_list, footer=footer)





#  RICETTE
@app.route("/aggiungi_ricetta", methods=["GET", "POST"])
def aggiungi_ricetta():
    if request.method == "GET":
        # collects saved methods
        cur = mysql.connection.cursor()
        cur.execute("SELECT nome FROM metodo;")
        methods = cur.fetchall()

        methods_names = ""
        saved_methods = ""
        if methods is not None:
            for name in methods:
                methods_names += "<option value='" + normalize(name[0]) + "'>" + name[0] + "</option>"
            saved_methods = methods_names

        # collects saved ingredients
        cur = mysql.connection.cursor()
        cur.execute("SELECT nome FROM ingrediente;")
        ingredients = cur.fetchall()

        ingredients_names = ""
        saved_ingredients = ""
        if ingredients is not None:
            for name in ingredients:
                ingredients_names += "<option value='" + normalize(name[0]) + "'>" + name[0] + "</option>"
            # ingredients_names += "<option value='_nuovo_'>+ SERVER...</option>"
            saved_ingredients = ingredients_names

        return render_template("aggiungi_ricetta.html", page_head=page_head, navbar=navbar, menu_options=menu_options, saved_methods=saved_methods, saved_ingredients=saved_ingredients, footer=footer)

    name = upper_first(request.form["nome"])
    dish_type = request.form["tipo"]
    people = request.form["persone"]
    duration = request.form["durata"]
    difficulty = request.form["difficolta"]
    score = request.form["punteggio"]
    method = reverse_normalize(request.form["metodo"])
    description = upper_first(request.form["descrizione"])

    # invalid values
    if name == "" or description == "" or len(name) > 100 or len(description) > 65535:
        return "1"

    if nel_database(name, "ricetta") == "1":        # recipe is already present in database
        return "0"

    picture_path = None

    picture = request.files["foto"]
    # if picture and allowed_file(normalize(name) + "." + picture.filename.split(".")[-1]):
    if picture:
        filename = secure_filename(normalize(name) + "." + picture.filename.split(".")[-1])
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'] + "/ricette", filename)
        picture.save(picture_path)

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO ricetta (nome, tipo, persone, durata, difficolta, foto, punteggio, metodo, descrizione) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", [name, dish_type, people, duration, difficulty, picture_path, score, method, description])

    # gathering dynamically added ingredients
    n = int(request.form["counter"])
    ingredient_list = []
    for i in range(0, n):
        ingredient = request.form["ingr_" + str(i + 1)]
        unit = request.form["unita_" + str(i + 1)]

        if unit_map(int(unit)) == "q.b.":
            quantity = 0
        else:
            if request.form["quantita_" + str(i + 1)] == "":
                return "2"
            quantity = request.form["quantita_" + str(i + 1)]

        if ingredient in ingredient_list:   # double ingredient, ignore it
            # return "2"
            continue

        ingredient_list.append(ingredient)
        cur.execute("INSERT INTO ricetta_ingrediente (ricetta, ingrediente, quantita, unita) VALUES (%s, %s, %s, %s);", [name, reverse_normalize(ingredient), quantity, unit])

    mysql.connection.commit()

    url = "/ricette/" + normalize(str(name))
    return url
@app.route("/ricette/cancella_<string:name>", methods=["GET"])
def cancella_ricetta(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT nome, foto FROM ricetta WHERE nome = %s;", [name])
    path = cur.fetchone()

    if path is None:
        return redirect("/errore")

    # delete from DB
    cur.execute("DELETE FROM ricetta WHERE nome = %s;", [name])
    cur.execute("DELETE FROM ricetta_ingrediente WHERE ricetta = %s;", [name])

    mysql.connection.commit()

    # delete pic from disk
    if path[1] is not None:
        if os.path.exists(str(path[1])):
            os.remove(str(path[1]))

    # delete pdf from disk
    pdf_path = "static/pdf/ricette/" + secure_filename(normalize(name) + ".pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return redirect("/ricette")
@app.route("/ricette/<string:name>", methods=["GET"])
def ricetta(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ricetta WHERE nome = %s;", [name])
    recipe = cur.fetchone()

    if recipe is None:
        return redirect("/non_presente_" + normalize(name) + "_cat:ricetta")

    dish_type = dish_type_map(int(recipe[1]))
    people = recipe[2]
    duration = recipe[3]
    difficulty = difficulty_map(int(recipe[4]))
    picture_path = recipe[5]
    score = recipe[6]
    method = recipe[7]
    description = recipe[8]

    method_url = "<a href='/metodi/" + normalize(method) + "'>" + method + "</a>"

    picture = '<div class="row mobile_row"><form class="col s12" enctype="multipart/form-data"><div class="file-field input-field col s12"><div class="btn"><span>Foto</span><input type="file" id="foto" name="foto" accept=".jpg, .jpeg, .png, .bmp, .gif"></div><div class="file-path-wrapper"><input id="foto_path" class="file-path" type="text" placeholder="Carica una foto!"></div></div></form></div>'

    if picture_path:
        picture = '<div class="row mobile-row col s12"><div class="card detail_picture"><div class="card-image"><img class="materialboxed" src="' + str(picture_path)[1:] + '" alt="' + name + '"></div></div></div>'

    cur = mysql.connection.cursor()
    cur.execute("SELECT ingrediente, quantita, unita FROM ricetta_ingrediente WHERE ricetta = %s;", [name])
    ingredients = cur.fetchall()

    tot_price = 0
    ingredient_rows = ""
    uncountable = False
    for ingredient in ingredients:
        unit = unit_map(int(ingredient[2]))
        if unit == "q.b.":
            quantity = " "
        else:
            quantity = str(ingredient[1]) + " "

            cur.execute("SELECT prezzokg FROM ingrediente where nome = %s", [ingredient[0]])
            pricekg = cur.fetchone()

            if pricekg:
                pricekg = pricekg[0]
                if unit == "gr":
                    tot_price += pricekg * (float(quantity) / 1000)
                elif unit == "kg":
                    tot_price += pricekg * float(quantity)
                elif unit == "ml":
                    tot_price += pricekg * (float(quantity) / 1000)
                elif unit == "lt":
                    tot_price += pricekg * float(quantity)
                else:
                    uncountable = True

        ingredient_rows += "<tr><td onClick='document.location.href=\"/ingredienti/" + normalize(str(ingredient[0])) + "\";'><a href='/ingredienti/" + normalize(str(ingredient[0])) + "'>" + str(ingredient[0]) + "</a></td><td onClick='document.location.href=\"/ingredienti/" + normalize(str(ingredient[0])) + "\";'><a class='quantity' href='/ingredienti/" + normalize(str(ingredient[0])) + "'>" + quantity + unit + "</td></tr>"

        # cur.execute("SELECT 1 FROM ingrediente WHERE nome = %s;", [str(ingredient[0])])
        # present = cur.fetchone()

        # if present:
        #     ingredient_rows += "<tr><td onClick='document.location.href=\"/ingredienti/" + normalize(str(ingredient[0])) + "\";'><a href='/ingredienti/" + normalize(str(ingredient[0])) + "'>" + str(ingredient[0]) + "</a></td><td onClick='document.location.href=\"/ingredienti/" + normalize(str(ingredient[0])) + "\";'><a class='quantity' href='/ingredienti/" + normalize(str(ingredient[0])) + "'>" + quantity + unit + "</td></tr>"
        # else:
        #     ingredient_rows += "<tr><td onClick='document.location.href=\"/non_presente_" + str(ingredient[0]) + "_cat:ingrediente\";'><a href='/non_presente_" + str(ingredient[0]) + "_cat:ingrediente'>" + str(ingredient[0]) + "</a></td><td onClick='document.location.href=\"/non_presente_" + str(ingredient[0]) + "_cat:ingrediente\";'><a class='quantity' href='/non_presente_" + str(ingredient[0]) + "_cat:ingrediente'>" + quantity + unit + "</td></tr>"

    integer_digits = str(tot_price).split('.')[0]
    decimal_digits = str(tot_price).split('.')[-1]
    if len(decimal_digits) > 2:
        if decimal_digits[2] >= "0" and decimal_digits[2] <= "4":
            tot_price = float(integer_digits + "." + decimal_digits[:2])
        else:
            tot_price = float(integer_digits + "." + decimal_digits[:2]) + 0.01


    tot_price = str(tot_price) + "€"
    if uncountable:
        tot_price += " + sfusi"

    delete_recipe = "/ricette/cancella_" + normalize(name)
    download_pdf = "/pdf_" + normalize(name) + "_cat:ricetta"

    # menu_options = options["ricette"] + options["preparazioni"] + \
    #     options["ingredienti"] + options["metodi"] + \
    #     options["menu"] + options["ricerca"]

    return render_template("mostra_ricetta.html", page_head=page_head, navbar=navbar, menu_options=menu_options, name=name, picture=picture, type=dish_type, people=people, duration=duration, difficulty=difficulty, score=score, method=method_url, ingredient_rows=ingredient_rows, tot_price=tot_price, description=description, delete_recipe=delete_recipe, download_pdf=download_pdf, footer=footer)





# INGREDIENTI
@app.route("/aggiungi_ingrediente", methods=["GET", "POST"])
def aggiungi_ingrediente():
    if request.method == "GET":
        return render_template("aggiungi_ingrediente.html", page_head=page_head, navbar=navbar, menu_options=menu_options, footer=footer)

    name = upper_first(request.form["nome"])
    family = upper_first(request.form["famiglia"])
    subfamily = upper_first(request.form["sottofamiglia"])
    pricekg = float(request.form["prezzokg"])
    seasonality_start = request.form["stagionalita_start"]
    seasonality_end = request.form["stagionalita_end"]
    description = upper_first(request.form["descrizione"])

    # invalid values
    if name == "" or description == "" or family == "" or subfamily == "" or str(pricekg) == "" or len(name) > 100 or len(family) > 100 or len(subfamily) > 100 or len(description) > 65535:
        return "1"

    if nel_database(name, "ingrediente") == "1":        # ingrediente is already present in database
        return "0"

    seasonality = seasonality_start + "-" + seasonality_end
    if seasonality_end < seasonality_start:
        seasonality = seasonality_start + "-" + str(int(seasonality_end) + 12)

    picture_path = None

    picture = request.files["foto"]
    # if picture and allowed_file(normalize(name) + "." + picture.filename.split(".")[-1]):
    if picture:
        filename = secure_filename(normalize(name) + "." + picture.filename.split(".")[-1])
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'] + "/ingredienti", filename)
        picture.save(picture_path)

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO ingrediente (nome, famiglia, sottofamiglia, stagionalita, prezzokg, descrizione, foto) VALUES (%s, %s, %s, %s, %s, %s, %s);", [name, family, subfamily, seasonality, pricekg, description, picture_path])

    mysql.connection.commit()

    url = "/ingredienti/" + normalize(str(name))
    return url
@app.route("/ingredienti/cancella_<string:name>", methods=["GET"])
def cancella_ingredienti(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT nome, foto FROM ingrediente WHERE nome = %s;", [name])
    path = cur.fetchone()

    if path is None:
        return redirect("/errore")

    # delete from DB
    cur.execute("DELETE FROM ingrediente WHERE nome = %s;", [name])
    # cur.execute("DELETE FROM ricetta_ingrediente WHERE ricetta = %s;", [name])

    mysql.connection.commit()

    # delete pic from disk
    if path[1] is not None:
        if os.path.exists(str(path[1])):
            os.remove(str(path[1]))

    return redirect("/ingredienti")
@app.route("/ingredienti/<string:name>", methods=["GET"])
def ingrediente(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ingrediente WHERE nome = %s;", [name])
    ingredient = cur.fetchone()

    if ingredient is None:
        return redirect("/non_presente_" + normalize(name) + "_cat:ingrediente")

    family = ingredient[1]
    subfamily = ingredient[2]
    seasonality_range = ingredient[3]
    pricekg = str(ingredient[4]) + " €/kg"
    description = ingredient[5]
    picture_path = ingredient[6]

    seasonality_start = int(seasonality_range.split("-")[0])
    seasonality_end = int(seasonality_range.split("-")[1])

    if seasonality_start - seasonality_end == 0:
        seasonality = months_map[seasonality_start]
    elif seasonality_start == 1 and seasonality_end == 12:
        seasonality = "Tutto l'anno"
    else:
        if seasonality_end > 12:
            seasonality = months_map[seasonality_start] + " - " + months_map[seasonality_end - 12]
        else:
            seasonality = months_map[seasonality_start] + " - " + months_map[seasonality_end]

    picture = '<div class="row mobile_row"><form class="col s12" enctype="multipart/form-data"><div class="file-field input-field col s12"><div class="btn"><span>Foto</span><input type="file" id="foto" name="foto" accept=".jpg, .jpeg, .png, .bmp, .gif"></div><div class="file-path-wrapper"><input id="foto_path" class="file-path" type="text" placeholder="Carica una foto!"></div></div></form></div>'

    if picture_path:
        picture = '<div class="row mobile-row col s12"><div class="card detail_picture"><div class="card-image"><img class="materialboxed" src="' + str(picture_path)[1:] + '" alt="' + name + '"></div></div></div>'

    delete_ingredient = "/ingredienti/cancella_" + normalize(name)

    # menu_options = options["ricette"] + options["preparazioni"] + \
    #     options["ingredienti"] + options["metodi"] + \
    #     options["menu"] + options["ricerca"]

    return render_template("mostra_ingrediente.html", page_head=page_head, navbar=navbar, menu_options=menu_options, name=name, picture=picture, family=family, subfamily=subfamily, seasonality=seasonality, pricekg=pricekg, description=description, delete_ingredient=delete_ingredient, footer=footer)





# METODI
@app.route("/aggiungi_metodo", methods=["GET", "POST"])
def aggiungi_metodo():
    if request.method == "GET":
        return render_template("aggiungi_metodo.html", page_head=page_head, navbar=navbar, menu_options=menu_options, footer=footer)

    name = upper_first(request.form["nome"])
    description = upper_first(request.form["descrizione"])

    # invalid values
    if name == "" or description == "" or len(name) > 100 or len(description) > 65535:
        return "1"

    if nel_database(name, "metodo") == "1":        # method is already present in database
        return "0"

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO metodo (nome, descrizione) VALUES (%s, %s);", [name, description])

    mysql.connection.commit()

    url = "/metodi/" + normalize(str(name))
    return url
@app.route("/metodi/cancella_<string:name>", methods=["GET"])
def cancella_metodi(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM metodo WHERE nome = %s;", [name])
    path = cur.fetchone()

    if path is None:
        return redirect("/errore")

    # delete from DB
    cur.execute("DELETE FROM metodo WHERE nome = %s;", [name])

    mysql.connection.commit()

    return redirect("/metodi")
@app.route("/metodi/<string:name>", methods=["GET"])
def metodo(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM metodo WHERE nome = %s;", [name])
    method = cur.fetchone()

    if method is None:
        return redirect("/non_presente_" + normalize(name) + "_cat:metodo")

    description = method[1]

    delete_method = "/metodi/cancella_" + normalize(name)

    # menu_options = options["ricette"] + options["preparazioni"] + \
    #     options["ingredienti"] + options["metodi"] + \
    #     options["menu"] + options["ricerca"]

    return render_template("mostra_metodo.html", page_head=page_head, navbar=navbar, menu_options=menu_options, name=name, description=description, delete_method=delete_method, footer=footer)





#  PREPARAZIONI
@app.route("/aggiungi_preparazione", methods=["GET", "POST"])
def aggiungi_preparazione():
    if request.method == "GET":
        # collects saved methods
        cur = mysql.connection.cursor()
        cur.execute("SELECT nome FROM metodo;")
        methods = cur.fetchall()

        methods_names = ""
        saved_methods = ""
        if methods is not None:
            for name in methods:
                methods_names += "<option value=\"" + normalize(name[0]) + "\">" + name[0] + "</option>"
            saved_methods = methods_names

        # collects saved ingredients
        cur = mysql.connection.cursor()
        cur.execute("SELECT nome FROM ingrediente;")
        ingredients = cur.fetchall()

        ingredients_names = ""
        saved_ingredients = ""
        if ingredients is not None:
            for name in ingredients:
                ingredients_names += "<option value=\"" + normalize(name[0]) + "\">" + name[0] + "</option>"
            # ingredients_names += "<option value='_nuovo_'>+ SERVER...</option>"
            saved_ingredients = ingredients_names

        return render_template("aggiungi_preparazione.html", page_head=page_head, navbar=navbar, menu_options=menu_options, saved_methods=saved_methods, saved_ingredients=saved_ingredients, footer=footer)

    name = upper_first(request.form["nome"])
    people = request.form["persone"]
    duration = request.form["durata"]
    difficulty = request.form["difficolta"]
    score = request.form["punteggio"]
    method = reverse_normalize(request.form["metodo"])
    description = upper_first(request.form["descrizione"])

    # invalid values
    if name == "" or description == "" or len(name) > 100 or len(description) > 65535:
        return "1"

    if nel_database(name, "preparazione") == "1":        # preparation is already present in database
        return "0"

    picture_path = None

    picture = request.files["foto"]
    # if picture and allowed_file(normalize(name) + "." + picture.filename.split(".")[-1]):
    if picture:
        filename = secure_filename(normalize(name) + "." + picture.filename.split(".")[-1])
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'] + "/preparazioni", filename)
        picture.save(picture_path)

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO preparazione (nome, persone, durata, difficolta, foto, punteggio, metodo, descrizione) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", [name, people, duration, difficulty, picture_path, score, method, description])

    # gathering dynamically added ingredients
    n = int(request.form["counter"])
    ingredient_list = []
    for i in range(0, n):
        ingredient = request.form["ingr_" + str(i + 1)]
        unit = request.form["unita_" + str(i + 1)]

        if unit_map(int(unit)) == "q.b.":
            quantity = 0
        else:
            if request.form["quantita_" + str(i + 1)] == "":
                return "2"
            quantity = request.form["quantita_" + str(i + 1)]

        if ingredient in ingredient_list:   # double ingredient, ignore it
            # return "2"
            continue

        ingredient_list.append(ingredient)
        cur.execute("INSERT INTO preparazione_ingrediente (preparazione, ingrediente, quantita, unita) VALUES (%s, %s, %s, %s);", [name, reverse_normalize(ingredient), quantity, unit])

    mysql.connection.commit()

    url = "/preparazioni/" + normalize(str(name))
    return url
@app.route("/preparazioni/cancella_<string:name>", methods=["GET"])
def cancella_preparazione(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT nome, foto FROM preparazione WHERE nome = %s;", [name])
    path = cur.fetchone()

    if path is None:
        return redirect("/errore")

    # delete from DB
    cur.execute("DELETE FROM preparazione WHERE nome = %s;", [name])
    cur.execute("DELETE FROM preparazione_ingrediente WHERE preparazione = %s;", [name])

    mysql.connection.commit()

    # delete pic from disk
    if path[1] is not None:
        if os.path.exists(str(path[1])):
            os.remove(str(path[1]))

    # delete pdf from disk
    pdf_path = "static/pdf/preparazioni/" + secure_filename(normalize(name) + ".pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return redirect("/preparazioni")
@app.route("/preparazioni/<string:name>", methods=["GET"])
def preparazione(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM preparazione WHERE nome = %s;", [name])
    preparation = cur.fetchone()

    if preparation is None:
        return redirect("/non_presente_" + normalize(name) + "_cat:preparazione")

    people = preparation[1]
    duration = preparation[2]
    difficulty = difficulty_map(int(preparation[3]))
    picture_path = preparation[4]
    score = preparation[5]
    method = preparation[6]
    description = preparation[7]

    method_url = "<a href='/metodi/" + normalize(method) + "'>" + method + "</a>"

    picture = '<div class="row mobile_row"><form class="col s12" enctype="multipart/form-data"><div class="file-field input-field col s12"><div class="btn"><span>Foto</span><input type="file" id="foto" name="foto" accept=".jpg, .jpeg, .png, .bmp, .gif"></div><div class="file-path-wrapper"><input id="foto_path" class="file-path" type="text" placeholder="Carica una foto!"></div></div></form></div>'

    if picture_path:
        picture = '<div class="row mobile-row col s12"><div class="card detail_picture"><div class="card-image"><img class="materialboxed" src="' + str(picture_path)[1:] + '" alt="' + name + '"></div></div></div>'

    cur = mysql.connection.cursor()
    cur.execute("SELECT ingrediente, quantita, unita FROM preparazione_ingrediente WHERE preparazione = %s;", [name])
    ingredients = cur.fetchall()

    tot_price = 0
    ingredient_rows = ""
    uncountable = False
    for ingredient in ingredients:
        unit = unit_map(int(ingredient[2]))
        if unit == "q.b.":
            quantity = " "
        else:
            quantity = str(ingredient[1]) + " "

            cur.execute("SELECT prezzokg FROM ingrediente where nome = %s", [ingredient[0]])
            pricekg = cur.fetchone()

            if pricekg:
                pricekg = pricekg[0]
                if unit == "gr":
                    tot_price += pricekg * (float(quantity) / 1000)
                elif unit == "kg":
                    tot_price += pricekg * float(quantity)
                elif unit == "ml":
                    tot_price += pricekg * (float(quantity) / 1000)
                elif unit == "lt":
                    tot_price += pricekg * float(quantity)
                else:
                    uncountable = True

        ingredient_rows += "<tr><td onClick='document.location.href=\"/ingredienti/" + normalize(str(ingredient[0])) + "\";'><a href='/ingredienti/" + normalize(str(ingredient[0])) + "'>" + str(ingredient[0]) + "</a></td><td onClick='document.location.href=\"/ingredienti/" + normalize(str(ingredient[0])) + "\";'><a class='quantity' href='/ingredienti/" + normalize(str(ingredient[0])) + "'>" + quantity + unit + "</td></tr>"

    integer_digits = str(tot_price).split('.')[0]
    decimal_digits = str(tot_price).split('.')[-1]
    if len(decimal_digits) > 2:
        if decimal_digits[2] >= "0" and decimal_digits[2] <= "4":
            tot_price = float(integer_digits + "." + decimal_digits[:2])
        else:
            tot_price = float(integer_digits + "." + decimal_digits[:2]) + 0.01

    tot_price = str(tot_price) + "€"
    if uncountable:
        tot_price += " + sfusi"

    delete_preparation = "/preparazioni/cancella_" + normalize(name)
    download_pdf = "/pdf_" + normalize(name) + "_cat:preparazione"

    return render_template("mostra_preparazione.html", page_head=page_head, navbar=navbar, menu_options=menu_options, name=name, picture=picture, people=people, duration=duration, difficulty=difficulty, score=score, method=method_url, ingredient_rows=ingredient_rows, description=description, tot_price=tot_price, delete_preparation=delete_preparation, download_pdf=download_pdf, footer=footer)





#  MENU
@app.route("/aggiungi_menu", methods=["GET", "POST"])
def aggiungi_menu():
    if request.method == "GET":
        # collects recipes
        cur = mysql.connection.cursor()
        cur.execute("SELECT nome, tipo FROM ricetta;")
        recipes = cur.fetchall()

        saved_recipes = {"entree" : [], "antipasti" : [], "primi" : [], "secondi" : [], "dessert" : []}
        if recipes is not None:
            for recipe in recipes:
                saved_recipes[dish_type_map(recipe[1], javascriptFormat=True)].append(normalize(recipe[0]))

        return render_template("aggiungi_menu.html", page_head=page_head, navbar=navbar, menu_options=menu_options, saved_recipes=json.dumps(saved_recipes), footer=footer)

    name = request.form["nome"]

    # invalid values
    if name == "" or len(name) > 20:
        return "1"

    name = name.split(" ")[0] + "-" + str(months_map_inverse[name.split(" ")[1]]) + "-" + name.split(" ")[2]

    if nel_database(name, "menu_ricetta") == "1":        # menu is already present in database
        return "0"

    cur = mysql.connection.cursor()

    # gathering dynamically added recipes
    n = int(request.form["counter"])
    recipe_list = []
    for i in range(0, n):
        recipe = request.form["recipe_" + str(i + 1)]

        if recipe in recipe_list:   # double recipe, ignore it
            # return "2"
            continue

        recipe_list.append(recipe)
        cur.execute("SELECT tipo FROM ricetta WHERE nome = %s", [reverse_normalize(recipe)])
        dish_type = cur.fetchone()
        cur.execute("INSERT INTO menu_ricetta (nome, ricetta, tipo) VALUES (%s, %s, %s);", [name, reverse_normalize(recipe), str(dish_type[0])])

    mysql.connection.commit()

    url = "/menu/" + normalize(str(name))
    return url
@app.route("/menu/cancella_<string:name>", methods=["GET"])
def cancella_menu(name):
    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM menu_ricetta WHERE nome = %s;", [name])
    path = cur.fetchone()

    if path is None:
        return redirect("/errore")

    # delete from DB
    cur.execute("DELETE FROM menu_ricetta WHERE nome = %s;", [name])

    mysql.connection.commit()

    # delete pdf from disk
    pdf_path = "static/pdf/menu/" + secure_filename(normalize(name) + ".pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return redirect("/menu")
@app.route("/menu/<string:name>", methods=["GET"])
def menu_show(name):

    # collects recipes
    cur = mysql.connection.cursor()
    cur.execute("SELECT ricetta, tipo FROM menu_ricetta WHERE nome = %s;", [reverse_normalize(name)])
    recipes = cur.fetchall()

    recipe_list = []
    saved_recipes = {"entree" : [], "antipasti" : [], "primi" : [], "secondi" : [], "dessert" : []}
    if recipes is not None:
        for recipe in recipes:
            saved_recipes[dish_type_map(recipe[1], javascriptFormat=True)].append(normalize(recipe[0]))
            recipe_list.append(recipe[0])

    tot_price = 0
    ingredients_list = []
    ingredients_quantity = []
    ingredients_units = []

    for recipe in recipe_list:
        cur = mysql.connection.cursor()
        cur.execute("SELECT ingrediente, quantita, unita FROM ricetta_ingrediente WHERE ricetta = %s;", [recipe])
        ingredients = cur.fetchall()

        recipe_price = 0
        uncountable = False

        if ingredients:
            for ingredient in ingredients:
                unit = unit_map(int(ingredient[2]))
                if unit == "q.b.":
                    quantity = " "
                else:
                    quantity = str(ingredient[1]) + " "

                    cur.execute("SELECT prezzokg FROM ingrediente where nome = %s", [ingredient[0]])
                    pricekg = cur.fetchone()

                    if pricekg:
                        pricekg = pricekg[0]
                        if unit == "gr":
                            recipe_price += pricekg * (float(quantity) / 1000)
                        elif unit == "kg":
                            recipe_price += pricekg * float(quantity)
                        elif unit == "ml":
                            recipe_price += pricekg * (float(quantity) / 1000)
                        elif unit == "lt":
                            recipe_price += pricekg * float(quantity)
                        else:
                            uncountable = True

                if str(ingredient[0]) in ingredients_list:
                    ingredients_quantity[ingredients_list.index(str(ingredient[0]))] += quantity
                else:
                    ingredients_list.append(str(ingredient[0]))
                    ingredients_quantity.append(quantity)
                    ingredients_units.append(unit)

        tot_price += recipe_price

    ingredient_rows = ""
    for ingredient in ingredients_list:
        ingredient_rows += "<tr><td onClick='document.location.href=\"/ingredienti/" + normalize(ingredient) + "\";'><a href='/ingredienti/" + normalize(ingredient) + "'>" + ingredient + "</a></td><td onClick='document.location.href=\"/ingredienti/" + normalize(ingredient) + "\";'><a class='quantity' href='/ingredienti/" + normalize(ingredient) + "'>" + ingredients_quantity[ingredients_list.index(ingredient)] + ingredients_units[ingredients_list.index(ingredient)] + "</td></tr>"

    integer_digits = str(tot_price).split('.')[0]
    decimal_digits = str(tot_price).split('.')[-1]
    if len(decimal_digits) > 2:
        if decimal_digits[2] >= "0" and decimal_digits[2] <= "4":
            tot_price = float(integer_digits + "." + decimal_digits[:2])
        else:
            tot_price = float(integer_digits + "." + decimal_digits[:2]) + 0.01


    tot_price = str(tot_price) + "€"
    if uncountable:
        tot_price += " + sfusi"

    delete_menu = "/menu/cancella_" + normalize(name)
    download_pdf = "/menu_pdf_" + normalize(name)

    name = name.split("-")[0] + " " + months_map[int(name.split("-")[1])] + " " + name.split("-")[2]

    return render_template("mostra_menu.html", page_head=page_head, navbar=navbar, menu_options=menu_options, name=name, saved_recipes=json.dumps(saved_recipes), ingredient_rows=ingredient_rows, tot_price=tot_price, delete_menu=delete_menu, download_pdf=download_pdf, footer=footer)





# GENERALI
@app.route("/non_presente_<string:name>_cat:<string:element_type>", methods=["GET"])
def non_presente(name, element_type):
    if element_type == "ingrediente":
        message = "L'ingrediente <span class='red-text'>" + reverse_normalize(name) + "</span> non è presente tra gli ingredienti salvati."
        add_url = "/aggiungi_ingrediente"
        add_msg = "Aggiungilo!"
    elif element_type == "ricetta":
        message = "La ricetta <span class='red-text'>" + reverse_normalize(name) + "</span> non è presente tra le ricette salvate."
        add_url = "/aggiungi_ricetta"
        add_msg = "Aggiungila!"
    elif element_type == "metodo":
        message = "Il metodo <span class='red-text'>" + reverse_normalize(name) + "</span> non è presente tra i metodi salvati."
        add_url = "/aggiungi_metodo"
        add_msg = "Aggiungilo!"
    elif element_type == "preparazione":
        message = "La preparazione <span class='red-text'>" + reverse_normalize(name) + "</span> non è presente tra le preparazioni salvate."
        add_url = "/aggiungi_preparazione"
        add_msg = "Aggiungila!"
    elif element_type == "menu":
        message = "Il menu <span class='red-text'>" + reverse_normalize(name) + "</span> non è presente tra i menu salvati."
        add_url = "/aggiungi_menu"
        add_msg = "Aggiungilo!"

    return render_template("template_non_presente.html", page_head=page_head, navbar=navbar, menu_options=menu_options, message=message, add_url=add_url, add_msg=add_msg, footer=footer)
@app.route("/aggiungi_foto_<string:name>_cat:<string:category>", methods=["POST"])
def aggiungi_foto(name, category):
    if category == "ricetta":
        subpath_save = "/ricette"
    elif category == "ingrediente":
        subpath_save = "/ingredienti"
    elif category == "preparazione":
        subpath_save = "/preparazioni"

    # name = reverse_normalize(name)

    picture_path = None
    picture = request.files["foto"]
    if picture and allowed_file(name + "." + picture.filename.split(".")[-1]):
        filename = secure_filename(name + "." + picture.filename.split(".")[-1])
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'] + subpath_save, filename)
        picture.save(picture_path)

        cur = mysql.connection.cursor()
        cur.execute("UPDATE " + category + " SET foto = %s WHERE nome = %s;", [picture_path, name])
        mysql.connection.commit()
        return "1"

    return "0"
@app.route("/nel_database_<string:name>_cat:<string:category>", methods=["GET"])
def nel_database(name, category):
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM " + category + " WHERE nome = %s;", [reverse_normalize(name)])
    data = cur.fetchone()

    if data is None:
        return "0"
    else:
        return "1"
@app.route("/pdf_<string:name>_cat:<string:category>", methods=["GET"])
def pdf(name, category):
    subpath_save = ""
    ingredient_table = ""

    if category == "ricetta":
        subpath_save = "ricette"
        ingredient_table = "ricetta_ingrediente"
    elif category == "preparazione":
        subpath_save = "preparazioni"
        ingredient_table = "preparazione_ingrediente"

    # if not allowed_file(normalize(name) + ".pdf"):
    #     return redirect('/errore')

    pdf_path = "static/pdf/" + subpath_save + "/" + secure_filename(normalize(name) + ".pdf")

    if os.path.exists(pdf_path):
        return send_file(pdf_path)

    name = reverse_normalize(name)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM " + category + " WHERE nome = %s;", [name])
    recipe = cur.fetchone()

    if recipe is None:
        return redirect("/errore")

    i = 1
    dish_type = ""
    if category == "ricetta":
        dish_type = '<tr><th class="bold">Tipo di portata</th><th class="normal">' + dish_type_map(int(recipe[i])) + '</th></tr>'
        i += 1

    people = recipe[i]
    i += 1
    duration = recipe[i]
    i += 1
    difficulty = difficulty_map(int(recipe[i]))
    i += 1
    # picture_path = recipe[i]
    i += 1
    score = recipe[i]
    i += 1
    method = recipe[i]
    i += 1
    description = recipe[i]

    cur = mysql.connection.cursor()
    cur.execute("SELECT ingrediente, quantita, unita FROM " + ingredient_table + " WHERE " + category + " = %s;", [name])
    ingredients = cur.fetchall()

    tot_price = 0
    ingredient_rows = ""
    uncountable = False
    for ingredient in ingredients:
        unit = unit_map(int(ingredient[2]))
        if unit == "q.b.":
            quantity = " "
        else:
            quantity = str(ingredient[1]) + " "

            cur.execute("SELECT prezzokg FROM ingrediente where nome = %s", [ingredient[0]])
            pricekg = cur.fetchone()[0]

            if unit == "gr":
                tot_price += pricekg * (float(quantity) / 1000)
            elif unit == "kg":
                tot_price += pricekg * float(quantity)
            elif unit == "ml":
                tot_price += pricekg * (float(quantity) / 1000)
            elif unit == "lt":
                tot_price += pricekg * float(quantity)
            else:
                uncountable = True

        ingredient_rows += '<tr><td> ' + str(ingredient[0]) + '</td><td>' + quantity + unit + '</td><td>' + str(pricekg) + ' €</td></tr>'

    integer_digits = str(tot_price).split('.')[0]
    decimal_digits = str(tot_price).split('.')[-1]
    if len(decimal_digits) > 2:
        if decimal_digits[2] >= "0" and decimal_digits[2] <= "4":
            tot_price = float(integer_digits + "." + decimal_digits[:2])
        else:
            tot_price = float(integer_digits + "." + decimal_digits[:2]) + 0.01

    tot_price = str(tot_price) + " €"
    if uncountable:
        tot_price += " + sfusi"

    pdf_html = HTML(string=render_template("pdf.html", name=name, type=dish_type, people=people, duration=duration, difficulty=difficulty, score=score, method=method, tot_price=tot_price, ingredient_rows=ingredient_rows, description=description)).write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])

    with open(pdf_path, "w") as pdf_file:
        pdf_file.write(pdf_html)

    return send_file(pdf_path)
    # return render_template("pdf.html", name=name, type=dish_type, people=people, duration=duration, difficulty=difficulty, score=score, method=method, ingredient_rows=ingredient_rows, description=description)
@app.route("/menu_pdf_<string:name>", methods=["GET"])
def menu_pdf(name):
    pdf_path = "static/pdf/menu/" + secure_filename(name + ".pdf")

    if os.path.exists(pdf_path):
        return send_file(pdf_path)

    # collects recipes
    cur = mysql.connection.cursor()
    cur.execute("SELECT ricetta, tipo FROM menu_ricetta WHERE nome = %s;", [reverse_normalize(name)])
    recipes = cur.fetchall()

    recipe_list = []
    type_ordered_list = {"entree" : "", "antipasti" : "", "primi" : "", "secondi" : "", "dessert" : ""}
    if recipes is not None:
        for recipe in recipes:
            recipe_list.append(recipe[0])
            type_ordered_list[dish_type_map(recipe[1], javascriptFormat=True)] += "<p>" + recipe[0] + "</p>"

    recipe_ul = "<h3 class='bold'>Entrée</h3>" + type_ordered_list["entree"] + "<br/>" + \
                "<h3 class='bold'>Antipasti</h3>" + type_ordered_list["antipasti"] + "<br/>" + \
                "<h3 class='bold'>Primi</h3>" + type_ordered_list["primi"] + "<br/>" + \
                "<h3 class='bold'>Secondi</h3>" + type_ordered_list["secondi"] + "<br/>" + \
                "<h3 class='bold'>Dessert</h3>" + type_ordered_list["dessert"]

    tot_price = 0
    ingredients_list = []
    ingredients_quantity = []
    ingredients_units = []
    ingredients_pricekg = []

    for recipe in recipe_list:
        cur = mysql.connection.cursor()
        cur.execute("SELECT ingrediente, quantita, unita FROM ricetta_ingrediente WHERE ricetta = %s;", [recipe])
        ingredients = cur.fetchall()

        recipe_price = 0
        uncountable = False

        for ingredient in ingredients:
            pricekg = 0

            unit = unit_map(int(ingredient[2]))
            if unit == "q.b.":
                quantity = " "
            else:
                quantity = str(ingredient[1]) + " "

                cur.execute("SELECT prezzokg FROM ingrediente where nome = %s", [ingredient[0]])
                pricekg = cur.fetchone()[0]

                if unit == "gr":
                    recipe_price += pricekg * (float(quantity) / 1000)
                elif unit == "kg":
                    recipe_price += pricekg * float(quantity)
                elif unit == "ml":
                    recipe_price += pricekg * (float(quantity) / 1000)
                elif unit == "lt":
                    recipe_price += pricekg * float(quantity)
                else:
                    uncountable = True

            if str(ingredient[0]) in ingredients_list:
                ingredients_quantity[ingredients_list.index(str(ingredient[0]))] += quantity
            else:
                ingredients_list.append(str(ingredient[0]))
                ingredients_quantity.append(quantity)
                ingredients_units.append(unit)
                ingredients_pricekg.append(pricekg)

        tot_price += recipe_price

    ingredient_rows = ""
    for ingredient in ingredients_list:
        index = ingredients_list.index(ingredient)
        ingredient_rows += "<tr><td>" + ingredient + "</td><td>" + ingredients_quantity[index] + ingredients_units[index] + "</td><td>" + str(ingredients_pricekg[index]) + " €</td></tr>"

    integer_digits = str(tot_price).split('.')[0]
    decimal_digits = str(tot_price).split('.')[-1]
    if len(decimal_digits) > 2:
        if decimal_digits[2] >= "0" and decimal_digits[2] <= "4":
            tot_price = float(integer_digits + "." + decimal_digits[:2])
        else:
            tot_price = float(integer_digits + "." + decimal_digits[:2]) + 0.01


    tot_price = str(tot_price) + " €"
    if uncountable:
        tot_price += " + sfusi"


    pdf_html = HTML(string=render_template("pdf_menu.html", name=name, recipe_ul=recipe_ul, tot_price=tot_price, ingredient_rows=ingredient_rows)).write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])

    with open(pdf_path, "w") as pdf_file:
        pdf_file.write(pdf_html)

    return send_file(pdf_path)
@app.route("/errore")
def error(msg=""):
    error_message = "Errore."
    contacts = "In caso l'errore si verifichi di nuovo, scrivere una mail a <a href='mailto:alezini94@hotmail.it?Subject=In merito al sito: \"" + site_name + "\"' target='_top'>Alessandro Zini</a>."

    if msg != "":
        error_message = msg
        contacts = ""

    return render_template("errore.html", page_head=page_head, navbar=navbar, menu_options=options["home"], error_message=error_message, contacts=contacts, footer=footer)





# RICERCA
@app.route("/cerca", methods=["GET", "POST"])
def cerca():
    if request.method == "GET":
        return render_template("ricerca.html", page_head=page_head, navbar=navbar, menu_options=menu_options, footer=footer)

    cat = request.form["category"]
    prop = request.form["property"]
    keyword = request.form["keyword"]

    if keyword == "" or len(keyword) > 100:
        return "0"

    # map correct keyword alphabetic value with the numeric ones in db
    if prop == "tipo":
        comp_keyword = str(keyword.lower())
        if comp_keyword == "entrée" or comp_keyword == "entrèe" or comp_keyword == "entree":
            keyword = 1
        elif comp_keyword == "antipasto" or comp_keyword == "antipasti":
            keyword = 2
        elif comp_keyword == "primo" or comp_keyword == "primi":
            keyword = 3
        elif comp_keyword == "secondo" or comp_keyword == "secondi":
            keyword = 4
        elif comp_keyword == "dessert" or comp_keyword == "desserts" or comp_keyword == "desser":
            keyword = 5

    cur = mysql.connection.cursor()

    if cat == "Ricette":
        if prop == "ingrediente":
            query = "SELECT ricetta, ingrediente FROM ricetta_ingrediente;"
        elif prop == "nome":
            query = "SELECT nome FROM ricetta;"
        else:
            query = "SELECT nome, " + prop + " FROM ricetta;"

    elif cat == "Preparazioni":
        if prop == "ingrediente":
            query = "SELECT preparazione, ingrediente FROM preparazione_ingrediente;"
        elif prop == "nome":
            query = "SELECT nome FROM ingrediente;"
        else:
            query = "SELECT nome, " + prop + " FROM preparazione;"

    elif cat == "Ingredienti":
        if prop == "nome":
            query = "SELECT nome FROM ingrediente;"
        else:
            query = "SELECT nome, " + prop + " FROM ingrediente;"

    elif cat == "Metodi":
        query = "SELECT nome FROM metodo;"

    elif cat == "Menu":
        if prop == "nome":
            query = "SELECT nome FROM menu_ricetta;"
        else:
            query = "SELECT nome, " + prop + " FROM menu_ricetta;"

    cur.execute(query)
    res = cur.fetchall()

    res_collection = ""
    res_list = []
    if res is not None:
        for r in res:
            if cat == "Menu":   # custom handler for menu
                v = str(r[0]).split("-")[0] + " " + months_map[int(r[0].split("-")[1])] + " " + str(r[0]).split("-")[2]

                if prop == "nome":  # the custom handler is needed to deal with name search
                    sep_in_key = False

                    separators = ('/', '-', '_', ' ', ',', '.', '\\')

                    for sep in separators:
                        if sep in keyword:
                            sep_in_key = True
                            break

                    if not sep_in_key:  # day or month or year SINGLE
                        if str(keyword).lower() in str(r[0]).lower():   # search for single day or month or year, where month intended as numeric
                            if v not in res_list:
                                res_list.append(v)
                        elif str(keyword).lower() in months_map[int(r[0].split('-')[1])].lower():   # month intended as alphabetic
                            if v not in res_list:
                                res_list.append(v)
                    else:   # alternatively, split the query in parts
                        all_match = True

                        for sep in separators:
                            parts = keyword.split(sep)
                            for part in parts:
                                part = part.replace(" ", "")
                                if not (str(part).lower() in str(r[0]).lower() or str(part).lower() in months_map[int(r[0].split('-')[1])].lower()):
                                    all_match = False
                            if all_match and v not in res_list: # every part of the query must match (e.g. if query = "3 sett" and in database "14 settembre" and "3 ottobre", query doesn't match thus v is not added)
                                res_list.append(v)
                            all_match = True
                else:
                    if str(keyword).lower() in str(r[1]).lower():
                        res_list.append(v)

            elif cat == "Ingredienti" and prop == "stagionalita":   # custom handler for ingredient
                db_start = int(r[1].split("-")[0])
                db_end = int(r[1].split("-")[1])

                if db_end > 12:
                    v = months_map[db_start] + " - " + months_map[db_end - 12]
                else:
                    v = months_map[db_start] + " - " + months_map[db_end]

                # parse seasonality
                db_seas_list = []
                for i in range(db_start, db_end + 1):
                    if i % 12 == 0:
                        db_seas_list.append(months_map[12])
                    else:
                        db_seas_list.append(months_map[i % 12])
                
                # print db_seas_list

                sep_in_key = False

                separators = ('/', '-', '_', ',', '.', '\\')

                for sep in separators:
                    if sep in keyword:
                        sep_in_key = True
                        break

                if not sep_in_key:  # single seasonality keyword
                    for month in db_seas_list:
                        if str(keyword).lower() in month.lower():
                            if r[0] not in res_list:
                                res_list.append(r[0])
                                break
                else:   # alternatively, split the query in parts
                    for counter in range(0,2):
                        q_start = -1
                        q_end = -1

                        for sep in separators:
                            parts = keyword.split(sep)

                            if len(parts) == 2:  # if more than two months or separators were used, query is bad formatted and is ignored
                                for part in parts:
                                    for v in months_map.values():
                                        if part.lower() in v.lower():
                                            if q_start == -1:
                                                q_start = months_map_inverse[v]
                                            else:
                                                q_end = months_map_inverse[v] + 12 * counter
                                                break

                        # print "Ing: " + r[0] + ", q_start: " + str(q_start) + ", q_end " + str(q_end) + ", db_start: " + str(db_start) + ", db_end " + str(db_end)

                        if q_start <= q_end and q_start >= db_start and q_start <= db_end and q_end >= db_start and q_end <= db_end and r[0] not in res_list:    # query range is inside or equal to db range
                            res_list.append(r[0])

            else:
                try:    # if a tuple (name, property) has been selected, the try will succed
                    if str(keyword).lower() in str(r[1]).lower():
                        res_list.append(r[0])
                except IndexError:
                    if str(keyword).lower() in str(r[0]).lower():
                        res_list.append(r[0])

        res_links = ""
        res_collection = ""

        if cat == "Menu":
            for r in res_list:
                link_menu_name = r.split(" ")[0] + "-" + str(months_map_inverse[r.split(" ")[1]]) + "-" + r.split(" ")[2]
                res_links += "<a href='/" + cat.lower() + "/" + link_menu_name + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + r + "</a>"
        else:
            for r in res_list:
                res_links += "<a href='/" + cat.lower() + "/" + normalize(r) + "' class='collection-item teal lighten-5 teal-text darken-4-text'>" + r + "</a>"
        res_collection = "<div class='collection center' id='results'>" + res_links + "</div>__?num=" + str(len(res_list))

    return res_collection




# ROOT
@app.route("/", methods=["GET"])
def main():
    # menu_options = options["ricette"] + options["preparazioni"] + \
    #     options["ingredienti"] + options["metodi"] + \
    #     options["menu"] + options["ricerca"]
    return render_template("index.html", page_head=page_head, navbar=navbar, menu_options=menu_options, footer=footer)




# FAVICONS
@app.route('/apple-touch-icon.png', methods=["GET"])
def apple_touch_icon():
    return send_from_directory(os.path.join(app.root_path, 'static/img/favicons_old'), 'apple-touch-icon.png', mimetype='image/vnd.microsoft.icon')
@app.route('/favicon.ico', methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img/favicons_old'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if "apple" in path and "icon" in path:    # if path == "apple-touch-icon-precomposed.png":
        return apple_touch_icon()

    return error("Ops. Quello che stai cercando non è qui.")



if __name__ == "__main__":
    app.run()
