SET mypath=%~dp0
cd %mypath:~0,-1%\..\..\server && pipenv run python console.py extract_stations