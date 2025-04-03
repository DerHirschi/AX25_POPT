"""
by Grok3-beta (AI by x.com)
Ported from:
   TheNetNode
   File: src/graph.c
"""
from math import atan2, pi, cos, sin

def generate_ascii_pie_chart(data, titel, datasets, fill_pie=True, radius=15, outline_thickness=0.5):
    """
    Generiert ein ASCII-Tortendiagramm aus den gegebenen Daten.

    Parameter:
    - data (list): Liste von Dictionaries mit beliebigen Datensätzen
    - titel (str): Titel des Diagramms
    - datasets (dict): Dictionary mit Datensatz-Schlüsseln und zugehörigen Zeichen
                       z.B. {'min': '#', 'ave': '*', 'max': '+'}
    - fill_pie (bool): Ob die Segmente gefüllt werden sollen
    - radius (int): Radius des Kreises (Standard: 15)
    - outline_thickness (float): Dicke des Umrisses (Standard: 0.5)

    Rückgabe:
    - str: Das Tortendiagramm als String
    """
    # Berechne die Summe der Werte für jeden Datensatz
    totals = {key: sum(d.get(key, 0) for d in data if d.get(key) is not None)
              for key in datasets.keys()}
    total_sum = sum(totals.values())
    if total_sum == 0:
        raise ValueError("Die Summe der Werte darf nicht 0 sein")

    # Berechne die Anteile (in Grad)
    shares = {key: (value / total_sum) * 360 for key, value in totals.items()}

    # Initialisiere den Ausgabe-String
    output = f"{titel}\n"
    output += f"  Total: {total_sum:.2f}\n"
    for key, value in totals.items():
        output += f"  {key.capitalize()}: {value:.2f} ({(value / total_sum * 100):.1f}%)\n"

    # Legende
    output += "\nLegende:\n"
    for key, symbol in datasets.items():
        output += f"  {symbol} = {key.capitalize()}\n"
    output += "\n"

    # Größe des Tortendiagramms
    width_factor = 2
    chart = [[' ' for _ in range(2 * radius * width_factor + 1)] for _ in range(2 * radius + 1)]
    center_x, center_y = radius * width_factor, radius

    # Fülle oder zeichne das Tortendiagramm
    current_angle = 0
    segment_angles = [0]  # Startwinkel für Trennlinien
    for key, angle in shares.items():
        symbol = datasets[key]
        end_angle = current_angle + angle
        segment_angles.append(end_angle % 360)

        if fill_pie:
            # Gefüllte Segmente
            for y in range(2 * radius + 1):
                for x in range(2 * radius * width_factor + 1):
                    dx = (x - center_x) / width_factor
                    dy = y - center_y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance <= radius:
                        point_angle = atan2(dy, dx) * 180 / pi
                        if point_angle < 0:
                            point_angle += 360
                        if current_angle <= point_angle < end_angle or \
                           (end_angle > 360 and point_angle < (end_angle % 360)):
                            chart[y][x] = symbol
        else:
            # Nur Außenkanten und Trennlinien
            for y in range(2 * radius + 1):
                for x in range(2 * radius * width_factor + 1):
                    dx = (x - center_x) / width_factor
                    dy = y - center_y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if abs(distance - radius) < outline_thickness:  # Äußere Kante
                        point_angle = atan2(dy, dx) * 180 / pi
                        if point_angle < 0:
                            point_angle += 360
                        if current_angle <= point_angle < end_angle or \
                           (end_angle > 360 and point_angle < (end_angle % 360)):
                            chart[y][x] = symbol

        current_angle = end_angle % 360

    if not fill_pie:
        # Zeichne Trennlinien (Radien) zwischen Segmenten
        for i, angle in enumerate(segment_angles):
            rad = angle * pi / 180
            # Wähle das Symbol des aktuellen Segments (oder des letzten bei angle=0)
            segment_idx = min(i, len(shares) - 1) if i > 0 else len(shares) - 1
            symbol = datasets[list(datasets.keys())[segment_idx]]
            for r in range(int(radius * 10)):  # Feinere Schritte für Trennlinien
                x = int(center_x + r * cos(rad) * width_factor / 10)
                y = int(center_y - r * sin(rad) / 10)
                if 0 <= y < len(chart) and 0 <= x < len(chart[0]):
                    chart[y][x] = symbol

    # Konvertiere das Diagramm in einen String
    for row in chart:
        output += ''.join(row) + '\n'

    return output

