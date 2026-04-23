import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import calendar

from sqlalchemy import select
from db import Product, SessionLocal, init_db

calendar_popup = None

root = None
tree = None
entry_name = None
entry_weight = None
expiration_var = None
entry_filter_name = None
entry_filter_weight = None
filter_date_var = None


def load_products(products=None):
    global tree

    for row in tree.get_children():
        tree.delete(row)

    if products is None:
        with SessionLocal() as session:
            products = session.scalars(select(Product)).all()

    for product in products:
        tree.insert(
            "",
            tk.END,
            values=(
                product.id,
                product.name,
                product.weight,
                product.expiration_date.strftime("%Y-%m-%d"),
            )
        )


def add_product():
    global entry_name, entry_weight, expiration_var

    name = entry_name.get().strip()
    weight_text = entry_weight.get().strip()
    expiration_text = expiration_var.get().strip()

    if not name or not weight_text or not expiration_text:
        messagebox.showerror("Ошибка", "Заполните все поля")
        return

    try:
        weight = int(weight_text)
        if weight <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Вес должен быть положительным целым числом")
        return

    try:
        expiration_date = datetime.strptime(expiration_text, "%Y-%m-%d").date()
    except ValueError:
        messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
        return

    with SessionLocal() as session:
        product = Product(
            name=name,
            weight=weight,
            expiration_date=expiration_date
        )
        session.add(product)
        session.commit()

    entry_name.delete(0, tk.END)
    entry_weight.delete(0, tk.END)
    expiration_var.set("")

    load_products()


def delete_product():
    global tree

    selected_item = tree.selection()

    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите строку для удаления")
        return

    values = tree.item(selected_item[0], "values")
    product_id = int(values[0])

    with SessionLocal() as session:
        product = session.get(Product, product_id)
        if product:
            session.delete(product)
            session.commit()

    load_products()


def filter_products():
    global entry_filter_name, entry_filter_weight, filter_date_var

    name_filter = entry_filter_name.get().strip().lower()
    min_weight_text = entry_filter_weight.get().strip()
    max_expiration_text = filter_date_var.get().strip()

    with SessionLocal() as session:
        products = session.scalars(select(Product)).all()

    filtered = []

    for product in products:
        if name_filter and name_filter not in product.name.lower():
            continue

        if min_weight_text:
            try:
                min_weight = int(min_weight_text)
                if product.weight < min_weight:
                    continue
            except ValueError:
                messagebox.showerror("Ошибка", "Минимальный вес должен быть числом")
                return

        if max_expiration_text:
            try:
                max_expiration = datetime.strptime(max_expiration_text, "%Y-%m-%d").date()
                if product.expiration_date > max_expiration:
                    continue
            except ValueError:
                messagebox.showerror("Ошибка", "Дата фильтра должна быть в формате ГГГГ-ММ-ДД")
                return

        filtered.append(product)

    load_products(filtered)


def reset_filters():
    global entry_filter_name, entry_filter_weight, filter_date_var

    entry_filter_name.delete(0, tk.END)
    entry_filter_weight.delete(0, tk.END)
    filter_date_var.set("")
    load_products()


def open_date_picker(date_var, anchor_widget):
    global calendar_popup, root

    if calendar_popup is not None and calendar_popup.winfo_exists():
        calendar_popup.destroy()

    try:
        initial_date = datetime.strptime(date_var.get(), "%Y-%m-%d").date()
    except ValueError:
        initial_date = datetime.today().date()

    current_year = [initial_date.year]
    current_month = [initial_date.month]

    popup = tk.Toplevel(root)
    calendar_popup = popup
    popup.title("Календарь")
    popup.resizable(False, False)
    popup.transient(root)

    x = anchor_widget.winfo_rootx()
    y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height() + 2
    popup.geometry(f"+{x}+{y}")

    def close_popup(_event=None):
        global calendar_popup
        if popup.winfo_exists():
            popup.destroy()
        calendar_popup = None

    def pick_day(day):
        date_var.set(f"{current_year[0]:04d}-{current_month[0]:02d}-{day:02d}")
        close_popup()

    header = tk.Frame(popup)
    header.pack(padx=6, pady=(6, 0))

    month_title = tk.Label(header, width=18, anchor="center")
    month_title.grid(row=0, column=1, padx=4)

    days_frame = tk.Frame(popup)
    days_frame.pack(padx=6, pady=6)

    def render_calendar():
        for child in days_frame.winfo_children():
            child.destroy()

        month_title.config(text=f"{calendar.month_name[current_month[0]]} {current_year[0]}")

        for col, day_name in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            tk.Label(days_frame, text=day_name, width=3).grid(row=0, column=col, padx=1, pady=1)

        for row, week in enumerate(calendar.monthcalendar(current_year[0], current_month[0]), start=1):
            for col, day in enumerate(week):
                if day == 0:
                    tk.Label(days_frame, text="", width=3).grid(row=row, column=col, padx=1, pady=1)
                else:
                    tk.Button(
                        days_frame,
                        text=str(day),
                        width=3,
                        command=lambda d=day: pick_day(d),
                    ).grid(row=row, column=col, padx=1, pady=1)

    def show_prev_month():
        if current_month[0] == 1:
            current_month[0] = 12
            current_year[0] -= 1
        else:
            current_month[0] -= 1
        render_calendar()

    def show_next_month():
        if current_month[0] == 12:
            current_month[0] = 1
            current_year[0] += 1
        else:
            current_month[0] += 1
        render_calendar()

    tk.Button(header, text="<", width=3, command=show_prev_month).grid(row=0, column=0)
    tk.Button(header, text=">", width=3, command=show_next_month).grid(row=0, column=2)

    popup.protocol("WM_DELETE_WINDOW", close_popup)
    popup.bind("<Escape>", close_popup)

    render_calendar()


