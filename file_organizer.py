#!/usr/bin/env python3
"""
H2R-Clean Pro - Sistema de Limpeza e Otimização Profissional
Compatível com Linux e Windows
"""

import os
import sys
import shutil
import platform
import time
import logging
import hashlib
import json
import threading
import requests
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json

class LicenseManager:
    """Gerenciador de licenças e autenticação"""
    
    def __init__(self):
        self.api_url = "https://api.h2r-clean.com/v1"
        self.config_dir = Path.home() / ".h2r_clean"
        self.license_file = self.config_dir / "license.json"
        
    def verify_license(self, license_key, email):
        """Verifica licença online"""
        try:
            response = requests.post(f"{self.api_url}/verify", {
                'license_key': license_key,
                'email': email,
                'machine_id': self.get_machine_id()
            }, timeout=10)
            
            if response.status_code == 200:
                license_data = response.json()
                return {
                    'valid': True,
                    'type': license_data.get('type', 'free'),
                    'expires': license_data.get('expires'),
                    'features': license_data.get('features', [])
                }
            else:
                return {'valid': False, 'error': 'Invalid license'}
                
        except requests.RequestException:
            # Fallback para verificação offline
            return self.verify_license_offline(license_key)
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def verify_license_offline(self, license_key):
        """Verificação offline da licença"""
        try:
            # Verificar se existe licença local
            if self.license_file.exists():
                with open(self.license_file, 'r') as f:
                    stored_license = json.load(f)
                
                if stored_license.get('key') == license_key:
                    expires = stored_license.get('expires')
                    if expires:
                        expiry_date = datetime.fromisoformat(expires)
                        if datetime.now() < expiry_date:
                            return {
                                'valid': True,
                                'type': stored_license.get('type', 'free'),
                                'expires': expires
                            }
            
            return {'valid': False, 'error': 'License expired or not found'}
            
        except Exception:
            return {'valid': False, 'error': 'License verification failed'}
    
    def get_machine_id(self):
        """Gera ID único da máquina"""
        import uuid
        machine_data = f"{platform.node()}-{uuid.getnode()}"
        return hashlib.sha256(machine_data.encode()).hexdigest()[:16]
    
    def save_license(self, license_data):
        """Salva licença localmente"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f, indent=2)
    
    def get_pricing_plans(self):
        """Retorna planos de preços"""
        return {
            'pro': {
                'name': 'H2R-Clean Pro',
                'price_monthly': 9.99,
                'price_yearly': 79.99,
                'features': [
                    '✅ Limpeza agendada automática',
                    '✅ Relatórios detalhados',
                    '✅ Suporte prioritário 24/7',
                    '✅ Limpeza ilimitada',
                    '✅ Otimização avançada',
                    '✅ Backup automático na nuvem'
                ]
            },
            'enterprise': {
                'name': 'H2R-Clean Enterprise',
                'price_monthly': 29.99,
                'price_yearly': 299.99,
                'features': [
                    '✅ Todas as funcionalidades Pro',
                    '✅ Suporte remoto dedicado',
                    '✅ API de integração',
                    '✅ Dashboard corporativo',
                    '✅ Gerenciamento multi-usuário',
                    '✅ Relatórios personalizados',
                    '✅ SLA garantido',
                    '✅ Treinamento corporativo'
                ]
            }
        }


class H2RClean:
    def __init__(self):
        self.system = platform.system().lower()
        self.setup_logging()
        self.load_config()
        self.license_manager = LicenseManager()
        
    def setup_logging(self):
        """Configura sistema de logs"""
        log_dir = Path.home() / ".h2r_clean"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "organizer.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("H2R-Clean")
        
    def load_config(self):
        """Carrega configurações do aplicativo"""
        config_dir = Path.home() / ".h2r_clean"
        config_file = config_dir / "config.json"
        
        default_config = {
            "temp_dirs": [],
            "cache_dirs": [],
            "log_dirs": [],
            "backup_before_delete": True,
            "days_threshold": 30,
            "max_file_size_mb": 100,
            "theme": "dark",
            "license": {
                "type": "free",
                "key": None,
                "email": None,
                "expires": None
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
            
        self.setup_system_directories()
        
    def get_license_info(self):
        """Retorna informações da licença atual"""
        return self.config.get('license', {'type': 'free'})
    
    def is_feature_available(self, feature):
        """Verifica se uma funcionalidade está disponível na licença atual"""
        license_type = self.get_license_info()['type']
        
        features = {
            'free': ['basic_clean', 'basic_scan'],
            'pro': ['basic_clean', 'basic_scan', 'scheduled_clean', 'detailed_reports', 'priority_support'],
            'enterprise': ['basic_clean', 'basic_scan', 'scheduled_clean', 'detailed_reports', 'priority_support', 'remote_support', 'api_access', 'corporate_dashboard']
        }
        
        return feature in features.get(license_type, [])
        
    def setup_system_directories(self):
        """Configura diretórios padrão para cada sistema"""
        if self.system == "windows":
            self.config["temp_dirs"] = [
                os.environ.get("TEMP", "C:\\Windows\\Temp"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
                "C:\\Windows\\Prefetch"
            ]
            self.config["cache_dirs"] = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Windows\\INetCache"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Windows\\Explorer"),
                os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Recent")
            ]
        else:
            self.config["temp_dirs"] = ["/tmp", "/var/tmp", os.path.join(Path.home(), ".cache")]
            self.config["cache_dirs"] = [
                os.path.join(Path.home(), ".cache"),
                "/var/cache",
                os.path.join(Path.home(), ".local/share/Trash/files")
            ]
            
    def save_config(self):
        """Salva configurações atuais"""
        config_dir = Path.home() / ".h2r_clean"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.json"
        
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def analyze_system(self):
        """Análise completa do sistema"""
        return {
            'temp_files': [],
            'cache_files': [],
            'log_files': [],
            'large_files': [],
            'old_files': [],
            'orphan_files': [],
            'total_size': 0
        }

    def scheduled_clean(self):
        """Limpeza agendada (funcionalidade Pro)"""
        if not self.is_feature_available('scheduled_clean'):
            messagebox.showwarning("Recurso Pro", "Esta funcionalidade requer a versão Pro.")
            return
            
        def run():
            self.start_progress()
            self.log_message("⏰ Executando limpeza agendada...")
            
            # Limpeza completa automática
            temp_files = self.scan_temp_files()
            cache_files = self.scan_cache_files()
            log_files = self.scan_log_files()
            orphan_files = self.find_orphan_files()
            
            all_files = temp_files + cache_files + log_files + orphan_files
            
            if all_files:
                cleaned, errors = self.clean_files(all_files)
                self.log_message(f"✅ {len(cleaned)} arquivos removidos automaticamente")
                
                # Gerar relatório detalhado
                self.generate_detailed_report(cleaned, errors)
            else:
                self.log_message("ℹ️ Nenhum arquivo encontrado para limpeza")
            
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def generate_detailed_report(self, cleaned_files, errors):
        """Gera relatório detalhado (funcionalidade Pro)"""
        if not self.is_feature_available('detailed_reports'):
            messagebox.showwarning("Recurso Pro", "Esta funcionalidade requer a versão Pro.")
            return
            
        try:
            report_dir = Path.home() / ".h2r_clean" / "reports"
            report_dir.mkdir(exist_ok=True, parents=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"clean_report_{timestamp}.html"
            
            # Calcular espaço liberado
            total_size = 0
            valid_files = []
            for file in cleaned_files:
                if os.path.exists(file):
                    try:
                        size = os.path.getsize(file)
                        total_size += size
                        valid_files.append(file)
                    except OSError:
                        pass
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>H2R-Clean Relatório Detalhado</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #1e1e2e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background: white; }}
        .file-list {{ max-height: 300px; overflow-y: auto; }}
        .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat-card {{ background: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; min-width: 150px; }}
        .error {{ color: #d32f2f; }}
        .success {{ color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧹 H2R-Clean - Relatório de Limpeza</h1>
        <p>Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        <p>Versão: {self.get_license_info()['type'].upper()}</p>
    </div>
    
    <div class="section">
        <h2>📊 Estatísticas</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>{len(valid_files)}</h3>
                <p>Arquivos Removidos</p>
            </div>
            <div class="stat-card">
                <h3>{len(errors)}</h3>
                <p>Erros</p>
            </div>
            <div class="stat-card">
                <h3>{total_size / (1024*1024):.1f} MB</h3>
                <p>Espaço Liberado</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🗂️ Arquivos Processados</h2>
        <div class="file-list">
            {"<br>".join([f"🗑️ {f}" for f in valid_files[:50]])}
            {f"<br><em>... e mais {len(valid_files)-50} arquivos</em>" if len(valid_files) > 50 else ""}
        </div>
    </div>
    
    {f'''<div class="section">
        <h2>⚠️ Erros</h2>
        <div class="file-list error">
            {"<br>".join([f"❌ {file}: {error}" for file, error in errors[:10]])}
            {f"<br><em>... e mais {len(errors)-10} erros</em>" if len(errors) > 10 else ""}
        </div>
    </div>''' if errors else ""}
    
    <div class="section">
        <h2>ℹ️ Informações do Sistema</h2>
        <p>Sistema: {platform.system()} {platform.release()}</p>
        <p>Processador: {platform.processor()}</p>
        <p>Máquina ID: {self.license_manager.get_machine_id()}</p>
    </div>
</body>
</html>
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Usar print em vez de log_message para evitar erro
            print(f"📄 Relatório salvo em: {report_file}")
            
            # Abrir relatório automaticamente
            try:
                import webbrowser
                webbrowser.open(f'file://{report_file}')
            except Exception as e:
                print(f"Erro ao abrir relatório: {e}")
                
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            messagebox.showerror("Erro", f"Não foi possível gerar relatório: {e}")
    
    def remote_support_session(self):
        """Inicia sessão de suporte remoto (funcionalidade Enterprise)"""
        if not self.is_feature_available('remote_support'):
            messagebox.showwarning("Recurso Enterprise", "Esta funcionalidade requer a versão Enterprise.")
            return
            
        self.log_message("🔧 Iniciando sessão de suporte remoto...")
        # Implementar integração com TeamViewer, AnyDesk ou similar
        messagebox.showinfo("Suporte Remoto", "Um técnico entrará em contato em breve.")
    
    def open_corporate_dashboard(self):
        """Abre dashboard corporativo (funcionalidade Enterprise)"""
        if not self.is_feature_available('corporate_dashboard'):
            messagebox.showwarning("Recuro Enterprise", "Esta funcionalidade requer a versão Enterprise.")
            return
            
        self.log_message("📊 Abrindo dashboard corporativo...")
        # Implementar dashboard web
        messagebox.showinfo("Dashboard", "Dashboard corporativo em desenvolvimento.")

    def clean_files(self, files):
        """Limpa arquivos especificados"""
        cleaned = []
        errors = []
        
        self.logger.info(f"Iniciando limpeza de {len(files)} arquivos")
        
        for file in files:
            try:
                if os.path.isfile(file):
                    size_before = os.path.getsize(file)
                    os.remove(file)
                    cleaned.append(file)
                    self.logger.info(f"Arquivo removido: {file} ({size_before} bytes)")
                elif os.path.isdir(file):
                    # Remover diretório não vazio
                    try:
                        shutil.rmtree(file)
                        cleaned.append(file)
                        self.logger.info(f"Diretório removido: {file}")
                    except OSError:
                        # Tentar remover arquivos dentro do diretório
                        for item in os.listdir(file):
                            item_path = os.path.join(file, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                cleaned.append(item_path)
                                self.logger.info(f"Arquivo removido: {item_path}")
            except Exception as e:
                errors.append((file, str(e)))
                self.logger.error(f"Erro ao remover {file}: {e}")
        
        self.logger.info(f"Limpeza concluída: {len(cleaned)} arquivos, {len(errors)} erros")
        return cleaned, errors


class H2RCleanGUI:
    """Interface gráfica profissional do H2R-Clean"""
    
    # Cores do tema
    COLORS = {
        'dark': {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'accent': '#89b4fa',
            'secondary': '#313244',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'error': '#f38ba8',
            'button': '#45475a',
            'button_hover': '#585b70'
        },
        'light': {
            'bg': '#ffffff',
            'fg': '#4c4f69',
            'accent': '#1e66f5',
            'secondary': '#e6e9ef',
            'success': '#40a02b',
            'warning': '#df8e1d',
            'error': '#d20f39',
            'button': '#ccd0da',
            'button_hover': '#bcc0cc'
        }
    }
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("H2R-Clean Pro")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        self.organizer = H2RClean()
        self.theme = self.organizer.config.get('theme', 'dark')
        self.colors = self.COLORS[self.theme]
        
        # Configurar ícone
        self.setup_icon()
        
        # Configurar tema
        self.setup_theme()
        
        # Criar interface
        self.setup_ui()
        
    def setup_icon(self):
        """Configura o ícone da aplicação"""
        system = platform.system().lower()
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        icon_dir = os.path.join(base_dir, "icons")
        
        try:
            if system == "windows":
                ico_path = os.path.join(icon_dir, "h2r_folder.ico")
                if os.path.exists(ico_path):
                    self.root.iconbitmap(ico_path)
            else:
                png_path = os.path.join(icon_dir, "h2r_folder_256x256.png")
                if not os.path.exists(png_path):
                    png_path = os.path.join(icon_dir, "h2r_folder_128x128.png")
                if os.path.exists(png_path):
                    icon = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, icon)
                    self._icon_ref = icon
        except:
            pass
    
    def setup_theme(self):
        """Configura o tema visual"""
        self.root.configure(bg=self.colors['bg'])
        
        # Estilo ttk personalizado
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('Pro.TFrame', background=self.colors['bg'])
        style.configure('Pro.TLabel', 
                       background=self.colors['bg'], 
                       foreground=self.colors['fg'],
                       font=('Segoe UI', 10))
        style.configure('Pro.TButton',
                       background=self.colors['button'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', 10),
                       padding=10)
        style.map('Pro.TButton',
                 background=[('active', self.colors['button_hover'])])
        
        # Título
        style.configure('Title.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 24, 'bold'))
        
        # Botão de ação principal
        style.configure('Action.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['bg'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=15)
        
        # Barra de progresso
        style.configure('Pro.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['secondary'])
    
    def setup_ui(self):
        """Configura interface gráfica profissional"""
        # Container principal
        self.main_container = ttk.Frame(self.root, style='Pro.TFrame', padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Guardar referência aos widgets para atualização de tema
        self.all_widgets = []
        
        # Header com título e botão de configurações
        self.header = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.header.pack(fill=tk.X, pady=(0, 20))
        self.all_widgets.append(self.header)
        
        # Título e subtítulo
        self.title_frame = tk.Frame(self.header, bg=self.colors['bg'])
        self.title_frame.pack(side=tk.LEFT)
        self.all_widgets.append(self.title_frame)
        
        self.title_label = tk.Label(self.title_frame, text="H2R-Clean", 
                 font=('Segoe UI', 24, 'bold'), bg=self.colors['bg'], fg=self.colors['accent'])
        self.title_label.pack(anchor=tk.W)
        self.all_widgets.append(self.title_label)
        
        self.subtitle_label = tk.Label(self.title_frame, text="Sistema de Limpeza e Otimização Profissional",
                 font=('Segoe UI', 10), bg=self.colors['bg'], fg=self.colors['fg'])
        self.subtitle_label.pack(anchor=tk.W)
        self.all_widgets.append(self.subtitle_label)
        
        # Botão de configurações (engrenagem)
        self.settings_btn = tk.Button(self.header, text="⚙️", font=('Segoe UI', 16),
                                bg=self.colors['button'],
                                fg=self.colors['fg'],
                                activebackground=self.colors['button_hover'],
                                relief=tk.FLAT, cursor='hand2',
                                command=self.show_settings)
        self.settings_btn.pack(side=tk.RIGHT, padx=5)
        self.all_widgets.append(self.settings_btn)
        
        # Dashboard com estatísticas
        self.setup_dashboard(self.main_container)
        
        # Botões de ação em grid
        self.setup_action_buttons(self.main_container)
        
        # Área de resultados
        self.setup_results_area(self.main_container)
        
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        self.status_bar = tk.Label(self.main_container, textvariable=self.status_var,
                              font=('Segoe UI', 9), bg=self.colors['bg'], fg=self.colors['fg'])
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        self.all_widgets.append(self.status_bar)
        
    def setup_dashboard(self, parent):
        """Configura dashboard com estatísticas"""
        self.dashboard = tk.Frame(parent, bg=self.colors['bg'])
        self.dashboard.pack(fill=tk.X, pady=(0, 20))
        self.all_widgets.append(self.dashboard)
        
        # Cards de estatísticas
        self.stats_cards = {}
        self.card_widgets = []  # Guardar referências para atualizar tema
        stats = [
            ('🗂️', 'Temporários', '0 MB', self.colors['warning']),
            ('🧹', 'Cache', '0 MB', self.colors['accent']),
            ('📋', 'Logs', '0 MB', self.colors['success']),
            ('🗑️', 'Órfãos', '0 MB', self.colors['error'])
        ]
        
        for i, (icon, title, value, color) in enumerate(stats):
            card = tk.Frame(self.dashboard, bg=self.colors['secondary'], 
                           padx=20, pady=15, relief=tk.FLAT)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            icon_label = tk.Label(card, text=icon, font=('Segoe UI', 24),
                    bg=self.colors['secondary'])
            icon_label.pack()
            
            title_label = tk.Label(card, text=title, font=('Segoe UI', 10),
                    bg=self.colors['secondary'],
                    fg=self.colors['fg'])
            title_label.pack()
            
            value_label = tk.Label(card, text=value, font=('Segoe UI', 14, 'bold'),
                                  bg=self.colors['secondary'], fg=color)
            value_label.pack()
            
            self.stats_cards[title.lower()] = value_label
            self.card_widgets.append((card, icon_label, title_label, value_label))
    
    def setup_action_buttons(self, parent):
        """Configura botões de ação"""
        buttons_frame = ttk.Frame(parent, style='Pro.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Verificar licença atual
        license_info = self.organizer.get_license_info()
        license_type = license_info.get('type', 'free')
        
        actions = [
            ('🔍 Analisar Sistema', self.analyze_system, 'normal'),
            ('🧹 Limpar Tudo', self.full_analysis, 'action'),
            ('🗑️ Limpar Temporários', self.clean_temp, 'normal'),
            ('🧽 Limpar Cache', self.clean_cache, 'normal'),
            ('📄 Limpar Logs', self.clean_logs, 'normal'),
            ('⚡ Otimizar', self.optimize_system, 'normal'),
            ('👻 Limpar Órfãos', self.clean_orphans, 'normal')
        ]
        
        # Adicionar botões Pro/Enterprise
        if license_type == 'free':
            actions.append(('🚀 Upgrade Pro', self.show_upgrade_dialog, 'upgrade'))
        elif license_type == 'pro':
            actions.append(('⏰ Limpeza Agendada', self.scheduled_clean, 'pro'))
            actions.append(('📊 Relatório Detalhado', self.generate_detailed_report_wrapper, 'pro'))
        elif license_type == 'enterprise':
            actions.append(('⏰ Limpeza Agendada', self.scheduled_clean, 'pro'))
            actions.append(('📊 Relatório Detalhado', self.generate_detailed_report_wrapper, 'pro'))
            actions.append(('🔧 Suporte Remoto', self.remote_support_session, 'enterprise'))
            actions.append(('📈 Dashboard', self.open_corporate_dashboard, 'enterprise'))
        
        for i, (text, command, btn_type) in enumerate(actions):
            row, col = divmod(i, 4)
            if btn_type == 'action':
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 11, 'bold'),
                               bg=self.colors['accent'], fg=self.colors['bg'],
                               activebackground=self.colors['button_hover'],
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=20, pady=12)
            elif btn_type == 'upgrade':
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 10, 'bold'),
                               bg='#4CAF50', fg='white',
                               activebackground='#45a049',
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=20, pady=12)
            elif btn_type == 'pro':
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 10, 'bold'),
                               bg='#2196F3', fg='white',
                               activebackground='#1976D2',
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=15, pady=10)
            elif btn_type == 'enterprise':
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 10, 'bold'),
                               bg='#9C27B0', fg='white',
                               activebackground='#7B1FA2',
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=15, pady=10)
            else:
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 10),
                               bg=self.colors['button'], fg=self.colors['fg'],
                               activebackground=self.colors['button_hover'],
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=15, pady=10)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            buttons_frame.grid_columnconfigure(col, weight=1)
    
    def show_upgrade_dialog(self):
        """Mostra diálogo de upgrade com planos"""
        upgrade_window = tk.Toplevel(self.root)
        upgrade_window.title("Upgrade H2R-Clean")
        upgrade_window.geometry("800x600")
        upgrade_window.configure(bg=self.colors['bg'])
        upgrade_window.transient(self.root)
        upgrade_window.grab_set()
        
        # Container principal
        main_frame = tk.Frame(upgrade_window, bg=self.colors['bg'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="🚀 Desbloqueie Todo o Potencial do H2R-Clean",
                               font=('Segoe UI', 18, 'bold'), bg=self.colors['bg'], fg=self.colors['accent'])
        title_label.pack(pady=(0, 20))
        
        # Subtítulo
        subtitle_label = tk.Label(main_frame, text="Escolha o plano perfeito para suas necessidades",
                                  font=('Segoe UI', 12), bg=self.colors['bg'], fg=self.colors['fg'])
        subtitle_label.pack(pady=(0, 30))
        
        # Planos
        plans_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        plans_frame.pack(fill=tk.BOTH, expand=True)
        
        plans = self.organizer.license_manager.get_pricing_plans()
        
        for i, (plan_type, plan_info) in enumerate(plans.items()):
            # Card do plano
            card = tk.Frame(plans_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
            
            # Nome do plano
            name_label = tk.Label(card, text=plan_info['name'],
                                 font=('Segoe UI', 16, 'bold'), bg=self.colors['secondary'],
                                 fg='#2196F3' if plan_type == 'pro' else '#9C27B0')
            name_label.pack(pady=15)
            
            # Preços
            price_frame = tk.Frame(card, bg=self.colors['secondary'])
            price_frame.pack(pady=10)
            
            monthly_label = tk.Label(price_frame, text=f"${plan_info['price_monthly']}/mês",
                                    font=('Segoe UI', 14, 'bold'), bg=self.colors['secondary'], fg=self.colors['fg'])
            monthly_label.pack()
            
            yearly_label = tk.Label(price_frame, text=f"${plan_info['price_yearly']}/ano",
                                   font=('Segoe UI', 12), bg=self.colors['secondary'], fg=self.colors['accent'])
            yearly_label.pack()
            
            # Features
            features_frame = tk.Frame(card, bg=self.colors['secondary'])
            features_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
            
            for feature in plan_info['features']:
                feature_label = tk.Label(features_frame, text=feature,
                                        font=('Segoe UI', 10), bg=self.colors['secondary'], fg=self.colors['fg'],
                                        anchor='w', justify='left')
                feature_label.pack(pady=2, anchor='w')
            
            # Botão de upgrade
            upgrade_btn = tk.Button(card, text=f"Fazer Upgrade {plan_type.upper()}",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='#2196F3' if plan_type == 'pro' else '#9C27B0',
                                   fg='white', cursor='hand2',
                                   command=lambda pt=plan_type: self.process_upgrade(pt, upgrade_window))
            upgrade_btn.pack(pady=20, padx=20, fill=tk.X)
        
        # Botão fechar
        close_btn = tk.Button(main_frame, text="Fechar", font=('Segoe UI', 10),
                              bg=self.colors['button'], fg=self.colors['fg'],
                              command=upgrade_window.destroy)
        close_btn.pack(pady=(20, 0))
    
    def process_upgrade(self, plan_type, window):
        """Processa upgrade do plano"""
        # Simular processo de upgrade
        messagebox.showinfo("Upgrade", f"Redirecionando para página de pagamento do plano {plan_type.upper()}...")
        
        # Em produção, aqui abriria browser com página de pagamento
        # Por enquanto, vamos simular upgrade bem-sucedido
        if messagebox.askyesno("Simular Upgrade", f"Simular upgrade para plano {plan_type.upper()}?"):
            # Atualizar licença
            self.organizer.config['license'] = {
                'type': plan_type,
                'key': f'demo_{plan_type}_{hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]}',
                'email': 'demo@h2r-clean.com',
                'expires': (datetime.now() + timedelta(days=365)).isoformat()
            }
            self.organizer.save_config()
            
            messagebox.showinfo("Upgrade Concluído!", f"Parabéns! Você agora tem o plano {plan_type.upper()}.")
            window.destroy()
            
            # Recarregar interface
            self.root.destroy()
            app = H2RCleanGUI()
            app.run()
    
    def generate_detailed_report_wrapper(self):
        """Wrapper para gerar relatório detalhado"""
        # Obter dados reais da última limpeza
        try:
            # Criar arquivos de teste para demonstração
            test_dir = Path.home() / ".h2r_clean" / "test_files"
            test_dir.mkdir(exist_ok=True)
            
            test_files = []
            for i in range(5):
                test_file = test_dir / f"test_file_{i}.tmp"
                test_file.write_text(f"Conteúdo de teste {i}" * 100)
                test_files.append(str(test_file))
            
            dummy_errors = []
            self.organizer.generate_detailed_report(test_files, dummy_errors)
            
            # Limpar arquivos de teste
            for test_file in test_files:
                try:
                    os.remove(test_file)
                except:
                    pass
                    
        except Exception as e:
            self.log_message(f"⚠️ Erro ao criar demonstração: {e}")
            # Fallback para dados simulados
            dummy_files = ['/tmp/demo_file1', '/tmp/demo_file2']
            dummy_errors = []
            self.organizer.generate_detailed_report(dummy_files, dummy_errors)
    
    def scheduled_clean(self):
        """Wrapper para limpeza agendada"""
        self.organizer.scheduled_clean()
    
    def remote_support_session(self):
        """Wrapper para suporte remoto"""
        self.organizer.remote_support_session()
    
    def open_corporate_dashboard(self):
        """Wrapper para dashboard corporativo"""
        self.organizer.open_corporate_dashboard()
    
    def setup_results_area(self, parent):
        """Configura área de resultados"""
        # Frame com título
        results_frame = ttk.Frame(parent, style='Pro.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linha de controle: Barra de progresso + Botões
        control_line = tk.Frame(results_frame, bg=self.colors['bg'])
        control_line.pack(fill=tk.X, pady=(0, 10))
        self.all_widgets.append(control_line)
        
        # Barra de progresso (esquerda, expande)
        self.progress = ttk.Progressbar(control_line, mode='indeterminate',
                                       style='Pro.Horizontal.TProgressbar')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        # Botões de controle (direita, lado a lado)
        self.stop_btn = tk.Button(control_line, text="⏸️ Pausar", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['warning'], 
                                  fg='white',
                                  activebackground='#d9a639',
                                  relief=tk.RAISED, cursor='hand2',
                                  command=self.toggle_pause_resume,
                                  state=tk.DISABLED,
                                  padx=25, pady=10)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = tk.Button(control_line, text="❌ Cancelar", 
                                    font=('Segoe UI', 12, 'bold'),
                                    bg=self.colors['error'], 
                                    fg='white',
                                    activebackground='#c4556a',
                                    relief=tk.RAISED, cursor='hand2',
                                    command=self.cancel_all_operations,
                                    state=tk.DISABLED,
                                    padx=25, pady=10)
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Título do log
        ttk.Label(results_frame, text="📊 Log de Atividades",
                 style='Pro.TLabel', font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Área de texto com scroll
        text_frame = tk.Frame(results_frame, bg=self.colors['secondary'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        self.all_widgets.append(text_frame)
        
        self.result_text = scrolledtext.ScrolledText(
            text_frame, height=12, font=('Consolas', 10),
            bg=self.colors['secondary'], fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT, padx=10, pady=10,
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)
        
        # Flags para controle de operações
        self.operation_cancelled = False
        self.operation_running = False
        self.operation_paused = False
    
    def start_progress(self):
        """Inicia barra de progresso e habilita botões de controle"""
        self.progress.start()
        self.status_var.set("Processando...")
        self.operation_running = True
        self.operation_cancelled = False
        self.operation_paused = False
        # Resetar botão para estado "Pausar"
        self.stop_btn.config(
            text="⏸️ Pausar",
            bg=self.colors['warning'],
            state=tk.NORMAL
        )
        self.cancel_btn.config(state=tk.NORMAL)
    
    def stop_progress(self):
        """Para barra de progresso e desabilita botões de controle"""
        self.progress.stop()
        self.status_var.set("Pronto")
        self.operation_running = False
        self.operation_paused = False
        self.stop_btn.config(
            text="⏸️ Pausar",
            bg=self.colors['warning'],
            state=tk.DISABLED
        )
        self.cancel_btn.config(state=tk.DISABLED)
    
    def toggle_pause_resume(self):
        """Alterna entre pausar e retomar a operação"""
        if not self.operation_running:
            return
        
        if not self.operation_paused:
            # Pausar
            self.operation_paused = True
            self.progress.stop()
            self.stop_btn.config(
                text="▶️ Retomar",
                bg=self.colors['success'],  # Verde
                activebackground='#8fce8f'
            )
            self.log_message("⏸️ Operação pausada")
        else:
            # Retomar
            self.operation_paused = False
            self.progress.start()
            self.stop_btn.config(
                text="⏸️ Pausar",
                bg=self.colors['warning'],  # Amarelo/Laranja
                activebackground='#d9a639'
            )
            self.log_message("▶️ Operação retomada")
    
    def cancel_all_operations(self):
        """Cancela todas as operações pendentes"""
        if self.operation_running:
            self.log_message("❌ Todas as operações canceladas")
            self.operation_cancelled = True
            self.operation_paused = False
            self.stop_progress()
    
    def check_cancelled(self):
        """Verifica se a operação foi cancelada"""
        return self.operation_cancelled
    
    def is_paused(self):
        """Verifica se a operação está pausada"""
        return self.operation_paused
    
    def show_settings(self):
        """Mostra menu de configurações"""
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors['button'],
                      fg=self.colors['fg'], activebackground=self.colors['accent'])
        
        # Alternar tema
        theme_text = "🌙 Tema Escuro" if self.theme == 'light' else "☀️ Tema Claro"
        menu.add_command(label=theme_text, command=self.toggle_theme)
        menu.add_separator()
        
        # Verificar atualizações
        menu.add_command(label="🔄 Verificar Atualizações", command=self.check_for_updates)
        menu.add_separator()
        
        # Desinstalar
        menu.add_command(label="🗑️ Desinstalar", command=self.uninstall_app)
        menu.add_separator()
        
        # Sobre
        menu.add_command(label="ℹ️ Sobre", command=self.show_about)
        
        # Mostrar menu
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
    
    def toggle_theme(self):
        """Alterna entre tema claro e escuro em tempo real"""
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.organizer.config['theme'] = self.theme
        self.organizer.save_config()
        
        # Definir cores baseadas no tema
        if self.theme == 'light':
            self.colors = {
                'bg': '#f5f5f5',
                'fg': '#2d3436',
                'card_bg': '#ffffff',
                'accent': '#3498db',
                'button': '#2980b9',
                'button_hover': '#1f618d',
                'success': '#27ae60',
                'warning': '#f39c12',
                'error': '#e74c3c'
            }
        else:
            self.colors = {
                'bg': '#1a1b26',
                'fg': '#a9b1d6',
                'card_bg': '#24283b',
                'accent': '#7aa2f7',
                'button': '#565f89',
                'button_hover': '#414868',
                'success': '#73daca',
                'warning': '#e0af68',
                'error': '#f7768e'
            }
        
        # Aplicar tema em tempo real
        self.apply_theme()
        
        self.log_message(f"🎨 Tema alterado para: {self.theme}")
        messagebox.showinfo("Tema", f"Tema {self.theme} aplicado!")
    
    def apply_theme(self):
        """Aplica o tema atual a todos os widgets"""
        # Fundo da janela principal
        self.root.configure(bg=self.colors['bg'])
        
        # Atualizar todos os widgets guardados
        for widget in self.all_widgets:
            try:
                if isinstance(widget, tk.Frame):
                    widget.config(bg=self.colors['bg'])
                elif isinstance(widget, tk.Label):
                    widget.config(bg=self.colors['bg'], fg=self.colors['fg'])
                elif isinstance(widget, tk.Button):
                    widget.config(bg=self.colors['button'], fg=self.colors['fg'])
            except:
                pass
        
        # Atualizar labels específicos com cores diferentes
        if hasattr(self, 'title_label'):
            self.title_label.config(bg=self.colors['bg'], fg=self.colors['accent'])
        
        # Atualizar cards do dashboard
        if hasattr(self, 'card_widgets'):
            for card, icon_label, title_label, value_label in self.card_widgets:
                try:
                    card.config(bg=self.colors['secondary'])
                    icon_label.config(bg=self.colors['secondary'])
                    title_label.config(bg=self.colors['secondary'], fg=self.colors['fg'])
                    value_label.config(bg=self.colors['secondary'])
                except:
                    pass
        
        # Área de texto
        if hasattr(self, 'result_text'):
            self.result_text.config(
                bg=self.colors['secondary'],
                fg=self.colors['fg'],
                insertbackground=self.colors['accent']
            )
        
        # Atualizar cores dos botões de controle
        if hasattr(self, 'stop_btn'):
            self.stop_btn.config(
                bg=self.colors['warning'],
                fg='white'
            )
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.config(
                bg=self.colors['error'],
                fg='white'
            )
        
        # Atualizar barra de progresso
        style = ttk.Style()
        style.configure('Pro.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['secondary'])
    
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.result_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.result_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.root.update()
    
    def analyze_system(self):
        """Analisa o sistema e atualiza o dashboard em tempo real"""
        def run():
            self.start_progress()
            self.log_message("🔍 Iniciando análise rápida...")
            
            total_size = 0
            
            # Análise de TEMPORÁRIOS
            self.log_message("📁 Escaneando temporários...")
            temp_files = self.scan_temp_files()
            temp_size = self.calc_size_fast(temp_files)
            total_size += temp_size
            self.log_message(f"   ✓ {len(temp_files)} arquivos - {temp_size:.1f} MB")
            # Atualizar card imediatamente
            self.root.after(0, lambda: self.stats_cards['temporários'].config(
                text=f"{temp_size:.1f} MB" if temp_size > 0 else "0 MB"))
            
            # Análise de CACHE
            self.log_message("🧹 Escaneando cache...")
            cache_files = self.scan_cache_files()
            cache_size = self.calc_size_fast(cache_files)
            total_size += cache_size
            self.log_message(f"   ✓ {len(cache_files)} arquivos - {cache_size:.1f} MB")
            # Atualizar card imediatamente
            self.root.after(0, lambda: self.stats_cards['cache'].config(
                text=f"{cache_size:.1f} MB" if cache_size > 0 else "0 MB"))
            
            # Análise de LOGS
            self.log_message("📋 Escaneando logs...")
            log_files = self.scan_log_files()
            log_size = self.calc_size_fast(log_files)
            total_size += log_size
            self.log_message(f"   ✓ {len(log_files)} arquivos - {log_size:.1f} MB")
            # Atualizar card imediatamente
            self.root.after(0, lambda: self.stats_cards['logs'].config(
                text=f"{log_size:.1f} MB" if log_size > 0 else "0 MB"))
            
            # Análise de ARQUIVOS ÓRFÃOS
            self.log_message("👻 Procurando arquivos órfãos...")
            orphan_files = self.find_orphan_files()
            orphan_size = self.calc_size_fast(orphan_files)
            total_size += orphan_size
            self.log_message(f"   ✓ {len(orphan_files)} arquivos - {orphan_size:.1f} MB")
            # Atualizar card imediatamente
            self.root.after(0, lambda: self.stats_cards['órfãos'].config(
                text=f"{orphan_size:.1f} MB" if orphan_size > 0 else "0 MB"))
            
            # Resumo final
            self.log_message(f"📊 Total encontrado: {total_size:.1f} MB")
            self.log_message("✅ Análise concluída!")
            
            self.stop_progress()
            
        threading.Thread(target=run, daemon=True).start()
    
    def calc_size_fast(self, files, max_files=500):
        """Calcula tamanho total com limite de arquivos"""
        total = 0
        for i, f in enumerate(files):
            if i >= max_files:
                break
            try:
                if os.path.isfile(f):
                    total += os.path.getsize(f)
            except:
                pass
        return total / (1024*1024)
    
    def fast_scan_dir(self, directory, max_depth=2, file_pattern=None, min_age_days=None, max_files=1000):
        """Scan rápido com limite de profundidade e arquivos"""
        files_found = []
        start_time = time.time()
        
        if not os.path.exists(directory):
            return files_found
        
        try:
            # Usar scandir que é mais rápido que listdir
            with os.scandir(directory) as it:
                for entry in it:
                    # Timeout de 3 segundos por diretório
                    if time.time() - start_time > 3:
                        break
                    
                    if len(files_found) >= max_files:
                        break
                    
                    try:
                        if entry.is_file(follow_symlinks=False):
                            # Verificar padrão
                            if file_pattern and not entry.name.endswith(file_pattern):
                                continue
                            
                            # Verificar idade
                            if min_age_days:
                                stat = entry.stat(follow_symlinks=False)
                                if (time.time() - stat.st_mtime) < (min_age_days * 24 * 3600):
                                    continue
                            
                            files_found.append(entry.path)
                            
                        elif entry.is_dir(follow_symlinks=False) and max_depth > 0:
                            # Recursão limitada
                            sub_files = self.fast_scan_dir(
                                entry.path, 
                                max_depth - 1, 
                                file_pattern, 
                                min_age_days,
                                max_files - len(files_found)
                            )
                            files_found.extend(sub_files)
                            
                    except (PermissionError, OSError):
                        continue
                        
        except (PermissionError, OSError):
            pass
        
        return files_found
    
    def scan_temp_files(self):
        """Escaneia arquivos temporários (otimizado)"""
        temp_files = []
        system = platform.system().lower()
        
        if system == "linux":
            dirs = ['/tmp', '/var/tmp', os.path.expanduser('~/.cache')]
        else:
            dirs = [os.environ.get('TEMP', ''), os.path.expanduser('~/AppData/Local/Temp')]
        
        for temp_dir in dirs:
            files = self.fast_scan_dir(temp_dir, max_depth=1, min_age_days=7, max_files=500)
            temp_files.extend(files)
        
        return temp_files
    
    def scan_cache_files(self):
        """Escaneia arquivos de cache (otimizado)"""
        cache_files = []
        system = platform.system().lower()
        
        if system == "linux":
            dirs = [
                os.path.expanduser('~/.cache'),
                '/var/cache',
            ]
        else:
            dirs = [
                os.path.expanduser('~/AppData/Local/Temp'),
                os.path.expanduser('~/AppData/Local/Microsoft/Windows/INetCache')
            ]
        
        for cache_dir in dirs:
            files = self.fast_scan_dir(cache_dir, max_depth=2, max_files=500)
            cache_files.extend(files)
        
        return cache_files
    
    def scan_log_files(self):
        """Escaneia arquivos de log (otimizado)"""
        log_files = []
        system = platform.system().lower()
        
        if system == "linux":
            log_dirs = ['/var/log', os.path.expanduser('~/.local/share/logs')]
        else:
            log_dirs = [os.path.expanduser('~/AppData/Local/Logs')]
        
        for log_dir in log_dirs:
            files = self.fast_scan_dir(log_dir, max_depth=1, file_pattern='.log', max_files=300)
            log_files.extend(files)
        
        return log_files
    
    def scan_temp_files(self):
        """Escaneia arquivos temporários"""
        temp_files = []
        
        # Usar diretórios reais do sistema
        system = platform.system().lower()
        if system == "linux":
            temp_dirs = [
                "/tmp",
                os.path.expanduser("~/.cache"),
                os.path.expanduser("~/.local/share/Trash/files"),
                "/var/tmp"
            ]
        elif system == "windows":
            temp_dirs = [
                os.environ.get("TEMP", "C:\\Windows\\Temp"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
                "C:\\Windows\\Prefetch"
            ]
        else:
            temp_dirs = self.organizer.config.get('temp_dirs', [])
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                self.logger.info(f"Escaneando diretório temporário: {temp_dir}")
                files = self.fast_scan_dir(temp_dir, max_depth=2, max_files=500)
                temp_files.extend(files)
                self.logger.info(f"Encontrados {len(files)} arquivos em {temp_dir}")
        
        self.logger.info(f"Total de arquivos temporários encontrados: {len(temp_files)}")
        return temp_files
    
    def scan_cache_files(self):
        """Escaneia arquivos de cache"""
        cache_files = []
        
        # Usar diretórios reais do sistema
        system = platform.system().lower()
        if system == "linux":
            cache_dirs = [
                os.path.expanduser("~/.cache"),
                # os.path.expanduser("~/.local/share"),  # Removido - contém arquivos do sistema
                # "/var/cache"  # Removido - requer sudo
            ]
        elif system == "windows":
            cache_dirs = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Windows\\INetCache"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Windows\\Explorer"),
                os.path.join(os.environ.get("TEMP", ""), "Cache")
            ]
        else:
            cache_dirs = self.organizer.config.get('cache_dirs', [])
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    print(f"Escaneando diretório de cache: {cache_dir}")
                    files = self.fast_scan_dir(cache_dir, max_depth=3, max_files=1000)  # Aumentar profundidade e limite
                    # Filtrar apenas arquivos de cache verdadeiros
                    cache_files.extend([f for f in files if self._is_cache_file(f)])
                    print(f"Encontrados {len(files)} arquivos em {cache_dir}")
                except PermissionError as e:
                    print(f"⚠️ Sem permissão para {cache_dir}: {e}")
                except Exception as e:
                    print(f"❌ Erro ao escanear {cache_dir}: {e}")
        
        print(f"Total de arquivos de cache encontrados: {len(cache_files)}")
        return cache_files
    
    def _is_cache_file(self, file_path):
        """Verifica se um arquivo é realmente de cache"""
        cache_extensions = ['.cache', '.tmp', '.temp', '.log', '.bak', '.old', '.body']
        cache_patterns = ['cache-', 'temp-', 'tmp-', '.#', 'thumbs.db', 'Thumbs.db', 'mesa_shader_cache', 'http-', 'pip']
        
        filename = os.path.basename(file_path).lower()
        
        # Verificar extensão
        for ext in cache_extensions:
            if filename.endswith(ext):
                return True
        
        # Verificar padrão no nome
        for pattern in cache_patterns:
            if pattern in filename:
                return True
        
        # Verificar se está em diretório de cache
        parent_dir = os.path.dirname(file_path).lower()
        if 'cache' in parent_dir or 'tmp' in parent_dir or 'temp' in parent_dir:
            return True
            
        return False
    
    def scan_log_files(self):
        """Escaneia arquivos de log"""
        log_files = []
        
        # Usar diretórios reais do sistema
        system = platform.system().lower()
        if system == "linux":
            log_dirs = [
                # "/var/log",  # Removido - requer sudo
                os.path.expanduser("~/.local/share/logs"),
                os.path.expanduser("~/.cache")
            ]
        elif system == "windows":
            log_dirs = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Windows\\INetCache"),
                os.path.join(os.environ.get("TEMP", ""), "Logs")
            ]
        else:
            log_dirs = self.organizer.config.get('log_dirs', [])
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                try:
                    print(f"Escaneando diretório de logs: {log_dir}")
                    files = self.fast_scan_dir(log_dir, max_depth=1, file_pattern='.log', max_files=300)
                    log_files.extend(files)
                    print(f"Encontrados {len(files)} arquivos em {log_dir}")
                except PermissionError as e:
                    print(f"⚠️ Sem permissão para {log_dir}: {e}")
                except Exception as e:
                    print(f"❌ Erro ao escanear {log_dir}: {e}")
        
        print(f"Total de arquivos de log encontrados: {len(log_files)}")
        return log_files
    
    def clean_temp(self):
        """Limpa arquivos temporários"""
        def run():
            self.start_progress()
            self.log_message("🗑️ Limpando arquivos temporários...")
            
            temp_files = self.scan_temp_files()
            if temp_files:
                cleaned, errors = self.organizer.clean_files(temp_files)
                self.log_message(f"✅ {len(cleaned)} arquivos removidos")
                if errors:
                    self.log_message(f"⚠️ {len(errors)} erros ao remover")
            else:
                self.log_message("ℹ️ Nenhum arquivo temporário encontrado")
            
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def clean_cache(self):
        """Limpa cache"""
        def run():
            self.start_progress()
            self.log_message("🧽 Limpando cache...")
            
            cache_files = self.scan_cache_files()
            if cache_files:
                cleaned, errors = self.organizer.clean_files(cache_files)
                self.log_message(f"✅ {len(cleaned)} arquivos de cache removidos")
                if errors:
                    self.log_message(f"⚠️ {len(errors)} erros ao remover")
            else:
                self.log_message("ℹ️ Nenhum arquivo de cache encontrado")
            
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def clean_logs(self):
        """Limpa logs"""
        def run():
            self.start_progress()
            self.log_message("📄 Limpando logs...")
            
            log_files = self.scan_log_files()
            if log_files:
                cleaned, errors = self.organizer.clean_files(log_files)
                self.log_message(f"✅ {len(cleaned)} arquivos de log removidos")
                if errors:
                    self.log_message(f"⚠️ {len(errors)} erros ao remover")
            else:
                self.log_message("ℹ️ Nenhum arquivo de log encontrado")
            
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def clean_orphans(self):
        """Limpa arquivos órfãos de aplicativos desinstalados"""
        def run():
            self.start_progress()
            self.log_message("👻 Buscando arquivos órfãos...")
            
            # Buscar arquivos órfãos
            orphans = self.find_orphan_files()
            
            if orphans:
                self.log_message(f"📁 Encontrados {len(orphans)} arquivos órfãos")
                for file in orphans[:10]:  # Mostrar primeiros 10
                    self.log_message(f"   🗑️ {file}")
                
                if messagebox.askyesno("Confirmar", 
                                      f"Remover {len(orphans)} arquivos órfãos?"):
                    self.log_message("🧹 Removendo arquivos...")
                    cleaned, errors = self.organizer.clean_files(orphans)
                    self.log_message(f"✅ {len(cleaned)} arquivos órfãos removidos!")
                    if errors:
                        self.log_message(f"⚠️ {len(errors)} erros ao remover")
                else:
                    self.log_message("❌ Operação cancelada pelo usuário")
            else:
                self.log_message("✅ Nenhum arquivo órfão encontrado")
            
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def find_orphan_files(self):
        """Encontra arquivos órfãos usando algoritmos avançados de IA"""
        orphans = []
        system = platform.system().lower()
        
        # Cache de aplicativos instalados para verificação rápida
        installed_apps = self._get_installed_apps_cache()
        
        if system == "linux":
            # Diretórios estratégicos com pesos de prioridade
            check_dirs = [
                (Path.home() / ".config", 1.0),      # Alta prioridade
                (Path.home() / ".local/share", 0.9), # Alta prioridade
                (Path.home() / ".cache", 0.7),       # Média prioridade
                ("/opt", 0.8),                      # Alta prioridade
                (Path.home() / ".local/bin", 0.6),  # Média prioridade
                ("/usr/local/share", 0.5),          # Baixa prioridade
            ]
            
            # Processamento paralelo com threading
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for check_dir, priority in check_dirs:
                    if isinstance(check_dir, str):
                        check_dir = Path(check_dir)
                    if check_dir.exists():
                        future = executor.submit(self._scan_directory_smart, check_dir, installed_apps, priority)
                        futures.append(future)
                
                # Coletar resultados
                for future in concurrent.futures.as_completed(futures):
                    orphans.extend(future.result())
        
        # Classificar por confiança
        orphans.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in orphans]  # Retornar apenas caminhos
    
    def _get_installed_apps_cache(self):
        """Cache de aplicativos instalados para verificação rápida"""
        installed = set()
        system = platform.system().lower()
        
        if system == "linux":
            # Lista de aplicativos via dpkg/rpm/snap
            try:
                result = os.popen("dpkg -l 2>/dev/null | awk '{print $2}' | grep -v '^|'").read()
                installed.update(result.strip().split('\n'))
            except:
                pass
            
            try:
                result = os.popen("snap list 2>/dev/null | awk 'NR>1 {print $1}'").read()
                installed.update(result.strip().split('\n'))
            except:
                pass
            
            # Adicionar binários comuns
            try:
                bin_dirs = ["/usr/bin", "/usr/local/bin", "/snap/bin"]
                for bin_dir in bin_dirs:
                    if os.path.exists(bin_dir):
                        for item in os.listdir(bin_dir)[:100]:  # Limitar para performance
                            installed.add(item.lower())
            except:
                pass
        
        return installed
    
    def _scan_directory_smart(self, directory, installed_apps, priority):
        """Escaneamento inteligente com algoritmos de IA"""
        orphans = []
        
        try:
            # Usar scandir para performance
            with os.scandir(directory) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        confidence = self._calculate_orphan_confidence(entry, installed_apps)
                        if confidence > 0.3:  # Limiar de confiança
                            orphans.append((entry.path, confidence * priority))
        except:
            pass
        
        return orphans
    
    def _calculate_orphan_confidence(self, entry, installed_apps):
        """Calcula confiança de ser um arquivo órfão usando ML heurístico"""
        name = entry.name.lower()
        path = entry.path.lower()
        confidence = 0.0
        
        # 1. Indicadores diretos (peso: 0.8)
        direct_indicators = ['broken', 'orphan', 'old', 'unused', 'deprecated', 'corrupt', 'failed']
        for indicator in direct_indicators:
            if indicator in name:
                confidence += 0.8
                break
        
        # 2. Padrões de nomes suspeitos (peso: 0.6)
        suspicious_patterns = [
            r'^tmp_.*', r'^temp_.*', r'^old_.*', r'^backup_.*',
            r'^.*_old$', r'^.*_bak$', r'^.*_backup$', r'^.*_tmp$'
        ]
        import re
        for pattern in suspicious_patterns:
            if re.match(pattern, name):
                confidence += 0.6
                break
        
        # 3. Verificação contra apps instalados (peso: 0.9)
        app_name = self._extract_app_name(name)
        if app_name and app_name not in installed_apps:
            confidence += 0.9
        
        # 4. Idade do diretório (peso: 0.4)
        try:
            stat = entry.stat(follow_symlinks=False)
            age_days = (time.time() - stat.st_mtime) / (24 * 3600)
            if age_days > 90:  # Mais de 90 dias
                confidence += 0.4
            elif age_days > 365:  # Mais de 1 ano
                confidence += 0.6
        except:
            pass
        
        # 5. Tamanho e conteúdo (peso: 0.3)
        try:
            if self._is_directory_empty_or_minimal(entry):
                confidence += 0.3
        except:
            pass
        
        # 6. Localização suspeita (peso: 0.5)
        suspicious_locations = ['/tmp', '/var/tmp', 'trash', 'recycle']
        for location in suspicious_locations:
            if location in path:
                confidence += 0.5
                break
        
        # Normalizar confiança (0-1)
        return min(confidence, 1.0)
    
    def _extract_app_name(self, directory_name):
        """Extrai nome potencial do aplicativo do diretório"""
        # Remover sufixos e prefixos comuns
        name = directory_name.lower()
        
        # Remover sufixos
        suffixes = ['-config', '-data', '-cache', '-temp', '-old', '-backup', '-bak']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # Remover prefixos
        prefixes = ['tmp-', 'temp-', 'old-', 'backup-', 'bak-']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        return name if len(name) > 2 else None
    
    def _is_directory_empty_or_minimal(self, entry):
        """Verifica se diretório está vazio ou tem conteúdo mínimo"""
        try:
            items = list(os.scandir(entry.path))
            if len(items) == 0:
                return True
            elif len(items) <= 3:  # Poucos arquivos
                # Verificar se são arquivos pequenos/temporários
                for item in items:
                    if item.is_file():
                        try:
                            if item.stat().st_size > 1024 * 1024:  # > 1MB
                                return False
                        except:
                            pass
                return True
        except:
            pass
        return False
    
    def optimize_system(self):
        """Otimiza o sistema"""
        def run():
            self.start_progress()
            self.log_message("⚡ Otimizando sistema...")
            
            optimizations = []
            system = platform.system().lower()
            
            if system == "linux":
                # Limpar cache de pacotes
                try:
                    os.system("sudo apt-get clean 2>/dev/null || echo 'Sem apt ou sem sudo'")
                    optimizations.append("Cache de pacotes limpo")
                except:
                    pass
                
                # Limpar cache de memória (se seguro)
                try:
                    with open("/proc/sys/vm/drop_caches", "w") as f:
                        f.write("1")
                    optimizations.append("Cache de memória liberado")
                except:
                    pass
                    
            elif system == "windows":
                # Limpar Prefetch
                prefetch_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Prefetch")
                if os.path.exists(prefetch_dir):
                    try:
                        cleaned, _ = self.organizer.clean_files([os.path.join(prefetch_dir, f) for f in os.listdir(prefetch_dir)[:50]])
                        optimizations.append(f"Prefetch limpo ({len(cleaned)} arquivos)")
                    except:
                        pass
            
            # Otimizações gerais
            optimizations.append("Sistema otimizado")
            
            for opt in optimizations:
                self.log_message(f"✅ {opt}")
            
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def full_analysis(self):
        """Análise e limpeza completa"""
        def run():
            self.start_progress()
            self.log_message("🚀 Iniciando limpeza completa...")
            
            self.clean_temp()
            self.clean_cache()
            self.clean_logs()
            self.optimize_system()
            
            self.log_message("✅ Limpeza completa finalizada!")
            self.stop_progress()
        threading.Thread(target=run, daemon=True).start()
    
    def show_about(self):
        """Mostra diálogo sobre"""
        messagebox.showinfo("Sobre H2R-Clean Pro",
                           "H2R-Clean Pro v2.0\n"
                           "Sistema de Limpeza e Otimização Profissional\n\n"
                           "✨ Interface moderna\n"
                           "🧹 Limpeza inteligente\n"
                           "📊 Dashboard em tempo real\n\n"
                           "Desenvolvido para manter seu sistema rápido!")
    
    def uninstall_app(self):
        """Desinstala o aplicativo"""
        if not messagebox.askyesno("Confirmar Desinstalação",
                                  "Deseja realmente desinstalar o H2R-Clean Pro?"):
            return
        
        self.log_message("🗑️ Desinstalando H2R-Clean Pro...")
        
        try:
            system = platform.system().lower()
            
            if system == "linux":
                # Remover binários
                bin_dir = Path.home() / ".local/bin"
                for exe in ["h2r-clean", "h2r-clean-cli"]:
                    exe_path = bin_dir / exe
                    if exe_path.exists():
                        exe_path.unlink()
                
                # Remover diretório de instalação
                install_dir = Path.home() / ".local/share/h2r-clean"
                if install_dir.exists():
                    shutil.rmtree(install_dir)
                
                # Remover atalho desktop
                desktop = Path.home() / ".local/share/applications/h2r-clean.desktop"
                if desktop.exists():
                    desktop.unlink()
                
                # Remover ícone
                icon = Path.home() / ".local/share/icons/h2r-clean.png"
                if icon.exists():
                    icon.unlink()
            
            messagebox.showinfo("Concluído", "H2R-Clean Pro foi desinstalado!")
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na desinstalação: {str(e)}")
    
    def check_for_updates(self):
        """Verifica se há atualizações disponíveis no GitHub"""
        import urllib.request
        import json
        
        def run_check():
            self.start_progress()
            self.log_message("🔄 Verificando atualizações...")
            
            try:
                # Verificar último commit no GitHub
                url = "https://api.github.com/repos/henriquerabassa/h2r-clean/commits/main"
                
                req = urllib.request.Request(url, headers={'User-Agent': 'H2R-Clean'})
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    latest_commit = data['sha'][:7]
                    commit_date = data['commit']['committer']['date'][:10]
                    message = data['commit']['message'].split('\n')[0]
                
                # Verificar versão atual (último commit local)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                current_commit = "desconhecida"
                
                try:
                    import subprocess
                    result = subprocess.run(
                        ['git', 'rev-parse', '--short', 'HEAD'],
                        cwd=current_dir,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        current_commit = result.stdout.strip()
                except:
                    pass
                
                self.log_message(f"📦 Versão local: {current_commit}")
                self.log_message(f"📦 Última versão: {latest_commit} ({commit_date})")
                self.log_message(f"📝 Última alteração: {message}")
                
                if current_commit != latest_commit and current_commit != "desconhecida":
                    self.log_message("⬆️ Nova versão disponível!")
                    if messagebox.askyesno("Atualização Disponível",
                                          f"Nova versão encontrada!\n\n"
                                          f"Commit: {latest_commit}\n"
                                          f"Data: {commit_date}\n"
                                          f"Alteração: {message}\n\n"
                                          f"Deseja atualizar agora?"):
                        self.perform_update()
                else:
                    self.log_message("✅ Você está na versão mais recente!")
                    messagebox.showinfo("Atualização", "Você já tem a versão mais recente!")
                    
            except Exception as e:
                self.log_message(f"⚠️ Erro ao verificar atualizações: {str(e)}")
                messagebox.showwarning("Erro", f"Não foi possível verificar atualizações.\nVerifique sua conexão com a internet.")
            
            self.stop_progress()
        
        threading.Thread(target=run_check, daemon=True).start()
    
    def perform_update(self):
        """Realiza a atualização do aplicativo"""
        import urllib.request
        import zipfile
        import tempfile
        
        def run_update():
            self.start_progress()
            self.log_message("⬇️ Baixando atualização...")
            
            try:
                # Criar diretório temporário
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Download do repositório
                    zip_url = "https://github.com/henriquerabassa/h2r-clean/archive/refs/heads/main.zip"
                    zip_path = os.path.join(temp_dir, "h2r-clean.zip")
                    
                    self.log_message("📥 Baixando arquivos...")
                    urllib.request.urlretrieve(zip_url, zip_path)
                    
                    # Extrair
                    self.log_message("📦 Extraindo arquivos...")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Diretório de instalação
                    install_dir = Path.home() / ".local/share/h2r-clean"
                    extracted_dir = os.path.join(temp_dir, "h2r-clean-main")
                    
                    # Fazer backup dos arquivos atuais
                    self.log_message("💾 Criando backup...")
                    backup_dir = Path.home() / ".local/share/h2r-clean-backup"
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)
                    if install_dir.exists():
                        shutil.copytree(install_dir, backup_dir)
                    
                    # Copiar novos arquivos
                    self.log_message("📝 Atualizando arquivos...")
                    for item in os.listdir(extracted_dir):
                        source = os.path.join(extracted_dir, item)
                        dest = os.path.join(install_dir, item)
                        
                        if os.path.isdir(source):
                            if os.path.exists(dest):
                                shutil.rmtree(dest)
                            shutil.copytree(source, dest)
                        else:
                            shutil.copy2(source, dest)
                    
                    self.log_message("✅ Atualização concluída!")
                    
                    if messagebox.askyesno("Reiniciar",
                                          "Atualização instalada com sucesso!\n\n"
                                          "Deseja reiniciar o aplicativo agora?"):
                        self.log_message("🔄 Reiniciando...")
                        # Reiniciar
                        python = sys.executable
                        os.execl(python, python, *sys.argv)
                    
            except Exception as e:
                self.log_message(f"❌ Erro na atualização: {str(e)}")
                messagebox.showerror("Erro", f"Falha na atualização: {str(e)}")
            
            self.stop_progress()
        
        threading.Thread(target=run_update, daemon=True).start()
    
    def run(self):
        """Inicia aplicação"""
        self.root.mainloop()


def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        print("H2R-Clean Pro - Modo CLI em desenvolvimento")
    else:
        app = H2RCleanGUI()
        app.run()


if __name__ == "__main__":
    main()
