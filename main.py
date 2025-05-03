import re

archivo = open("grammar.txt","r",encoding="utf-8")
sent = archivo.readlines()
variables = []
terminales = []
start = [sent[0][0]]
for i in range(len(sent)):
    sent[i] = re.sub('[^\\w]', '', sent[i])
    sent[i] = re.sub(r'\s+', '', sent[i])


for i in sent:
    for j in i:
        if j in ["ε", '""', "''", '"']: # epsilon
            if not ('ε' in terminales):
                terminales.append('ε')
        elif j == j.upper(): # Variables no terminales
            if not(j in variables) and not(j in start):
                variables.append(j)
        else: # Terminales
            if not(j in terminales):
                terminales.append(j)

grammar = {}
tabla = {}

# Crear matriz de parsing
for i in start + variables:
    tabla[i]={}
    for j in terminales:
        tabla[i][j]=[]
    tabla[i]["$"]=[]

# la variable inicial
for i in start:
    grammar[i]={"tipo":"I","first":[],"follow":["$"]}

# los terminales (su first siempre es sí mismo)
for j in terminales:
    grammar[j]={"tipo":"T","first":[j]}

# las variables no terminales
for j in variables:
    grammar[j]={"tipo":"V","first":[],"follow":[]}

reglas ={}

# cabecera para las reglas
for i in range(len(sent)):
    reglas['regla'+str(i+1)] = {}

# parte izquierda (solo la primera letra)
for i, j in enumerate(reglas.keys()):
    reglas[j]['Izq'] = sent[i][0]

# parte derecha (all the rest) (todo: varaibles de longitud 2)
for i, j in enumerate(reglas.keys()):
    reglas[j]['Der'] = list(sent[i][1:])

################################### FIRST ###################################
def first(symbol):
    if grammar[symbol]['first']:
        return grammar[symbol]['first']
    else:
        first_set = set()
        for _, r in reglas.items():
            if r['Izq'] == symbol:
                derivada = r['Der']
                i = 0
                while i < len(derivada):
                    temp_first = set(first(derivada[i]))
                    first_set |= temp_first - {'ε'} # first_set U (temp_first \ ε)
                    if 'ε' in temp_first:
                        i += 1
                    else:
                        break
                else:
                    first_set.add('ε') # si no hay break
        return list(first_set)


for i in grammar.keys():
    grammar[i]['first'] = first(i)

################################### FOLLOWS ###################################
dependencia = {key: set() for key in variables + start}
for _, r in reglas.items():
    der = r['Der']
    i = len(der) - 1
    while i >= 0:
        A = der[i]
        if grammar[A]['tipo'] == 'T':
            i -= 1
            continue
        follow_set = set()
        j = i+1
        while j < len(der):
            gamma = der[j]
            temp_follow = set(grammar[gamma]['first'])
            follow_set |= temp_follow - {'ε'}
            if 'ε' in temp_follow:
                j += 1
            else:
                break
        else:
            dependencia[A].add(r['Izq'])
        grammar[A]['follow'] = list(set(grammar[A]['follow']) | follow_set)
        i -= 1

#funcion recursiva para los includes
def includes(symbol, visited=None):
    if visited is None:
        visited = set()
    if symbol in visited:
        return set(grammar[symbol]['follow'])
    visited.add(symbol)

    while dependencia[symbol]:
        i = next(iter(dependencia[symbol]))
        dependencia[symbol].discard(i)
        follow_incl = includes(i, visited)
        grammar[symbol]['follow'] = list(set(grammar[symbol]['follow']) | follow_incl)
    return set(grammar[symbol]['follow'])

for A in dependencia.keys():
    includes(A)

################################### TABLITA ###################################
for i in reglas.keys():
    alpha = grammar[reglas[i]['Der'][0]]
    for j in alpha['first']:
        if j == 'ε':
            for k in grammar[reglas[i]['Izq']]['follow']:
                tabla[reglas[i]['Izq'][0]][k].append(reglas[i])
        else:
            tabla[reglas[i]['Izq'][0]][j].append(reglas[i])

################################ PRINT ###################################33
print("TABLA")
print("\n")
print(f"{'Símbolo':<10} {'Tipo':<8} {'FIRST':<20} {'FOLLOW':<20}")
print("-" * 60)

for simbolo, datos in grammar.items():
    tipo = datos['tipo']
    first = ", ".join(datos.get('first', []))
    follow = ", ".join(datos.get('follow', [])) if 'follow' in datos else "-"
    print(f"{simbolo:<10} {tipo:<8} {first:<20} {follow:<20}")

##################
print("\n")
print("\n")
print("MATRIZ")

terminales.append("$")
if 'ε' in terminales:
    terminales.remove('ε')
print(f"{'':20}", end="")
for t in terminales:
    print(f"{t:<20}", end="")
print()

print("-" * (12 + 20 * len(terminales)))
for no_terminal, reglas in tabla.items():
    print(f"{no_terminal:20}", end="")
    for t in terminales:
        producciones = reglas[t]
        if producciones:
            produccion_strs = ["{} → {}".format(p["Izq"], " ".join(p["Der"])) for p in producciones]
            print(f"{' / '.join(produccion_strs):<20}", end="")
        else:
            print(f"{'-':<20}", end="")
    print()


###########
code = open("input.txt","r")
sent = code.readlines()

cadena = sent[0]+"$"
pila = start

##################
print("\n")
print("\n")
print("ANALISIS")

while True:
    if (len(cadena)==1) and (len(pila)==0):
        print("CADENA VALIDA")
        break
    pila_str = ' '.join(pila)
    entrada_str = ''.join(cadena)
    pila_fin = pila[-1]
    cad_ini = cadena[0]
    if grammar[pila_fin]["tipo"] != 'T' and tabla[pila_fin][cad_ini]:
        produccion = tabla[pila_fin][cad_ini][0]
        produccion_str = f"{produccion['Izq']} → {' '.join(produccion['Der'])}"
        print(f"{pila_str:<30} {entrada_str:<30} {'Regla: ' + produccion_str}")
        a = pila_fin
        pila.pop()
        if produccion['Der'][0] != 'ε':
            pila+=tabla[a][cad_ini][0]['Der'][::-1]
    elif grammar[pila_fin]["tipo"]=="T":
        if pila_fin == cad_ini:
            print(f"{pila_str:<30} {entrada_str:<30} {'Match: ' + cad_ini}")
            pila.pop()
            cadena = cadena[1:]
    else:
        print("Cadena no valida")
        break
