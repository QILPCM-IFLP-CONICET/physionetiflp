"""
Rutinas para importar y  exportar los registros.
"""

import csv
import os
from urllib import request
from urllib.error import HTTPError

import pandas as pd
import pyedflib as plib
from pyedflib import highlevel
from scipy.io import savemat

SRC_URL_FORMAT = (
    "https://physionet.org/files/eegmmidb/1.0.0"
    "/{paciente_id}/{paciente_id}{registro_id}.edf"
)


def descargar_paciente_registro(paciente_id, registro_id, path):
    """
    Descarga un registro asociado a un paciente
    paciente_id: str
        el identificador de paciente (Ej, "S002").
    registro_id: str
        el identificador del registro (Ej, "R03").
    path: str
        la ruta donde se guardará el registro.
    """
    try:
        url = SRC_URL_FORMAT.format(paciente_id=paciente_id, registro_id=registro_id)
        print(url)
        handler = request.build_opener(request.HTTPCookieProcessor).open(
            url,
        )
    except HTTPError as e:
        print(e)
        print("paciente o registro no encontrado")
        return None

    while path[-1] == "/":
        path = path[:-1]

    path = f"{path}/{paciente_id}/{paciente_id}{registro_id}.edf"
    with open(path, "wb") as f:
        f.write(handler.read())
        handler.close

    return path


def dic_elemento_a_ruta_elemento(
    ruta, condicion="elemento[0]=='S' and len(elemento)==4", verbo=None
) -> dict:
    """
    Crea un diccionario con los identificadores de los pacientes como clave,
    y la ruta de la carpeta con los registros como argumento.

    """
    elementos_todos = os.listdir(ruta)
    dic_elemento_ruta = {}

    for elemento in elementos_todos:
        if eval(condicion):  # Evaluar la condición pasada como argumento
            if verbo is not None:
                verbo(elemento)
            dic_elemento_ruta[elemento] = os.path.join(
                ruta, elemento
            )  # os.sep reemplazado por os.path.join

    return dic_elemento_ruta


def lista_elemento_en_ruta(ruta, condicion="1", verbo=None) -> list:
    """
    Devuelve una lista con los nombres de los archivos y carpetas
    compatibles con `condicion`.
    """
    elementos_todos = os.listdir(ruta)
    elementos = []

    for elemento in elementos_todos:
        if eval(condicion):  # Evaluar la condición pasada como argumento
            if verbo is not None:
                verbo(elemento)
            elementos.append(elemento)
    return elementos


def obtener_dic_rutas(ruta_dataset) -> dict:
    """
    A partir de una ruta, construye un diccionario
    que tiene como claves los identificadores de paciente,
    y como elementos diccionarios asociados a los registros
    de ese paciente.
    """
    dic_pacientes_ruta = dic_elemento_a_ruta_elemento(ruta_dataset)
    dic_paciente_dic_records_ruta = {}
    for elemento, ruta in dic_pacientes_ruta.items():
        dic_paciente_dic_records_ruta[elemento] = {}
        for records, ruta_records in dic_elemento_a_ruta_elemento(
            ruta, condicion="elemento.endswith('.edf')"
        ).items():
            dic_paciente_dic_records_ruta[elemento][records[4:-4]] = ruta_records
    return dic_paciente_dic_records_ruta


def guardar_arrays_en_mat(arrays, nombres, carpeta_destino):
    """
    Exporta un conjunto de arrays en archivos .mat (matlab)
    en  `carpeta_destino`
    """
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    for array, nombre in zip(arrays, nombres):
        nombre_archivo = os.path.join(carpeta_destino, f"{nombre}.mat")
        savemat(nombre_archivo, {nombre: array})
        # print(f"Guardado: {nombre_archivo}", end="\r")


def guardar_diccionario_en_csv(diccionario, nombre_archivo, carpeta_destino):
    """
    Exporta un conjunto de arrays en archivos .mat (matlab)
    en  `carpeta_destino`
    """
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino, exist_ok=True)

    ruta_archivo = os.path.join(carpeta_destino, f"{nombre_archivo}.csv")

    # Obtener las claves del diccionario como nombres de las columnas
    columnas = diccionario.keys()

    # Abrir el archivo y escribir los datos
    with open(ruta_archivo, mode="w", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv)

        # Escribir los nombres de las columnas
        writer.writerow(columnas)

        # Escribir los datos fila por fila
        # (usando zip para agrupar los valores de cada lista)
        writer.writerows(zip(*diccionario.values()))

    # print(f"Guardado: {ruta_archivo}", end="\r")


