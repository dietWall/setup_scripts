
#python with venv needs to be installed (Microsoft Store)

#optional: install latest powershell 
winget install --id Microsoft.PowerShell --source winget

#activate script execution: 
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

#activate virtual environment:
.\.venv\Scripts\activate

#install requirements:
pip install -r .\config\requirements.txt

#there is no shebang for windows implemented yet, so:
.venv\Scripts\python.exe ssh\ssh-keys.py --generate rsa --deploy-to-host <user@host>
