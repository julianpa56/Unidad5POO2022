from datetime import datetime
import hashlib
from sqlalchemy import desc, update

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
                    return render_template('menu.html')
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
            idusuarioactual= usuario_actual.id
            nueva_receta = Receta(nombre = request.form['nombre'], tiempo = request.form['tiempo'], fecha = datetime.today(), elaboracion = request.form['descripcion'], cantidadmegusta = 0, usuarioid = idusuarioactual)
            db.session.add( nueva_receta )
            db.session.commit()
            cantidad = request.form['cantidad'] 
            return render_template('ingrediente.html', recetaActual = nueva_receta.id, cantidadIngredientes = int(cantidad)) 
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
    # if usuario_actual == -1 and request.method == 'GET': #--------------------------- HABILITAR PARA INICIO DE SESION RESTRINGIDO
    #     return redirect(url_for('login'))
    if request.method == 'GET':
        recetas= Receta.query.order_by(desc(Receta.cantidadmegusta)).limit(5).all()
        return render_template('ranking.html', listarecetas= recetas)

@app.route('/tiempoelaboracion/', methods = ['GET' , 'POST'])
def tiempoelaboracion ():
    # if usuario_actual == -1 and request.method == 'GET': #--------------------------- HABILITAR PARA INICIO DE SESION RESTRINGIDO
    #     return redirect(url_for('login'))
    if request.method == 'POST':
        tiempo= int(request.form['tiempolimite'])
        recetas= Receta.query.filter(Receta.tiempo <= tiempo).all()  
        return render_template('portiempo.html', listaRecetas= recetas,condicion= True)
    return render_template('portiempo.html',condicion= False)

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
    # if usuario_actual == -1 and request.method == 'GET': #--------------------------- HABILITAR PARA INICIO DE SESION RESTRINGIDO
    #     return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('menu.html')

@app.route('/megusta/', methods = ['GET', 'POST'])
def megusta ():
    # if usuario_actual == -1 and request.method == 'GET': #--------------------------- HABILITAR PARA INICIO DE SESION RESTRINGIDO
    #     return redirect(url_for('login'))
    if request.method == 'POST':
        receta= Receta.query.filter_by(id = request.form['idreceta']).first()
        actualizacion = (update(Receta)
            .where(Receta.id == receta.id)
            .values(cantidadmegusta=Receta.cantidadmegusta + 1)
            )
        db.session.execute(actualizacion)
        db.session.commit()
        return render_template('aviso.html', mensaje= 'Me gusta agregado')
    else:
        dato = db.session.query(Receta).order_by(Receta.nombre)
        return render_template('megusta.html', listaRecetas = dato)

@app.route('/mostrar/', methods = ['GET', 'POST'])
def mostrar ():
    # if usuario_actual == -1 and request.method == 'GET': #--------------------------- HABILITAR PARA INICIO DE SESION RESTRINGIDO
    #     return redirect(url_for('login'))
    if request.method == 'POST':
        receta= Receta.query.filter_by(id = request.form['idreceta']).first()
        usuario= Usuario.query.filter_by(id = receta.usuarioid).first()
        ingredientes= Ingrediente.query.filter_by(recetaid= receta.id).all()
        idusuario= usuario_actual.id
        return render_template ('mostrar.html', receta= receta, usuario= usuario, listaIngredientes= ingredientes, usuarioActual=idusuario)
    
@app.route('/poringrediente/', methods = ['GET', 'POST'])
def poringrediente ():
    # if usuario_actual == -1 and request.method == 'GET': #--------------------------- HABILITAR PARA INICIO DE SESION RESTRINGIDO
    #     return redirect(url_for('login'))
    if request.method == 'POST':
        listaIngredientes= Ingrediente.query.filter_by(nombre= request.form['nombreingrediente']).all()
        listaRecetas=[]
        auxlista=[]
        for ing in listaIngredientes:
            auxlista.append(int(ing.recetaid))
        print(auxlista)
        for aux in auxlista:
            receta= Receta.query.filter(Receta.id == aux).first()
            listaRecetas.append(receta)
        return render_template('poringrediente.html',listaRecetas= listaRecetas, condicion = True)
    return render_template('poringrediente.html',condicion= False)




if __name__ == '__main__':
    app.run(debug = True)
    