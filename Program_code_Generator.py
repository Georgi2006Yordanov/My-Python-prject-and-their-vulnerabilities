from string import Template

def generate_code():
    templates = {
        "1": {
            "name": "first exercise exam",
            "template": Template(
                "${name}=[]\nfor x in range(${range_number}):\n    num = int(input(f'{x}'))\n    ${name}.append(num)\n\nprint(f'Резултат: {${name}}')\n${new_list}=[]\nfor x in ${name}:\n    if x%2==0:\n        ${new_list}.append(x)\ncount = len(${new_list})\nprint(count)\n${sec_list}=[]\nfor x in ${name}:\n    if x>10:\n        ${sec_list}.append(x)"),
            "placeholders": ["name", "range_number"]
        }
    }

    selected = templates["1"]
    result = selected["template"].substitute(name="my_list", range_number="20",new_list="New_list",lenght="len",sec_list="Sec_list")
    print(result)
    save = input("\nИскате ли да го запишете във файл? (y/n): ")
    if save.lower() == 'y':
        filename = input("Име на файл (напр. code.py): ")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Файлът {filename} е създаден!")

generate_code()