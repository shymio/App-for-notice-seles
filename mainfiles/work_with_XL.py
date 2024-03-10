import flet as ft
import psycopg2
from config import host, user, password, db_name
import datetime

main_table = []

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM products"
        )
        spisok = list(cursor)

        for i in range(0, 16):
            els = str(spisok[i])[1:-1].split(", ")
            result = [el for el in els]
            main_table.append(result)

        print(main_table)

        print("[INFO] Table created succesfully")

except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)

# PLACE_IN_TABLE["H9"].value = str(PLACE_IN_TABLE["H9"].value) + "+23+12"
# x = PLACE_IN_TABLE["H9"].value[1:]
# result = sum(map(int, x.split('+')))
# print(result)

############################################################

def main(page):
    page.title = "Учет статистики"
    scroll = ft.ScrollMode.AUTO

    def add_sum(e):
        summa.value = int(summa.value) + int(new_sum.value)
        new_sum.value = ""
        page.update()

    text = ft.Text("Общая сумма закупок", size=20)
    summa = ft.Text("0000", size=20)
    new_sum = ft.TextField(label="Введите сумму", width=150, height=45)
    row1 = ft.Row([text, summa], spacing=10)
    row2 = ft.Row([new_sum, ft.ElevatedButton("Добавить сумму", on_click=add_sum)], spacing=10)
    row_together = ft.Row([row1, row2], spacing=100)

    product = ft.Text("Товар", size=20)
    list_products = ft.Dropdown(
        width=250,
        options=[
            ft.dropdown.Option("Сникерс 1 шт"),
            ft.dropdown.Option("Сникерс 2 шт"),
            ft.dropdown.Option("Твикс"),
            ft.dropdown.Option("Шоколадка Альпен Гольд"),
            ft.dropdown.Option("Кукурузные палочки"),
            ft.dropdown.Option("Чипсы большая пачка"),
            ft.dropdown.Option("Чипсы начос"),
            ft.dropdown.Option("Газировка (2л)"),
            ft.dropdown.Option("Газировка (0,5)"),
            ft.dropdown.Option("Дошик"),
            ft.dropdown.Option("Орео"),
            ft.dropdown.Option("Чокопай"),
            ft.dropdown.Option("Мини круассаны"),
            ft.dropdown.Option("Барни"),
            ft.dropdown.Option("Мармеладные мишки"),
            ft.dropdown.Option("Лейс СТАКС"),
            ft.dropdown.Option("Поп-корн"),])

    towar_row = ft.Row([product, list_products], spacing=20)

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=80)

    def minus_click(e):
        txt_number.value = int(txt_number.value) - 1
        page.update()

    def plus_click(e):
        txt_number.value = int(txt_number.value) + 1
        page.update()

    count_products_row = ft.Row(
        [ft.IconButton(ft.icons.REMOVE, on_click=minus_click), txt_number,
         ft.IconButton(ft.icons.ADD, on_click=plus_click)])

    with connection.cursor() as cursor:
        cursor.execute("SELECT finish_gain FROM sales_history")
        column_sum = sum(row[0] for row in cursor)
        general_profit = ft.Text(f"Общая прибыль {column_sum}", size=30, weight=ft.FontWeight.BOLD)

    with connection.cursor() as cursor:
        cursor.execute("SELECT finish_gain FROM sales_history WHERE date_of_sale = CURRENT_DATE")
        column_sum_today = sum(row[0] for row in cursor)
        today_profit = ft.Text(f"Прибыль сегодня {column_sum_today}", size=30, weight=ft.FontWeight.BOLD)

    with connection.cursor() as cursor:
        cursor.execute("SELECT sales_history.date_of_sale, products.position_name, sales_history.counts, sales_history.finish_gain FROM sales_history JOIN products ON products.id = sales_history.product_id")
        h_l = list(cursor)
        print(h_l)
        history_list = [[item for item in tpl] for tpl in h_l]
        print(history_list)



