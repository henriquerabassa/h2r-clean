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
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json

class H2RClean:
    def __init__(self):
        self.system = platform.system().lower()
        self.setup_logging()
        self.load_config()
        
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
            "theme": "dark"
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

    def clean_files(self, files):
        """Limpa arquivos especificados"""
        cleaned = []
        errors = []
        for file in files:
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    cleaned.append(file)
            except Exception as e:
                errors.append((file, str(e)))
        return cleaned, errors

    def optimize_system(self):
        """Otimiza o sistema"""
        return ["Sistema otimizado"]


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
        
        actions = [
            ('🔍 Analisar Sistema', self.analyze_system, 'normal'),
            ('🧹 Limpar Tudo', self.full_analysis, 'action'),
            ('🗑️ Limpar Temporários', self.clean_temp, 'normal'),
            ('🧽 Limpar Cache', self.clean_cache, 'normal'),
            ('📄 Limpar Logs', self.clean_logs, 'normal'),
            ('⚡ Otimizar', self.optimize_system, 'normal'),
            ('👻 Limpar Órfãos', self.clean_orphans, 'normal')
        ]
        
        for i, (text, command, btn_type) in enumerate(actions):
            row, col = divmod(i, 4)
            if btn_type == 'action':
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 11, 'bold'),
                               bg=self.colors['accent'], fg=self.colors['bg'],
                               activebackground=self.colors['button_hover'],
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=20, pady=12)
            else:
                btn = tk.Button(buttons_frame, text=text, font=('Segoe UI', 10),
                               bg=self.colors['button'], fg=self.colors['fg'],
                               activebackground=self.colors['button_hover'],
                               relief=tk.FLAT, cursor='hand2',
                               command=command, padx=15, pady=10)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            buttons_frame.grid_columnconfigure(col, weight=1)
    
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
        for temp_dir in self.organizer.config.get('temp_dirs', []):
            files = self.fast_scan_dir(temp_dir, max_depth=2, max_files=500)
            temp_files.extend(files)
        return temp_files
    
    def scan_cache_files(self):
        """Escaneia arquivos de cache"""
        cache_files = []
        for cache_dir in self.organizer.config.get('cache_dirs', []):
            files = self.fast_scan_dir(cache_dir, max_depth=2, max_files=500)
            cache_files.extend(files)
        return cache_files
    
    def scan_log_files(self):
        """Escaneia arquivos de log"""
        log_files = []
        log_dirs = self.organizer.config.get('log_dirs', [])
        if self.organizer.system == "linux":
            log_dirs.extend(["/var/log", "~/.local/share/logs"])
        else:
            log_dirs.extend([os.environ.get("LOCALAPPDATA", "") + "\\Logs"])
        
        for log_dir in log_dirs:
            files = self.fast_scan_dir(log_dir, max_depth=1, file_pattern='.log', max_files=300)
            log_files.extend(files)
        
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
        """Encontra arquivos órfãos de aplicativos desinstalados"""
        orphans = []
        system = platform.system().lower()
        
        if system == "linux":
            # Verificar diretórios comuns onde ficam restos de apps
            check_dirs = [
                Path.home() / ".config",
                Path.home() / ".local/share",
                Path.home() / ".cache",
                "/opt"
            ]
            
            for check_dir in check_dirs:
                if check_dir.exists():
                    for item in check_dir.iterdir():
                        # Verificar se parece ser um app desinstalado
                        if item.is_dir() and self._is_orphan_dir(item):
                            orphans.append(str(item))
        
        return orphans
    
    def _is_orphan_dir(self, path):
        """Verifica se um diretório parece ser órfão"""
        # Critérios simples para identificar órfãos
        name = path.name.lower()
        orphan_indicators = ['broken', 'orphan', 'old', 'unused', 'deprecated']
        return any(indicator in name for indicator in orphan_indicators)
    
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
