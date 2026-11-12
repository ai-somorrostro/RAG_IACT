# RAG_IACT

El objetivo de este proyecto educativo es tanto ayudar a estudiantes como aprender el funcionamiento de un rag.

#### Requerimientos previos
4GB minimos de VRAM disponible
Python3.12 o mas

## Instalación y primer uso
Para empezar la instalación haremos `pip install requirements.txt`, esto instalara las dependencias necesarias para que el servicio pueda funcionar correctamente.

Posteriormente iniciaremos por primera vez el RAG con `python3 rag.py` esto convertira nuestro arhcivo PDF a markdown y desde ahi lo indexara. 
Es normal que tarde ya que es un proceso exigente para el hierro.
Cuando termine se abrira una pequeña consola que nos permitira preguntar, desde ahi podremos realizar cualquier consulta que tenga que ver con la ICT y el asistente ser acapaz de contestarnos.

### Backend
El codigo del rag se puede dividir en estos tres apartados explicados:
1. Preparación del markdown
2. Indexación
3. Modelo
