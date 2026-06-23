SET mypath=%~dp0
cd %mypath:~0,-1%\..\..\server && pipenv run python console.py extract_history london
cd %mypath:~0,-1%\..\..\server && pipenv run python console.py extract_history beijing