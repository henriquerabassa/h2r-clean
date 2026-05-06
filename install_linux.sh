#!/bin/bash

# Script de instalação do H2R-Clean para Linux
# Autor: File Organizer Team
# Versão: 1.0

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script não deve ser executado como root!"
        print_info "Execute como usuário normal para instalação no diretório home"
        exit 1
    fi
}

# Verificar dependências
check_dependencies() {
    print_info "Verificando dependências..."
    
    # Verificar Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 não encontrado. Instalando..."
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    else
        print_info "Python3 encontrado: $(python3 --version)"
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 não encontrado. Instalando..."
        sudo apt-get install -y python3-pip
    else
        print_info "pip3 encontrado: $(pip3 --version)"
    fi
    
    # Verificar tkinter
    if ! python3 -c "import tkinter" &> /dev/null; then
        print_warning "tkinter não encontrado. Instalando..."
        sudo apt-get install -y python3-tk
    else
        print_info "tkinter encontrado"
    fi
}

# Criar diretório de instalação
create_install_dir() {
    INSTALL_DIR="$HOME/.local/share/h2r-clean"
    BIN_DIR="$HOME/.local/bin"
    DESKTOP_DIR="$HOME/.local/share/applications"
    
    print_info "Criando diretórios de instalação..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$HOME/.config/h2r-clean"
    mkdir -p "$HOME/.local/share/icons"
}

# Instalar arquivos do aplicativo
install_app() {
    print_info "Instalando arquivos do aplicativo..."
    
    # Copiar arquivo principal
    cp file_organizer.py "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/file_organizer.py"
    
    # Copiar requirements.txt se existir
    if [[ -f "requirements.txt" ]]; then
        cp requirements.txt "$INSTALL_DIR/"
    fi
    
    # Instalar dependências Python
    if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
        print_info "Instalando dependências Python..."
        # Tentar instalar com --user primeiro
        pip3 install --user -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || {
            print_warning "Não foi possível instalar com pip3 --user, tentando com --break-system-packages..."
            pip3 install --user --break-system-packages -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || {
                print_warning "Não foi possível instalar dependências Python automaticamente"
                print_info "Você pode instalar manualmente com: pip3 install --user --break-system-packages -r $INSTALL_DIR/requirements.txt"
            }
        }
    fi
    
    # Criar script de execução
    cat > "$BIN_DIR/h2r-clean" << 'EOF'
#!/bin/bash
python3 "$HOME/.local/share/h2r-clean/file_organizer.py" "$@"
EOF
    
    chmod +x "$BIN_DIR/h2r-clean"
    
    # Criar script CLI
    cat > "$BIN_DIR/h2r-clean-cli" << 'EOF'
#!/bin/bash
python3 "$HOME/.local/share/h2r-clean/file_organizer.py" --cli "$@"
EOF
    
    chmod +x "$BIN_DIR/h2r-clean-cli"
}