def generate_ascii_graph(data, titel, datasets, expand=False, x_scale=True, bar_mode=False, chart_type='line', fill_pie=True, radius=15, outline_thickness=0.5):
    """
    Generiert ein ASCII-Diagramm (Linien-, Balken- oder Tortendiagramm) aus den gegebenen Daten.

    Parameter:
    - data (list): Liste von Dictionaries mit beliebigen Datensätzen
    - titel (str): Titel des Diagramms
    - datasets (dict): Dictionary mit Datensatz-Schlüsseln und zugehörigen Zeichen
    - expand (bool): Ob der Graph zwischen Min und Max gestreckt werden soll (nur Linien/Balken)
    - x_scale (bool): Ob die X-Achse skaliert werden soll (nur Linien/Balken)
    - bar_mode (bool): Ob der Graph als Balkendiagramm dargestellt werden soll (nur Linien/Balken)
    - chart_type (str): 'line' für Linien-/Balkendiagramm, 'pie' für Tortendiagramm
    - fill_pie (bool): Ob die Segmente im Tortendiagramm gefüllt werden sollen
    - radius (int): Radius des Tortendiagramms (Standard: 15)
    - outline_thickness (float): Dicke des Umrisses im Tortendiagramm (Standard: 0.5)

    Rückgabe:
    - str: Das Diagramm als String
    """
    if chart_type.lower() == 'pie':
        return generate_ascii_pie_chart(data, titel, datasets, fill_pie, radius, outline_thickness)

    # Linien- oder Balkendiagramm
    elements = len(data)
    if elements == 0:
        raise ValueError("Datenliste darf nicht leer sein")

    all_values = []
    for d in data:
        for key in datasets.keys():
            if key in d and d[key] is not None:
                all_values.append(d[key])

    if not all_values:
        raise ValueError("Keine gültigen Datenwerte vorhanden")

    maximum = max(all_values)
    minimum = min(all_values)
    valid_averages = [sum(d.get(key, 0) for key in datasets.keys() if d.get(key) is not None) /
                      len([k for k in datasets.keys() if d.get(k) is not None])
                      for d in data if any(k in d and d[k] is not None for k in datasets.keys())]
    average = sum(valid_averages) / len(valid_averages) if valid_averages else 0

    output = f"{titel}\n"
    output += f"  Maximum: {maximum}\n"
    output += f"  Average: {average:.2f}\n"
    output += f"  Minimum: {minimum}\n\n"

    GRAPH_LINES = 10
    if expand:
        range_value = maximum - minimum
    else:
        range_value = maximum

    raster = range_value / GRAPH_LINES
    if raster == 0 or range_value % GRAPH_LINES > 0:
        raster += 1

    lines = int(range_value / raster)
    if range_value % raster > 0:
        lines += 1
    if lines < 5:
        lines = 5

    expandwert = minimum if expand else 0
    dataset_keys = list(datasets.keys())

    for line in range(lines, -1, -1):
        y_value = raster * line + expandwert
        output += f"{y_value:6.0f}|"
        for d in data:
            char = " "
            if bar_mode:
                for key in dataset_keys:
                    if key in d and d[key] is not None and d[key] >= y_value:
                        char = datasets[key]
                        break
            else:
                closest_key = None
                min_diff = float('inf')
                for key in dataset_keys:
                    if key in d and d[key] is not None:
                        diff = abs(d[key] - y_value)
                        if diff < min_diff and diff < raster / 2:
                            min_diff = diff
                            closest_key = key
                if closest_key:
                    char = datasets[closest_key]
            output += char
        output += "\n"

    output += "      +"
    if x_scale:
        scale_str = f"0{'-' * (elements - len(str(elements - 1)) - 1)}{elements - 1}"
        output += scale_str
    else:
        output += "-" * elements
    output += "\n"

    return output

# Beispielaufruf
if __name__ == "__main__":
    # Beispiel-Daten
    custom_data = [{'low': i, 'high': i * i} for i in range(70)]
    datasets_custom = {'low': '#', 'high': '+'}
    test_data = [{'min': i, 'ave': i + 0.5, 'max': i + 1} for i in range(60)]
    datasets_test = {'min': '#', 'ave': '*', 'max': '+'}

    custom_data2 = [
        {'temp':8},
        {'temp':9},
        {'temp':12},
        {'temp':14},
        {'temp':16},
        {'temp':21},
        {'temp':23},
        {'temp':24},
        {'temp':24.5},
        {'temp':25},
        {'temp':23},
        {'temp':21},
        {'temp':18},
        {'temp':17},
        {'temp':14},
        {'temp':12},
        {'temp':8},
        {'temp':5},
        {'temp':6},
        {'temp':8},
        {'temp':10},
        {'temp':12},
        {'temp':13},
        {'temp':15},
        {'temp':18},
        {'temp':20},
        {'temp':22},
        {'temp':24},
        {'temp':26},
        {'temp':27},
    ]
    datasets_custom2 = {'temp': '+'}

    # Tortendiagramm (gefüllt, Radius 15)
    graph_custom_pie_filled = generate_ascii_graph(custom_data, "Custom Graph (Pie, Filled, Radius 15)", datasets_custom, chart_type='pie', fill_pie=True, radius=15)
    print(graph_custom_pie_filled)

    # Tortendiagramm (nur Umriss und Trennlinien, Radius 15)
    graph_custom_pie_outline = generate_ascii_graph(custom_data, "Custom Graph (Pie, Outline, Radius 15)", datasets_custom, chart_type='pie', fill_pie=False, radius=15)
    print(graph_custom_pie_outline)

    # Tortendiagramm (nur Umriss und Trennlinien, Radius 10)
    graph_custom_pie_small = generate_ascii_graph(custom_data, "Custom Graph (Pie, Outline, Radius 10)", datasets_custom, chart_type='pie', fill_pie=False, radius=10)
    print(graph_custom_pie_small)

    # Test Graph als Tortendiagramm (gefüllt, Radius 15)
    graph_test_pie_filled = generate_ascii_graph(test_data, "Test Graph (Pie, Filled, Radius 15)", datasets_test, chart_type='pie', fill_pie=True, radius=15)
    print(graph_test_pie_filled)

    # Test Graph als Tortendiagramm (nur Umriss und Trennlinien, Radius 15)
    graph_test_pie_outline = generate_ascii_graph(test_data, "Test Graph (Pie, Outline, Radius 15)", datasets_test, chart_type='pie', fill_pie=False, radius=8)
    print(graph_test_pie_outline)

    graph_test_pie_outline = generate_ascii_graph(test_data, "Test Graph (Line, Outline)", datasets_test,
                                                  chart_type='line', )
    print(graph_test_pie_outline)
    graph_test_pie_outline = generate_ascii_graph(custom_data, "Custom Graph (Line, Outline)", datasets_custom,
                                                  chart_type='line', )
    print(graph_test_pie_outline)
    graph_test_pie_outline = generate_ascii_graph(custom_data2, "Custom Graph (Line, Outline)", datasets_custom2,
                                                  chart_type='line', )
    print(graph_test_pie_outline)