class DatosRI:
    """
    Tabla de datos asociados a una ruta.
    """

    def __init__(self, ruta):
        self.ruta = ruta
        self.dic_rutas = obtener_dic_rutas(self.ruta)
        self._tabla = self.nueva_tabla()

    def nueva_tabla(self, verbo=None):
        """
        Genera una tabla y la almacena en el atributo `self.tabla`
        """
        dic_rutas = self.dic_rutas
        rec_base = [
            "R01",
            "R02",
            "R03",
            "R04",
            "R05",
            "R06",
            "R07",
            "R08",
            "R09",
            "R10",
            "R11",
            "R12",
            "R13",
            "R14",
        ]
        tipo_base = [
            "baseline",
            "baseline",
            "Realizada",
            "Imaginada",
            "Realizada",
            "Imaginada",
            "Realizada",
            "Imaginada",
            "Realizada",
            "Imaginada",
            "Realizada",
            "Imaginada",
            "Realizada",
            "Imaginada",
        ]
        accion_base = [
            "None",
            "None",
            "1",
            "1",
            "2",
            "2",
            "1",
            "1",
            "2",
            "2",
            "1",
            "1",
            "2",
            "2",
        ]

        dic_tipos = dict(zip(rec_base, tipo_base))
        dic_acciones = dict(zip(rec_base, accion_base))

        pacientes = []
        num_pacientes = []
        records = []
        tipos = []
        acciones = []
        tiempos = []
        duraciones = []
        descripciones = []

        for paciente in list(dic_rutas.keys()):
            for record in dic_rutas[paciente].keys():
                ruta_edf = dic_rutas[paciente][record]
                archivo_edf = plib.EdfReader(ruta_edf)

                (tiempos_r, duraciones_r, descripciones_r) = (
                    archivo_edf.readAnnotations()
                )
                archivo_edf.close()
                for tiempo, duracion, descripcion in zip(
                    tiempos_r, duraciones_r, descripciones_r
                ):

                    records.append(record)
                    pacientes.append(paciente)
                    num_pacientes.append(int(paciente[1:]))

                    tipo = dic_tipos[record]
                    tipos.append(tipo)

                    accion = dic_acciones[record]
                    acciones.append(accion)

                    tiempos.append(tiempo)
                    duraciones.append(duracion)
                    descripciones.append(descripcion)

        # print(len(pacientes),len(records), len(tipos),
        # len(acciones), len( tiempos), len(duraciones), len(descripciones))

        tabla = {
            "paciente": pacientes,
            "numero_paciente": num_pacientes,
            "record": records,
            "tipo": tipos,
            "accion": acciones,
            "tiempo": tiempos,
            "duracion": duraciones,
            "descripcion": descripciones,
        }
        tabla_df = pd.DataFrame(tabla)
        if verbo is not None:
            verbo(tabla_df)
        self.tabla = tabla_df

    def filtrar(self, queryF="", verbo=None):
        """
        Filtra elementos de la tabla de acuerdo a
        queryF.
        """
        tabla = self.tabla
        if queryF != "":
            tabla = tabla.query(queryF)

        self.tabla = tabla
        if verbo is not None:
            verbo(tabla)

    def unicos(self):
        tabla = self.tabla
        return {col: tabla[col].unique() for col in tabla.columns}

    def armar_dataset(self, duracion_max_recorte=""):
        tabla = self.tabla
        dic_rutas = self.dic_rutas

        temp_pr = ""

        data = []

        for i, paciente, record, tiempo, duracion in zip(
            range(len(tabla["paciente"])),
            tabla["paciente"],
            tabla["record"],
            tabla["tiempo"],
            tabla["duracion"],
        ):

            if temp_pr != paciente + record:
                temp_pr = paciente + record
                signals, signal_headers, header = highlevel.read_edf(
                    dic_rutas[paciente][record]
                )

            fs = signal_headers[0]["sample_frequency"]

            duracion = duracion_max_recorte if duracion_max_recorte != "" else duracion

            t_start = int(tiempo * fs)
            t_end = int((tiempo + duracion) * fs)
            recorte = signals[:, t_start:t_end]

            data.append(recorte)

        labels = tabla.to_dict(orient="list")
        return data, labels
