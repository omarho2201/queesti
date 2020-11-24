
from flask import Flask, render_template, request, session, logging, url_for,redirect,json,flash   
from flask_login import login_user, logout_user, login_required,current_user
from flaskext.mysql import MySQL
import os
import urllib.request
from PyPDF4 import PdfFileReader
from pathlib import Path
import Modelo as Modelo
import time
import re
import os 
from werkzeug.utils import secure_filename
from io import BytesIO
import os
from PIL import Image, ImageDraw
import requests

from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import FaceAttributeType
from msrest.authentication import CognitiveServicesCredentials

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'sepherot_omar'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BAg2v4tk5h'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_omarBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)  

KEY = 'b5e6f9bef05f4ba2a9f6b979597484e7'
ENDPOINT = 'https://facialdeteccion.cognitiveservices.azure.com/'

_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

""" UPLOAD_FOLDER= os.path.abspath("C:/Users/omiha/Desktop/ejercicio1/entornovirtual1/fotos curso") """

app.secret_key="holayadios"

app.config['UPLOAD_FOLDER'] = 'entornovirtual1\\fotos curso'
app.config['UPLOAD_EXTENSIONS'] = ['png','jpg','jpeg']


#registro
@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == 'POST':
            _user=request.form['username']
            _email=request.form['email']
            _pass1=request.form['password1']
            print (_user)
            consulta=Modelo.register(_user,_email,_pass1) 
            if consulta:
                Modelo.entities(_user,'Registro usuario','Usuario registrado correctamente')
                flash("Registro éxitoso")
            else:
                Modelo.entities(_user,'Registro falil','Error al registrarse')
    return render_template("login.html")
    

#login

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method== "POST":
        _user1=request.form["name"]
        _pass=request.form["password"]
        _cambio=Modelo.login(_user1,_pass)
        print(_user1)
        print(_pass)
        if _cambio:
            Modelo.entities(_user1,'Login','Usuario logeado correctamente')
            return redirect(url_for("home",user=_user1))
        else:
            Modelo.entities(_user1,'Login fail','Error al logear')
            print("Contraseña incorrecta","error")

    return render_template ("login.html")

##########################parte para el gamifiication##########################

@app.route("/actividad", methods = ["GET","POST"])
def actividad():
    cur=mysql.get_db().cursor()
    cur.execute('select meta from gamification')
    meta = cur.fetchall()
    cur=mysql.get_db().cursor()
    cur.execute('select sum(puntos) from gamification')
    puntos = cur.fetchall()
    cur=mysql.get_db().cursor()
    cur.execute('select meta-sum(puntos) from gamification')
    diferencias= cur.fetchall()
    print(diferencias)
    return render_template("actividad.html",meta=meta,diferencias=diferencias,puntos=puntos)
#PARTE DE CREAR CUESTIONARIOS, EDITAR Y ELIMINAR

@app.route("/addpregunta", methods= ['GET','POST'])
def addpregunta():
    if request.method =='POST':
        insertp = request.form['insertp']
        print(insertp)
        cur = mysql.get_db().cursor()
        cur.execute('insert into preguntas (cuestionario) values (%s)', (insertp))
        mysql.get_db().commit()
        #flash ('Pregunta agregada')
    return redirect(url_for("cuestionario"))


@app.route("/cuestionario")
def cuestionario():
    cur=mysql.get_db().cursor()
    cur.execute('select * from preguntas')
    data = cur.fetchall()
    return render_template("cuestionario.html",clientes=data)

@app.route('/delete/<string:id>')
def delete_cliente(id):
    cur= mysql.get_db().cursor()
    cur.execute('delete from preguntas where id_pregunta = {0}'.format(id))
    mysql.get_db().commit()
    # flash('Pregunta eliminada correctamente')
    return redirect(url_for("cuestionario")) 
    

@app.route('/edit/<id>')
def get_cliente(id):
    cur=mysql.get_db().cursor()
    cur.execute('SELECT * FROM preguntas where id_pregunta = %s', (id))
    data = cur.fetchall()
    #flash("éxitoso")
    return render_template('editpregunta.html', cliente = data[0])

@app.route('/update/<id>', methods=['POST'])
def update_cliente(id):
    if request.method == 'POST':
        pregunta = request.form['pregunta']
        cur=mysql.get_db().cursor()
        cur.execute("UPDATE preguntas SET cuestionario = %s where id_pregunta= %s", (pregunta,id))
        mysql.get_db().commit()
    return redirect(url_for("cuestionario")) 


@app.route("/preguntasqr")
def preguntasqr():
    return render_template("preguntasqr.html")
#ENCUESTA----------------------------------------------------------------------------------
@app.route("/ingresoencuesta")
def ingresoencuesta():
    cur=mysql.get_db().cursor()
    cur.execute('select * from preguntas')
    data = cur.fetchall()
    return render_template("ingresoencuesta.html",clientes=data)

@app.route("/resulcliente")
def resulcliente():
    cur=mysql.get_db().cursor()
    cur.execute('select * from preguntas where estado = 1')
    data = cur.fetchall()
    return render_template("resulcliente.html",clientes=data)

@app.route("/resulcliente1", methods= ['GET','POST'])
def resulcliente1():
    if request.method == 'POST':
        cur=mysql.get_db().cursor()
        cur.execute('select id_pregunta from preguntas where estado = 1')
        ids = cur.fetchall()
        
        for arg in request.form:
            valor = request.form.getlist(arg)
            idcurso=request.form['idcurso']
            contador = 0
            for data in valor:
                cur=mysql.get_db().cursor()
                idp=ids[contador][0]
                cur.execute('insert into crespuestas (respuesta,curso,id_pregunta) values (%s,%s,%s) ', (data,idcurso,idp,))
                contador = contador + 1
                mysql.get_db().commit()
    return redirect(url_for("gracias"))


    

