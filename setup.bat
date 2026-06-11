@echo off
REM Setup script for Windows
REM Run: setup.bat

echo ==================================
echo Marketplace System Setup
echo ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found
    exit /b 1
)

echo Prerequisites OK
echo.

REM Backend setup
echo Setting up backend...
cd marketplace-backend

if not exist .env (
    echo Creating .env from .env.example
    copy .env.example .env
    echo WARNING: Edit .env with your configuration
)

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Initializing database...
python init_db.py

echo Backend setup complete!
echo.

REM Seller Portal setup
echo Setting up seller portal...
cd ..\seller-portal

if not exist .env.local (
    echo Creating .env.local from .env.example
    copy .env.example .env.local
)

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo Seller portal setup complete!
echo.

REM Storefront setup
echo Setting up customer storefront...
cd ..\customer-storefront

if not exist .env.local (
    echo Creating .env.local from .env.example
    copy .env.example .env.local
    echo WARNING: Edit .env.local with your Stripe key
)

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo Storefront setup complete!
echo.

echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env files with your configuration
echo 2. Start PostgreSQL and Redis
echo 3. Run backend: cd marketplace-backend && venv\Scripts\activate && python -m uvicorn main:app --reload
echo 4. Run seller portal: cd seller-portal && npm run dev
echo 5. Run storefront: cd customer-storefront && npm run dev
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Seller Portal: http://localhost:5173
echo Storefront: http://localhost:5174
echo.
