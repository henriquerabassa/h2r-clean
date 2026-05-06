@echo off
:: Script de instalação do H2R-Clean para Windows
:: Autor: File Organizer Team
:: Versão: 1.0

setlocal enabledelayedexpansion

echo [INFO] Iniciando instalação do H2R-Clean para Windows...
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [WARNING] Detectada execução como administrador.
    echo [INFO] Recomendado executar como usuário normal para instalação no perfil do usuário.
    pause
)

:: Verificar Python
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python não encontrado!
    echo [INFO] Por favor, instale o Python em https://www.python.org/downloads/
    echo [INFO] Certifique-se de marcar "Add Python to PATH" durante a instalação.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo [INFO] Python encontrado: %%i
)

:: Verificar pip
echo [INFO] Verificando pip...
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] pip não encontrado!
    echo [INFO] Instalando pip...
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip
) else (
    for /f "tokens=1,2" %%i in ('pip --version') do echo [INFO] pip encontrado: %%i %%j
)

:: Criar diretórios de instalação
echo [INFO] Criando diretórios de instalação...
set "APP_DIR=%APPDATA%\H2RClean"
set "BIN_DIR=%APPDATA%\H2RClean\bin"
set "START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\H2RClean"

if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
if not exist "%START_MENU_DIR%" mkdir "%START_MENU_DIR%"

:: Instalar arquivos do aplicativo
echo [INFO] Copiar ícone pré-criado
if exist "icons\h2r_clean_v2_128x128.png" (
    copy "icons\h2r_clean_v2_128x128.png" "%APP_DIR%\icon.png" >nul
    echo [INFO] Ícone H2R-Clean v2 copiado com sucesso
) else if exist "icons\h2r_clean_v2.ico" (
    copy "icons\h2r_clean_v2.ico" "%APP_DIR%\icon.ico" >nul
    echo [INFO] Ícone H2R-Clean v2 copiado com sucesso
)

:: Instalar arquivos do aplicativo
echo [INFO] Instalando arquivos do aplicativo...
copy "file_organizer.py" "%APP_DIR%\" >nul
if exist "requirements.txt" copy "requirements.txt" "%APP_DIR%\" >nul

:: Instalar dependências Python
if exist "%APP_DIR%\requirements.txt" (
    echo [INFO] Instalando dependências Python...
    pip install -r "%APP_DIR%\requirements.txt"
)

:: Criar script de execução principal
echo [INFO] Criando atalhos...
(
echo @echo off
echo cd /d "%APP_DIR%"
echo python file_organizer.py %%*
) > "%BIN_DIR%\h2r-clean.bat"

:: Criar script CLI
(
echo @echo off
echo cd /d "%APP_DIR%"
echo python file_organizer.py --cli %%*
) > "%BIN_DIR%\h2r-clean-cli.bat"

:: Criar atalho no menu iniciar
echo [INFO] Criando atalho no menu iniciar...
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU_DIR%\H2R-Clean.lnk'); $Shortcut.TargetPath = '%BIN_DIR%\h2r-clean.bat'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = 'shell32.dll,14'; $Shortcut.Description = 'Sistema de limpeza e otimização de arquivos'; $Shortcut.Save()}"

:: Criar atalho CLI no menu iniciar
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU_DIR%\H2R-Clean CLI.lnk'); $Shortcut.TargetPath = '%BIN_DIR%\h2r-clean-cli.bat'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = 'shell32.dll,25'; $Shortcut.Description = 'H2R-Clean - Modo CLI'; $Shortcut.Save()}"

:: Criar script de desinstalação
echo [INFO] Criando script de desinstalação...
(
echo @echo off
echo echo Desinstalando H2R-Clean...
echo.
echo if exist "%APP_DIR%" rmdir /s /q "%APP_DIR%"
echo if exist "%START_MENU_DIR%" rmdir /s /q "%START_MENU_DIR%"
echo.
echo set /p "confirm=Deseja remover tambem as configuracoes? (s/N): "
echo if /i "!confirm!"=="s" (
echo     if exist "%USERPROFILE%\.h2r_clean" rmdir /s /q "%USERPROFILE%\.h2r_clean"
echo )
echo.
echo echo H2R-Clean desinstalado com sucesso!
echo pause
) > "%APP_DIR%\uninstall.bat"

:: Adicionar ao PATH do usuário (opcional)
echo [INFO] Configurando ambiente...
setx PATH "%PATH%;%BIN_DIR%" >nul 2>&1

:: Testar instalação
echo [INFO] Testando instalação...
cd /d "%APP_DIR%"
python file_organizer.py --help >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Teste de instalação bem-sucedido!
) else (
    echo [WARNING] Teste falhou, mas a instalação pode continuar
)

:: Criar ícone (simples)
echo [INFO] Criando ícone do aplicativo...
powershell -Command "& Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap 128, 128; $graphics = [System.Drawing.Graphics]::FromImage($bmp); $graphics.Clear([System.Drawing.Color]::Blue); $graphics.FillRectangle([System.Drawing.Brushes]::White, 20, 30, 88, 70); $graphics.FillRectangle([System.Drawing.Brushes]::Gray, 20, 30, 30, 20); $bmp.Save('%APP_DIR%\icon.png', [System.Drawing.Imaging.ImageFormat]::Png); $graphics.Dispose(); $bmp.Dispose()" 2>nul

:: Atualizar atalhos com ícone se foi criado
if exist "%APP_DIR%\icon.png" (
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU_DIR%\H2R-Clean.lnk'); $Shortcut.IconLocation = '%APP_DIR%\icon.png'; $Shortcut.Save()}"
)

echo.
echo [INFO] Instalação concluída com sucesso!
echo.
echo Para executar o aplicativo:
echo   • Modo grafico: Procure por "H2R-Clean" no menu iniciar
echo   • Modo CLI: Procure por "H2R-Clean CLI" no menu iniciar
echo   • Ou execute: h2r-clean.bat
echo.
echo Para desinstalar: %APP_DIR%\uninstall.bat
echo.
echo [WARNING] Se os comandos não forem reconhecidos, reinicie o prompt de comando.
echo.
pause