#### ПЕРВОЕ - СТРОКА, ВТОРОЕ - СТОЛБЕЦ [][]
#INSERT INTO sales_history (id, date_of_sale, counts, finish_gain, product_id)
#VALUES (1, NOW(), 1, 31, 5)

    def click_add_new_product(e):
        for i in range(len(main_table)):
            if list_products.value == main_table[i][1][1:-1]:
                profit = txt_number.value * int(main_table[i][4])
                text = ft.Text(f"+{profit}", size = 17)

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM sales_history")
                    spisok_id_history = list(cursor)
                    j = int(str(spisok_id_history[-1])[1:-2]) + 1

                    cursor.execute(
                        "INSERT INTO sales_history (id, date_of_sale, counts, finish_gain, product_id)"
                        "VALUES (%s, NOW(), %s, %s, %s)",
                        (j, txt_number.value, (txt_number.value * int(main_table[i][4])), main_table[i][0]))
        page.snack_bar = ft.SnackBar(text)
        page.snack_bar.open = True
        clean_fields()
        general_gain_func()
        today_gain_func()
        page.update()

    def clean_fields():
        list_products.value = ""
        txt_number.value = "0"
        page.update()

    def general_gain_func():
        with connection.cursor() as cursor:
            cursor.execute("SELECT finish_gain FROM sales_history")
            column_sum = sum(row[0] for row in cursor)
        general_profit.value = "Общая прибыль " + str(column_sum)
        page.update()

    def today_gain_func():
        with connection.cursor() as cursor:
            cursor.execute("SELECT finish_gain FROM sales_history WHERE date_of_sale = CURRENT_DATE")
            column_sum_today = sum(row[0] for row in cursor)
        today_profit.value = "Прибыль сегодня " + str(column_sum_today)
        page.update()

    button_add_new_product = ft.ElevatedButton("Добавить товар", on_click=click_add_new_product)

    MASSIVE_FOR_LEFT_SIDE = [row_together, ft.Row([towar_row, count_products_row, button_add_new_product], spacing=10)]

    main_card = ft.Card(
        elevation=15,
        expand=5,
        content=ft.Container(
            content=ft.Column(controls=MASSIVE_FOR_LEFT_SIDE),
            border_radius=ft.border_radius.all(20),
            bgcolor=ft.colors.WHITE24,
            padding=30,
        )
    )

    general_sum_card = ft.Card(
        elevation=15,
            content=ft.Container(
                content=general_profit,
                alignment=ft.alignment.center,
                border_radius=ft.border_radius.all(20),
                bgcolor=ft.colors.WHITE24,
                padding=10,
                width=361,
                height=100
            )
        )

    today_sum_card = ft.Card(
        elevation=15,
        content=ft.Container(
            content=today_profit,
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(20),
            bgcolor=ft.colors.WHITE24,
            padding=10,
            width=361,
            height=100
        )
    )

    row_sums = ft.Row([general_sum_card, today_sum_card])

    left_colum = ft.Column([main_card, row_sums])

    for_rows = [[datetime.date(2024, 2, 20), 'Кукурузные палочки', 1, 31], [datetime.date(2024, 2, 20), 'Дошик', 1, 16], [datetime.date(2024, 2, 20), 'Орео', 2, 112], [datetime.date(2024, 2, 19), 'Кукурузные палочки', 1, 31]]

#Запрос в бд
#"SELECT sales_history.date_of_sale, products.position_name, sales_history.counts, sales_history.finish_gain FROM sales_history
#JOIN products ON products.id = sales_history.product_id"

    datatable_tab = ft.Tab('История продаж')

    table_data = ft.DataTable(
        border_radius=12,
        columns=[
            ft.DataColumn(ft.Text("Дата")),
            ft.DataColumn(ft.Text("Товар")),
            ft.DataColumn(ft.Text("Количество"), numeric=True),
            ft.DataColumn(ft.Text("Прибыль"), numeric=True)
        ],
        rows=[]
        #          ft.DataRow(
        #              cells=[
        #                  ft.DataCell(ft.Text(for_rows[0][0])),
        #                  ft.DataCell(ft.Text(for_rows[0][1])),
        #                  ft.DataCell(ft.Text(for_rows[0][2])),
        #                  ft.DataCell(ft.Text(for_rows[0][3])),
        #              ],
        #          ),
        #          ft.DataRow(
        #              cells=[
        #                  ft.DataCell(ft.Text(for_rows[1][0])),
        #                  ft.DataCell(ft.Text(for_rows[1][1])),
        #                  ft.DataCell(ft.Text(for_rows[1][2])),
        #                  ft.DataCell(ft.Text(for_rows[1][3])),
        #              ],
        #          ),
        #          ft.DataRow(
        #              cells=[
        #                  ft.DataCell(ft.Text("Alice")),
        #                  ft.DataCell(ft.Text("Wong")),
        #                  ft.DataCell(ft.Text("25")),
        #                  ft.DataCell(ft.Text("25")),
        #              ],
        #          ),
        #      ] * 20,
    )

    cel1 = [
         ft.DataCell(ft.Text(for_rows[0][0])),
         ft.DataCell(ft.Text(for_rows[0][1])),
         ft.DataCell(ft.Text(for_rows[0][2])),
         ft.DataCell(ft.Text(for_rows[0][3])),
    ]

    tet = ft.DataRow(cel1)
    # table_data.cells = [ft.DataCell(ft.Text("Alice")),
    #                      ft.DataCell(ft.Text("Wong")),
    #                      ft.DataCell(ft.Text("25")),
    #                      ft.DataCell(ft.Text("25")),]

    table_data.row = [tet]

    datatable_tab.content = ft.Container(
        content=table_data,
        bgcolor=ft.colors.WHITE24,
        border_radius=ft.border_radius.all(20)
    )



    mytabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=3,
        tabs=[
            ft.Tab(),
        ],
    )

    mytabs.tabs = [datatable_tab]

    MAIN_GUI = ft.Container(
        expand=True,
        content=ft.Row([left_colum, mytabs]),
    )

    page.padding = 25
    page.add(MAIN_GUI)
    page.update()

if __name__ == '__main__':
    ft.app(target=main)

if connection:
    connection.close()
    print("[INFO] PostgreSQL connection closed")