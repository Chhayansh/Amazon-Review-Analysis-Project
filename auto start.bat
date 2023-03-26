@echo off

echo Installing Node.js...
choco install nodejs -y

echo Installing Angular CLI...
call npm install -g @angular/cli

echo Installing all the dependencies for BackEnd...
pip install --upgrade pip
pip install requests beautifulsoup4 pandas nltk textblob scikit-learn fastapi pydantic fake_useragent  nltk
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('wordnet')"

echo Running the BackEnd
start cmd /c "cd /d %~dp0 && uvicorn main:app --reload"

echo Waiting for backend to start...
timeout /t 5

echo Running FrontEnd Angular CLI...
start cmd /c "cd /d %~dp0AmzAnalysisApplication && npm i && ng serve"

echo Done.
pause
