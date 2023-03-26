@echo off

echo Running the BackEnd
start cmd /c "cd /d %~dp0 && uvicorn main:app --reload"

echo Waiting for backend to start...
timeout /t 5

echo Running FrontEnd Angular CLI...
start cmd /c "cd /d %~dp0AmzAnalysisApplication && npm i && ng serve"

echo Done.
pause