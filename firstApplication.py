from flask import Flask, render_template

app= Flask(__name__)


@app.route('/')
def saludo():
    return 'Saludo desde aplicacion Flask'

@app.route('/inicio/')
def inicio():
    return render_template('inicio.html')

@app.route('/template/')
def template():
    return render_template('inicio.html')
    # pass

@app.route('/inicio-sesion/')
def inicioSesion():
    return render_template('iniciar_sesion.html')

if __name__=='__main__':
    app.run(debug=True)