import flet as ft
from datetime import datetime, date
import json
import os

# --- AYARLAR ---
DATA_FILE = "namaz_takip_ultra_final.json"


def main(page: ft.Page):
    # --- 1. AYARLAR ---
    page.title = "Kaza Takipçisi"
    page.bgcolor = "#FAFAFA"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Yükleniyor...
    page.add(ft.Text("Başlatılıyor...", color="green"))
    page.update()

    # --- 2. VERİ ---
    def load_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_data(data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    # --- 3. HESAPLAMA ---
    def calculate_debt(birth, age, start):
        try:
            d_birth = datetime.strptime(birth, "%d/%m/%Y").date()
            d_start = date.today() if not start else datetime.strptime(start, "%d/%m/%Y").date()

            try:
                d_puberty = d_birth.replace(year=d_birth.year + int(age))
            except:
                d_puberty = d_birth.replace(year=d_birth.year + int(age), day=28)

            if d_start > date.today(): d_start = date.today()

            delta = d_start - d_puberty
            days = delta.days if delta.days > 0 else 0

            return {
                "Sabah": days, "Öğle": days, "İkindi": days,
                "Akşam": days, "Yatsı": days, "Vitir": days,
                "start_date": d_start.strftime("%d/%m/%Y"),
                "last_check": str(date.today())
            }
        except:
            return None

    # --- 4. EKRANLAR ---
    def show_setup():
        page.clean()

        def format_date(e):
            v = e.control.value
            digits = "".join(filter(str.isdigit, v))
            res = ""
            if len(digits) > 0: res += digits[:2]
            if len(digits) >= 2: res += "/" + digits[2:4]
            if len(digits) >= 4: res += "/" + digits[4:8]
            e.control.value = res
            e.control.update()

        # TARİH SEÇİCİ
        def open_date_picker(target_field):
            dd_d = ft.Dropdown(width=70, options=[ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 32)],
                               label="Gün", bgcolor="white", text_size=14)
            dd_m = ft.Dropdown(width=70, options=[ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 13)],
                               label="Ay", bgcolor="white", text_size=14)
            dd_y = ft.Dropdown(width=90, options=[ft.dropdown.Option(str(i)) for i in range(1950, 2026)], label="Yıl",
                               bgcolor="white", text_size=14)

            def save(e):
                if dd_d.value and dd_m.value and dd_y.value:
                    target_field.value = f"{dd_d.value}/{dd_m.value}/{dd_y.value}"
                    target_field.update()
                    picker_box.visible = False
                    picker_box.update()

            def close(e):
                picker_box.visible = False
                picker_box.update()

            picker_box = ft.Container(
                visible=False, bgcolor="#E8F5E9", padding=10, border_radius=10,
                border=ft.Border(
                    top=ft.BorderSide(1, "#2E7D32"), bottom=ft.BorderSide(1, "#2E7D32"),
                    left=ft.BorderSide(1, "#2E7D32"), right=ft.BorderSide(1, "#2E7D32")
                ),
                content=ft.Column([
                    ft.Text("Tarih Seçiniz:", weight="bold", color="#2E7D32"),
                    ft.Row([dd_d, dd_m, dd_y], alignment="center"),
                    ft.Row([
                        ft.FilledButton("İptal", on_click=close,
                                        style=ft.ButtonStyle(bgcolor={"": "#D32F2F"}, color={"": "white"})),
                        ft.FilledButton("Seç", on_click=save,
                                        style=ft.ButtonStyle(bgcolor={"": "#2E7D32"}, color={"": "white"}))
                    ], alignment="center")
                ])
            )
            return picker_box

        # GİRİŞ 1
        t1 = ft.TextField(label="Doğum Tarihi", width=200, on_change=format_date, text_align="center")
        p1 = open_date_picker(t1)
        b1 = ft.Container(
            content=ft.Icon("calendar_month", color="white"),
            width=50, height=50, bgcolor="#2E7D32", border_radius=8,
            alignment=ft.Alignment(0, 0),
            on_click=lambda _: setattr(p1, 'visible', not p1.visible) or p1.update()
        )

        # GİRİŞ 2
        t2 = ft.TextField(label="Buluğ Yaşı", value="13", width=100, text_align="center")

        # GİRİŞ 3
        t3 = ft.TextField(label="Namaza Başlama", width=200, on_change=format_date, text_align="center")
        p3 = open_date_picker(t3)
        b3 = ft.Container(
            content=ft.Icon("calendar_month", color="white"),
            width=50, height=50, bgcolor="#2E7D32", border_radius=8,
            alignment=ft.Alignment(0, 0),
            on_click=lambda _: setattr(p3, 'visible', not p3.visible) or p3.update()
        )

        def run_calc(e):
            if len(t1.value) < 10:
                page.snack_bar = ft.SnackBar(ft.Text("Doğum tarihi eksik"));
                page.snack_bar.open = True;
                page.update();
                return

            res = calculate_debt(t1.value, t2.value, t3.value)
            if res:
                save_data(res)
                show_dashboard(res)

        btn_run = ft.FilledButton("HESAPLA VE BAŞLA", on_click=run_calc,
                                  style=ft.ButtonStyle(bgcolor={"": "#2E7D32"}, color={"": "white"}), width=200,
                                  height=50)

        page.add(
            ft.Column([
                ft.Text("Hoşgeldin!", size=30, weight="bold", color="#2E7D32"),
                ft.Divider(),
                ft.Text("1. Doğum Tarihin:", weight="bold"),
                ft.Row([t1, b1], alignment="center"), p1,
                ft.Text("2. Buluğ Yaşın:", weight="bold"), t2,
                ft.Text("3. Namaza Başlama:", weight="bold"),
                ft.Row([t3, b3], alignment="center"), p3,
                ft.Divider(),
                btn_run
            ], horizontal_alignment="center", spacing=15)
        )
        page.update()

    # --- SONUÇ EKRANI ---
    def show_dashboard(data):
        page.clean()

        today = str(date.today())
        if data.get("last_check") != today:
            page.snack_bar = ft.SnackBar(ft.Text("Yeni gün eklendi!"))
            page.snack_bar.open = True
            for k in ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı", "Vitir"]: data[k] += 1
            data["last_check"] = today
            save_data(data)

        def make_card(vakit):
            count = data[vakit]

            def degis(miktar):
                data[vakit] += miktar
                if data[vakit] < 0: data[vakit] = 0
                save_data(data)
                show_dashboard(data)

            return ft.Container(
                bgcolor="white", padding=10, margin=ft.Margin(0, 0, 0, 10), border_radius=10,
                border=ft.Border(
                    top=ft.BorderSide(1, "#2E7D32"), bottom=ft.BorderSide(1, "#2E7D32"),
                    left=ft.BorderSide(1, "#2E7D32"), right=ft.BorderSide(1, "#2E7D32")
                ),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=3, color="#1A000000", offset=ft.Offset(0, 2)),
                content=ft.Row([
                    ft.Text(vakit, size=18, weight="bold", color="#2E7D32", width=80),

                    ft.Container(
                        content=ft.Text(str(count), size=22, weight="bold", color="#212121"),
                        expand=True, alignment=ft.Alignment(0, 0)
                    ),

                    ft.Row([
                        # TURUNCU EKLE (+)
                        ft.Container(
                            content=ft.Icon("add", color="white"),
                            width=45, height=45, bgcolor="#EF6C00", border_radius=10,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda _: degis(1),
                            tooltip="Ekle"
                        ),
                        # YEŞİL TİK (✔)
                        ft.Container(
                            content=ft.Icon("check", color="white"),
                            width=45, height=45, bgcolor="#2E7D32", border_radius=25,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda _: degis(-1),
                            tooltip="Kıl"
                        )
                    ], spacing=10)
                ], alignment="spaceBetween")
            )

        page.add(
            ft.Text("Kaza Borçların", size=28, weight="bold", color="#2E7D32"),
            ft.Divider(),
            make_card("Sabah"),
            make_card("Öğle"),
            make_card("İkindi"),
            make_card("Akşam"),
            make_card("Yatsı"),
            make_card("Vitir")
        )
        page.update()

    # BAŞLATMA
    data = load_data()
    if data:
        show_dashboard(data)
    else:
        show_setup()


if __name__ == "__main__":
    ft.app(main)