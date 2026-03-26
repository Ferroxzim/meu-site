import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "123456"

# criar banco
def init_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade INTEGER,
            email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            senha TEXT
        )
    ''')

    # cria login padrão
    cursor.execute("SELECT * FROM login")
    if not cursor.fetchall():
        cursor.execute("INSERT INTO login (usuario, senha) VALUES (?, ?)", ("admin", "123"))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'logado' not in session:
        return redirect('/login')

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    return render_template('index.html', usuarios=usuarios)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login WHERE usuario=? AND senha=?", (usuario, senha))
        result = cursor.fetchone()
        conn.close()

        if result:
            session['logado'] = True
            return redirect('/')
        else:
            return "Login inválido"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logado', None)
    return redirect('/login')

@app.route('/add', methods=['POST'])
def add_usuario():
    if 'logado' not in session:
        return redirect('/login')

    nome = request.form['nome']
    idade = request.form['idade']
    email = request.form['email']

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, idade, email) VALUES (?, ?, ?)",
                   (nome, idade, email))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/delete/<int:id>')
def delete_usuario(id):
    if 'logado' not in session:
        return redirect('/login')

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
