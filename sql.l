%{
    #include <stdio.h>    
    #include <string.h>
    char* keywords[] = { "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "TABLE", "VALUES", "AND", "OR", "NOT", "ORDER", "BY", "GROUP", "HAVING", "JOIN", "ON", "AS", "NULL", "INTO", "SET", "DISTINCT" };
    int keyword_count = sizeof(keywords) / sizeof(keywords[0]);
    int is_keyword(char* word){
        for(int i = 0; i < keyword_count; i++){
            if(strcmp(keywords[i], word) == 0) return 1;
        }
        return 0;
    }

%}

identifier [a-zA-Z_][a-zA-Z0-9_]*
digit [0-9]

integer [0-9]+
float [0-9]+"."[0-9]+

double_quotation ["][^"]*["]
single_quotation ['][^']*[']

%%

{double_quotation} {
    printf("STRING LITERAL: %s", yytext);
}

{single_quotation} {
    printf("STRING LITERAL: %s", yytext);
}

{identifier} {
    if(is_keyword(yytext)) printf("KEYWORD: %s ", yytext);
    else printf("IDENTIFIER: %s ", yytext);
}

{integer} {
    printf("NUMBER: %s", yytext);
}

{float} {
    printf("NUMBER: %s", yytext);
}

"<>"|"="|"!="|"<"|">"|"<="|">=" {
    printf("COMPARISON OPERATOR: %s", yytext);
}

"+"|"-"|"/"|"*"|"%" {
    printf("ARITHMETIC OPERATOR: %s", yytext);
}

%%

int yywrap(void) {return 1;}

int main(void){

    yylex();
    return 0;
}