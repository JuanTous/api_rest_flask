from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config

app = Flask(__name__)
CORS(app, resources={r"/users/*": {"origins": "http://localhost:3200"}})
con = MySQL(app)


@app.route('/users/', methods=['POST'])
def add():
    try:
        cursor = con.connection.cursor()
        sql = "insert into usuarios (nombre, apellido, edad) values ('{0}', '{1}', {2})".format(
            request.json['nombre'], request.json['apellido'], request.json['edad'])
        cursor.execute(sql)
        con.connection.commit()
        return jsonify({'message': 'Usuario registrado', 'state': True})
    except Exception as ex:
        return jsonify({'message': 'Error: {}'.format(ex), 'state': False})


@app.route("/users/", methods=['GET'])
def getAll():
    try:
        cursor = con.connection.cursor()
        sql = "select * from usuarios ORDER BY nombre ASC"
        cursor.execute(sql)
        data = cursor.fetchall()
        usuarios = []
        for d in data:
            usuarios.append({'id': d[0], 'nombre': d[1],
                             'apellido': d[2], 'edad': d[3]})
        return jsonify({'message': '{} usuarios encontrados'.format(len(usuarios)), 'responseBody': usuarios, 'state': True})
    except Exception as ex:
        return jsonify({'message': 'Error: {}'.format(ex), 'state': False})


@app.route("/users/<id>", methods=['GET'])
def getById(id):
    response = getUser(id)
    if response != None:
        return jsonify({'message': 'Usuario encontrado', 'responseBody': response, 'state': True})
    else:
        return jsonify({'message': 'Usuario no encontrado', 'state': False})


def getUser(id):
    try:
        cursor = con.connection.cursor()
        sql = "select * from usuarios where id = '{0}'".format(id)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            usuario = {'id': data[0], 'nombre': data[1],
                       'apellido': data[2], 'edad': data[3]}
            return usuario
        else:
            return None
    except Exception as ex:
        raise print(ex)


@app.route('/users/<id>', methods=['PUT'])
def update(id):
    try:
        usuario = getUser(id)
        if usuario != None:
            cursor = con.connection.cursor()
            sql = "update usuarios set nombre='{}', apellido='{}', edad={} where id={}".format(
                request.json['nombre'], request.json['apellido'], request.json['edad'], id)
            cursor.execute(sql)
            con.connection.commit()
            return jsonify({'message': 'Usuario modificado', 'responseBody': request.json, 'state': True})
        else:
            return jsonify({'message': 'Error: No existe tal usuario', 'state': False})
    except Exception as ex:
        return jsonify({'message': 'Error: {}'.format(ex), 'state': False})


@app.route('/users/<id>', methods=['DELETE'])
def delete(id):
    try:
        if getUser(id) != None:
            cursor = con.connection.cursor()
            sql = "delete from usuarios where id={}".format(id)
            cursor.execute(sql)
            con.connection.commit()
            return jsonify({'message': 'Usuario eliminado', 'state': True})
        else:
            return jsonify({'message': 'Error: No se puede eliminar este usuario', 'state': False})
    except Exception as ex:
        return jsonify({'message': 'Error: {}'.format(ex), 'state': False})


def page_not_found(err):
    return jsonify({'ErrorType': str(err), 'state': False})

if __name__ == "__main__":
    app.register_error_handler(404, page_not_found)
    app.config.from_object(config['development'])
    app.run()
