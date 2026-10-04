from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import cv2
from PIL import Image

from dsvision.catalog import PATTERN_CATALOG
from dsvision.confluence import analyze_timeframe, combine_timeframes
from dsvision.journal import append_signal, load_recent
from dsvision.storage import load_config, save_config
from dsvision.timing import countdown_text
from dsvision.vision import capture_region, detect_candles

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


class RegionSelector(tk.Toplevel):
    def __init__(self, master, timeframe: str, callback):
        super().__init__(master)
        self.timeframe = timeframe
        self.callback = callback
        self.start = None
        self.rect = None

        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.28)
        self.attributes("-topmost", True)
        self.configure(bg="black")

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.bind("<Escape>", lambda _: self.destroy())

        tk.Label(
            self,
            text=f"SELECIONE SOMENTE AS VELAS DO GRÁFICO {timeframe} • ESC cancela",
            font=("Segoe UI", 20, "bold"),
            bg="black",
            fg="white",
        ).place(relx=0.5, y=30, anchor="n")

    def _press(self, event):
        self.start = (event.x_root, event.y_root)
        self.rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="white", width=3
        )

    def _drag(self, event):
        if not self.start or not self.rect:
            return
        sx = self.start[0] - self.winfo_rootx()
        sy = self.start[1] - self.winfo_rooty()
        self.canvas.coords(self.rect, sx, sy, event.x, event.y)

    def _release(self, event):
        if not self.start:
            return
        x0, y0 = self.start
        x1, y1 = event.x_root, event.y_root
        region = {
            "left": min(x0, x1),
            "top": min(y0, y1),
            "width": abs(x1 - x0),
            "height": abs(y1 - y0),
        }
        if region["width"] < 150 or region["height"] < 120:
            messagebox.showwarning("DS VISION PRO", "Selecione uma área maior.")
            return
        self.destroy()
        self.callback(self.timeframe, region)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("DS VISION PRO")
        self.geometry("1220x790")
        self.minsize(1080, 720)

        self.cfg = load_config()
        self.running = False
        self.last_signal_key = ""
        self.preview_refs = {}
        self.voice = None

        if pyttsx3 is not None and self.cfg.get("voice_alerts", True):
            try:
                self.voice = pyttsx3.init()
                self.voice.setProperty("rate", 175)
            except Exception:
                self.voice = None

        self._build()
        self._tick_clock()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="DS VISION", font=("Segoe UI", 26, "bold")).pack(pady=(28, 0))
        ctk.CTkLabel(sidebar, text="PRO", font=("Segoe UI", 17, "bold"), text_color="#8b5cf6").pack()
        ctk.CTkLabel(sidebar, text="M5 • M15 • 60s", text_color="#9ca3af").pack(pady=(4, 22))

        for tf in ("M5", "M15", "M1"):
            ctk.CTkButton(
                sidebar,
                text=f"Selecionar gráfico {tf}",
                command=lambda timeframe=tf: self.select_region(timeframe),
                height=38,
            ).pack(fill="x", padx=16, pady=5)

        self.start_button = ctk.CTkButton(
            sidebar,
            text="INICIAR LEITURA",
            command=self.toggle,
            height=46,
            fg_color="#16a34a",
            hover_color="#15803d",
        )
        self.start_button.pack(fill="x", padx=16, pady=(20, 8))

        ctk.CTkButton(
            sidebar,
            text="Analisar agora",
            command=self.scan_once,
            height=38,
        ).pack(fill="x", padx=16, pady=5)

        ctk.CTkButton(
            sidebar,
            text="Catálogo de padrões",
            command=self.open_catalog,
            height=38,
            fg_color="#6d28d9",
            hover_color="#5b21b6",
        ).pack(fill="x", padx=16, pady=(16, 5))

        ctk.CTkButton(
            sidebar,
            text="Histórico de sinais",
            command=self.open_history,
            height=38,
            fg_color="#374151",
            hover_color="#4b5563",
        ).pack(fill="x", padx=16, pady=5)

        ctk.CTkLabel(
            sidebar,
            text="M1 é opcional para timing.\nM5 e M15 formam o contexto.",
            text_color="#9ca3af",
            justify="left",
        ).pack(padx=16, pady=18, anchor="w")

        main = ctk.CTkFrame(self, corner_radius=0, fg_color="#0b1020")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure((0, 1, 2), weight=1)
        main.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(16, 6))

        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left")
        ctk.CTkLabel(left_header, text="Central Tática", font=("Segoe UI", 25, "bold")).pack(side="left")

        self.clock_label = ctk.CTkLabel(
            left_header,
            text="PRÓXIMO MINUTO 00:60",
            font=("Segoe UI", 15, "bold"),
            text_color="#38bdf8",
        )
        self.clock_label.pack(side="left", padx=18)

        self.status = ctk.CTkLabel(header, text="● PARADO", text_color="#f59e0b")
        self.status.pack(side="right")

        signal_card = ctk.CTkFrame(main, height=150, fg_color="#111827")
        signal_card.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        signal_card.grid_columnconfigure((0, 1, 2), weight=1)

        self.direction_label = ctk.CTkLabel(signal_card, text="AGUARDAR", font=("Segoe UI", 42, "bold"))
        self.direction_label.grid(row=0, column=0, rowspan=2, padx=22, pady=18, sticky="w")

        self.strength_label = ctk.CTkLabel(signal_card, text="Força técnica\n0/100", font=("Segoe UI", 18, "bold"))
        self.strength_label.grid(row=0, column=1, rowspan=2, padx=20, pady=18)

        self.score_label = ctk.CTkLabel(signal_card, text="ALTA 0 × 0 BAIXA", font=("Segoe UI", 18, "bold"))
        self.score_label.grid(row=0, column=2, padx=20, pady=(25, 0))
        ctk.CTkLabel(
            signal_card,
            text="Expiração operacional configurada: 60 segundos",
            text_color="#9ca3af",
        ).grid(row=1, column=2, padx=20, pady=(0, 20))

        self.cards = {}
        for col, tf in enumerate(("M5", "M15", "M1")):
            card = ctk.CTkFrame(main, fg_color="#111827")
            card.grid(
                row=2,
                column=col,
                sticky="nsew",
                padx=(20 if col == 0 else 7, 20 if col == 2 else 7),
                pady=10,
            )
            ctk.CTkLabel(card, text=tf, font=("Segoe UI", 20, "bold")).pack(pady=(14, 4))
            state = ctk.CTkLabel(card, text="NÃO CONFIGURADO", text_color="#9ca3af")
            state.pack()
            preview = ctk.CTkLabel(card, text="")
            preview.pack(fill="x", padx=10, pady=10)
            detail = ctk.CTkTextbox(card, height=260, wrap="word")
            detail.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            detail.insert("1.0", "Selecione a região do gráfico.")
            detail.configure(state="disabled")
            self.cards[tf] = {"state": state, "preview": preview, "detail": detail}

        footer = ctk.CTkLabel(
            main,
            text="Assistente de análise. Score = confluência técnica; não é probabilidade garantida.",
            text_color="#6b7280",
        )
        footer.grid(row=3, column=0, columnspan=3, pady=(2, 10))

    def _tick_clock(self):
        self.clock_label.configure(text=f"PRÓXIMO MINUTO {countdown_text()}")
        self.after(250, self._tick_clock)

    def select_region(self, timeframe: str):
        self.running = False
        self.start_button.configure(text="INICIAR LEITURA", fg_color="#16a34a", hover_color="#15803d")
        self.status.configure(text="● PARADO", text_color="#f59e0b")
        self.withdraw()
        self.after(250, lambda: RegionSelector(self, timeframe, self._region_selected))

    def _region_selected(self, timeframe: str, region: dict):
        self.deiconify()
        self.lift()
        self.cfg["regions"][timeframe] = region
        save_config(self.cfg)
        self.cards[timeframe]["state"].configure(text="CONFIGURADO", text_color="#22c55e")
        self.scan_once()

    def toggle(self):
        if not self.cfg["regions"].get("M5") and not self.cfg["regions"].get("M15"):
            messagebox.showinfo("DS VISION PRO", "Selecione pelo menos M5 ou M15.")
            return
        self.running = not self.running
        if self.running:
            self.start_button.configure(text="PARAR LEITURA", fg_color="#dc2626", hover_color="#b91c1c")
            self.status.configure(text="● ANALISANDO", text_color="#22c55e")
            self._loop()
        else:
            self.start_button.configure(text="INICIAR LEITURA", fg_color="#16a34a", hover_color="#15803d")
            self.status.configure(text="● PARADO", text_color="#f59e0b")

    def _loop(self):
        if not self.running:
            return
        self.scan_once()
        self.after(int(self.cfg.get("scan_ms", 1000)), self._loop)

    def scan_once(self):
        analyses = {}

        for tf in ("M5", "M15", "M1"):
            region = self.cfg["regions"].get(tf)
            if not region:
                continue

            try:
                frame = capture_region(region)
                candles = detect_candles(frame)

                if len(candles) < int(self.cfg.get("min_candles", 14)):
                    self._update_tf_error(tf, frame, candles)
                    continue

                analysis = analyze_timeframe(candles, tf, self.cfg)
                analyses[tf] = analysis
                self._update_tf(tf, frame, candles, analysis)
            except Exception as exc:
                self._set_detail(tf, f"Erro na leitura:\n{exc}")

        if not analyses:
            return

        combined = combine_timeframes(analyses)
        self._update_combined(combined)

    def _update_combined(self, result):
        self.direction_label.configure(text=result.direction)
        self.strength_label.configure(text=f"Força técnica\n{result.strength}/100")
        self.score_label.configure(text=f"ALTA {result.bull_score} × {result.bear_score} BAIXA")

        if result.direction == "ALTA":
            self.direction_label.configure(text_color="#22c55e")
        elif result.direction == "BAIXA":
            self.direction_label.configure(text_color="#ef4444")
        else:
            self.direction_label.configure(text_color="#f59e0b")

        signal_key = f"{result.direction}:{result.bull_score}:{result.bear_score}"
        if result.direction in ("ALTA", "BAIXA") and signal_key != self.last_signal_key:
            append_signal(result)
            self._speak(
                f"DS Vision. Sinal de {result.direction.lower()}. "
                f"Força técnica {result.strength}."
            )
        self.last_signal_key = signal_key

    def _update_tf(self, tf, frame, candles, analysis):
        self.cards[tf]["state"].configure(
            text=f"{analysis.direction} • {analysis.strength}/100 • {len(candles)} velas",
            text_color=(
                "#22c55e"
                if analysis.direction == "ALTA"
                else "#ef4444"
                if analysis.direction == "BAIXA"
                else "#f59e0b"
            ),
        )

        lines = [
            f"ALTA {analysis.bull_score} × {analysis.bear_score} BAIXA",
            "",
        ] + [f"• {reason}" for reason in analysis.reasons[:16]]

        self._set_detail(tf, "\n".join(lines))
        self._set_preview(tf, frame, candles)

    def _update_tf_error(self, tf, frame, candles):
        count = len(candles)
        self.cards[tf]["state"].configure(
            text=f"AJUSTAR ÁREA • {count} velas",
            text_color="#f59e0b",
        )
        self._set_detail(
            tf,
            "Poucas velas detectadas.\n\n"
            "Selecione somente a área central das velas, evitando textos, menus e eixo de preços.\n\n"
            "As marcações no preview mostram o que o robô reconheceu como candle.",
        )
        self._set_preview(tf, frame, candles)

    def _set_detail(self, tf, text):
        box = self.cards[tf]["detail"]
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def _set_preview(self, tf, frame, candles):
        annotated = frame.copy()

        # Overlay de calibração: retângulos mostram exatamente os candles
        # reconhecidos pelo motor visual.
        for candle in candles:
            x = int(round(candle.x))
            y_high = max(0, int(round(-candle.high)))
            y_low = min(annotated.shape[0] - 1, int(round(-candle.low)))
            color = (0, 220, 0) if candle.bull else (0, 0, 235)
            cv2.rectangle(
                annotated,
                (max(0, x - 4), y_high),
                (min(annotated.shape[1] - 1, x + 4), y_low),
                color,
                1,
            )

        h, w = annotated.shape[:2]
        scale = min(310 / max(1, w), 180 / max(1, h), 1)
        preview = cv2.resize(
            annotated,
            (max(1, int(w * scale)), max(1, int(h * scale))),
            interpolation=cv2.INTER_AREA,
        )
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(preview)
        ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size,
        )
        self.preview_refs[tf] = ctk_image
        self.cards[tf]["preview"].configure(image=ctk_image)

    def open_catalog(self):
        win = ctk.CTkToplevel(self)
        win.title("DS VISION PRO • Catálogo de Padrões")
        win.geometry("900x700")
        win.transient(self)

        ctk.CTkLabel(
            win,
            text="CATÁLOGO PROFISSIONAL DE PADRÕES",
            font=("Segoe UI", 24, "bold"),
        ).pack(pady=(18, 4))
        ctk.CTkLabel(
            win,
            text="O padrão sozinho não gera entrada: o motor cruza contexto, estrutura e timeframes.",
            text_color="#9ca3af",
        ).pack(pady=(0, 14))

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        scroll.grid_columnconfigure(0, weight=1)

        for row, item in enumerate(PATTERN_CATALOG):
            if item["direction"] == "ALTA":
                color = "#22c55e"
            elif item["direction"] == "BAIXA":
                color = "#ef4444"
            else:
                color = "#f59e0b"

            card = ctk.CTkFrame(scroll, fg_color="#111827")
            card.grid(row=row, column=0, sticky="ew", padx=6, pady=5)
            ctk.CTkLabel(
                card,
                text=item["name"],
                font=("Segoe UI", 15, "bold"),
                text_color=color,
                width=220,
                anchor="w",
            ).pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(
                card,
                text=f'{item["family"]} • {item["direction"]}',
                width=180,
                anchor="w",
            ).pack(side="left", padx=8)
            ctk.CTkLabel(
                card,
                text=item["description"],
                justify="left",
                wraplength=420,
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=8, pady=8)

    def open_history(self):
        win = ctk.CTkToplevel(self)
        win.title("DS VISION PRO • Histórico")
        win.geometry("900x620")
        win.transient(self)

        ctk.CTkLabel(
            win,
            text="HISTÓRICO DE SINAIS",
            font=("Segoe UI", 24, "bold"),
        ).pack(pady=(18, 4))
        ctk.CTkLabel(
            win,
            text="Sinais registrados automaticamente para validação do modelo.",
            text_color="#9ca3af",
        ).pack(pady=(0, 12))

        box = ctk.CTkTextbox(win, wrap="word")
        box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        rows = load_recent(100)
        if not rows:
            box.insert("1.0", "Ainda não há sinais registrados.")
        else:
            for item in rows:
                box.insert(
                    "end",
                    f'{item.get("timestamp", "")}  |  '
                    f'{item.get("direction", "")}  |  '
                    f'força {item.get("strength", "")}  |  '
                    f'ALTA {item.get("bull_score", "")} × '
                    f'{item.get("bear_score", "")} BAIXA\n',
                )
        box.configure(state="disabled")

    def _speak(self, text):
        if self.voice is None:
            return

        def run():
            try:
                self.voice.say(text)
                self.voice.runAndWait()
            except Exception:
                pass

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
