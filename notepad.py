# (window) PowerShell의 실행 정책(Execution Policy) 때문에 .ps1 스크립트를 실행하지 못할때
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# .\venv\Scripts\Activate.ps1 

# netstat -ano | findstr :9000
# Get-Process -Id (Get-NetTCPConnection -LocalPort 9000).OwningProcess | Stop-Process -Force
