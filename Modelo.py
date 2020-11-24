from flask import Flask, render_template, request, json,session
from flaskext.mysql import MySQL
import Modelo as Modelo
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MYSQL_DATABASE_USER'] = 'sepherot_omar'
app.config['MYSQL_DATABASE_PASSWORD'] = 'BAg2v4tk5h'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_omarBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)

app.secret_key="holayadios"

def insertarLectura(_nombre, _apellidos, _correo, _numcliente):
    try:
        if _nombre and _apellidos and _correo and _numcliente:
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="T_clientes"
            sqlDropProcedure="DROP PROCEDURE IF EXISTS InsertLecturas;"
            cursor.execute(sqlDropProcedure)
            sqlCreateSP="CREATE PROCEDURE InsertLecturas(IN Pnumcliente VARCHAR(200),IN Pnombre VARCHAR(200),IN Papellidos VARCHAR(100), IN Pemail VARCHAR(200), IN Ptelefono int(200)) INSERT INTO "+_TABLA+"( numcliente,nombre, apellidos, email) VALUES (Pnumcliente,Pnombre, Papellidos, Pemail)"
            cursor.execute("CREATE TABLE IF NOT EXISTS `sepherot_omarBD`.`"+_TABLA+"` ( `idclientes` INT NOT NULL AUTO_INCREMENT , `numcliente` VARCHAR(60) NOT NULL ,`nombre` VARCHAR(60) NOT NULL , `apellidos` VARCHAR(60) NOT NULL ,`email` VARCHAR(60) NOT NULL ,  PRIMARY KEY (`ID`)) ENGINE = InnoDB;")
            cursor.execute(sqlCreateSP)
            cursor.callproc('InsertLecturas',(_numcliente,_nombre, _apellidos, _correo))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'Clientes registrados correctamente !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
       cursor.close() 
       conn.close()

def selectALLLecturas():
    try:
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('select * from T_clientes order by idclientes')
        eventos=cursor.fetchall()
        return eventos
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()



def cuestionario(_pregunta1,_pregunta2,_pregunta3,_pregunta4,_pregunta5):
    try:
        conn=mysql.connect()
        cursor=conn.cursor()
        _cuesti=cursor.execute('select * from preguntas order by id_pregunta')
        print(_cuesti)
        conn.commit()
        return "success"
    except Exception as e:
            return json.dumps({'error':str(e)})
    finally:
       cursor.close() 
       conn.close()
        

def login(_user1,_pass):
    try:
        conn=mysql.connect()
        cursor=conn.cursor()
        _resultado= cursor.execute('select id,user,email,password from users where user = %s',_user1)
        _datos=cursor.fetchall()
        if _pass == _datos[0][3]:
            session['name']=_datos[0][1]
            print("informacion correcta")
            return _datos
        else:
            print("incorrecto")    
            return False
    except:
       print("salio mal")
    return False

def encuesta(SERCHT):
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('select * from preguntas where id_pregunta = %s',SERCHT)
        preguntas=cursor.fetchall()
        return preguntas

def register(_user,_email,_pass1):
    try:           
        conn=mysql.connect()
        cursor=conn.cursor()
        _result=cursor.execute('insert into users (user,email,password) values (%s,%s,%s)', (_user,_email,_pass1))
        print(_result)
        cursor.execute(_result)
        conn.commit()
        return "success"
    except Exception as a:
            return json.dumps({'error':str(a)})
    finally:
        cursor.close() 
        conn.close()

def union():
    try:           
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT a.id_respuesta,a.id_pregunta,b.id_pregunta,a.respuesta from crespuestas a,preguntas b where a.id_pregunta = b.id_pregunta')
        _hola=cursor()
        conn.commit()
    except:
       print("salio mal")
    return False

def entities(user,stage,info):
    conn=mysql.connect()
    cursor = conn.cursor()
    query = "insert into eventos (user, stage, stage_info) values (%s,%s,%s)"
    try:
        done=cursor.execute(query,(user,stage, info))
        if done:
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False
    cursor.close()
    conn.close()


        

if __name__=="__main__":
    app.run(debug=True)