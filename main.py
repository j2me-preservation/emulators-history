import subprocess

all_dates = set()
lineages = {}
derivations = []

with open("history.txt", "rt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("$"):
            lineages[line[1:]] = {}
            lin = lineages[line[1:]]
            continue
        elif line.startswith("DERIVE "):
            to, from_ = line[7:].split("~")
            derivations.append((from_, to))
            continue

        space = line.find(" ")

        date = line[:space]
        label = line[space + 1:]

        # print(date, ":", label)

        all_dates.add(date)
        lin[date] = label

# for y in range(2001, 2022):
#     all_dates.add(f"{y}-01-01")

with open("history.dot", "wt") as f:
    name_map = {}

    f.write("""
    digraph unix {
        rankdir=BT;

        {
            node [shape=plaintext,fontsize=20,fontname="Roboto"];
""")

    for date in sorted(all_dates):
        if date != "today":
            f.write(f'        "{date}" ->\n')

    f.write('''        "today";

        }
''')

    f.write("""
        {
            node [shape=box,style=filled,color=lightblue,fontsize=20,fontname="Roboto"];
""")

    for lineage, contents in lineages.items():
        defs = []
        # entries = []
        joins = []
        invis_joins = []
        prev = None
        prev_visible = False
        last_visible = None

        dc = 0

        for date in sorted(all_dates):
            name = lineage + str(dc); dc += 1

            if date in contents:
                defs.append(f'{name} [label="{contents[date]}"]')
                name_map[contents[date]] = name
                # entries.append(f'"{label}"')

                visible = True
            else:
                visible = False

            if last_visible is not None and visible:
                joins.append((last_visible, name))

            prev = name
            prev_visible = visible
            if visible:
                last_visible = name

        f.write("\n".join(defs))
        for a, b in joins:
            f.write(f"{a} -> {b};\n")
        f.write("\n")

    for from_, to in derivations:
        a = name_map[from_]
        b = name_map[to]
        f.write(f"{a} -> {b}[style=dashed, constraint=false];\n")

    f.write(' }\n')
    for dc, date in enumerate(sorted(all_dates)):
        f.write('{ rank=same; "' + date + '"')

        for lineage, contents in lineages.items():
            if date in contents:
                name = lineage + str(dc)
                f.write(f' "{name}"')
        f.write(' }\n')

    f.write('''
    //    }
    }
''')

subprocess.check_call("dot -Tpng -o history.png history.dot".split(" "))