#resultados
 
@app.route("/resultadocurso", methods= ['GET','POST'])
def resultadoscurso():
    if request.method=="POST":
        cur=mysql.get_db().cursor()
        cur.execute('insert into gamification (puntos) values (%s)',(1))
        mysql.get_db().commit()
        curso=request.form['resul']
        cur=mysql.get_db().cursor()
        cur.execute('select nom_curso from T_cursos where id_cursos=%s',curso)
        nomcurso = cur.fetchall()
        promedios=[]
        cur=mysql.get_db().cursor()
        cur.execute('select DISTINCT id_pregunta from crespuestas where curso=%s',curso)
        preguntas = cur.fetchall()
        for pregunta in preguntas:
            cur.execute('select cuestionario, round(AVG (respuesta),1) from preguntas p,crespuestas c where c.id_pregunta=%s and curso=%s and c.id_pregunta= p.id_pregunta',(pregunta[0],curso))
            promed = cur.fetchall()
            promedios.append(promed)
        print(promedios)
        return render_template("resultadocurso.html",cursos=nomcurso,promedios=promedios)

@app.route("/resultados", methods= ['GET','POST'])
def resultados():
    cur=mysql.get_db().cursor()
    cur.execute('select * from T_cursos')
    data = cur.fetchall()
    cur=mysql.get_db().cursor()
    cur.execute('select round(AVG (respuesta),1) from crespuestas where curso=1')
    promedio = cur.fetchall()
    cur=mysql.get_db().cursor()
    cur.execute('select round(AVG (respuesta),1) from crespuestas where curso=2')
    promedio1 = cur.fetchall()
    cur=mysql.get_db().cursor()
    cur.execute('select round(AVG (respuesta),1) from crespuestas where curso=3')
    promedio2 = cur.fetchall()
    cur=mysql.get_db().cursor()
    cur.execute('select round(AVG (respuesta),1) from crespuestas where curso=4')
    promedio3 = cur.fetchall()
    return render_template("resultados.html",resultados=data,promedio=promedio,promedio1=promedio1,promedio2=promedio2,promedio3=promedio3) 

@app.route("/home")
def home():
    return render_template("home.html", usuario = "_user1")

@app.route("/")
def inicio():   
    return redirect(url_for("login"))

@app.route("/errores")
def error():
    return render_template("errores.html")

@app.route('/faceid', methods=['GET','POST'])
def faceid():
    if request.method=='POST':
        print ("Analizando foto")
        file= request.files['file']
        filename = secure_filename(file.filename)
        #print(filename)
        #print(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],filename)))
        file.save(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],filename)))
        _url1= open(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],filename)),'rb').read()
        _urls = [_url1]

        _attributes = ['age', 'gender', 'headPose', 'smile', 'facialHair', 'glasses', 'emotion']

        for image in _urls:
            _faces = _client.face.detect_with_stream(image=BytesIO(image),return_face_attributes=_attributes)

            if not _faces:
                raise Exception(
                    'No face detected from image {}'.format(os.path.basename(image)))

            resultados=[]

            for face in _faces:
                print()
                print('Detected face ID from', os.path.basename(image), ':')
                # ID of detected face
                print(face.face_id)
                # Show all facial attributes from the results
                print()
                print('Facial attributes detected:')
                print('Age:', face.face_attributes.age)
                print('Gender:', face.face_attributes.gender)
                print('Smile:', face.face_attributes.smile)
                print('Emotion:', face.face_attributes.emotion)
                
                genero = face.face_attributes.gender
                edad   = face.face_attributes.age
                emocion = face.face_attributes.emotion

                
                enojo= emocion.anger
                desprecio=emocion.contempt
                disgusto=emocion.disgust
                miedo=emocion.fear
                felicidad=emocion.happiness
                neutro=emocion.neutral
                triste=emocion.sadness
                sorpresivo=emocion.surprise
                emociones=[enojo,desprecio,disgusto,miedo,felicidad,neutro,triste,sorpresivo]
                print(enojo)

                
                maxemotion = emociones.index(max(emociones))



                def numbers_to_emotions(argument):
                    switcher = {
                        0: "enojo",
                        1: "desprecio",
                        2: "disgusto",
                        3: "espantado",
                        4: "felicidad",
                        5: "neutral",
                        6: "tristeza",
                        7: "sorprendido"
                    }
                    return switcher.get(argument, "nothing")
                emotion = numbers_to_emotions(maxemotion)
                print(emotion)
                persona=[edad,genero,emotion]
                resultados.append(persona)


                def getRectangle(faceDictionary):
                    rect = faceDictionary.face_rectangle
                    left = rect.left
                    top = rect.top
                    right = left + rect.width
                    bottom = top + rect.height

                    return ((left, top), (right, bottom))

                #response = requests.get(image)
                img = Image.open(BytesIO(image))
                print('Identificando rostros en las imagenes...')
                draw = ImageDraw.Draw(img)
                for face in _faces:
                    draw.rectangle(getRectangle(face), outline='red')

        return json.dumps(resultados,ensure_ascii=False)

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/resulscrum100")
def resulscrum100():
    return render_template("resulscrum100.html")

@app.route("/resulitil100")
def resulitil100():
    return render_template("resulitil100.html")

@app.route("/resulagile100")
def resulagile100():
    return render_template("resulagile100.html")

    
@app.route("/gracias")
def gracias():
    return render_template("gracias.html")

@app.route("/errorzombie")
def errorzombie():
    return render_template("errorzombie.html")

if __name__=="__main__":
    app.run(debug=True)


