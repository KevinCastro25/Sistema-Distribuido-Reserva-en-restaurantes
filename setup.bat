@echo off
echo ===============================
echo Creando entorno virtual...
echo ===============================
python -m venv venv

echo ===============================
echo Activando entorno virtual...
echo ===============================
call venv\Scripts\activate

echo ===============================
echo Instalando dependencias...
echo ===============================
pip install -r requirements.txt

echo ===============================
echo Listo! Ejecuta con:
echo flask run
