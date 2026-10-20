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

%%

{identifier} {
    if(is_keyword(yytext)) printf("KEYWORD: %s", yytext);
    printf("IDENTIFIER: %s", yytext);
}

%%

int yywrap(void) {return 1;}

int main(void){

    yylex();
    return 0;
}