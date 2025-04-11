import sys
from antlr4 import *
from CSVLexer import CSVLexer
from CSVParser import CSVParser
from CSVListener import CSVListener
from collections import defaultdict, Counter
import json

class Loader(CSVListener):
    EMPTY = ""
    def __init__(self):
        self.rows = []
        self.header = []
        self.currentRowFieldValues = []

    def enterRow(self, ctx:CSVParser.RowContext):
        self.currentRowFieldValues = []

    def exitText(self, ctx:CSVParser.TextContext):
        self.currentRowFieldValues.append(ctx.getText())

    def exitString(self, ctx:CSVParser.StringContext):
        self.currentRowFieldValues.append(ctx.getText())

    def exitEmpty(self, ctx:CSVParser.EmptyContext):
        self.currentRowFieldValues.append(self.EMPTY)

    def exitHeader(self, ctx:CSVParser.HeaderContext):
        self.header = list(self.currentRowFieldValues)

    def exitRow(self, ctx:CSVParser.RowContext):
        # Evita procesar la fila si es parte del header
        if ctx.parentCtx.getRuleIndex() == CSVParser.RULE_header:
            return

        m = {}
        for i, val in enumerate(self.currentRowFieldValues):
            key = self.header[i] if i < len(self.header) else f"col_{i}"
            m[key] = val
        self.rows.append(m)

    def exportar_a_json(self, data, filename="output.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def detect_repeated_rows(rows):
    seen_rows = set()
    repeated_rows = set()
    for row in rows:
        row_tuple = tuple(row.values())  # Convertir la fila a una tupla
        if row_tuple in seen_rows:
            repeated_rows.add(row_tuple)
        seen_rows.add(row_tuple)
    return repeated_rows


def count_month_occurrences(rows):
    month_counter = Counter()
    for row in rows:
        mes = row.get("Mes", "").strip('"')  # Suponiendo que la columna se llama 'Mes'
        if mes:
            month_counter[mes] += 1
    return month_counter


def detect_invalid_amounts(rows):
    invalid_amounts = []
    for row in rows:
        monto = row.get("Cantidad", "").replace('"', '').replace('$', '').replace(',', '').strip()
        if monto == "" or monto.lower() in ["n/a", "na"]:
            invalid_amounts.append(row)
    return invalid_amounts


def sum_amounts_by_month(rows):
    montos_por_mes = defaultdict(int)
    for row in rows:
        mes = row.get("Mes", "").strip('"')
        monto = row.get("Cantidad", "").replace('"', '').replace('$', '').replace(',', '').strip()
        if mes and monto.isdigit():
            montos_por_mes[mes] += int(monto)
        elif mes:
            try:
                montos_por_mes[mes] += float(monto)
            except ValueError:
                pass  # Si no se puede convertir a número, lo ignoramos
    return montos_por_mes


def main(argv):
    input_stream = FileStream(argv[1], encoding='utf-8')
    lexer = CSVLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CSVParser(stream)
    tree = parser.csvFile()

    loader = Loader()
    walker = ParseTreeWalker()
    walker.walk(loader, tree)

    # Detectar filas repetidas
    repeated_rows = detect_repeated_rows(loader.rows)
    if repeated_rows:
        print("\n⚠️ Filas repetidas:")
        for rep in repeated_rows:
            print(f"• {rep}")
    else:
        print("\n✔️ No hay filas repetidas.")

    # Contar cuántas veces aparece cada mes
    month_counter = count_month_occurrences(loader.rows)
    print("\n🔄 Estadísticas de meses (cuántas veces aparece cada mes):")
    for mes, count in month_counter.items():
        print(f"• {mes}: {count} veces")

    # Detectar "Cantidad" vacíos o mal formateados
    invalid_amounts = detect_invalid_amounts(loader.rows)
    if invalid_amounts:
        print("\n⚠️ Filas con 'Cantidad' inválida o vacía:")
        for invalid_row in invalid_amounts:
            print(f"• {invalid_row}")

    # Crear diccionario de totales por mes
    montos_por_mes = sum_amounts_by_month(loader.rows)
    print("\n💰 Totales por mes:")
    for mes, total in montos_por_mes.items():
        print(f"• {mes}: {total}")

    # Exportar los datos totales por mes a un archivo JSON
    loader.exportar_a_json(montos_por_mes, "montos_por_mes.json")


if __name__ == '__main__':
    main(sys.argv)
