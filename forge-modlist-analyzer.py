import os
import zipfile
import re
import json

def extract_mods_toml(jar_file):
    with zipfile.ZipFile(jar_file, 'r') as zip_ref:
        if 'META-INF/mods.toml' in zip_ref.namelist():
            with zip_ref.open('META-INF/mods.toml') as toml_file:
                return toml_file.read().decode()
        else:
            return None

def extract_display_name(mods_toml_content, jar_filename):
    match = re.search(r'\[\[mods\]\](.*?)displayName\s*=\s*"([^"]+)"', mods_toml_content, re.DOTALL)
    return match.group(2) if match else "Display name not found"


def extract_side_for_dependencies(mods_toml_content):
    sides = set()
    dependencies = re.findall(r'\[\[dependencies\.[^\]]+\]\](.*?)(?=\[\[|$)', mods_toml_content, re.DOTALL)
    for dependency_block in dependencies:
        if re.search(r'modId\s*=\s*"(minecraft|forge)"', dependency_block):
            side_match = re.search(r'side\s*=\s*"([^"]+)"', dependency_block)
            if side_match:
                sides.add(side_match.group(1))
    return ', '.join(sides)

def delete_jars_by_side(directory, chosen_side):
    for filename in os.listdir(directory):
        if filename.endswith(".jar"):
            mods_toml_content = extract_mods_toml(os.path.join(directory, filename))
            if mods_toml_content:
                side = extract_side_for_dependencies(mods_toml_content)
                if not side:
                    side = "UNKNOWN"
                if side.upper() == chosen_side:
                    os.remove(os.path.join(directory, filename))
                    print(f"Deleted {filename}")


def load_existing_data(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            return json.load(json_file)
    return []

def main():
    directory = input("Informe o diretório: ")
    json_output_path = os.path.join(directory, 'mods.json')

    # Apagar o arquivo mods.json existente, se houver
    if os.path.exists(json_output_path):
        os.remove(json_output_path)

    json_data = []

    for filename in os.listdir(directory):
        if filename.endswith(".jar"):
            mods_toml_content = extract_mods_toml(os.path.join(directory, filename))
            if mods_toml_content:
                display_name = extract_display_name(mods_toml_content, filename)
                side = extract_side_for_dependencies(mods_toml_content)
                if not side:
                    side = "UNKNOWN"
                json_data.append({"name": display_name, "side": side, "filename": filename})

    with open(json_output_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON data saved to {json_output_path}")

    # Perguntar ao usuário sobre a exclusão de arquivos
    print("Você deseja apagar quais mods?\n"
          "1 - CLIENTSIDE\n"
          "2 - SERVERSIDE\n"
          "3 - BOTH\n"
          "4 - UNKNOWN\n"
          "5 - Nenhum (padrão)")
    choice = input("Escolha uma opção: ") or "5"

    if choice == "1":
        delete_jars_by_side(directory, "CLIENT")
    elif choice == "2":
        delete_jars_by_side(directory, "SERVER")
    elif choice == "3":
        delete_jars_by_side(directory, "BOTH")
    elif choice == "4":
        delete_jars_by_side(directory, "UNKNOWN")

if __name__ == "__main__":
    main()
