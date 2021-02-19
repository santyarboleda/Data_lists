# Automatización de consultas en listas restrictivas para delitos relacionados con LAFT

Esta aplicación se construyó como propuesta de solución para el trabajo de grado: "Automatización de consultas de terceros en listas restrictivas para delitos relacionados con lavado de Activos y Financiación del terrorismo" para optar por el título de Magister en Ingeniería - Analítica, trabajo dirigido por el Doctor Juan David Velásquez, Profesor Titular del Departamento de Ciencias de la Computación y la Decisión, Facultad de Minas, Universidad Nacional de Colombia.

Las listas que se consultan son las siguientes:

- Lista de terroristas de la Unión Europea
- Lista de Organizaciones Terroristas del Extranjero del Departamento de Estado de Estados Unidos
- Lista OFAC - Clinton
- Lista de las Naciones Unidas
- Lista de proveedores ficticios en Colombia
- Lista PEPs en Colombia

# Consultas en las bases de datos

Dado que las bases de datos tienen diferentes formatos, y contienen información de los terceros solo de nombres, nombres e identificación, nombres y pasaportes y nombres en diferente orden (nombres y apellidos - apellidos y nombres), se presenta la siguiente imagen como resumen de estos casos y la integracion de cada lista en la aplicación:

![Screenshot](Fuentes%20de%20datos.png)


# Instalación

La aplicación ha sido contenerizado mediante docker.


### Pre-requisitos

Tener instalado docker en la máquina donde se va a desplegar

Tamaño de la imagen: 799.35 MB

### Ejecución

Ejecutar en la consola el siguiente comando:

`
docker pull sarboledaq/laft_lists:latest
`

Posterioremente, debe ser desplegado un contenedor usando el siguiente comando:

`
docker run -d -p 3000:3000 sarboledaq/laft_lists
`

Una vez se haya desplegado el contenedor, se puede acceder a la aplicación a traves del siguiente enlace en el navegador:

`
http://localhost:3000/
`

Para verificar la programación de las extracciones, se debe ingresar en bash al contenedor desplegado, se puede hacer con el siguiente comando:

`
docker container exec -it nombre_contenedor bash
`

Una vez se ingresa a la consola, ejecutar el siguiente comando:

`
crontab -l
`

Debe aparecer como resultado lo siguiente:

`
1 5 * * * python3 update_lists.py
`






**Trabajo desarrollado por:** Santiago Arboleda Quiroz.

**Email:** sarboledaq@unal.edu.co

**© Copyright 2021, Santiago Arboleda**
