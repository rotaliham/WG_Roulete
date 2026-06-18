import json
import random
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox

DATA_FILE = "games.json"
game_list = []
imported_games = [] 
heat_del = 0
local_heat = 0

def choose_file():
    """Открывает диалог выбора файла, подставляет имя без расширения"""
    global selected_path
    file_path = filedialog.askopenfilename(
        title="Выберите игру",
        filetypes=[
            ("Ярлык\Скрипт\Exe\Steam-ярлык", "*.url *.exe *.bat *.lnk")        # ← URL файлы
            #("Ярлыки", "*.lnk"),                 # ← Ярлыки Windows
            #("Исполняемые файлы", "*.exe *.bat *.cmd"),
            #("JAR файлы", "*.jar"),
            #("Все файлы", "*.*")     
        ]
    )
    if file_path:
        selected_path = file_path
        field_path.delete(0, END)
        field_path.insert(0, file_path)
        # Автоматически подставляем имя без расширения
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]  # Убираем расширение
        field_name.delete(0, END)
        field_name.insert(0, name_without_ext)  # ← Подставляем имя!
        #status_label.config(text=f"✅ Выбран: {base_name}")

def mass_import_from_file(filename="games_import.txt"):
    global imported_games
    imported_games = []
    print("Добавляет игры из текстового файла в game_list.\nФормат строки: название|вес|путь\nВес может быть целым или дробным")
  
    if not os.path.exists(filename):
        print(f"Файл {filename} не найден!")
        return 0
    
    added = 0
    errors = 0
    
    with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            parts = line.split("|")
            if len(parts) < 2:
                print(f"⚠️ Строка {line_num}: неверный формат (нужно имя|вес|путь)")
                errors += 1
                continue
            
            name = parts[0].strip()
            # Парсим минимальный вес
            try:
                min_weight = float(parts[1].strip())
            except ValueError:
                print(f"⚠️ Строка {line_num}: вес не число, пропускаем")
                errors += 1
                continue
            # Путь опционально
            path = parts[2].strip() if len(parts) >= 3 else ""
            
            # Добавляем игру
            game_list.append({
                "name": name,
                "weight": 10,
                "path": path,
                "min_weight": min_weight 
            })
            imported_games.append({
                "name": name,
                "weight": 10,
                "path": path,
                "min_weight": min_weight 
            })
            added += 1
            print(f"✓ {name} (мин.вес: {min_weight})")
    look_game()
    save_to_json()
    print(f"\n✅ Добавлено {added} игр, ошибок {errors}")
    return added

def rng_weight(number):
    pulweight = game_list[number]['weight'] - game_list[number]['min_weight']
    game_list[number]['weight'] = game_list[number]['min_weight']
    try:
        new_weight = pulweight / (len(game_list)-1)
    except:
        print("Мало игр, фу")
    i = 0
    for game in game_list:
        if i != number:
           game['weight'] += new_weight
        i += 1

