import sys
import json
from antlr4 import *
from JSONLexer import JSONLexer
from JSONParser import JSONParser
from JSONListener import JSONListener

class XMLEmitter(JSONListener):
    def __init__(self):
        self.xml_map = {}

    def getXML(self, ctx):
        return self.xml_map.get(ctx, '')

    def setXML(self, ctx, value):
        self.xml_map[ctx] = value

    def exitAtom(self, ctx):
        self.setXML(ctx, ctx.getText())

    def exitString(self, ctx):
        self.setXML(ctx, ctx.getText().strip('"'))

    def exitObjectValue(self, ctx):
        self.setXML(ctx, self.getXML(ctx.jsonObject()))

    def exitPair(self, ctx):
        tag = ctx.STRING().getText().strip('"')
        val = self.getXML(ctx.value())
        self.setXML(ctx, f"<{tag}>{val}</{tag}>\n")

    def exitAnObject(self, ctx):
        self.setXML(ctx, ''.join(self.getXML(p) for p in ctx.pair()))

    def exitEmptyObject(self, ctx):
        self.setXML(ctx, '')

    def exitArrayOfValues(self, ctx):
        body = ''.join(f"<element>{self.getXML(v)}</element>\n" for v in ctx.value())
        self.setXML(ctx, body)

    def exitEmptyArray(self, ctx):
        self.setXML(ctx, '')

    def exitJson(self, ctx):
        self.setXML(ctx, self.getXML(ctx.getChild(0)))

    def generate_xml(self, json_data):
        # Validamos el JSON antes de procesarlo
        parsed_json = self.validate_json(json_data)
        
        # Aquí iría el resto del procesamiento del JSON, luego lo convertimos a XML
        # Ejemplo: Convertir el JSON a un XML básico (esto puede ser más complejo según el caso)
        return self.convert_json_to_xml(parsed_json)

    def validate_json(self, json_data):
        try:
            parsed_json = json.loads(json_data)  # Convertimos la cadena JSON a un diccionario de Python
            return parsed_json
        except ValueError as e:
            print(f"Error al procesar el JSON: {e}")
            sys.exit(1)

    def convert_json_to_xml(self, parsed_json):
        # Aquí agregas el código para convertir el JSON a XML.
        # Simplemente un ejemplo, podrías usar un generador XML más sofisticado
        xml = "<root>\n"
        for key, value in parsed_json.items():
            xml += f"  <{key}>{value}</{key}>\n"
        xml += "</root>"
        return xml

    def save_xml_to_file(self, xml_data, file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(xml_data)

def main(argv):
    if len(argv) < 2:
        print("Por favor, proporciona el archivo JSON como argumento.")
        sys.exit(1)

    input_file = argv[1]

    # Leemos el archivo JSON
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = f.read()  # Leemos el archivo completo como una cadena
    except FileNotFoundError:
        print(f"El archivo {input_file} no se encuentra.")
        sys.exit(1)

    # Usamos InputStream para pasar el contenido como cadena
    input_stream = InputStream(input_data)

    lexer = JSONLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JSONParser(stream)
    tree = parser.json()

    xml_emitter = XMLEmitter()
    xml_output = xml_emitter.generate_xml(input_data)  # Le pasamos la cadena leída del archivo
    xml_emitter.save_xml_to_file(xml_output, 'output.xml')
    print("XML generado y guardado en 'output.xml'")

if __name__ == '__main__':
    main(sys.argv)
