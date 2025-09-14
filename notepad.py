# (window) PowerShell의 실행 정책(Execution Policy) 때문에 .ps1 스크립트를 실행하지 못할때
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# .\venv\Scripts\Activate.ps1 

# netstat -ano | findstr :9000

# netstat -ano | findstr :9000 | ForEach-Object {
#     $parts = ($_ -split '\s+')
#     taskkill /PID $parts[-1] /F
# }

# 포트 9000 점유 중인 모든 프로세스 종료
# Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue |
#     Select-Object -ExpandProperty OwningProcess -Unique |
#     ForEach-Object { Stop-Process -Id $_ -Force }

# taskkill /PID 10136 /F


# function Kill-Port {
#   param([int]$Port)
#   $pids = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
#           Select-Object -ExpandProperty OwningProcess -Unique
#   if ($pids) {
#     $pids | ForEach-Object {
#       try { Stop-Process -Id $_ -Force; Write-Host "Killed PID $_" }
#       catch { Write-Host "Skip PID $_: $($_.Exception.Message)" }
#     }
#   } else {
#     Write-Host "No process is listening on port $Port."
#   }
# }

