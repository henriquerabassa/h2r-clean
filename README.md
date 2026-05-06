# H2R-Clean - Sistema de Limpeza e Otimização

Um aplicativo completo para organização, limpeza e otimização de arquivos do sistema, compatível com Linux e Windows.

## 🚀 Funcionalidades

- **Limpeza de Arquivos Temporários**: Remove arquivos temporários obsoletos
- **Limpeza de Cache**: Limpa cache de aplicativos e sistema
- **Remoção de Logs Antigos**: Elimina arquivos de log desnecessários
- **Identificação de Arquivos Grandes**: Encontra arquivos que ocupam muito espaço
- **Otimização do Sistema**: Executa otimizações específicas para cada sistema operacional
- **Backup Automático**: Cria backup antes de remover arquivos
- **Interface Gráfica Intuitiva**: Fácil de usar com modo CLI avançado

## 📋 Requisitos

- Python 3.7 ou superior
- tkinter (geralmente incluído com Python)
- Sistema operacional: Linux ou Windows

## 🛠️ Instalação

### Linux

1. Clone ou baixe os arquivos do projeto:
```bash
git clone <repositório>
cd H2R-Clean
```

2. Execute o script de instalação:
```bash
chmod +x install_linux.sh
./install_linux.sh
```

3. Execute o aplicativo:
```bash
h2r-clean          # Modo gráfico
h2r-clean-cli      # Modo CLI
```

### Windows

1. Baixe e descompacte os arquivos do projeto
2. Execute o script de instalação como usuário normal:
```cmd
install_windows.bat
```

3. Execute o aplicativo:
- Procure por "H2R-Clean" no menu iniciar
- Ou execute: `h2r-clean.bat`

## 📖 Como Usar

### Modo Gráfico

1. Execute o aplicativo
2. Escolha uma das opções:
   - **Analisar Sistema**: Escaneia o sistema em busca de arquivos desnecessários
   - **Limpar Temporários**: Remove apenas arquivos temporários
   - **Limpar Cache**: Remove arquivos de cache
   - **Limpar Logs**: Remove logs antigos
   - **Otimizar Sistema**: Executa otimizações do sistema
   - **Análise Completa**: Análise completa com limpeza automática

### Modo CLI

Execute `file-organizer-cli` e escolha uma opção:
- 1: Analisar sistema
- 2: Limpar temporários
- 3: Limpar cache
- 4: Otimizar sistema
- 5: Limpeza completa

## 🔧 Configuração

O aplicativo cria automaticamente os seguintes diretórios:

- `~/.h2r_clean/` (Linux) ou `%USERPROFILE%\.h2r_clean\` (Windows): Logs e configurações
- `~/.config/h2r-clean/` (Linux) ou `%APPDATA%\H2RClean\` (Windows): Arquivos do aplicativo

### Configurações Personalizadas

Edite o arquivo `config.json` no diretório de configurações para personalizar:

```json
{
    "temp_dirs": ["/tmp", "/var/tmp"],
    "cache_dirs": ["~/.cache"],
    "log_dirs": ["/var/log"],
    "backup_before_delete": true,
    "days_threshold": 30,
    "max_file_size_mb": 100
}
```

## 🛡️ Segurança

- **Backup Automático**: Todos os arquivos são backup antes da remoção
- **Confirmação**: Operações destrutivas exigem confirmação
- **Permissões**: Opera apenas com permissões de usuário normal
- **Logs Detalhados**: Todas as operações são registradas

## 📊 O que o Aplicativo Limpa

### Arquivos Temporários
- Arquivos em `/tmp` (Linux)
- Arquivos em `%TEMP%` (Windows)
- Arquivos em `%LOCALAPPDATA%\Temp` (Windows)
- Arquivos Prefetch (Windows)

### Cache
- Cache de navegadores
- Cache de aplicativos
- Cache do sistema
- Thumbnails

### Logs
- Logs de aplicativos antigos
- Logs do sistema (com mais de 90 dias)
- Logs de erros

### Otimizações do Sistema
- **Linux**: Limpa cache de pacotes, logs do sistema, cache de memória
- **Windows**: Limpa Prefetch, otimiza inicialização

## 🗑️ Desinstalação

### Linux
```bash
~/.local/share/h2r-clean/uninstall.sh
```

### Windows
Execute: `%APPDATA%\H2RClean\uninstall.bat`

## 🔍 Solução de Problemas

### Problema: "Comando não encontrado"
**Solução**: Reinicie o terminal ou execute:
```bash
export PATH="$HOME/.local/bin:$PATH"  # Linux
```

### Problema: "Permissão negada"
**Solução**: Execute o script de instalação como usuário normal (não como root)

### Problema: Interface gráfica não abre
**Solução**: Verifique se o tkinter está instalado:
```bash
sudo apt-get install python3-tk  # Linux
```

### Problema: Erro ao acessar arquivos
**Solução**: Alguns arquivos do sistema exigem permissões administrativas. Isso é normal e seguro.

## 📝 Logs

Todos as operações são registradas em:
- `~/.h2r_clean/organizer.log` (Linux)
- `%USERPROFILE%\.h2r_clean\organizer.log` (Windows)

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License.

## ⚠️ Aviso Legal

Este software modifica arquivos do seu sistema. Sempre faça backup dos seus dados importantes antes de usar. Os desenvolvedores não são responsáveis por qualquer perda de dados.

## 📞 Suporte

Se encontrar algum problema:
1. Verifique os logs em `~/.h2r_clean/organizer.log`
2. Tente executar como usuário normal
3. Verifique se as dependências estão instaladas

---

**Desenvolvido com ❤️ para manter seu sistema limpo e rápido!**
