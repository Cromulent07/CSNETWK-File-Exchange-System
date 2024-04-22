pause
start cmd /k "TITLE Server && python server\server.py"
pause && start cmd /c "TITLE Alice && cd client && python client.py"
pause && start cmd /c "TITLE Bob && cd client && python client.py"
pause && start cmd /c "TITLE Charlie && cd client && python client.py"