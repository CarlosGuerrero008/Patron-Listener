grammar JSON;

json        : jsonObject | array ;
jsonObject  : '{' pair (',' pair)* '}'     #AnObject
            | '{' '}'                      #EmptyObject
            ;
array       : '[' value (',' value)* ']'   #ArrayOfValues
            | '[' ']'                      #EmptyArray
            ;

pair        : STRING ':' value ;
value       : STRING      #String
            | NUMBER      #Atom
            | jsonObject  #ObjectValue
            | array       #ArrayValue
            | 'true'      #Atom
            | 'false'     #Atom
            | 'null'      #Atom
            ;

STRING : '"' (ESC | ~["\\])* '"' ;
fragment ESC : '\\' ["\\/bfnrt] ;
NUMBER : '-'? INT ('.' [0-9] +)? EXP? ;
fragment INT : '0' | [1-9] [0-9]* ;
fragment EXP : [Ee] [+-]? [0-9]+ ;
WS : [ \t\n\r]+ -> skip ;