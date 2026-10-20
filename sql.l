%{
    #include <stdio.h>    
    #include <string.h>
    char* keywords[] = { "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "TABLE", "VALUES", "AND", "OR", "NOT", "ORDER", "BY", "GROUP", "HAVING", "JOIN", "ON", "AS", "NULL", "INTO", "SET", "DISTINCT" };
    int keyword_count = sizeof(keywords) / sizeof(keywords[0]);

%}

identifier [a-zA-Z_][a-zA-Z0-9_]*

%%

{identifier}                                    { printf("IDENTIFIER"); }

%%

int yywrap(void) {return 1;}

int main(void){

    yylex();
    return 0;
}