def save_to_json():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(game_list, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_from_json():
    global game_list
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            game_list = json.load(f)
        print("Список Игра-Вес найден!")
        return True
    except FileNotFoundError:
        print("Файл не найден, создан новый список")
        game_list = []
        return False
    except json.JSONDecodeError:
        print("Ошибка чтения файла! Файл повреждён.")
        game_list = []
        return False
    
def start_game(path):
    if not os.path.exists(path):
        print("Данной директории нет")
        return False
    os.startfile(path)
    return True

load_from_json()

def add_game(): 
    name = field_name.get()
    path = field_path.get()
    weight_input = field_weight.get()
    if weight_input == "": 
       inweights = None
    else:
        try:
            inweights = float(weight_input)
        except ValueError:
            nweights = None
    if inweights is None: 
        game_list.append ({"name": name,"weight": 10,"path": path, "min_weight": 0})
    else: game_list.append ({"name": name,"weight": 10,"path": path, "min_weight": inweights})
    look_game()
    save_to_json()

def look_game():
    list_game_list.delete(0, END)  # Очищаем список
    if not game_list:
        list_game_list.insert(END, "Список игр пуст!")
        return
    for i, game in enumerate(game_list, 1):
        list_game_list.insert(END, f"{i}. {game['name']} - Вес: {game['weight']}")

def delete_game(): 
    global local_heat
    local_heat +=1
    if local_heat == 5:
        local_heat = 0
        selected = list_game_list.curselection()
        if not selected:
            return
        index = selected[0]
        
        removed_game = game_list.pop(index)
        look_game()
        save_to_json()

def randomize():
    weights = [game["weight"] for game in game_list]
    chosen = random.choices(game_list, weights=weights, k=1)[0]
    chosen_index = game_list.index(chosen)  
    rng_weight(chosen_index)
    start_game(chosen['path'])
    label_fate.config(text=(f"Выбрано: {chosen['name']}"))
    look_game()
    save_to_json()

def update_listbox():
    list_game_imp.delete(0, END)
    for i, game in enumerate(imported_games, 1):
        list_game_imp.insert(
            END, 
            f"{i:>3}. {game['name']} | Путь: {game['path']} | Мин: {game.get('min_weight', '—')}"
        )

def pull_up():
    result_text = mass_import_from_file("games_import.txt")
    update_listbox()

def wipe_out():
    global heat_del
    heat_del += 1
    if heat_del == 5:
        game_list.clear()
        heat_del = 0
    look_game()
    save_to_json()

def create_template_file():
    """Создаёт файл-шаблон games_import.txt с примерами"""
    
    # Проверяем, существует ли уже файл
    if os.path.exists("games_import.txt"):
        if not messagebox.askyesno(
            "Файл уже существует",
            "Файл games_import.txt уже существует.\nПерезаписать его?"
        ):
            
            return
    
    # Содержимое шаблона
    template = """# Файл для массового импорта игр
# Формат: название|вес|путь
# Примеры:

The Witcher 3|50|C:\\Games\\The Witcher 3.exe
Minecraft|10|C:\\Games\\Minecraft.exe
GTA V|65|C:\\Games\\GTA5.exe
Cyberpunk 2077|70|C:\\Games\\Cyberpunk.exe

# Можно добавлять игры без пути
Stardew Valley|8

# И с путём без расширения
Terraria|15|C:\\Games\\Terraria

# Комментарии начинаются с #
# Пустые строки игнорируются
"""
    
    try:
        with open("games_import.txt", "w", encoding="utf-8") as f:
            f.write(template)
        
        messagebox.showinfo(
            "Шаблон создан",
            f"Файл games_import.txt создан в папке:\n{os.getcwd()}\n\nЗаполните его и нажмите 'Пул-ап из файла games_import.txt'"
        )
    except Exception as e:

        messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{e}")
#Блок TKinter!!!!!!!!!
root = Tk()
root.title("Game Choiser with Weight")
root.geometry("960x550")

fr_interact = Frame(borderwidth=1) #Кнопки\поля
fr_list = Frame(borderwidth=1) #Списки
fr_input = Frame(fr_interact,borderwidth=1) #Поля и лейблы
fr_io = Frame(fr_interact,borderwidth=1) #Кнопки
fr_labels = Frame(fr_input,borderwidth=1) #Лейблы
fr_field = Frame(fr_input,borderwidth=1) #Поля
fr_one_button = Frame(fr_input,borderwidth=1) #Список(импорт)

fr_inbase = Frame(fr_list,borderwidth=1) #Список
fr_import = Frame(fr_list,borderwidth=1) #Список(импорт)

field_name = Entry(fr_field, width=40) #Ввод названия
field_path = Entry(fr_field, width=70) #Ввод пути
field_weight = Entry(fr_field, width=5) #Ввод минимального веса
label_name = Label(fr_labels,text="Название") #Описание названия
label_path = Label(fr_labels,text="Путь") #Описание пути
label_minweight = Label(fr_labels,text="Минимальный вес") #Описание минимального веса
label_fate = Label(fr_io,text="Судьба за тебя решит...", bg="white") #Выбранная игра

add_game_button = ttk.Button(fr_io,text="Добавить игру", command=add_game) #Кнопка добавить игру
wipe_out_button = ttk.Button(fr_io,text="Стереть список(нажать 5 раз)", command=wipe_out) #Кнопка стереть список игр
delete_game_button = ttk.Button(fr_io,text="Удалить игру(нажать 5 раз)", command=delete_game) #Кнопка удалить одну игру
randomize_button = ttk.Button(fr_io,text="Рулетка", command=randomize) #Кнопка рандомизации
pull_up_button = ttk.Button(fr_io,text="Пул-ап из файла games_import.txt", command=pull_up) #Кнопка массового импорта
choose_file_button = ttk.Button(fr_one_button,text="Обзор", command=choose_file) #Кнопка обзор
create_template_file_button = ttk.Button(fr_io,text="Создать шаблон games_import.txt", command=create_template_file) #Кнопка обзор

label_game_list = Label(fr_inbase,text="Номер, название, текущий вес", width=50) #Описание списка игр
list_game_list = Listbox(fr_inbase, bg="white", width=60, height= 20) #Список игр
list_game_list.insert(0,"Ожидание games.json")

label_game_imp = Label(fr_import,text="Список импортируемых игр", width=50) #Описание списка импорта
list_game_imp = Listbox(fr_import, bg="white" , width=100, height= 20) #Список импорта
list_game_imp.insert(0,"Ожидание games_import.txt")

fr_interact.pack(side='top', pady=25, anchor="center",fill=BOTH, expand=True) 
fr_list.pack(side='top',fill=BOTH, expand=True)
fr_input.pack(side='left', anchor='nw',fill=X, expand=True)
fr_io.pack(side='left', anchor='ne',fill=X, expand=True)
fr_labels.pack(side='left')
fr_field.pack(side='left')
fr_one_button.pack(side='left', anchor='n')
fr_inbase.pack(side='left',fill=BOTH, expand=True)
fr_import.pack(side='left',fill=BOTH, expand=True)

label_path.pack(side='top', anchor='w')
label_name.pack(side='top', anchor='w')
label_minweight.pack(side='top', anchor='w')

field_path.pack(side='top', anchor='w', pady=2)
field_name.pack(side='top', anchor='w', pady=2)
field_weight.pack(side='top', anchor='w', pady=2)

choose_file_button.pack(side='top', anchor='n')
add_game_button.pack(side='top', anchor='e')
wipe_out_button.pack(side='top', anchor='e')
delete_game_button.pack(side='top', anchor='e')
randomize_button.pack(side='top', anchor='e')
pull_up_button.pack(side='top', anchor='e')
create_template_file_button.pack(side='top', anchor='e')
label_fate.pack(side='top', anchor='e')

label_game_list.pack(side='top')
list_game_list.pack(side='top')
label_game_imp.pack(side='top')
list_game_imp.pack(side='top')

look_game()
root.mainloop()
