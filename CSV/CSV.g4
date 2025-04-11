// CSV.g4
grammar CSV; // Nombre de la gramática: CSV

// Reglas del parser (estructura sintáctica)

// Un archivo CSV comienza con una fila de cabecera (header) seguida de una o más filas de datos
csvFile : header row+ ;

// La cabecera es una única fila que contiene los nombres de las columnas
header : row ;

// Una fila está compuesta por uno o más campos (field) separados por comas,
// y termina opcionalmente con un retorno de carro, seguido de un salto de línea
row : field (',' field)* '\r'? '\n' ;

// Un campo puede ser:
// - texto sin comillas (TEXT)
// - texto entre comillas (STRING)
// - un campo vacío (por ejemplo: ,,)
field
    : TEXT   # text   // Campo de texto simple
    | STRING # string // Campo de texto entre comillas dobles
    |        # empty  // Campo vacío
    ;

// Reglas léxicas (tokens)

// Un campo de tipo TEXT no puede contener comas, saltos de línea, retornos de carro ni comillas
TEXT : ~[,\n\r"]+ ;

// Un campo de tipo STRING está entre comillas dobles,
// puede contener comillas escapadas con doble comilla ("")
STRING : '"' ('""'|~'"')* '"' ;

// Espacios en blanco (como tabulaciones) se ignoran
WS : [ \t]+ -> skip ;