# Criar atalho no desktop
create_desktop_entry() {
    print_info "Criando atalho no menu de aplicativos..."
    
    cat > "$DESKTOP_DIR/h2r-clean.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=H2R-Clean
Name[pt_BR]=H2R-Clean
Comment=Sistema de limpeza e otimização de arquivos
Comment[pt_BR]=Sistema de limpeza e otimização de arquivos
Exec=python3 $INSTALL_DIR/file_organizer.py
Icon=$HOME/.local/share/icons/h2r-clean.png
Terminal=false
Categories=System;Utility;FileTools;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_DIR/h2r-clean.desktop"
    
    # Copiar ícones pré-criados
    if [[ -f "icons/h2r_folder_128x128.png" ]]; then
        cp icons/h2r_folder_128x128.png "$HOME/.local/share/icons/h2r-clean.png"
        print_info "Ícone da pasta H2R copiado com sucesso"
    elif [[ -f "icons/h2r_clean_v2_128x128.png" ]]; then
        cp icons/h2r_clean_v2_128x128.png "$HOME/.local/share/icons/h2r-clean.png"
        print_info "Ícone H2R v2 copiado com sucesso"
    elif [[ -f "icons/icon.svg" ]]; then
        # Tentar converter SVG para PNG
        rsvg-convert icons/icon.svg -o "$HOME/.local/share/icons/h2r-clean.png" 2>/dev/null || \
        convert icons/icon.svg "$HOME/.local/share/icons/h2r-clean.png" 2>/dev/null || \
        print_warning "Não foi possível converter o ícone SVG"
    else
        # Criar ícone simples usando Python
        python3 -c "
import tkinter as tk
from PIL import Image, ImageDraw
import os

# Criar ícone simples
img = Image.new('RGBA', (128, 128), (41, 128, 185, 255))
draw = ImageDraw.Draw(img)

# Desenhar pasta simples
draw.rectangle([20, 30, 108, 100], fill=(236, 240, 241, 255))
draw.rectangle([20, 30, 50, 50], fill=(189, 195, 196, 255))

# Salvar ícone
icon_path = '$HOME/.local/share/icons/h2r-clean.png'
img.save(icon_path)
print('Ícone criado em:', icon_path)
" 2>/dev/null || print_warning "Não foi possível criar o ícone (PIL não disponível)"
    fi
}

# Configurar permissões
setup_permissions() {
    print_info "Configurando permissões..."
    
    # Adicionar ao PATH se necessário
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
        print_warning "Adicionado $HOME/.local/bin ao PATH. Reinicie o terminal ou execute:"
        print_warning "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

# Criar script de desinstalação
create_uninstaller() {
    print_info "Criando script de desinstalação..."
    
    cat > "$INSTALL_DIR/uninstall.sh" << EOF
#!/bin/bash

# Script de desinstalação do File Organizer

echo "Desinstalando H2R-Clean..."

# Remover arquivos do aplicativo
rm -rf "$INSTALL_DIR"

# Remover scripts de execução
rm -f "$BIN_DIR/h2r-clean"
rm -f "$BIN_DIR/h2r-clean-cli"

# Remover atalho do desktop
rm -f "$DESKTOP_DIR/h2r-clean.desktop"

# Remover ícone
rm -f "$HOME/.local/share/icons/h2r-clean.png"

# Remover configuração (opcional)
read -p "Deseja remover também as configurações? (s/N): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Ss]$ ]]; then
    rm -rf "$HOME/.config/h2r-clean"
    rm -rf "$HOME/.h2r_clean"
fi

echo "H2R-Clean desinstalado com sucesso!"
EOF
    
    chmod +x "$INSTALL_DIR/uninstall.sh"
}

# Testar instalação
test_installation() {
    print_info "Testando instalação..."
    
    # Testar modo CLI
    if python3 "$INSTALL_DIR/file_organizer.py" --help &> /dev/null; then
        print_info "Teste CLI passed!"
    else
        print_warning "Teste CLI falhou, mas a instalação pode continuar"
    fi
}

# Função principal
main() {
    print_info "Iniciando instalação do H2R-Clean para Linux..."
    
    check_root
    check_dependencies
    create_install_dir
    install_app
    create_desktop_entry
    setup_permissions
    create_uninstaller
    test_installation
    
    print_info "Instalação concluída com sucesso!"
    echo
    print_info "Para executar o aplicativo:"
    echo "  • Modo gráfico: h2r-clean"
    echo "  • Modo CLI: h2r-clean-cli"
    echo "  • Ou procure por 'H2R-Clean' no menu de aplicativos"
    echo
    print_info "Para desinstalar: $INSTALL_DIR/uninstall.sh"
    echo
    print_warning "Se o terminal não reconhecer os comandos, reinicie o terminal ou execute:"
    print_warning "export PATH=\"\$HOME/.local/bin:\$PATH\""
}

# Executar instalação
main "$@"
