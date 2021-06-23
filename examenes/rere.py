import re


string = "pregunta-10-opcion-4"

ultima_pregunta = int(re.search(r'(\d+)', string).group(1))
print(ultima_pregunta)
