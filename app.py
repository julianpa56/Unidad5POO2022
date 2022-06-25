from datetime import datetime
import hashlib

from flask import Flask, request, render_template, Response, flash, get_flashed_messages, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' #flash 
usuario_actual = ''

from Clases import db
from Clases import Usuario, Receta, Ingrediente

@app.route('/') #ruta raiz
def index ():
    global usuario_actual
    usuario_actual= -1
    return render_template('principal.html')

@app.route('/login/', methods = [ 'GET', 'POST' ])
def login ():
    global usuario_actual
    if request.method == 'POST':
        if not request.form[ 'email' ] or not request.form[ 'password' ]:
            return render_template('error.html', mensaje = 'Los datos no son correctos')
        else:
            usuario_actual = Usuario.query.filter_by(correo = request.form['email']).first()
            if usuario_actual is None:
                return render_template('error.html', error = 'El correo no esta registrado', tipoError= 'login')
            else:
                verificacion = hashlib.md5(bytes(request.form['password'], encoding = 'utf-8'))
                if (usuario_actual.clave == verificacion.hexdigest()):
                    return render_template('receta.html', usuarioActual = usuario_actual.id)
                else:
                    return render_template('error.html', error = 'La contraseña no es valida', tipoError= 'login')
    else:
        return render_template('login.html')

@app.route('/receta/', methods = [ 'GET', 'POST' ])
def receta ():
    if usuario_actual == -1 and request.method == 'GET':
        return redirect(url_for('login'))
    if request.method == 'POST':
        print(request.form['nombre'])
        if not request.form['nombre'] or not request.form['tiempo'] or not request.form['descripcion']:
            return render_template('error.html', error='Contenido no ingresado')
        else:
            nueva_receta = Receta(nombre = request.form['nombre'], tiempo = request.form['tiempo'], fecha = datetime.today(), elaboracion = request.form['descripcion'], cantidadmegusta = 0, usuarioid = request.form['usuario_id'])
            db.session.add( nueva_receta )
            db.session.commit()
            flash('Receta agregada exitosamente')
            cantidad = request.form['cantidad'] #obtengo la cantidad de ingredientes que se ingreso en el form
            #receta_actual = Receta.query.filter_by(nombre = request.form['nombreReceta']).first()
            return render_template('ingrediente.html', recetaActual = nueva_receta.id, cantidadIngredientes = int(cantidad)) #le envio al html para usar el for
    else:
        return render_template('receta.html')

@app.route('/ingrediente/', methods = [ 'GET', 'POST' ])
def ingrediente ():
    i = 0
    if usuario_actual == -1 and request.method == 'GET':
        return redirect(url_for('login'))
    if request.method == 'POST':
        nroIngredientes= int(request.form['cantidadIngredientes'])
        for i in range(nroIngredientes):
            aux='nombreIngrediente'+str(i)
            aux2='cantidad'+str(i)
            aux3='unidad'+str(i)
            if not request.form[aux] or not request.form[aux2] or not request.form[aux3]:
                return render_template('error.html', error='Contenido no ingresado')
            else:
                if request.form[aux] is not None and request.form[aux2] is not None and request.form[aux3] is not None:
                    nuevo_ingrediente = Ingrediente(nombre = request.form[aux], cantidad = request.form[aux2], unidad = request.form[aux3], recetaid = request.form['receta_id'])
                    db.session.add( nuevo_ingrediente )
                    db.session.commit()
        return render_template('aviso.html', mensaje='Ingredientes agregados')
    return render_template('ingrediente.html') 

@app.route('/ranking/', methods = ['GET'])
def ranking ():
    # if usuario_actual == -1 and request.method == 'GET': # --------------------------------- VERIFICACION PARA NO INGRESAR SI NO ESTA LOGGEADO
    #     return redirect(url_for('login'))
    if request.method == 'GET':
        recetas= Receta.query.order_by(Receta.cantidadmegusta).limit(5).all()
        return render_template('ranking.html', listarecetas= recetas)

@app.route('/tiempoelaboracion/', methods = ['GET' , 'POST'])
def tiempoelaboracion ():
    # if usuario_actual == -1 and request.method == 'GET':
    #     return redirect(url_for('login'))
    if request.method == 'POST':
        tiempo= int(request.form['tiempolimite'])
        recetas= Receta.query.order_by(Receta.tiempo <= tiempo).all() # ----------------------- HAY QUE ARREGLAR EL FILTRADO 
        return render_template('portiempo.html', listarecetas= recetas)
    return render_template('portiempo.html')

@app.route('/poringrediente/', methods = ['GET'])
def poringrediente ():
    # if usuario_actual == -1 and request.method == 'GET':
    #     return redirect(url_for('login'))
    if request.method == 'GET':
        recetas= Receta.query.order_by(Receta.cantidadmegusta).limit(5).all()
        return render_template('ranking.html', listarecetas= recetas)

@app.route('/logout/', methods = ['GET'])
def logout ():
    global usuario_actual
    if usuario_actual != -1:
        usuario_actual = -1
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/menu/', methods = ['GET'])
def menu ():
    # if usuario_actual == -1 and request.method == 'GET':
    #     return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('menu.html')


if __name__ == '__main__':
    app.run(debug = True)
    