def main():
    global root
    global tree
    global entry_name
    global entry_weight
    global expiration_var
    global entry_filter_name
    global entry_filter_weight
    global filter_date_var

    init_db()

    root = tk.Tk()
    root.title("Учёт продуктов")
    root.geometry("900x520")
    root.resizable(False, False)

    columns = ("id", "name", "weight", "expiration_date")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

    tree.heading("id", text="ID")
    tree.heading("name", text="Название")
    tree.heading("weight", text="Вес")
    tree.heading("expiration_date", text="Срок годности")

    tree.column("id", width=60, anchor="center")
    tree.column("name", width=250, anchor="center")
    tree.column("weight", width=120, anchor="center")
    tree.column("expiration_date", width=150, anchor="center")

    tree.pack(pady=10)

    frame_add = tk.LabelFrame(root, text="Добавление товара", padx=10, pady=10)
    frame_add.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_add, text="Название").grid(row=0, column=0, padx=5, pady=5)
    entry_name = tk.Entry(frame_add, width=25)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_add, text="Вес").grid(row=0, column=2, padx=5, pady=5)
    entry_weight = tk.Entry(frame_add, width=15)
    entry_weight.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_add, text="Срок годности (ГГГГ-ММ-ДД)").grid(row=0, column=4, padx=5, pady=5)
    expiration_var = tk.StringVar()
    entry_expiration = ttk.Entry(frame_add, width=15, textvariable=expiration_var)
    entry_expiration.grid(row=0, column=5, padx=5, pady=5)

    btn_pick_expiration = tk.Button(
        frame_add,
        text="...",
        width=3,
        command=lambda: open_date_picker(expiration_var, entry_expiration),
    )
    btn_pick_expiration.grid(row=0, column=6, padx=3, pady=5)

    btn_add = tk.Button(frame_add, text="Добавить", width=15, command=add_product)
    btn_add.grid(row=0, column=7, padx=10, pady=5)

    frame_delete = tk.Frame(root)
    frame_delete.pack(fill="x", padx=10, pady=5)

    btn_delete = tk.Button(frame_delete, text="Удалить выбранную строку", width=25, command=delete_product)
    btn_delete.pack(anchor="w")

    frame_filter = tk.LabelFrame(root, text="Фильтрация", padx=10, pady=10)
    frame_filter.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_filter, text="Название содержит").grid(row=0, column=0, padx=5, pady=5)
    entry_filter_name = tk.Entry(frame_filter, width=20)
    entry_filter_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_filter, text="Вес от").grid(row=0, column=2, padx=5, pady=5)
    entry_filter_weight = tk.Entry(frame_filter, width=10)
    entry_filter_weight.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_filter, text="Годен до").grid(row=0, column=4, padx=5, pady=5)
    filter_date_var = tk.StringVar()
    entry_filter_date = ttk.Entry(frame_filter, width=15, textvariable=filter_date_var)
    entry_filter_date.grid(row=0, column=5, padx=5, pady=5)

    btn_pick_filter_date = tk.Button(
        frame_filter,
        text="...",
        width=3,
        command=lambda: open_date_picker(filter_date_var, entry_filter_date),
    )
    btn_pick_filter_date.grid(row=0, column=6, padx=3, pady=5)

    btn_filter = tk.Button(frame_filter, text="Фильтровать", width=15, command=filter_products)
    btn_filter.grid(row=0, column=7, padx=10, pady=5)

    btn_reset = tk.Button(frame_filter, text="Сбросить фильтры", width=15, command=reset_filters)
    btn_reset.grid(row=0, column=8, padx=10, pady=5)

    load_products()
    root.mainloop()


if __name__ == "__main__":
    main()