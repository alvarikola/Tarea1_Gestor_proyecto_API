from crypt import methods

import psycopg2
from flask import Flask, jsonify, request


# Álvaro
# Lista de métodos TODO
# Login
# Crear proyecto
# Asignar gestor a proyecto
# Asignar cliente a proyecto
# Crear tareas a proyecto (debo estar asignado)
# Asignar programador a proyecto
# Asignar programadores a tareas
# Obtener programadores
# Obtener proyectos (activos o todos)
# Obtener tareas de un proyecto (sin asignar o asignada)
app = Flask(__name__)

def ejecutar_sql(sql_text):
    host = "localhost"
    port = "5432"
    dbname = "alexsoft"
    user = "postgres"
    password = "postgres"

    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            options="-c search_path=public"
        )
        # Crear un cursor para ejecutar
        cursor = connection.cursor()

        # Consulta SQL (por ejemplo, selecciona todos los registros de una tabla llamada usuarios)
        cursor.execute(sql_text)

        if "UPDATE" in sql_text:
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'msg': 'actualizado'})


        if "INSERT" in sql_text:
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'msg': 'insertado'})

        # Obtener columnas para contruir claves del JSON
        columnas = [desc[0] for desc in cursor.description]

        # Convertir resultados a JSON
        resultados = cursor.fetchall()
        empleados = [dict(zip(columnas, fila)) for fila in resultados]

        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()

        return jsonify(empleados)

    except psycopg2.Error as e:
        print("error", e)


@app.route('/hola_mundo', methods=['GET'])
def hola_mundo():
    return jsonify({ "msg": "Hola, mundo!" })


@app.route('/empleado/empleados', methods=['GET'])
def obtener_lista_empleados():
    resultado1 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Gestor\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Gestor" g ON e.id = g.empleado;'
    )
    resultado2 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Programador\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Programador" p on e.id = p.empleado;'
    )

    resultadoFinal = resultado1.json + resultado2.json

    return jsonify(resultadoFinal)

@app.route('/proyecto/proyectos', methods=['GET'])
def obtener_proyectos():
    return ejecutar_sql(
        'SELECT * FROM public."Proyecto";'
    )


@app.route('/proyecto/proyectos_activos', methods=['GET'])
def obtener_proyectos_activos():
    return ejecutar_sql(
        'SELECT nombre, descripcion, fecha_creacion, fecha_inicio, cliente FROM public."Proyecto" WHERE fecha_finalizacion is null OR fecha_finalizacion >= CURRENT_TIMESTAMP;'
    )


@app.route('/proyecto/proyectos_gestor', methods=['GET'])
def obtener_proyectos_gestor_id():

    empleado_id = request.args.get('id')

    return ejecutar_sql(
        f'SELECT * FROM public."Proyecto" p INNER JOIN public."GestoresProyecto" gp ON p.id = gp.proyecto where gp.gestor = {empleado_id};'
    )

@app.route('/login', methods=['POST'])
def gestor_login():
    body_request = request.json
    user = body_request["usuario"]
    passwd = body_request["passwd"]

    is_logged = ejecutar_sql(
        f"SELECT * FROM public.\"Gestor\" WHERE usuario = '{user}' AND passwd = '{passwd}';"
    )

    if len(is_logged.json) == 0:
        return jsonify({"msg": "No mi rey así no"})
    empleado = ejecutar_sql(
        f"SELECT * FROM public.\"Empleado\" WHERE id = '{is_logged.json[0]["empleado"]}';"
    )

    return jsonify(
        {
            "id_empleado": empleado.json[0]["id"],
            "id_gestor": is_logged.json[0]["id"],
            "nombre": empleado.json[0]["nombre"],
            "email": empleado.json[0]["email"]
        }
    )


@app.route('/proyecto/crear_proyecto', methods=['POST'])
def crear_proyectos():
    body_request = request.json
    nombre = body_request["nombre"]
    descripcion = body_request["descripcion"]
    fecha_creacion = body_request["fecha_creacion"]
    fecha_inicio = body_request["fecha_inicio"]
    cliente = body_request["cliente"]
    sql = f"""
        INSERT INTO public."Proyecto" (nombre, descripcion, fecha_creacion, fecha_inicio, cliente)
        VALUES (
            '{nombre}',
            '{descripcion}',
            '{fecha_creacion}',
            '{fecha_inicio}',
            {cliente}
        )
    """
    return jsonify(ejecutar_sql(sql))


@app.route('/proyecto/asignar_gestor_proyecto', methods=['POST'])
def asignar_gestor_proyecto():
    body_request = request.json
    gestor = body_request["gestor"]
    proyecto = body_request["proyecto"]
    sql = f"""
            INSERT INTO public."GestoresProyecto" (gestor, proyecto, fecha_asignacion)
            VALUES (
                {gestor},
                {proyecto},
                NOW()
            )
        """
    return jsonify(ejecutar_sql(sql))


@app.route('/proyecto/asignar_cliente_proyecto', methods=['POST'])
def asignar_cliente_proyecto():
    body_request = request.json
    id_cliente = body_request["id_cliente"]
    id_proyecto = body_request["id_proyecto"]
    sql = f"""
            UPDATE public."Proyecto"
            SET cliente = {id_cliente}
            WHERE id = {id_proyecto}
        """
    return jsonify(ejecutar_sql(sql))



if __name__=='__main__':
    app.run(debug=True)
