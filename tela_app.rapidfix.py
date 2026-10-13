import hashlib
import json
import re
import sqlite3
import threading
import time
import random
import base64
import io
import tempfile
import webbrowser
import calendar  # Importado uma única vez no topo
from datetime import datetime, timedelta
from functools import lru_cache

import flet as ft
# Tentar importar bibliotecas opcionais
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

DB_FILE = "rapidfix.db"

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e))

def strong_password(p: str) -> bool:
    return len(p) >= 8 and any(c.isalpha() for c in p) and any(c.isdigit() for c in p)

def generate_referral_code(email):
    """Gera código de indicação único"""
    code = hashlib.md5(f"{email}{datetime.now()}".encode()).hexdigest()[:8].upper()
    return code

def main(page: ft.Page):
    page.title = "Rapidfix"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(color_scheme_seed="#0B5FFF", use_material3=True)
    page.window_width = 420
    page.window_height = 820
    page.padding = 16
    page.bgcolor = "#F3FBFD"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Cores
    C_PRIMARY, C_ACCENT, C_TEXT, C_MUTED, C_PANEL, C_BG = "#0B5FFF", "#0FA37F", "#10233F", "#5C6F82", "#FFFFFF", "#F3FBFD"
    
    # Modo escuro
    dark_mode = False
    
    def toggle_theme(e):
        nonlocal dark_mode, C_PRIMARY, C_ACCENT, C_TEXT, C_MUTED, C_PANEL, C_BG
        dark_mode = not dark_mode
        if dark_mode:
            page.theme_mode = ft.ThemeMode.DARK
            C_BG = "#121212"
            C_PANEL = "#1E1E1E"
            C_TEXT = "#FFFFFF"
            C_MUTED = "#B0B0B0"
            C_PRIMARY = "#3B82F6"
            C_ACCENT = "#10B981"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            C_BG = "#F3FBFD"
            C_PANEL = "#FFFFFF"
            C_TEXT = "#10233F"
            C_MUTED = "#5C6F82"
            C_PRIMARY = "#0B5FFF"
            C_ACCENT = "#0FA37F"
        page.update()
    
    # Constantes
    status_flow = ["Solicitado", "Confirmado", "Em andamento", "Finalizado"]
    weekday = {0: "Segunda", 1: "Terca", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sabado", 6: "Domingo"}
    services = {
        "Limpeza basica": {"base": 120, "h": 3},
        "Limpeza detalhada": {"base": 160, "h": 4},
        "Limpeza pesada": {"base": 220, "h": 5},
        "Pos-obra": {"base": 260, "h": 6},
        "Higienizacao": {"base": 190, "h": 4},
        "Passadoria": {"base": 90, "h": 2},
    }
    size_factor = {"Pequeno": 1.0, "Medio": 1.25, "Grande": 1.5}
    extras_price = {"Geladeira": 35, "Janelas": 45}
    coupons = {"BEMVINDO10": 0.10, "VIP15": 0.15}
    
    # Planos de assinatura
    subscription_plans = {
        "basic": {"price": 29.90, "features": ["Destaque por 7 dias", "5 fotos no perfil", "Estatísticas básicas"]},
        "pro": {"price": 79.90, "features": ["Destaque permanente", "Selo verificado", "20 fotos", "Estatísticas avançadas", "Suporte prioritário"]},
        "enterprise": {"price": 199.90, "features": ["Todos os benefícios PRO", "API de integração", "Suporte 24/7", "Gestor de contas"]}
    }
    
    rate_config = {"platform_fee": 0.08, "cancel_fee": 0.2}
    security_config = {"max_login_attempts": 5, "2fa_enabled": False}
    neighborhood_factor = {"centro": 1.08, "zona sul": 1.1, "zona norte": 1.03, "zona leste": 1.0, "zona oeste": 1.05}
    spam_words = ["pix urgente", "link suspeito", "clique aqui", "senha"]

    # Estruturas de dados
    users, avail, reqs, favs, notes, chats = {}, {}, [], {}, {}, {}
    notes_seen, login_attempts, audit_logs = {}, {}, []
    disputes = []  # Sistema de disputas
    location_history = {}  # Histórico de localização
    next_id = {"v": 1}
    cur_user, selected_provider, selected_chat_req = {"d": None}, {"d": None}, {"d": None}
    recent_searches = {"v": []}
    
    # Notificações em tempo real
    last_unread_count = 0
    notification_thread_running = False

    # Funções de banco de dados
    def db_exec(sql, args=(), one=False):
        with sqlite3.connect(DB_FILE) as c:
            cur = c.execute(sql, args)
            c.commit()
            return cur.fetchone() if one else cur.fetchall()

    def db_get(k, default):
        db_exec("CREATE TABLE IF NOT EXISTS app_state(k TEXT PRIMARY KEY, v TEXT)")
        row = db_exec("SELECT v FROM app_state WHERE k=?", (k,), one=True)
        if not row:
            return default
        try:
            return json.loads(row[0])
        except Exception:
            return default

    def db_set(k, v):
        db_exec("CREATE TABLE IF NOT EXISTS app_state(k TEXT PRIMARY KEY, v TEXT)")
        db_exec("INSERT INTO app_state(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, json.dumps(v)))

    def save_all():
        db_set("users", users)
        db_set("avail", avail)
        db_set("reqs", reqs)
        db_set("favs", {k: list(v) for k, v in favs.items()})
        db_set("notes", notes)
        db_set("notes_seen", notes_seen)
        db_set("chats", chats)
        db_set("next_id", next_id)
        db_set("recent_searches", recent_searches)
        db_set("coupons", coupons)
        db_set("rate_config", rate_config)
        db_set("audit_logs", audit_logs)
        db_set("disputes", disputes)
        db_set("location_history", location_history)

    # Loading overlay
    loading_overlay = ft.Container(visible=False, expand=True, bgcolor="#80000000", content=ft.Row([ft.Column([ft.ProgressRing(), ft.Text("Carregando...", color=ft.Colors.WHITE)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER))

    def show_loading():
        if loading_overlay not in page.overlay:
            page.overlay.append(loading_overlay)
        loading_overlay.visible = True
        page.update()

    def hide_loading():
        loading_overlay.visible = False
        page.update()

    def vibrate_feedback():
        if hasattr(page, "vibrate"):
            try:
                page.vibrate(30)
            except Exception:
                pass

    # Carregar dados
    def load_all():
        users.update(db_get("users", {}))
        avail.update(db_get("avail", {}))
        reqs.extend(db_get("reqs", []))
        for k, v in db_get("favs", {}).items():
            favs[k] = set(v)
        notes.update(db_get("notes", {}))
        notes_seen.update(db_get("notes_seen", {}))
        chats.update(db_get("chats", {}))
        next_id["v"] = int(db_get("next_id", {"v": 1}).get("v", 1))
        recent_searches["v"] = db_get("recent_searches", {"v": []}).get("v", [])
        coupons.update(db_get("coupons", {}))
        rate_config.update(db_get("rate_config", {"platform_fee": 0.08, "cancel_fee": 0.2}))
        audit_logs.extend(db_get("audit_logs", []))
        disputes.extend(db_get("disputes", []))
        location_history.update(db_get("location_history", {}))
        
        if users:
            for u in users.values():
                u.setdefault("pro_plan", False)
                u.setdefault("verified", False)
                u.setdefault("featured", False)
                u.setdefault("blocked", False)
                u.setdefault("is_admin", False)
                u.setdefault("identity_ok", False)
                u.setdefault("residence_ok", False)
                u.setdefault("accept_rate", 0.85)
                u.setdefault("avg_response_min", 15)
                u.setdefault("reliability", 80)
                u.setdefault("plan", "free")
                u.setdefault("referral_code", generate_referral_code(u["email"]) if u.get("email") else "")
                u.setdefault("referral_bonus", 0)
                u.setdefault("push_token", "")
                u.setdefault("2fa_enabled", False)
                u.setdefault("2fa_secret", "")
            return
            
        # Dados iniciais
        users.update(
            {
                "demo@rapidfix.com": {"name": "Rapidfix Demo", "email": "demo@rapidfix.com", "password": hash_password("12345678"), "profile_type": "Empresa de limpeza", "bio": "Equipe especializada em limpeza residencial e comercial.", "rating": 4.9, "reviews": 187, "avatar_url": "https://picsum.photos/id/1011/200/200", "cover_url": "https://picsum.photos/id/1018/800/260", "work_photos": ["https://picsum.photos/id/1060/320/220", "https://picsum.photos/id/1048/320/220", "https://picsum.photos/id/1074/320/220", "https://picsum.photos/id/1043/320/220"], "areas": "Centro, Zona Sul e Zona Oeste", "neighborhood": "Centro", "services": ["Limpeza basica", "Limpeza pesada", "Pos-obra"], "base_price": 170, "avg_duration_min": 210, "response_rate": 98, "is_admin": True, "verified": True, "identity_ok": True, "residence_ok": True, "plan": "enterprise", "referral_code": "DEMO2026", "referral_bonus": 0},
                "brilho@rapidfix.com": {"name": "Brilho Total", "email": "brilho@rapidfix.com", "password": hash_password("12345678"), "profile_type": "Empresa de limpeza", "bio": "Limpeza pesada e pos-obra.", "rating": 4.8, "reviews": 93, "avatar_url": "https://picsum.photos/id/1027/200/200", "cover_url": "https://picsum.photos/id/1021/800/260", "work_photos": ["https://picsum.photos/id/1033/320/220", "https://picsum.photos/id/1041/320/220", "https://picsum.photos/id/1050/320/220"], "areas": "Centro e Zona Norte", "neighborhood": "Zona Norte", "services": ["Limpeza pesada", "Pos-obra", "Higienizacao"], "base_price": 190, "avg_duration_min": 240, "response_rate": 95, "featured": True, "pro_plan": True, "verified": True, "accept_rate": 0.93, "avg_response_min": 9, "plan": "pro", "referral_code": "BRILHO88"},
                "ana@rapidfix.com": {"name": "Ana Diarista", "email": "ana@rapidfix.com", "password": hash_password("12345678"), "profile_type": "Diarista", "bio": "Atendimento caprichoso para casas e apartamentos.", "rating": 4.7, "reviews": 64, "avatar_url": "https://picsum.photos/id/1005/200/200", "cover_url": "https://picsum.photos/id/1003/800/260", "work_photos": ["https://picsum.photos/id/1067/320/220", "https://picsum.photos/id/1068/320/220", "https://picsum.photos/id/1070/320/220"], "areas": "Zona Leste e Centro", "neighborhood": "Zona Leste", "services": ["Limpeza basica", "Passadoria", "Limpeza detalhada"], "base_price": 140, "avg_duration_min": 180, "response_rate": 97, "accept_rate": 0.9, "avg_response_min": 11, "plan": "basic", "referral_code": "ANA007"},
            }
        )
        avail.update({"demo@rapidfix.com": ["2026-02-27 08:00", "2026-02-27 13:00", "2026-02-28 09:00"], "brilho@rapidfix.com": ["2026-02-27 10:00", "2026-02-28 08:30", "2026-03-01 09:00"], "ana@rapidfix.com": ["2026-02-27 09:00", "2026-02-27 15:00", "2026-02-28 08:00"]})
        chats["perfil:demo@rapidfix.com"] = [{"author": "Cliente", "text": "Oi, voces atendem no sabado?", "time": now_str()}, {"author": "Rapidfix Demo", "text": "Atendemos sim, das 8h as 17h.", "time": now_str()}]
        save_all()

    load_all()

    # File Picker para upload de fotos
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    # Componentes UI
    login_email = ft.TextField(label="E-mail", border_radius=12)
    login_password = ft.TextField(label="Senha", password=True, can_reveal_password=True, border_radius=12)
    reg_name = ft.TextField(label="Nome", border_radius=12)
    reg_email = ft.TextField(label="E-mail", border_radius=12)
    reg_password = ft.TextField(label="Senha (min 8, letras e numeros)", password=True, can_reveal_password=True, border_radius=12)
    reg_type = ft.Dropdown(label="Tipo de perfil", value="Usuario normal (cliente)", border_radius=12, options=[ft.dropdown.Option("Usuario normal (cliente)"), ft.dropdown.Option("Empresa de limpeza"), ft.dropdown.Option("Diarista")])
    reg_neighborhood = ft.TextField(label="Bairro", border_radius=12)
    reg_bio = ft.TextField(label="Descricao", multiline=True, min_lines=2, max_lines=4, border_radius=12)
    reg_referral = ft.TextField(label="Código de indicação (opcional)", border_radius=12)

    search = ft.TextField(prefix_icon=ft.Icons.SEARCH, hint_text="Pesquisar...", border_radius=12)
    req_coupon = ft.TextField(label="Cupom (opcional)", border_radius=12)
    req_date_picker = ft.DatePicker()
    req_selected_day = {"v": None}
    
    # Filtros básicos
    f_type = ft.Dropdown(label="Tipo", value="Todos", width=180, border_radius=12, options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Empresa de limpeza"), ft.dropdown.Option("Diarista")])
    f_rate = ft.Dropdown(label="Nota", value="Todas", width=180, border_radius=12, options=[ft.dropdown.Option("Todas"), ft.dropdown.Option("4.5+"), ft.dropdown.Option("4.8+")])
    f_price = ft.Dropdown(label="Preco", value="Qualquer", width=180, border_radius=12, options=[ft.dropdown.Option("Qualquer"), ft.dropdown.Option("Ate R$ 150"), ft.dropdown.Option("Ate R$ 200"), ft.dropdown.Option("Ate R$ 250")])
    f_neighborhood = ft.TextField(label="Bairro", width=180, border_radius=12)
    f_day = ft.Dropdown(label="Dia disponivel", value="Todos", width=180, border_radius=12, options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(v) for v in ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]])
    
    # Filtros avançados
    advanced_filters_expanded = False
    f_distancia = ft.Slider(min=1, max=50, value=10, label="{value} km", width=200)
    f_tempo_resposta = ft.Dropdown(
        label="Tempo de resposta",
        value="Qualquer",
        width=180,
        border_radius=12,
        options=[ft.dropdown.Option("Qualquer"), ft.dropdown.Option("15 min"), ft.dropdown.Option("30 min"), ft.dropdown.Option("1 hora")]
    )
    f_aceita_cartao = ft.Checkbox(label="Aceita cartão")
    f_atende_fds = ft.Checkbox(label="Atende fim de semana")
    f_com_selo = ft.Checkbox(label="Com selo verificado")

    provider_col, fav_col = ft.Column(spacing=10), ft.Column(spacing=8)
    chat_title, chat_list, chat_input, typing_text = ft.Text("Chat", size=20, weight=ft.FontWeight.BOLD), ft.ListView(expand=True, auto_scroll=True), ft.TextField(hint_text="Mensagem...", expand=True, border_radius=12), ft.Text("", size=11, color=C_MUTED)
    req_service = ft.Dropdown(label="Tipo de servico", border_radius=12)
    req_day = ft.Dropdown(label="Dia", border_radius=12)
    req_slot = {"v": None}
    req_slots = ft.ResponsiveRow(run_spacing=8, spacing=8)
    req_addr, req_size = ft.TextField(label="Endereco", border_radius=12), ft.Dropdown(label="Tamanho", value="Pequeno", border_radius=12, options=[ft.dropdown.Option("Pequeno"), ft.dropdown.Option("Medio"), ft.dropdown.Option("Grande")])
    req_pay = ft.Dropdown(label="Pagamento", value="PIX", border_radius=12, options=[ft.dropdown.Option("PIX"), ft.dropdown.Option("Cartao")])
    req_fridge, req_windows, req_notes = ft.Checkbox(label="Limpar geladeira"), ft.Checkbox(label="Limpar janelas"), ft.TextField(label="Observacoes", multiline=True, min_lines=2, max_lines=4, border_radius=12)
    req_slot_text, req_est = ft.Text("Horario selecionado: nenhum", color=C_MUTED, size=12), ft.Text("Estimativa: R$ 0 | 0h", color=C_PRIMARY, weight=ft.FontWeight.BOLD)

    # Aplicar estilo
    def style(c):
        if isinstance(c, ft.Checkbox):
            c.label_style = ft.TextStyle(color=C_TEXT)
            return
        c.bgcolor, c.border_color, c.focused_border_color = "#F7FAFD", "#CFDCEB", C_PRIMARY
        c.text_style = ft.TextStyle(color=C_TEXT)
        if hasattr(c, "label_style"):
            c.label_style = ft.TextStyle(color=C_MUTED)

    for c in [login_email, login_password, reg_name, reg_email, reg_password, reg_type, reg_neighborhood, reg_bio, reg_referral, search, f_type, f_rate, f_price, f_neighborhood, f_day, f_tempo_resposta, chat_input, req_service, req_day, req_addr, req_size, req_pay, req_fridge, req_windows, req_notes, req_coupon]:
        style(c)

    # Funções utilitárias
    def panel(content, expand=False):
        return ft.Container(padding=18, border_radius=20, bgcolor=C_PANEL, border=ft.border.all(1, "#DEE7F2"), shadow=ft.BoxShadow(blur_radius=16, color="#180A2540", offset=ft.Offset(0, 4)), content=content, expand=expand)

    def content_width():
        w = page.width or page.window_width or 420
        if w < 600:
            return max(int(w) - 24, 280)
        if w < 1024:
            return 760
        return 980

    def centered_view(route, content, scroll=ft.ScrollMode.AUTO):
        return ft.View(
            route=route,
            bgcolor=C_BG,
            scroll=scroll,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    [ft.Container(width=content_width(), content=content)],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
        )

    def btn(text, icon, on_click):
        return ft.ElevatedButton(text, icon=icon, on_click=on_click, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), bgcolor=C_PRIMARY, color=ft.Colors.WHITE, padding=14))

    def social_badge(brand):
        is_google = brand == "google"
        return ft.Container(
            width=22,
            height=22,
            border_radius=11,
            bgcolor="#FFFFFF" if is_google else "#1877F2",
            border=ft.border.all(1, "#D6E3EE" if is_google else "#1877F2"),
            content=ft.Row(
                [ft.Text("G" if is_google else "f", weight=ft.FontWeight.BOLD, color="#DB4437" if is_google else ft.Colors.WHITE, size=12)],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def social_btn(text, on_click, brand):
        return ft.OutlinedButton(
            on_click=on_click,
            content=ft.Row([social_badge(brand), ft.Text(text, color=C_TEXT)], spacing=8, tight=True),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(1, "#CFE0EE"),
                padding=14,
            ),
        )

    def chip(t, icon):
        return ft.Container(padding=ft.padding.symmetric(horizontal=10, vertical=6), border_radius=999, bgcolor="#ECF9FF", border=ft.border.all(1, "#D4E5F8"), content=ft.Row([ft.Icon(icon, size=14, color=C_PRIMARY), ft.Text(t, size=12, color=C_TEXT)], spacing=6))

    def notify(text, ok=True):
        page.snack_bar = ft.SnackBar(ft.Text(text), bgcolor="#1E8E3E" if ok else "#D93025", open=True)
        page.update()

    def push_note(email, text):
        notes.setdefault(email, [])
        notes[email].insert(0, f"[{now_str()}] {text}")
        notes[email] = notes[email][:30]
        save_all()

    def unread_count(email):
        return max(len(notes.get(email, [])) - int(notes_seen.get(email, 0)), 0)

    def mark_notes_seen(email):
        notes_seen[email] = len(notes.get(email, []))
        save_all()

    def audit(action, actor="", target="", details=""):
        audit_logs.insert(0, {"time": now_str(), "action": action, "actor": actor, "target": target, "details": details[:200]})
        del audit_logs[120:]
        save_all()

    def valid_address(addr):
        a = (addr or "").strip()
        return len(a) >= 8 and bool(re.search(r"\d", a))

    def is_valid_coupon(code):
        c = (code or "").strip().upper()
        return (not c) or c in coupons

    def is_admin(u):
        return bool(u and u.get("is_admin"))

    def is_provider(u): return u["profile_type"] in ["Empresa de limpeza", "Diarista"]
    def is_client(u): return u["profile_type"] == "Usuario normal (cliente)"
    def fav_set(email): favs.setdefault(email, set()); return favs[email]
    
    def day_name(slot):
        try: return weekday[datetime.strptime(slot, "%Y-%m-%d %H:%M").weekday()]
        except Exception: return "Indefinido"
    
    def status_color(s): return {"Solicitado": "#F59E0B", "Confirmado": "#0284C7", "Em andamento": "#0B5FFF", "Finalizado": "#1E8E3E"}.get(s, C_MUTED)

    def get_available_slots(provider_email):
        occupied = {r["date_slot"] for r in reqs if r["provider_email"] == provider_email and r["status"] != "Cancelado"}
        return [s for s in avail.get(provider_email, []) if s not in occupied]

    def next_slots_by_neighborhood(neighborhood, limit=4):
        nb = (neighborhood or "").strip().lower()
        ranked = []
        for p in users.values():
            if not is_provider(p):
                continue
            if nb and nb not in (p.get("neighborhood", "") or "").lower() and nb not in (p.get("areas", "") or "").lower():
                continue
            for s in get_available_slots(p["email"]):
                ranked.append((s, p))
        ranked.sort(key=lambda x: x[0])
        return ranked[:limit]

    def calc_est(provider, service, size, fridge, windows):
        d = services.get(service, services["Limpeza basica"])
        dur = float(d["h"]) + (0.5 if fridge else 0) + (1 if windows else 0)
        ext = (extras_price["Geladeira"] if fridge else 0) + (extras_price["Janelas"] if windows else 0)
        factor = max(provider.get("base_price", 120) / 120.0, 0.8)
        nb_factor = neighborhood_factor.get((provider.get("neighborhood", "") or "").strip().lower(), 1.0)
        price = int(d["base"] * size_factor.get(size, 1.0) * factor * nb_factor + ext)
        return price, round(dur * size_factor.get(size, 1.0), 1)

    def suggest_service_ai(text):
        t = (text or "").lower()
        if any(k in t for k in ["obra", "poeira", "cimento"]):
            return "Pos-obra"
        if any(k in t for k in ["gordura", "pesado", "muito sujo"]):
            return "Limpeza pesada"
        if any(k in t for k in ["detalhe", "detalhada"]):
            return "Limpeza detalhada"
        return "Limpeza basica"

    def update_est(_=None):
        p = selected_provider["d"]
        if not p:
            req_est.value = "Estimativa: R$ 0 | 0h"
            return
        price, h = calc_est(p, req_service.value or "Limpeza basica", req_size.value or "Pequeno", req_fridge.value, req_windows.value)
        discount = int(price * coupons.get((req_coupon.value or "").strip().upper(), 0))
        after_coupon = max(price - discount, 0)
        total = int(after_coupon * (1 + float(rate_config.get("platform_fee", 0.08))))
        req_est.value = f"Estimativa: R$ {total} | {h}h"
        if page.route == "/solicitar": page.update()

    req_service.on_change = update_est
    req_size.on_change = update_est
    req_fridge.on_change = update_est
    req_windows.on_change = update_est
    req_coupon.on_change = update_est

    # Funções de calendário
    def on_pick_date(e):
        if e.control.value:
            req_selected_day["v"] = e.control.value.strftime("%Y-%m-%d")
            req_day.value = req_selected_day["v"]
            rebuild_slots(selected_provider["d"]["email"] if selected_provider["d"] else "")
            page.update()

    req_date_picker.on_change = on_pick_date
    page.overlay.append(req_date_picker)

    def open_calendar(_):
        try:
            req_date_picker.pick_date()
        except Exception:
            try:
                page.open(req_date_picker)
            except Exception:
                notify("Calendario indisponivel nesta versao.", False)

    # Funções de filtro e busca
    def get_provider_list(query):
        ps = [u for u in users.values() if is_provider(u)]
        
        # Filtros básicos
        if (f_type.value or "Todos") != "Todos": 
            ps = [u for u in ps if u["profile_type"] == f_type.value]
        if (f_rate.value or "Todas") == "4.5+": 
            ps = [u for u in ps if u.get("rating", 0) >= 4.5]
        elif (f_rate.value or "Todas") == "4.8+": 
            ps = [u for u in ps if u.get("rating", 0) >= 4.8]
        
        cap = {"Ate R$ 150": 150, "Ate R$ 200": 200, "Ate R$ 250": 250}
        if f_price.value in cap: 
            ps = [u for u in ps if int(u.get("base_price", 9999)) <= cap[f_price.value]]
        
        nb = (f_neighborhood.value or "").strip().lower()
        if nb: 
            ps = [u for u in ps if nb in (u.get("neighborhood", "") or "").lower() or nb in (u.get("areas", "") or "").lower()]
        
        if (f_day.value or "Todos") != "Todos": 
            ps = [u for u in ps if any(day_name(s) == f_day.value for s in avail.get(u["email"], []))]
        
        # Filtros avançados
        if f_tempo_resposta.value != "Qualquer":
            minutos = {"15 min": 15, "30 min": 30, "1 hora": 60}
            ps = [u for u in ps if u.get("avg_response_min", 999) <= minutos.get(f_tempo_resposta.value, 999)]
        
        if f_aceita_cartao.value:
            # Implementar lógica de aceitação de cartão
            pass
        
        if f_atende_fds.value:
            ps = [u for u in ps if any(day_name(s) in ["Sabado", "Domingo"] for s in avail.get(u["email"], []))]
        
        if f_com_selo.value:
            ps = [u for u in ps if u.get("verified")]
        
        # Busca por texto
        q = (query or "").strip().lower()
        if q and q not in recent_searches["v"]:
            recent_searches["v"] = ([q] + recent_searches["v"])[:8]
            save_all()
        if q: 
            ps = [u for u in ps if q in u["name"].lower() or q in u["profile_type"].lower() or q in u.get("bio", "").lower() or q in u.get("areas", "").lower()]
        
        # Smart ranking para clientes
        if cur_user["d"] and is_client(cur_user["d"]):
            me = cur_user["d"]["email"]
            used = {r["provider_email"] for r in reqs if r["client_email"] == me}
            for p in ps:
                p["_smart"] = 1 if p["email"] in used else 0
        
        return sorted(ps, key=lambda p: (1 if p.get("featured") else 0, 1 if p.get("pro_plan") else 0, p.get("_smart", 0), p.get("rating", 0), p.get("reviews", 0)), reverse=True)

    def refresh_fav():
        fav_col.controls.clear()
        u = cur_user["d"]
        if not u or not is_client(u): return
        p = [users[e] for e in fav_set(u["email"]) if e in users and is_provider(users[e])]
        if not p: 
            fav_col.controls.append(ft.Text("Voce ainda nao favoritou nenhum prestador.", size=12, color=C_MUTED))
            return
        for pr in p: 
            fav_col.controls.append(ft.TextButton(f"{pr['name']} ({pr['profile_type']})", icon=ft.Icons.STAR, on_click=lambda _, x=pr: open_profile(x)))

    # CORREÇÃO: Indentação correta para open_profile
    def open_profile(p):
        selected_provider["d"], selected_chat_req["d"] = p, None
        page.go("/perfil-servico")

    def toggle_fav(p):
        u = cur_user["d"]
        if not u or not is_client(u): 
            notify("Somente clientes podem favoritar prestadores.", False); 
            return
        s = fav_set(u["email"])
        if p["email"] in s: 
            s.remove(p["email"]); 
            notify("Removido dos favoritos.")
        else: 
            s.add(p["email"]); 
            notify("Adicionado aos favoritos.")
        save_all(); 
        refresh_fav(); 
        refresh_providers()

    def provider_card(p):
        can_fav = cur_user["d"] and is_client(cur_user["d"])
        nxt = (get_available_slots(p["email"]) or ["Sem horarios livres"])[0]
        badges = []
        if p.get("verified"): 
            badges.append(chip("Selo verificado", ft.Icons.VERIFIED))
        if p.get("pro_plan"): 
            badges.append(chip("Plano PRO", ft.Icons.DIAMOND))
        if p.get("featured"): 
            badges.append(chip("Destaque", ft.Icons.AUTO_AWESOME))
        
        return ft.Container(
            padding=12, 
            border_radius=14, 
            bgcolor=C_PANEL, 
            border=ft.border.all(2 if p.get("featured") else 1, "#8EC5FF" if p.get("featured") else "#DFE8F3"), 
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT), 
            content=ft.Column([
                ft.Row([
                    ft.CircleAvatar(foreground_image_src=p.get("avatar_url"), 
                                   content=ft.Text(p["name"][:1].upper()), 
                                   bgcolor="#D8E9FF"), 
                    ft.Column([
                        ft.Text(p["name"], size=16, weight=ft.FontWeight.BOLD), 
                        ft.Text(p["profile_type"], color=C_MUTED, size=12)
                    ], spacing=2, expand=True), 
                    ft.Container(
                        padding=6, 
                        border_radius=10, 
                        bgcolor="#F1FBFF", 
                        content=ft.Text(f"{p.get('rating', 0)} ({p.get('reviews', 0)})", 
                                       size=11, color=C_PRIMARY)
                    )
                ]), 
                ft.Text(p["bio"], size=13, color="#31485F"), 
                ft.Row([
                    chip(f"Bairro: {p.get('neighborhood', 'Nao informado')}", ft.Icons.PLACE), 
                    chip(f"Base R$ {p.get('base_price', 120)}", ft.Icons.PAID)
                ], spacing=8, wrap=True), 
                ft.Row(badges, spacing=8, wrap=True) if badges else ft.Text(""), 
                ft.Text(f"Regioes: {p.get('areas', 'Nao informado')}", size=12, color=C_MUTED), 
                ft.Text(f"Proximo horario: {nxt}", size=12, color=C_MUTED), 
                ft.Row([
                    btn("Ver perfil", ft.Icons.PERSON, lambda _, x=p: open_profile(x)), 
                    ft.IconButton(
                        icon=ft.Icons.STAR if (cur_user["d"] and is_client(cur_user["d"]) and 
                                              p["email"] in fav_set(cur_user["d"]["email"])) else ft.Icons.STAR_BORDER, 
                        icon_color="#E5A100", 
                        on_click=lambda _, x=p: toggle_fav(x), 
                        disabled=not can_fav
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=8)
        )

    def refresh_providers():
        provider_col.controls.clear()
        ps = get_provider_list(search.value or "")
        if not ps: 
            provider_col.controls.append(ft.Container(
                padding=14, 
                border_radius=12, 
                bgcolor="#FFFFFF", 
                content=ft.Text("Nenhum perfil encontrado.", color=C_MUTED)
            ))
        else:
            for p in ps: 
                provider_col.controls.append(provider_card(p))
        if page.route == "/inicio": 
            page.update()

    search.on_change = lambda _: refresh_providers()
    f_neighborhood.on_change = lambda _: refresh_providers()
    for d in [f_type, f_rate, f_price, f_day, f_tempo_resposta, f_aceita_cartao, f_atende_fds, f_com_selo]: 
        d.on_change = lambda _: refresh_providers()

    # Funções de autenticação
    def do_login(_):
        show_loading()
        email, password = (login_email.value or "").strip().lower(), (login_password.value or "").strip()
        if not email or not password: 
            hide_loading(); 
            notify("Preencha e-mail e senha.", False); 
            return
        
        if int(login_attempts.get(email, 0)) >= int(security_config["max_login_attempts"]):
            hide_loading(); 
            notify("Muitas tentativas. Conta temporariamente bloqueada.", False); 
            audit("login_blocked", email, email, "max attempts"); 
            return
        
        u = users.get(email)
        if not u or u.get("password") != hash_password(password):
            login_attempts[email] = int(login_attempts.get(email, 0)) + 1
            audit("login_failed", email, email, f"attempt={login_attempts[email]}")
            hide_loading(); 
            notify("Credenciais invalidas.", False); 
            return
        
        if is_client(u):
            user_reqs = [r for r in reqs if r.get("client_email") == email]
            canc = len([r for r in user_reqs if r.get("status") == "Cancelado"])
            u["reliability"] = max(20, 100 - canc * 8)
            if canc >= 8:
                u["blocked"] = True
        
        if u.get("blocked"): 
            hide_loading(); 
            notify("Conta bloqueada por seguranca.", False); 
            return
        
        login_attempts[email] = 0
        
        # Verificação em duas etapas
        if u.get("2fa_enabled"):
            send_2fa_code(email)
            verify_2fa_dialog(email)
            hide_loading()
            return
        
        cur_user["d"], selected_chat_req["d"] = u, None
        push_note(email, "Login realizado com sucesso.")
        audit("login_success", email, email, "ok")
        vibrate_feedback()
        notify("Login realizado com sucesso.")
        hide_loading()
        
        # Iniciar notificações em tempo real
        start_notification_thread()
        
        page.go("/inicio-prestador" if is_provider(u) else "/inicio")

    def do_google_login(_):
        notify("Login com Google sera disponibilizado em breve.")

    def do_facebook_login(_):
        notify("Login com Facebook sera disponibilizado em breve.")

    def do_register(_):
        show_loading()
        name, email = (reg_name.value or "").strip(), (reg_email.value or "").strip().lower()
        pw, typ, nb = (reg_password.value or "").strip(), reg_type.value, (reg_neighborhood.value or "").strip()
        bio = (reg_bio.value or "").strip() or "Sem descricao por enquanto."
        referral = (reg_referral.value or "").strip().upper()
        
        if not all([name, email, pw, typ]): 
            hide_loading(); 
            notify("Preencha todos os campos obrigatorios.", False); 
            return
        
        if not valid_email(email): 
            hide_loading(); 
            notify("Informe um e-mail valido.", False); 
            return
        
        if not strong_password(pw): 
            hide_loading(); 
            notify("Senha fraca: minimo 8 caracteres com letras e numeros.", False); 
            return
        
        if email in users: 
            hide_loading(); 
            notify("Este e-mail ja esta cadastrado.", False); 
            return
        
        u = {
            "name": name, 
            "email": email, 
            "password": hash_password(pw), 
            "profile_type": typ, 
            "bio": bio, 
            "rating": 0, 
            "reviews": 0, 
            "avatar_url": "https://picsum.photos/id/1001/200/200", 
            "cover_url": "https://picsum.photos/id/1002/800/260", 
            "work_photos": ["https://picsum.photos/id/1035/320/220", "https://picsum.photos/id/1037/320/220", "https://picsum.photos/id/1038/320/220"], 
            "areas": nb or "Nao informado", 
            "neighborhood": nb or "Nao informado", 
            "services": ["Limpeza basica"], 
            "base_price": 120, 
            "avg_duration_min": 180, 
            "response_rate": 95, 
            "pro_plan": False, 
            "verified": False, 
            "featured": False, 
            "blocked": False, 
            "is_admin": False, 
            "identity_ok": False, 
            "residence_ok": False, 
            "accept_rate": 0.8, 
            "avg_response_min": 20, 
            "reliability": 80,
            "plan": "free",
            "referral_code": generate_referral_code(email),
            "referral_bonus": 0,
            "2fa_enabled": False
        }
        
        users[email] = u
        
        # Aplicar código de indicação se fornecido
        if referral and referral != u["referral_code"]:
            apply_referral(referral)
        
        if is_provider(u): 
            avail[email] = ["2026-02-27 09:00", "2026-02-27 14:00", "2026-02-28 09:00"]
        
        cur_user["d"] = u
        reg_name.value = reg_email.value = reg_password.value = reg_bio.value = reg_neighborhood.value = reg_referral.value = ""
        reg_type.value = "Usuario normal (cliente)"
        save_all(); 
        refresh_providers()
        audit("register", email, email, typ)
        vibrate_feedback()
        notify("Cadastro criado com sucesso.")
        hide_loading()
        
        # Iniciar notificações em tempo real
        start_notification_thread()
        
        page.go("/inicio-prestador" if is_provider(u) else "/inicio")

    # Sistema de notificações em tempo real
    def check_notifications():
        nonlocal last_unread_count
        global notification_thread_running
        notification_thread_running = True
        while notification_thread_running:
            if cur_user["d"]:
                current_unread = unread_count(cur_user["d"]["email"])
                if current_unread > last_unread_count:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Você tem {current_unread} novas notificações!"),
                        bgcolor=C_PRIMARY
                    )
                    page.snack_bar.open = True
                    page.update()
                    vibrate_feedback()
                last_unread_count = current_unread
            time.sleep(30)

    def start_notification_thread():
        global notification_thread_running
        if not notification_thread_running:
            thread = threading.Thread(target=check_notifications, daemon=True)
            thread.start()

    # Verificação em duas etapas
    def send_2fa_code(email):
        code = random.randint(100000, 999999)
        users[email]["2fa_code"] = code
        users[email]["2fa_expires"] = (datetime.now() + timedelta(minutes=5)).isoformat()
        save_all()
        
        # Simular envio de email/SMS
        notify(f"Código 2FA: {code} (simulado)")
        return code

    def verify_2fa_dialog(email):
        code_field = ft.TextField(label="Código de verificação", border_radius=12)
        
        def verify_code(e):
            if (code_field.value == str(users[email].get("2fa_code")) and 
                datetime.now() < datetime.fromisoformat(users[email]["2fa_expires"])):
                page.dialog.open = False
                cur_user["d"] = users[email]
                push_note(email, "Login com 2FA realizado com sucesso.")
                audit("login_success_2fa", email, email, "2fa")
                page.go("/inicio-prestador" if is_provider(users[email]) else "/inicio")
                page.update()
            else:
                notify("Código inválido ou expirado", False)
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Verificação em duas etapas"),
            content=ft.Column([ft.Text("Digite o código enviado para seu email"), code_field], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False)), 
                ft.ElevatedButton("Verificar", on_click=verify_code)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    # Biometria
    def setup_biometric():
        if cur_user["d"] and hasattr(page, "authenticate_with_biometrics"):
            try:
                success = page.authenticate_with_biometrics("Login no Rapidfix")
                if success:
                    notify("Autenticação biométrica bem-sucedida!")
                    return True
            except Exception:
                notify("Biometria não disponível neste dispositivo", False)
        return False

    # Upload de fotos
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files and cur_user["d"]:
            for f in e.files:
                try:
                    with open(f.path, "rb") as image_file:
                        encoded = base64.b64encode(image_file.read()).decode()
                        if page.route == "/perfil-servico" and selected_provider["d"] == cur_user["d"]:
                            cur_user["d"]["work_photos"].append(f"data:image/jpeg;base64,{encoded}")
                            notify("Foto adicionada ao perfil!")
                        elif page.route == "/chat":
                            active_msgs().append({
                                "author": cur_user["d"]["name"],
                                "text": f"📷 {f.name}",
                                "image": f"data:image/jpeg;base64,{encoded}",
                                "time": now_str()
                            })
                            save_all()
                            render_chat()
                            page.update()
                        elif page.route == "/avaliacao" and hasattr(page, "current_review"):
                            # Para avaliação com fotos
                            if "review_photos" not in page.current_review:
                                page.current_review["review_photos"] = []
                            page.current_review["review_photos"].append(f"data:image/jpeg;base64,{encoded}")
                            notify("Foto adicionada à avaliação!")
                except Exception as ex:
                    notify(f"Erro ao fazer upload: {str(ex)}", False)
            save_all()

    file_picker.on_result = pick_files_result

    # Função para mostrar mapa
    def show_map(address):
        if not HAS_FOLIUM:
            notify("Biblioteca folium não instalada. Use: pip install folium", False)
            return
        
        try:
            # Criar mapa com a localização (exemplo: São Paulo)
            m = folium.Map(location=[-23.5505, -46.6333], zoom_start=13)
            folium.Marker([-23.5505, -46.6333], popup=address).add_to(m)
            
            # Salvar como HTML temporário
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                m.save(f.name)
                webbrowser.open(f.name)
        except Exception as ex:
            notify(f"Erro ao abrir mapa: {str(ex)}", False)

    # Função para upgrade de plano
    def upgrade_plan(plan):
        if not cur_user["d"] or not is_provider(cur_user["d"]):
            notify("Apenas prestadores podem assinar planos", False)
            return
        
        plan_data = subscription_plans.get(plan)
        if not plan_data:
            return
        
        def confirm_upgrade(e):
            cur_user["d"]["plan"] = plan
            cur_user["d"]["pro_plan"] = plan in ["pro", "enterprise"]
            cur_user["d"]["featured"] = plan in ["pro", "enterprise"]
            cur_user["d"]["verified"] = plan in ["pro", "enterprise"]
            save_all()
            audit("plan_upgraded", cur_user["d"]["email"], "", f"plan={plan}")
            notify(f"Plano {plan.upper()} ativado com sucesso!")
            page.dialog.open = False
            page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Ativar plano {plan.upper()}"),
            content=ft.Column([
                ft.Text(f"Preço: R$ {plan_data['price']:.2f}/mês"),
                ft.Text("Benefícios:", weight=ft.FontWeight.BOLD),
                *[ft.Text(f"• {feat}", size=12) for feat in plan_data["features"]]
            ], tight=True, spacing=5),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False)),
                ft.ElevatedButton("Confirmar", on_click=confirm_upgrade)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    # Função para aplicar código de indicação
    def apply_referral(code):
        code = code.strip().upper()
        for u in users.values():
            if u.get("referral_code") == code and u["email"] != cur_user["d"]["email"]:
                u["referral_bonus"] = u.get("referral_bonus", 0) + 20
                cur_user["d"]["referral_bonus"] = cur_user["d"].get("referral_bonus", 0) + 20
                save_all()
                notify("Código de indicação aplicado! Você ganhou R$20 de bônus!")
                return True
        notify("Código de indicação inválido", False)
        return False

    # Função para abrir disputa
    def open_dispute(request):
        if not cur_user["d"]:
            return
        
        reason_dropdown = ft.Dropdown(
            label="Motivo da disputa",
            options=[
                ft.dropdown.Option("Profissional não compareceu"),
                ft.dropdown.Option("Serviço mal executado"),
                ft.dropdown.Option("Cobrança indevida"),
                ft.dropdown.Option("Danos ao imóvel"),
                ft.dropdown.Option("Outros")
            ],
            border_radius=12
        )
        description_field = ft.TextField(
            label="Descreva o problema",
            multiline=True,
            min_lines=3,
            border_radius=12
        )
        
        def submit_dispute(e):
            dispute = {
                "id": next_id["v"],
                "request_id": request["id"],
                "client_email": cur_user["d"]["email"],
                "provider_email": request["provider_email"],
                "reason": reason_dropdown.value,
                "description": description_field.value,
                "status": "Aberto",
                "created_at": now_str()
            }
            next_id["v"] += 1
            disputes.append(dispute)
            save_all()
            notify("Disputa registrada! Nossa equipe analisará em até 48h.")
            page.dialog.open = False
            page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Abrir disputa"),
            content=ft.Column([reason_dropdown, description_field], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False)),
                ft.ElevatedButton("Enviar", on_click=submit_dispute)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    # Função para rastrear localização
    def track_location(request_id):
        if request_id not in location_history:
            location_history[request_id] = []
        
        def update_location():
            # Simular obtenção de localização
            lat = -23.5505 + random.random()/100
            lng = -46.6333 + random.random()/100
            location_history[request_id].append({
                "time": now_str(),
                "lat": lat,
                "lng": lng
            })
            
            # Salvar a cada 5 minutos (simulado)
            if len(location_history[request_id]) % 6 == 0:
                for r in reqs:
                    if r["id"] == request_id:
                        r["location_history"] = location_history[request_id]
                        save_all()
                        break
            
            # Continuar rastreando se o serviço não foi finalizado
            for r in reqs:
                if r["id"] == request_id and r["status"] != "Finalizado":
                    threading.Timer(30, update_location).start()
                    break
        
        # Iniciar rastreamento
        threading.Timer(30, update_location).start()
        notify("Rastreamento de localização iniciado!")

    # Função para estatísticas do prestador
    def provider_stats(email):
        if not HAS_MATPLOTLIB:
            return ft.Container(
                content=ft.Text("Instale matplotlib para ver gráficos: pip install matplotlib", color=C_MUTED),
                padding=10
            )
        
        provider_reqs = [r for r in reqs if r["provider_email"] == email]
        
        # Estatísticas
        total_earned = sum(r["estimated_price"] for r in provider_reqs if r["payment_status"] == "Pago")
        reviewed_reqs = [r for r in provider_reqs if r.get("reviewed")]
        avg_rating = sum(r.get("review_score", 0) for r in reviewed_reqs) / max(len(reviewed_reqs), 1)
        completion_rate = len([r for r in provider_reqs if r["status"] == "Finalizado"]) / max(len(provider_reqs), 1) * 100
        
        # Criar gráfico de faturamento mensal
        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        earnings = []
        for i in range(1, 7):
            month = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_key = month.strftime("%Y-%m")
            month_earnings = sum(r["estimated_price"] for r in provider_reqs 
                                if r.get("created_at", "").startswith(month_key) and r["payment_status"] == "Pago")
            earnings.append(month_earnings)
        
        plt.figure(figsize=(6, 3))
        plt.bar(months, earnings, color=C_PRIMARY)
        plt.title("Faturamento Mensal")
        plt.ylabel("R$")
        plt.tight_layout()
        
        # Converter para imagem base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return ft.Column([
            ft.Row([
                ft.Container(content=ft.Text(f"💰 R$ {total_earned:.2f}", size=14), padding=10, bgcolor="#F0F0F0", border_radius=10),
                ft.Container(content=ft.Text(f"⭐ {avg_rating:.1f}", size=14), padding=10, bgcolor="#F0F0F0", border_radius=10),
                ft.Container(content=ft.Text(f"✅ {completion_rate:.0f}%", size=14), padding=10, bgcolor="#F0F0F0", border_radius=10),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Image(src_base64=img_base64, width=350, height=200),
        ], spacing=10)

    # Função para calendário visual (usando calendar já importado)
    def calendar_view(provider_email):
        today = datetime.now()
        cal = calendar.monthcalendar(today.year, today.month)
        
        slots = get_available_slots(provider_email)
        available_days = {int(s.split("-")[2]) for s in slots if s.startswith(today.strftime("%Y-%m"))}
        
        # Dias da semana
        weekdays = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        
        calendar_grid = ft.Column([
            ft.Row([ft.Text(day, size=12, weight=ft.FontWeight.BOLD, color=C_PRIMARY) for day in weekdays], 
                   alignment=ft.MainAxisAlignment.SPACE_AROUND),
            *[
                ft.Row([
                    ft.Container(
                        width=45,
                        height=45,
                        border_radius=25,
                        bgcolor=C_PRIMARY if day in available_days else "#F0F0F0",
                        alignment=ft.alignment.center,
                        content=ft.Text(str(day), 
                                       color=ft.Colors.WHITE if day in available_days else C_TEXT,
                                       weight=ft.FontWeight.BOLD if day in available_days else ft.FontWeight.NORMAL)
                    ) for day in week if day != 0
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND) for week in cal
            ]
        ], spacing=5)
        
        return ft.Container(
            content=calendar_grid,
            padding=10,
            bgcolor="#FFFFFF",
            border_radius=12,
            border=ft.border.all(1, "#E0E0E0")
        )

    # Função para avaliação com fotos
    def review_with_photos(r):
        if r.get("reviewed"):
            return None
        
        # Criar objeto para armazenar fotos da avaliação
        if not hasattr(page, "current_review"):
            page.current_review = {}
        
        page.current_review["photos"] = []
        photo_previews = ft.Row(spacing=5, wrap=True)
        
        def update_photo_preview():
            photo_previews.controls.clear()
            for i, photo in enumerate(page.current_review["photos"][-3:]):
                photo_previews.controls.append(
                    ft.Container(
                        width=60,
                        height=60,
                        border_radius=8,
                        content=ft.Image(src_base64=photo, fit=ft.BoxFit.COVER),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                    )
                )
            page.update()
        
        def add_photo(e):
            file_picker.pick_files(allow_multiple=True, allowed_extensions=["png", "jpg", "jpeg"])
            # A função pick_files_result já atualizará page.current_review["photos"]
        
        pdd = ft.Dropdown(label="Pontualidade", value="5", width=140, 
                         options=[ft.dropdown.Option(str(i)) for i in [5, 4, 3, 2, 1]])
        qdd = ft.Dropdown(label="Qualidade", value="5", width=140,
                         options=[ft.dropdown.Option(str(i)) for i in [5, 4, 3, 2, 1]])
        vdd = ft.Dropdown(label="Custo-beneficio", value="5", width=160,
                         options=[ft.dropdown.Option(str(i)) for i in [5, 4, 3, 2, 1]])
        cmt = ft.TextField(label="Comentário", multiline=True, min_lines=2, border_radius=12)
        
        def submit_review(e):
            p, q, v = int(pdd.value), int(qdd.value), int(vdd.value)
            score = round((p + q + v) / 3, 1)
            comment = cmt.value or "Serviço concluído com qualidade."
            
            r["reviewed"] = True
            r["review_score"] = score
            r["review_comment"] = comment
            r["review_punctuality"] = p
            r["review_quality"] = q
            r["review_value"] = v
            r["review_photos"] = page.current_review.get("photos", [])
            
            pr = users.get(r["provider_email"])
            if pr:
                old_r, old_s = pr.get("reviews", 0), pr.get("rating", 0)
                pr["rating"] = round(((old_s * old_r) + score) / (old_r + 1), 2)
                pr["reviews"] = old_r + 1
                push_note(pr["email"], f"Você recebeu nova avaliação: {score} estrelas com fotos!")
            
            save_all()
            push_note(r["client_email"], f"Avaliação do pedido #{r['id']} registrada.")
            notify("Avaliação enviada com sucesso!")
            page.dialog.open = False
            page.update()
        
        return ft.Column([
            ft.Text("Adicione fotos do serviço realizado:", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("➕ Adicionar fotos", icon=ft.Icons.ADD_PHOTO, on_click=add_photo),
                photo_previews
            ], wrap=True, spacing=10),
            ft.Divider(),
            ft.Row([pdd, qdd, vdd], wrap=True, spacing=8),
            cmt,
            ft.Row([
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False)),
                ft.ElevatedButton("Enviar avaliação", icon=ft.Icons.STAR, on_click=submit_review)
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=10)

    # Funções de notificação
    def notif_panel(email, limit=4):
        items = notes.get(email, [])[:limit]
        if not items: 
            return ft.Container(
                border_radius=12, 
                bgcolor="#F5FCFF", 
                padding=10, 
                content=ft.Text("Sem notificacoes por enquanto.", size=12, color=C_MUTED)
            )
        return ft.Container(
            border_radius=12, 
            bgcolor="#F5FCFF", 
            padding=10, 
            content=ft.Column([ft.Text(i, size=12, color=C_TEXT) for i in items], spacing=6)
        )

    # Views principais
    def home_view():
        refresh_providers()
        refresh_fav()
        u = cur_user["d"]
        total = len([x for x in users.values() if is_provider(x)])
        unread = unread_count(u["email"])
        
        smart_slots = next_slots_by_neighborhood(u.get("neighborhood", ""), 4)
        smart_controls = [ft.Text(f"{p['name']} - {slot}", size=12, color=C_TEXT) for slot, p in smart_slots] or [ft.Text("Sem sugestoes para seu bairro.", size=12, color=C_MUTED)]
        
        recent = ft.Row([
            ft.OutlinedButton(x, on_click=lambda _, q=x: (setattr(search, "value", q), refresh_providers(), page.update())) 
            for x in recent_searches["v"][:5]
        ], wrap=True, spacing=6) if recent_searches["v"] else ft.Text("Sem buscas recentes.", size=12, color=C_MUTED)
        
        ads = ft.Container(
            border_radius=12, 
            bgcolor="#E8F4FF", 
            padding=10, 
            content=ft.Column([
                ft.Text("Anuncios internos", weight=ft.FontWeight.BOLD), 
                ft.Text("Plano destaque: apareca no topo da busca por regiao.", size=12), 
                ft.Text("Plano PRO: selo verificado + prioridade + analytics.", size=12)
            ], spacing=4)
        )
        
        # Botão para expandir filtros avançados
        def toggle_advanced_filters(e):
            nonlocal advanced_filters_expanded
            advanced_filters_expanded = not advanced_filters_expanded
            page.update()
        
        advanced_filters = ft.Container(
            visible=advanced_filters_expanded,
            content=ft.Column([
                ft.Text("Filtros avançados", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([f_distancia], wrap=True),
                ft.Row([f_tempo_resposta], wrap=True),
                ft.Row([f_aceita_cartao, f_atende_fds, f_com_selo], wrap=True),
            ], spacing=8)
        )
        
        controls = [
            ft.Container(
                border_radius=16, 
                padding=14, 
                bgcolor="#ECFAFF", 
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CLEANING_SERVICES, color=C_PRIMARY), 
                        ft.Text("Encontre seu profissional ideal", size=16, weight=ft.FontWeight.BOLD, color=C_TEXT)
                    ], spacing=8), 
                    ft.Text("Busque por diaristas e empresas com melhores avaliacoes.", color=C_MUTED, size=12), 
                    ft.Row([
                        chip(f"{total} perfis", ft.Icons.PEOPLE), 
                        chip("Atendimento rapido", ft.Icons.FLASH_ON), 
                        chip("Ranking por regiao", ft.Icons.MAP), 
                        chip(f"Novas notificacoes: {unread}", ft.Icons.NOTIFICATIONS_ACTIVE)
                    ], spacing=8, wrap=True)
                ], spacing=8)
            ),
            ft.Row([
                btn("Meus pedidos", ft.Icons.LIST_ALT, lambda _: page.go("/pedidos")), 
                ft.OutlinedButton("Favoritos", icon=ft.Icons.STAR, on_click=lambda _: page.go("/favoritos")),
                ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
            ], spacing=8, wrap=True),
            ft.Text("Agenda inteligente", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Container(
                border_radius=12, 
                bgcolor="#F5FCFF", 
                padding=10, 
                content=ft.Column(smart_controls, spacing=6)
            ),
            ft.Text("Buscas recentes", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            recent,
            ads,
            ft.Text("Favoritos", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            fav_col,
            ft.Text("Notificacoes", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            notif_panel(u["email"], 3),
            search,
            ft.Row([f_type, f_rate], wrap=True, spacing=8),
            # CORREÇÃO: Linha duplicada removida
            ft.Row([f_price, f_neighborhood], wrap=True, spacing=8),
            ft.Row([f_day], wrap=True, spacing=8),
            ft.Row([
                ft.OutlinedButton(
                    "Filtros avançados ▼" if not advanced_filters_expanded else "Filtros avançados ▲",
                    icon=ft.Icons.TUNE,
                    on_click=toggle_advanced_filters
                )
            ]),
            advanced_filters,
            ft.Text("Perfis de servico", size=16, weight=ft.FontWeight.BOLD, color=C_TEXT),
            provider_col,
        ]
        
        if is_admin(u):
            controls.insert(2, ft.OutlinedButton("Painel admin", icon=ft.Icons.ADMIN_PANEL_SETTINGS, on_click=lambda _: page.go("/admin")))
        
        mark_notes_seen(u["email"])
        return centered_view("/inicio", panel(ft.Column(controls, spacing=12), True))

    def provider_home_view():
        u = cur_user["d"]
        if not u: 
            page.go("/login"); 
            return ft.View(route="/inicio-prestador", controls=[])
        
        rs = [r for r in reqs if r["provider_email"] == u["email"]]
        month_key = datetime.now().strftime("%Y-%m")
        month_rs = [r for r in rs if (r.get("created_at", "") or "").startswith(month_key)]
        pend, prog, done = len([r for r in rs if r["status"] in ["Solicitado", "Confirmado"]]), len([r for r in rs if r["status"] == "Em andamento"]), len([r for r in rs if r["status"] == "Finalizado"])
        gain = sum(r["estimated_price"] for r in rs if r["status"] == "Finalizado" and r["payment_status"] == "Pago")
        month_gain = sum(r["estimated_price"] for r in month_rs if r["status"] == "Finalizado" and r["payment_status"] == "Pago")
        month_done = len([r for r in month_rs if r["status"] == "Finalizado"])
        accept_rate = round((len([r for r in rs if r["status"] in ["Confirmado", "Finalizado"]]) / max(len(rs), 1)) * 100, 1)
        avg_response = u.get("avg_response_min", 15)
        monthly_rating = round(sum([r.get("review_score", 0) for r in rs if r.get("reviewed")]) / max(len([r for r in rs if r.get("reviewed")]), 1), 2) if rs else 0
        
        graph = ft.Row([ft.Container(width=14, height=min(70, max(8, int(v / 20))), bgcolor=C_PRIMARY, border_radius=4) for v in [gain % 600 + 80, done * 20 + 20, accept_rate, monthly_rating * 20]], spacing=6)
        unread = unread_count(u["email"])
        slots = get_available_slots(u["email"])
        
        # Estatísticas detalhadas
        stats_content = provider_stats(u["email"]) if u.get("plan") in ["pro", "enterprise"] else ft.Container(
            content=ft.Column([
                ft.Text("📊 Estatísticas avançadas disponíveis nos planos PRO", size=12, color=C_MUTED),
                ft.ElevatedButton("Conhecer planos", icon=ft.Icons.STAR, on_click=lambda _: show_plans_dialog())
            ], spacing=5),
            padding=10,
            bgcolor="#F5F5F5",
            border_radius=10
        )
        
        controls = [
            ft.Container(
                border_radius=16, 
                padding=14, 
                bgcolor="#ECFAFF", 
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.HOME_WORK, color=C_PRIMARY), 
                        ft.Text("Painel inicial", size=16, weight=ft.FontWeight.BOLD, color=C_TEXT)
                    ], spacing=8), 
                    ft.Text(f"Bem-vindo(a), {u['name']}.", color=C_MUTED, size=12),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme),
                        ft.Text(f"Plano: {u.get('plan', 'free').upper()}", size=12, color=C_PRIMARY)
                    ])
                ], spacing=8)
            ),
            ft.Row([
                chip(f"Ganhos totais: R$ {gain}", ft.Icons.PAID), 
                chip(f"Concluidos: {done}", ft.Icons.CHECK_CIRCLE), 
                chip(f"Aceitacao: {accept_rate}%", ft.Icons.TASK_ALT)
            ], spacing=8, wrap=True),
            ft.Row([
                chip(f"Mes atual: R$ {month_gain}", ft.Icons.QUERY_STATS), 
                chip(f"Finalizados no mes: {month_done}", ft.Icons.CALENDAR_MONTH), 
                chip(f"Resp. medio: {avg_response} min", ft.Icons.AV_TIMER), 
                chip(f"Avaliacao: {monthly_rating}", ft.Icons.STAR)
            ], spacing=8, wrap=True),
            ft.Row([
                chip(f"Pendentes: {pend}", ft.Icons.SCHEDULE), 
                chip(f"Em andamento: {prog}", ft.Icons.CLEANING_SERVICES), 
                chip(f"Novas notificacoes: {unread}", ft.Icons.NOTIFICATIONS_ACTIVE)
            ], spacing=8, wrap=True),
            ft.Text("Grafico rapido", size=14, weight=ft.FontWeight.BOLD),
            graph,
            ft.Text("Estatísticas detalhadas", size=14, weight=ft.FontWeight.BOLD),
            stats_content,
            ft.Text("Calendário de disponibilidade", size=14, weight=ft.FontWeight.BOLD),
            calendar_view(u["email"]),
            ft.Text("Disponibilidade", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Container(
                border_radius=12, 
                bgcolor="#F5FCFF", 
                padding=10, 
                content=ft.Column([ft.Text(s, size=12, color=C_TEXT) for s in slots[:6]] if slots else [ft.Text("Sem horarios livres.", size=12, color=C_MUTED)], spacing=6)
            ),
            ft.Text("Notificacoes", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            notif_panel(u["email"], 4),
            btn("Pedidos recebidos", ft.Icons.LIST_ALT, lambda _: page.go("/pedidos")),
            btn("Gerenciar planos", ft.Icons.DIAMOND, lambda _: show_plans_dialog()),
            btn("Meu perfil", ft.Icons.PERSON, lambda _: (selected_provider.__setitem__("d", u), page.go("/perfil-servico"))),
            btn("Mensagens", ft.Icons.CHAT, lambda _: page.go("/chat")),
        ]
        
        if is_admin(u):
            controls.insert(1, ft.OutlinedButton("Painel admin", icon=ft.Icons.ADMIN_PANEL_SETTINGS, on_click=lambda _: page.go("/admin")))
        
        mark_notes_seen(u["email"])
        return centered_view("/inicio-prestador", panel(ft.Column(controls, spacing=12), True))

    def show_plans_dialog():
        def select_plan(plan):
            upgrade_plan(plan)
        
        plans_content = ft.Column([
            ft.Text("Escolha o plano ideal para você", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Container(
                    width=200,
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(2, "#E0E0E0"),
                    content=ft.Column([
                        ft.Text("BÁSICO", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"R$ {subscription_plans['basic']['price']:.2f}/mês", size=14, color=C_PRIMARY),
                        ft.Divider(),
                        *[ft.Text(f"✓ {feat}", size=12) for feat in subscription_plans['basic']['features']],
                        ft.ElevatedButton("Escolher", on_click=lambda _: select_plan("basic"), width=150)
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
                ft.Container(
                    width=200,
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(2, C_PRIMARY),
                    bgcolor="#F0F8FF",
                    content=ft.Column([
                        ft.Text("PRO", size=16, weight=ft.FontWeight.BOLD, color=C_PRIMARY),
                        ft.Text(f"R$ {subscription_plans['pro']['price']:.2f}/mês", size=14, color=C_PRIMARY),
                        ft.Text("MAIS POPULAR", size=10, color=C_ACCENT),
                        ft.Divider(),
                        *[ft.Text(f"✓ {feat}", size=12) for feat in subscription_plans['pro']['features']],
                        ft.ElevatedButton("Escolher", on_click=lambda _: select_plan("pro"), width=150, bgcolor=C_PRIMARY, color=ft.Colors.WHITE)
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
                ft.Container(
                    width=200,
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(2, "#E0E0E0"),
                    content=ft.Column([
                        ft.Text("ENTERPRISE", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"R$ {subscription_plans['enterprise']['price']:.2f}/mês", size=14, color=C_PRIMARY),
                        ft.Divider(),
                        *[ft.Text(f"✓ {feat}", size=12) for feat in subscription_plans['enterprise']['features']],
                        ft.ElevatedButton("Escolher", on_click=lambda _: select_plan("enterprise"), width=150)
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ], wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Planos de assinatura"),
            content=ft.Container(content=plans_content, width=650, height=500),
            actions=[ft.TextButton("Fechar", on_click=lambda _: setattr(page.dialog, "open", False))],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    def login_view():
        return centered_view("/login", panel(ft.Column([
            ft.Text("Entrar", size=26, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            login_email, 
            login_password, 
            btn("Entrar", ft.Icons.LOGIN, do_login), 
            ft.Row([
                social_btn("Continuar com Google", do_google_login, "google"), 
                social_btn("Continuar com Facebook", do_facebook_login, "facebook")
            ], wrap=True, spacing=8), 
            ft.Text("Contas demo: senha 12345678", size=11, color=C_MUTED), 
            ft.Row([
                ft.Text("Nao tem conta?", color=C_MUTED), 
                ft.TextButton("Criar conta", on_click=lambda _: page.go("/cadastro"))
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
        ], spacing=14)))

    def register_view():
        return centered_view("/cadastro", panel(ft.Column([
            ft.Text("Criar conta", size=22, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            reg_name, 
            reg_email, 
            reg_password, 
            reg_type, 
            reg_neighborhood, 
            reg_bio,
            reg_referral,
            btn("Finalizar cadastro", ft.Icons.PERSON_ADD, do_register), 
            ft.Row([
                social_btn("Continuar com Google", do_google_login, "google"), 
                social_btn("Continuar com Facebook", do_facebook_login, "facebook")
            ], wrap=True, spacing=8), 
            ft.TextButton("Ja tenho conta", on_click=lambda _: page.go("/login"))
        ], spacing=12)))

    def profile_view(p, route="/perfil-servico"):
        actions = [
            btn("Abrir chat", ft.Icons.CHAT, lambda _: page.go("/chat")), 
            ft.OutlinedButton("Voltar", icon=ft.Icons.HOME, on_click=lambda _: page.go("/inicio-prestador" if cur_user["d"] and is_provider(cur_user["d"]) else "/inicio"))
        ]
        
        if cur_user["d"] and is_client(cur_user["d"]) and p["email"] != cur_user["d"]["email"]:
            actions.insert(0, btn("Solicitar servico", ft.Icons.ADD_TASK, lambda _: page.go("/solicitar")))
            actions.append(ft.OutlinedButton("Favoritar" if p["email"] not in fav_set(cur_user["d"]["email"]) else "Desfavoritar", icon=ft.Icons.STAR, on_click=lambda _: toggle_fav(p)))
        
        if cur_user["d"] and cur_user["d"]["email"] == p["email"] and is_provider(p):
            actions.append(ft.OutlinedButton("Editar perfil", icon=ft.Icons.EDIT, on_click=lambda _: notify("Edição de perfil em breve!")))
            actions.append(ft.OutlinedButton("Ver estatísticas", icon=ft.Icons.ANALYTICS, on_click=lambda _: show_stats_dialog(p["email"])))
        
        reviews = [r for r in reqs if r["provider_email"] == p["email"] and r.get("reviewed")]
        rev_controls = []
        for r in reviews[-4:]:
            photos = r.get("review_photos", [])
            photo_row = ft.Row([
                ft.Container(
                    width=50,
                    height=50,
                    border_radius=8,
                    content=ft.Image(src_base64=photo, fit=ft.BoxFit.COVER),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                ) for photo in photos[:3]
            ], spacing=5) if photos else ft.Text("")
            
            rev_controls.append(ft.Column([
                ft.Text(f"{r['client_name']} - {r.get('review_score', 5)} ⭐", weight=ft.FontWeight.BOLD),
                ft.Text(f"{r.get('review_comment', '')}", size=12),
                ft.Text(f"P:{r.get('review_punctuality', '-')} | Q:{r.get('review_quality', '-')} | V:{r.get('review_value', '-')}", size=11, color=C_MUTED),
                photo_row
            ], spacing=2))
        
        rev_controls = rev_controls or [ft.Text("Sem avaliacoes recentes.", size=12, color=C_MUTED)]
        
        # Verificar se usuário pode ver estatísticas
        can_see_stats = (cur_user["d"] and (
            cur_user["d"]["email"] == p["email"] or 
            is_admin(cur_user["d"]) or
            p.get("plan") in ["pro", "enterprise"]
        ))
        
        stats_section = ft.Container(
            visible=can_see_stats,
            content=ft.Column([
                ft.Text("Estatísticas do prestador", size=14, weight=ft.FontWeight.BOLD),
                provider_stats(p["email"])
            ], spacing=5)
        ) if can_see_stats else ft.Text("")
        
        return centered_view(route, panel(ft.Column([
            ft.Container(
                height=140, 
                border_radius=16, 
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
                content=ft.Image(src=p.get("cover_url"), fit=ft.BoxFit.COVER)
            ), 
            ft.Row([
                ft.CircleAvatar(
                    foreground_image_src=p.get("avatar_url"), 
                    content=ft.Text(p["name"][:1].upper()), 
                    bgcolor="#D8E9FF"
                ), 
                ft.Column([
                    ft.Text(p["name"], size=20, weight=ft.FontWeight.BOLD, color=C_TEXT), 
                    ft.Text(p["profile_type"], color=C_MUTED), 
                    ft.Text(f"Regioes atendidas: {p.get('areas', 'Nao informado')}", size=12, color=C_MUTED)
                ], spacing=2, expand=True), 
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=10, vertical=6), 
                    border_radius=999, 
                    bgcolor="#ECF9FF", 
                    content=ft.Text(f"{p.get('rating', 0)} estrelas", size=12, color=C_PRIMARY)
                )
            ], spacing=12), 
            ft.Text(p["bio"], size=13, color="#354A5F"), 
            ft.Row([
                chip(f"Preco base R$ {p.get('base_price', 120)}", ft.Icons.PAID), 
                chip(f"Tempo medio {p.get('avg_duration_min', 180)} min", ft.Icons.TIMER), 
                chip(f"Bairro: {p.get('neighborhood', 'Nao informado')}", ft.Icons.PLACE)
            ], spacing=8, wrap=True), 
            ft.Row([
                ft.Container(
                    width=110, 
                    height=90, 
                    border_radius=14, 
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
                    content=ft.Image(src=x, fit=ft.BoxFit.COVER)
                ) for x in p.get("work_photos", [])[:6]
            ], wrap=True, spacing=8),
            stats_section,
            ft.Container(
                border_radius=12, 
                bgcolor="#F5FCFF", 
                padding=12, 
                content=ft.Column(rev_controls, spacing=8)
            ), 
            ft.Row(actions, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True)
        ], spacing=12)))

    def show_stats_dialog(email):
        stats_content = provider_stats(email)
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Estatísticas detalhadas"),
            content=ft.Container(content=stats_content, width=400, height=400),
            actions=[ft.TextButton("Fechar", on_click=lambda _: setattr(page.dialog, "open", False))],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    def rebuild_slots(provider_email):
        slots = get_available_slots(provider_email)
        dates = sorted(list({s.split(" ")[0] for s in slots}))
        req_day.options = [ft.dropdown.Option(d) for d in dates]
        if not req_day.value and dates: 
            req_day.value = dates[0]
        if req_day.value not in dates: 
            req_day.value = dates[0] if dates else None
        sday = [s for s in slots if req_day.value and s.startswith(req_day.value)]
        if req_slot["v"] not in sday: 
            req_slot["v"] = sday[0] if sday else None
        req_slot_text.value = f"Horario selecionado: {req_slot['v']}" if req_slot["v"] else "Horario selecionado: nenhum"
        req_slots.controls.clear()
        if not sday: 
            req_slots.controls.append(ft.Text("Sem horarios livres para a data selecionada.", size=12, color=C_MUTED))
            return
        for s in sday:
            sel = s == req_slot["v"]
            req_slots.controls.append(ft.Container(
                col={"sm": 6, "md": 4}, 
                content=ft.ElevatedButton(
                    s.split(" ")[1], 
                    icon=ft.Icons.EVENT_AVAILABLE, 
                    on_click=lambda _, x=s: (
                        req_slot.__setitem__("v", x), 
                        rebuild_slots(provider_email), 
                        update_est(), 
                        page.update()
                    ), 
                    style=ft.ButtonStyle(
                        bgcolor="#0E8B72" if sel else "#FFFFFF", 
                        color=ft.Colors.WHITE if sel else C_TEXT, 
                        shape=ft.RoundedRectangleBorder(radius=12), 
                        side=ft.BorderSide(1, "#D5E3F2")
                    )
                )
            ))

    req_day.on_change = lambda _: rebuild_slots(selected_provider["d"]["email"] if selected_provider["d"] else "")

    def prep_request_form(p):
        srv = [s for s in p.get("services", []) if s in services] or ["Limpeza basica"]
        req_service.options, req_service.value = [ft.dropdown.Option(s) for s in srv], srv[0]
        req_addr.value, req_size.value, req_pay.value = "", "Pequeno", "PIX"
        req_coupon.value = ""
        req_fridge.value, req_windows.value, req_notes.value, req_day.value = False, False, "", None
        req_slot["v"] = None
        rebuild_slots(p["email"])
        update_est()

    def send_request(_):
        c, p = cur_user["d"], selected_provider["d"]
        if not c or not p or not is_client(c): 
            notify("Sessao invalida.", False); 
            return
        if not req_slot["v"]: 
            notify("Escolha um horario disponivel.", False); 
            return
        if not valid_address(req_addr.value): 
            notify("Endereco invalido. Inclua rua, numero e complemento.", False); 
            return
        if req_pay.value not in ["PIX", "Cartao"]: 
            notify("Forma de pagamento invalida.", False); 
            return
        if not is_valid_coupon(req_coupon.value): 
            notify("Cupom invalido.", False); 
            return
        
        same_slot = [r for r in reqs if r["provider_email"] == p["email"] and r["date_slot"] == req_slot["v"] and r["status"] != "Cancelado"]
        if same_slot: 
            notify("Este horario acabou de ser ocupado. Escolha outro.", False); 
            rebuild_slots(p["email"]); 
            return
        
        price, h = calc_est(p, req_service.value or "Limpeza basica", req_size.value or "Pequeno", req_fridge.value, req_windows.value)
        discount_rate = coupons.get((req_coupon.value or "").strip().upper(), 0)
        discounted = int(price * (1 - discount_rate))
        total = int(discounted * (1 + float(rate_config.get("platform_fee", 0.08))))
        auto_status = "Confirmado" if p.get("response_rate", 0) >= 96 else "Solicitado"
        rid = next_id["v"]; next_id["v"] += 1
        
        reqs.append({
            "id": rid, 
            "client_email": c["email"], 
            "client_name": c["name"], 
            "provider_email": p["email"], 
            "provider_name": p["name"], 
            "service_type": req_service.value, 
            "date_slot": req_slot["v"], 
            "address": req_addr.value.strip(), 
            "property_size": req_size.value, 
            "extras": [n for n, b in [("Geladeira", req_fridge.value), ("Janelas", req_windows.value)] if b], 
            "notes": (req_notes.value or "").strip(), 
            "payment_method": req_pay.value, 
            "payment_status": "Pendente", 
            "status": auto_status, 
            "estimated_price": total, 
            "base_price": price, 
            "coupon": (req_coupon.value or "").strip().upper(), 
            "discount_rate": discount_rate, 
            "platform_fee": int(total - discounted), 
            "cancel_fee": 0, 
            "provider_status_rt": "A caminho", 
            "shared_location": False, 
            "risk_flags": 0, 
            "estimated_hours": h, 
            "created_at": now_str(), 
            "paid_at": "", 
            "receipt": "", 
            "reviewed": False, 
            "review_score": 0, 
            "review_comment": "", 
            "review_punctuality": 0, 
            "review_quality": 0, 
            "review_value": 0
        })
        
        save_all()
        push_note(c["email"], f"Pedido #{rid} enviado para {p['name']}.")
        push_note(p["email"], f"Novo pedido #{rid} recebido de {c['name']}.")
        audit("request_created", c["email"], p["email"], f"id={rid}")
        notify("Pedido enviado com sucesso.")
        page.go("/pedidos")

    def request_view():
        p = selected_provider["d"]
        if not p: 
            page.go("/inicio"); 
            return ft.View(route="/solicitar", controls=[])
        
        prep_request_form(p)
        has_slots = bool(get_available_slots(p["email"]))
        alt_slots = next_slots_by_neighborhood(p.get("neighborhood", ""), 4)
        alt_controls = [ft.Text(f"{prov['name']}: {slot}", size=12, color=C_TEXT) for slot, prov in alt_slots if prov["email"] != p["email"]] or [ft.Text("Sem alternativas no bairro no momento.", size=12, color=C_MUTED)]
        
        return centered_view("/solicitar", panel(ft.Column([
            ft.Text(f"Solicitar servico com {p['name']}", size=19, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            req_service, 
            ft.Row([
                req_day, 
                ft.OutlinedButton("Calendario", icon=ft.Icons.CALENDAR_MONTH, on_click=open_calendar)
            ], wrap=True, spacing=8), 
            ft.Text("Selecione um horario:", size=13, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            req_slots, 
            req_slot_text, 
            ft.Container(
                border_radius=12, 
                bgcolor="#F5FCFF", 
                padding=10, 
                content=ft.Column([
                    ft.Text("Agenda inteligente no bairro", size=13, weight=ft.FontWeight.BOLD, color=C_TEXT), 
                    *alt_controls
                ], spacing=6)
            ), 
            req_addr, 
            req_size, 
            req_pay, 
            req_coupon, 
            req_fridge, 
            req_windows, 
            req_notes, 
            ft.Row([
                ft.OutlinedButton("IA sugerir servico", icon=ft.Icons.AUTO_AWESOME, on_click=lambda _: (
                    setattr(req_service, "value", suggest_service_ai(req_notes.value)), 
                    update_est(), 
                    page.update()
                )), 
                ft.OutlinedButton("Simular antes/depois", icon=ft.Icons.AUTO_FIX_HIGH, on_click=lambda _: notify("Simulacao visual ativada (modo MVP)."))
            ], wrap=True, spacing=8), 
            req_est, 
            ft.Row([
                btn("Enviar pedido", ft.Icons.SEND, send_request), 
                ft.OutlinedButton("Voltar", icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/perfil-servico"))
            ], wrap=True, spacing=8), 
            ft.Text("Nao ha horarios disponiveis para esse prestador agora." if not has_slots else "Escolha um horario livre para concluir o pedido.", size=12, color=C_MUTED)
        ], spacing=11)))

    def timeline(status):
        idx = status_flow.index(status) if status in status_flow else 0
        return ft.Row([
            ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=4), 
                border_radius=999, 
                bgcolor=status_color(s) if i <= idx else "#E5ECF5", 
                content=ft.Text(s, size=10, color=ft.Colors.WHITE if i <= idx else C_MUTED)
            ) for i, s in enumerate(status_flow)
        ], spacing=6, wrap=True)

    def pay_req(r):
        if r["payment_status"] == "Pago": 
            notify("Este pedido ja foi pago.", False); 
            return
        r["payment_status"], r["paid_at"], r["receipt"] = "Pago", now_str(), f"RC-{r['id']}-{datetime.now().strftime('%Y%m%d%H%M')}"
        save_all()
        push_note(r["provider_email"], f"Pedido #{r['id']} foi pago.")
        push_note(r["client_email"], f"Pagamento do pedido #{r['id']} aprovado.")
        audit("payment_done", r["client_email"], r["provider_email"], f"id={r['id']}")
        notify("Pagamento concluido. Recibo gerado.")
        page.update()

    def payment_dialog(r):
        def close(_): 
            page.dialog.open = False
            page.update()
        
        def confirm(_): 
            page.dialog.open = False
            pay_req(r)
            page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Resumo do pedido #{r['id']}"), 
            content=ft.Column([
                ft.Text(f"Servico: {r['service_type']}", size=12), 
                ft.Text(f"Data: {r['date_slot']}", size=12), 
                ft.Text(f"Endereco: {r['address']}", size=12), 
                ft.Text(f"Extras: {', '.join(r['extras']) if r['extras'] else 'Nenhum'}", size=12), 
                ft.Text(f"Forma de pagamento: {r['payment_method']}", size=12), 
                ft.Text(f"Total: R$ {r['estimated_price']}", size=14, weight=ft.FontWeight.BOLD, color=C_PRIMARY)
            ], tight=True, spacing=6), 
            actions=[
                ft.TextButton("Cancelar", on_click=close), 
                btn("Confirmar pagamento", ft.Icons.PAYMENTS, confirm)
            ], 
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    def receipt_dialog(r):
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Recibo #{r.get('receipt', 'N/A')}"), 
            content=ft.Column([
                ft.Text(f"Pedido: #{r['id']}", size=12), 
                ft.Text(f"Cliente: {r['client_name']}", size=12), 
                ft.Text(f"Prestador: {r['provider_name']}", size=12), 
                ft.Text(f"Valor: R$ {r['estimated_price']}", size=12), 
                ft.Text(f"Pago em: {r.get('paid_at', '-')}", size=12)
            ], tight=True, spacing=6), 
            actions=[ft.TextButton("Fechar", on_click=lambda _: (setattr(page.dialog, "open", False), page.update()))]
        )
        page.dialog.open = True
        page.update()

    def open_chat_req(r):
        selected_chat_req["d"], selected_provider["d"] = r, users.get(r["provider_email"])
        page.go("/chat")

    def request_card(r):
        u, prov = cur_user["d"], bool(cur_user["d"] and is_provider(cur_user["d"]))
        actions = [ft.OutlinedButton("Abrir chat", icon=ft.Icons.CHAT, on_click=lambda _, x=r: open_chat_req(x))]
        
        if u and is_client(u) and r["status"] not in ["Finalizado", "Cancelado"]:
            actions.append(ft.OutlinedButton("Cancelar", icon=ft.Icons.CANCEL, on_click=lambda _, x=r: (
                x.__setitem__("status", "Cancelado"), 
                x.__setitem__("cancel_fee", int(x.get("estimated_price", 0) * float(rate_config.get("cancel_fee", 0.2)))), 
                save_all(), 
                push_note(x["provider_email"], f"Pedido #{x['id']} foi cancelado pelo cliente."), 
                audit("request_cancelled", x["client_email"], x["provider_email"], f"id={x['id']}"), 
                notify("Pedido cancelado conforme politica."), 
                page.update()
            )))
        
        if prov and r["status"] != "Finalizado":
            actions.insert(0, btn("Avancar status", ft.Icons.NAVIGATE_NEXT, lambda _, x=r: (
                x.__setitem__("status", status_flow[min(status_flow.index(x["status"]) + 1, len(status_flow) - 1)]), 
                save_all(), 
                push_note(x["client_email"], f"Pedido #{x['id']} atualizado para {x['status']}."), 
                page.update()
            )))
            actions.append(ft.OutlinedButton("Status RT", icon=ft.Icons.LOCATION_ON, on_click=lambda _, x=r: (
                x.__setitem__("provider_status_rt", "Chegou" if x.get("provider_status_rt") == "A caminho" else "A caminho"), 
                save_all(), 
                push_note(x["client_email"], f"Pedido #{x['id']}: prestador agora esta '{x['provider_status_rt']}'."), 
                page.update()
            )))
            actions.append(ft.OutlinedButton("Compartilhar local", icon=ft.Icons.SHARE_LOCATION, on_click=lambda _, x=r: (
                x.__setitem__("shared_location", True), 
                save_all(), 
                push_note(x["client_email"], f"Pedido #{x['id']}: localizacao compartilhada."), 
                notify("Localizacao compartilhada."), 
                page.update(),
                track_location(x["id"])
            )))
        
        if prov and r["status"] == "Finalizado" and not r.get("client_reviewed"):
            actions.append(ft.OutlinedButton("Avaliar cliente", icon=ft.Icons.THUMB_UP, on_click=lambda _, x=r: (
                x.__setitem__("client_reviewed", True), 
                x.__setitem__("client_score", 5), 
                x.__setitem__("client_comment", "Cliente pontual e colaborativo."), 
                save_all(), 
                notify("Avaliacao do cliente registrada."), 
                page.update()
            )))
        
        if u and is_client(u):
            if r["status"] in ["Confirmado", "Em andamento", "Finalizado"] and r["payment_status"] != "Pago": 
                actions.append(btn("Resumo e pagar", ft.Icons.RECEIPT_LONG, lambda _, x=r: payment_dialog(x)))
            if r["payment_status"] == "Pago" and r.get("receipt"): 
                actions.append(ft.OutlinedButton("Ver recibo", icon=ft.Icons.DESCRIPTION, on_click=lambda _, x=r: receipt_dialog(x)))
            
            actions.append(ft.OutlinedButton("Denunciar", icon=ft.Icons.REPORT, on_click=lambda _, x=r: (
                x.__setitem__("risk_flags", int(x.get("risk_flags", 0)) + 1), 
                users.get(x["provider_email"], {}).__setitem__("blocked", True) if int(x.get("risk_flags", 0)) + 1 >= 3 else None, 
                save_all(), 
                audit("risk_reported", x["client_email"], x["provider_email"], f"id={x['id']} flags={x['risk_flags']}"), 
                notify("Denuncia registrada."), 
                page.update()
            )))
            
            actions.append(ft.OutlinedButton("Abrir disputa", icon=ft.Icons.GAVEL, on_click=lambda _, x=r: open_dispute(x)))
            
            if r["status"] == "Finalizado" and not r.get("reviewed"):
                review_btn = ft.OutlinedButton(
                    "Avaliar com fotos", 
                    icon=ft.Icons.STAR, 
                    on_click=lambda _, x=r: show_review_dialog(x)
                )
                actions.append(review_btn)
        
        reliability = users.get(r["client_email"], {}).get("reliability", "-")
        
        return ft.Container(
            padding=12, 
            border_radius=14, 
            bgcolor="#FFFFFF", 
            border=ft.border.all(1, "#DCE8F5"), 
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT), 
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Pedido #{r['id']}", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT), 
                    ft.Container(
                        border_radius=999, 
                        bgcolor="#EEF5FF", 
                        padding=ft.padding.symmetric(horizontal=10, vertical=4), 
                        content=ft.Text(r["status"], color=status_color(r["status"]), size=11)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                timeline(r["status"]), 
                ft.Text(f"Cliente: {r['client_name']} | Prestador: {r['provider_name']}", size=12, color=C_MUTED), 
                ft.Text(f"Confiabilidade do cliente: {reliability}", size=11, color=C_MUTED), 
                ft.Text(f"Servico: {r['service_type']} | Data: {r['date_slot']} ({day_name(r['date_slot'])})", size=12), 
                ft.Text(f"Endereco: {r['address']} ({r['property_size']})", size=12), 
                ft.Text(f"Extras: {', '.join(r['extras']) if r['extras'] else 'Nenhum'}", size=12), 
                ft.Text(f"Pagamento: {r['payment_method']} - {r['payment_status']}", size=12), 
                ft.Text(f"Orcamento: R$ {r['estimated_price']} ({r['estimated_hours']}h)", size=12, color=C_PRIMARY), 
                ft.Text(f"Cupom: {r.get('coupon', '-')} | Taxa plataforma: R$ {r.get('platform_fee', 0)} | Taxa cancel.: R$ {r.get('cancel_fee', 0)}", size=11, color=C_MUTED), 
                ft.Text(f"Status RT: {r.get('provider_status_rt', '-')} | Local compartilhada: {'Sim' if r.get('shared_location') else 'Nao'}", size=11, color=C_MUTED), 
                ft.Text(f"Obs: {r['notes'] if r['notes'] else 'Sem observacoes.'}", size=12, color=C_MUTED), 
                ft.Text(f"Criado em: {r.get('created_at', '-')}", size=11, color=C_MUTED), 
                ft.Text(f"Recibo: {r.get('receipt')}" if r.get("receipt") else "", size=11, color="#166534"), 
                ft.Row(actions, wrap=True, spacing=8)
            ], spacing=8)
        )

    def show_review_dialog(r):
        review_content = review_with_photos(r)
        if not review_content:
            notify("Este pedido já foi avaliado.", False)
            return
        
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Avaliar pedido #{r['id']}"),
            content=ft.Container(content=review_content, width=400),
            actions=[ft.TextButton("Fechar", on_click=lambda _: setattr(page.dialog, "open", False))],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()

    def orders_view():
        u = cur_user["d"]
        if not u: 
            page.go("/login"); 
            return ft.View(route="/pedidos", controls=[])
        
        vis = [r for r in reqs if r["provider_email"] == u["email"]] if is_provider(u) else [r for r in reqs if r["client_email"] == u["email"]]
        hist = [r for r in vis if r["status"] == "Finalizado"]
        title = "Pedidos recebidos" if is_provider(u) else "Meus pedidos"
        
        return centered_view("/pedidos", panel(ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            ft.Row([
                chip(f"Total: {len(vis)}", ft.Icons.LIST_ALT), 
                chip(f"Finalizados: {len(hist)}", ft.Icons.CHECK_CIRCLE)
            ], spacing=8, wrap=True), 
            ft.Column([request_card(r) for r in vis] if vis else [ft.Text("Nenhum pedido encontrado.", size=12, color=C_MUTED)], spacing=10), 
            ft.Divider(), 
            ft.Text("Historico", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            ft.Column([
                ft.Text(f"#{r['id']} - {r['service_type']} com {r['provider_name'] if is_client(u) else r['client_name']}", size=12, color=C_TEXT) 
                for r in hist
            ] if hist else [ft.Text("Sem servicos finalizados ainda.", size=12, color=C_MUTED)], spacing=6), 
            ft.OutlinedButton("Voltar", icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/inicio-prestador" if is_provider(u) else "/inicio"))
        ], spacing=12)))

    def favorites_view():
        u = cur_user["d"]
        if not u or not is_client(u): 
            page.go("/inicio"); 
            return ft.View(route="/favoritos", controls=[])
        
        ps = [users[e] for e in fav_set(u["email"]) if e in users and is_provider(users[e])]
        return centered_view("/favoritos", panel(ft.Column([
            ft.Text("Prestadores favoritos", size=20, weight=ft.FontWeight.BOLD, color=C_TEXT), 
            ft.Column([provider_card(p) for p in ps] if ps else [ft.Text("Voce ainda nao possui favoritos.", size=12, color=C_MUTED)], spacing=10), 
            ft.OutlinedButton("Voltar", icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/inicio"))
        ], spacing=12)))

    def chat_key():
        if selected_chat_req["d"]: 
            return f"pedido:{selected_chat_req['d']['id']}"
        p = selected_provider["d"]
        return f"perfil:{p['email']}" if p and p.get("email") else "geral"

    def active_msgs():
        k = chat_key()
        if k not in chats:
            who = selected_provider["d"]["name"] if selected_provider["d"] else "Atendente"
            chats[k] = [{"author": who, "text": "Ola! Como posso ajudar?", "time": now_str()}]
            save_all()
        return chats[k]

    def render_chat():
        chat_list.controls.clear()
        for m in active_msgs():
            mine = cur_user["d"] and m["author"] == cur_user["d"]["name"]
            has_image = "image" in m
            
            content_col = ft.Column([
                ft.Text(m["author"], size=11, weight=ft.FontWeight.BOLD, color="#37506A"),
                ft.Text(m["text"], size=13)
            ], spacing=4)
            
            if has_image:
                content_col.controls.append(
                    ft.Container(
                        width=200,
                        height=150,
                        border_radius=8,
                        content=ft.Image(src_base64=m["image"], fit=ft.BoxFit.COVER),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                    )
                )
            
            content_col.controls.append(ft.Text(m.get("time", ""), size=10, color=C_MUTED))
            
            chat_list.controls.append(ft.Row([
                ft.Container(
                    bgcolor="#D9F3FF" if mine else "#F8FBFF", 
                    border_radius=12, 
                    border=ft.border.all(1, "#DBE7F3"), 
                    padding=10, 
                    content=content_col
                )
            ], alignment=ft.MainAxisAlignment.END if mine else ft.MainAxisAlignment.START))

    chat_input.on_change = lambda e: (
        typing_text.__setattr__("value", "Voce esta digitando..." if (e.control.value or "").strip() else ""), 
        page.update() if page.route == "/chat" else None
    )

    def send_chat(_):
        if not cur_user["d"]: 
            notify("Faca login para enviar mensagens.", False)
            page.go("/login")
            return
        
        t = (chat_input.value or "").strip()
        if not t: 
            return
        
        if len(t) > 280:
            notify("Mensagem muito longa (max 280 caracteres).", False)
            return
        
        lower = t.lower()
        if any(w in lower for w in spam_words):
            audit("chat_blocked_spam", cur_user["d"]["email"], "", t[:80])
            notify("Mensagem bloqueada pelo filtro anti-spam.", False)
            return
        
        active_msgs().append({
            "author": cur_user["d"]["name"], 
            "text": t, 
            "time": now_str()
        })
        
        if lower.startswith("ia:") or "sugere" in lower:
            suggestion = "Sugestao IA: para gordura intensa, escolha Limpeza pesada; para manutencao semanal, Limpeza basica."
            active_msgs().append({
                "author": "Assistente Rapidfix", 
                "text": suggestion, 
                "time": now_str()
            })
        
        target_email = ""
        if selected_chat_req["d"]:
            r = selected_chat_req["d"]
            target_email = r["provider_email"] if cur_user["d"]["email"] == r["client_email"] else r["client_email"]
        elif selected_provider["d"] and selected_provider["d"]["email"] != cur_user["d"]["email"]:
            target_email = selected_provider["d"]["email"]
        
        if target_email:
            push_note(target_email, f"Nova mensagem de {cur_user['d']['name']}.")
        
        audit("chat_message", cur_user["d"]["email"], target_email, t[:80])
        chat_input.value, typing_text.value = "", ""
        save_all()
        render_chat()
        page.update()

    def chat_view():
        chat_title.value = f"Chat do pedido #{selected_chat_req['d']['id']}" if selected_chat_req["d"] else (f"Chat com {selected_provider['d']['name']}" if selected_provider["d"] else "Chat interno")
        render_chat()
        
        return centered_view("/chat", panel(ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: (
                    selected_chat_req.__setitem__("d", None), 
                    page.go("/perfil-servico" if selected_provider["d"] else ("/inicio-prestador" if cur_user["d"] and is_provider(cur_user["d"]) else "/inicio"))
                )), 
                chat_title,
                ft.IconButton(ft.Icons.ATTACH_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True))
            ]), 
            ft.Container(
                padding=10, 
                border_radius=12, 
                bgcolor="#F1FBFF", 
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=C_PRIMARY), 
                    ft.Text("Conversa segura para combinar horarios e detalhes do servico.", size=12, color=C_MUTED)
                ], spacing=8)
            ), 
            ft.Row([
                ft.OutlinedButton("Emergencia", icon=ft.Icons.SOS, on_click=lambda _: notify("Suporte acionado. Em breve um atendente entra em contato.", False)), 
                ft.OutlinedButton("Status GPS", icon=ft.Icons.MY_LOCATION, on_click=lambda _: notify("GPS do prestador atualizado.", True)),
                ft.OutlinedButton("Ver mapa", icon=ft.Icons.MAP, on_click=lambda _: show_map("Endereço do serviço"))
            ], wrap=True, spacing=8), 
            ft.Text("Historico por pedido habilitado.", color="#4C6174"), 
            ft.Divider(), 
            chat_list, 
            typing_text, 
            ft.Row([
                chat_input, 
                ft.FloatingActionButton(icon=ft.Icons.SEND, mini=True, bgcolor=C_PRIMARY, on_click=send_chat)
            ])
        ], spacing=10, expand=True), True))

    def admin_view():
        u = cur_user["d"]
        if not u: 
            page.go("/login"); 
            return ft.View(route="/admin", controls=[])
        if not is_admin(u): 
            page.go("/inicio-prestador" if is_provider(u) else "/inicio"); 
            return ft.View(route="/admin", controls=[])

        pending = [x for x in users.values() if is_provider(x) and (not x.get("verified") or not x.get("identity_ok") or not x.get("residence_ok"))]
        blocked_users = [x for x in users.values() if x.get("blocked")]
        manageable_users = [x for x in users.values() if x["email"] != u["email"]]
        flagged = [r for r in reqs if int(r.get("risk_flags", 0)) > 0]
        active_disputes = [d for d in disputes if d.get("status") == "Aberto"]
        
        coupon_code = ft.TextField(label="Cupom", value="NOVO5", width=140, border_radius=12)
        coupon_value = ft.TextField(label="Desconto (%)", value="5", width=140, border_radius=12)
        fee_platform = ft.TextField(label="Taxa plataforma (%)", value=str(round(float(rate_config.get("platform_fee", 0.08)) * 100, 2)), width=160, border_radius=12)
        fee_cancel = ft.TextField(label="Taxa cancelamento (%)", value=str(round(float(rate_config.get("cancel_fee", 0.2)) * 100, 2)), width=170, border_radius=12)
        
        for c in [coupon_code, coupon_value, fee_platform, fee_cancel]:
            style(c)

        def approve_provider(email):
            p = users.get(email)
            if not p:
                return
            p["verified"] = True
            p["identity_ok"] = True
            p["residence_ok"] = True
            save_all()
            push_note(email, "Seu cadastro foi aprovado pelo admin.")
            audit("admin_approved_provider", u["email"], email, "verified")
            page.go("/admin")

        def toggle_block(email):
            t = users.get(email)
            if not t:
                return
            t["blocked"] = not bool(t.get("blocked"))
            save_all()
            push_note(email, "Sua conta foi desbloqueada pelo admin." if not t["blocked"] else "Sua conta foi bloqueada pelo admin.")
            audit("admin_toggle_block", u["email"], email, f"blocked={t['blocked']}")
            page.go("/admin")

        def clear_flag(rid):
            for r in reqs:
                if r["id"] == rid:
                    r["risk_flags"] = 0
                    save_all()
                    audit("admin_clear_flag", u["email"], str(rid), "ok")
                    break
            page.go("/admin")

        def block_provider_from_flag(r):
            p = users.get(r["provider_email"])
            if p:
                p["blocked"] = True
                save_all()
                push_note(r["provider_email"], "Conta bloqueada apos revisao de denuncia.")
                audit("admin_block_from_flag", u["email"], r["provider_email"], f"pedido={r['id']}")
            page.go("/admin")

        def resolve_dispute(dispute_id, resolution):
            for d in disputes:
                if d["id"] == dispute_id:
                    d["status"] = "Resolvido"
                    d["resolution"] = resolution
                    d["resolved_at"] = now_str()
                    d["resolved_by"] = u["email"]
                    save_all()
                    push_note(d["client_email"], f"Sua disputa #{dispute_id} foi resolvida.")
                    push_note(d["provider_email"], f"Disputa #{dispute_id} foi resolvida.")
                    break
            page.go("/admin")

        def save_admin_config(_):
            try:
                p_fee = max(0.0, min(float((fee_platform.value or "0").replace(",", ".")) / 100.0, 0.4))
                c_fee = max(0.0, min(float((fee_cancel.value or "0").replace(",", ".")) / 100.0, 0.9))
                rate_config["platform_fee"] = p_fee
                rate_config["cancel_fee"] = c_fee
                cpn = (coupon_code.value or "").strip().upper()
                disc = max(0.0, min(float((coupon_value.value or "0").replace(",", ".")) / 100.0, 0.9))
                if cpn:
                    coupons[cpn] = disc
                save_all()
                audit("admin_config_updated", u["email"], "system", f"coupon={cpn} platform={p_fee} cancel={c_fee}")
                notify("Configuracoes salvas com sucesso.")
                page.go("/admin")
            except Exception:
                notify("Valores invalidos para taxas/cupom.", False)

        pending_controls = [ft.Container(
            border_radius=10, 
            bgcolor="#FFFFFF", 
            padding=10, 
            border=ft.border.all(1, "#E1EAF5"), 
            content=ft.Row([
                ft.Text(f"{p['name']} ({p['email']})", size=12, expand=True), 
                ft.OutlinedButton("Aprovar", icon=ft.Icons.CHECK, on_click=lambda _, e=p["email"]: approve_provider(e))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ) for p in pending] or [ft.Text("Sem aprovacoes pendentes.", size=12, color=C_MUTED)]
        
        account_controls = [ft.Container(
            border_radius=10, 
            bgcolor="#FFFFFF", 
            padding=10, 
            border=ft.border.all(1, "#E1EAF5"), 
            content=ft.Row([
                ft.Text(f"{x['name']} ({x['email']})", size=12, expand=True), 
                ft.OutlinedButton(
                    "Desbloquear" if x.get("blocked") else "Bloquear", 
                    icon=ft.Icons.LOCK_OPEN if x.get("blocked") else ft.Icons.BLOCK, 
                    on_click=lambda _, e=x["email"]: toggle_block(e)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ) for x in manageable_users]
        
        blocked_controls = [ft.Container(
            border_radius=10, 
            bgcolor="#FFFFFF", 
            padding=10, 
            border=ft.border.all(1, "#E1EAF5"), 
            content=ft.Row([
                ft.Text(f"{x['name']} ({x['email']})", size=12, expand=True), 
                ft.OutlinedButton("Desbloquear", icon=ft.Icons.LOCK_OPEN, on_click=lambda _, e=x["email"]: toggle_block(e))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ) for x in blocked_users] or [ft.Text("Nenhuma conta bloqueada.", size=12, color=C_MUTED)]
        
        flag_controls = [ft.Container(
            border_radius=10, 
            bgcolor="#FFFFFF", 
            padding=10, 
            border=ft.border.all(1, "#E1EAF5"), 
            content=ft.Column([
                ft.Text(f"Pedido #{r['id']} | Prestador: {r['provider_name']} | Flags: {r.get('risk_flags', 0)}", size=12), 
                ft.Row([
                    ft.OutlinedButton("Limpar denuncia", icon=ft.Icons.CHECK_CIRCLE, on_click=lambda _, rid=r["id"]: clear_flag(rid)), 
                    ft.OutlinedButton("Bloquear prestador", icon=ft.Icons.BLOCK, on_click=lambda _, rr=r: block_provider_from_flag(rr))
                ], wrap=True, spacing=8)
            ], spacing=8)
        ) for r in flagged] or [ft.Text("Sem denuncias pendentes.", size=12, color=C_MUTED)]
        
        dispute_controls = [ft.Container(
            border_radius=10, 
            bgcolor="#FFFFFF", 
            padding=10, 
            border=ft.border.all(1, "#E1EAF5"), 
            content=ft.Column([
                ft.Text(f"Disputa #{d['id']} - Pedido #{d['request_id']}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Cliente: {d['client_email']}", size=11),
                ft.Text(f"Prestador: {d['provider_email']}", size=11),
                ft.Text(f"Motivo: {d['reason']}", size=11),
                ft.Text(f"Descrição: {d['description']}", size=11),
                ft.Row([
                    ft.OutlinedButton("Resolver a favor do cliente", icon=ft.Icons.CHECK, on_click=lambda _, did=d["id"]: resolve_dispute(did, "Cliente")),
                    ft.OutlinedButton("Resolver a favor do prestador", icon=ft.Icons.CHECK, on_click=lambda _, did=d["id"]: resolve_dispute(did, "Prestador")),
                ], wrap=True, spacing=8)
            ], spacing=5)
        ) for d in active_disputes] or [ft.Text("Sem disputas ativas.", size=12, color=C_MUTED)]
        
        audit_controls = [ft.Text(f"{i['time']} | {i['action']} | {i.get('actor', '-')}", size=11, color=C_MUTED) for i in audit_logs[:12]] or [ft.Text("Sem logs.", size=11, color=C_MUTED)]

        return centered_view("/admin", panel(ft.Column([
            ft.Text("Painel Admin", size=22, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Row([
                chip(f"Pendentes: {len(pending)}", ft.Icons.PENDING_ACTION), 
                chip(f"Bloqueados: {len(blocked_users)}", ft.Icons.BLOCK), 
                chip(f"Denuncias: {len(flagged)}", ft.Icons.REPORT),
                chip(f"Disputas: {len(active_disputes)}", ft.Icons.GAVEL)
            ], wrap=True, spacing=8),
            ft.Text("Aprovacao de prestadores", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Column(pending_controls, spacing=8),
            ft.Text("Disputas ativas", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Column(dispute_controls, spacing=8),
            ft.Text("Bloquear/desbloquear contas", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Column(account_controls, spacing=8),
            ft.Text("Contas bloqueadas", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Column(blocked_controls, spacing=8),
            ft.Text("Denuncias", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Column(flag_controls, spacing=8),
            ft.Text("Cupons e taxas", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Row([coupon_code, coupon_value], wrap=True, spacing=8),
            ft.Row([fee_platform, fee_cancel], wrap=True, spacing=8),
            btn("Salvar configuracoes", ft.Icons.SAVE, save_admin_config),
            ft.Text("Auditoria", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Container(border_radius=12, bgcolor="#F5FCFF", padding=10, content=ft.Column(audit_controls, spacing=6)),
            ft.OutlinedButton("Voltar", icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/inicio-prestador" if is_provider(u) else "/inicio")),
        ], spacing=12), True))

    # Navegação
    def route_change(_):
        page.views.clear()
        if page.route == "/login": 
            page.views.append(login_view())
        elif page.route == "/cadastro": 
            page.views.append(register_view())
        elif page.route == "/perfil-servico":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            if not selected_provider["d"]: 
                page.go("/inicio-prestador" if cur_user["d"] and is_provider(cur_user["d"]) else "/inicio"); 
                return
            page.views.append(profile_view(selected_provider["d"]))
        elif page.route == "/solicitar":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            if not is_client(cur_user["d"]): 
                page.go("/inicio-prestador"); 
                return
            page.views.append(request_view())
        elif page.route == "/chat":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            page.views.append(chat_view())
        elif page.route == "/pedidos":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            page.views.append(orders_view())
        elif page.route == "/favoritos":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            page.views.append(favorites_view())
        elif page.route == "/admin":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            if not is_admin(cur_user["d"]): 
                page.go("/inicio-prestador" if is_provider(cur_user["d"]) else "/inicio"); 
                return
            page.views.append(admin_view())
        elif page.route == "/inicio-prestador":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            if not is_provider(cur_user["d"]): 
                page.go("/inicio"); 
                return
            page.views.append(provider_home_view())
        elif page.route == "/inicio":
            if not cur_user["d"]: 
                page.go("/login"); 
                return
            if is_provider(cur_user["d"]): 
                page.go("/inicio-prestador"); 
                return
            page.views.append(home_view())
        else: 
            page.go("/login"); 
            return
        page.update()

    def view_pop(_):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")


ft.app(target=main)