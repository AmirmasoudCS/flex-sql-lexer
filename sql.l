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

%x SINGLE_LINE_COMMENT

%x MULTI_LINE_COMMENT

identifier [a-zA-Z_][a-zA-Z0-9_]*
digit [0-9]

integer [0-9]+
float [0-9]+"."[0-9]+

double_quotation ["][^"]*["]
single_quotation ['][^']*[']

%%

{double_quotation} {
    printf("STRING LITERAL: %s ", yytext);
}

{single_quotation} {
    printf("STRING LITERAL: %s ", yytext);
}

{identifier} {
    if(is_keyword(yytext)) printf("KEYWORD: %s ", yytext);
    else printf("IDENTIFIER: %s ", yytext);
}

{integer} {
    printf("NUMBER: %s ", yytext);
}

{float} {
    printf("NUMBER: %s ", yytext);
}

"<>"|"="|"!="|"<"|">"|"<="|">=" {
    printf("COMPARISON OPERATOR: %s ", yytext);
}

"+"|"-"|"/"|"*"|"%" {
    printf("ARITHMETIC OPERATOR: %s ", yytext);
}

[;,().] {
    printf("PUNCT: %s ", yytext);
}

"--" {
    BEGIN(SINGLE_LINE_COMMENT);
}

<SINGLE_LINE_COMMENT>[^\n] {}

<SINGLE_LINE_COMMENT>[\n] {
    printf("SINGLE LINE COMMENT");
}

"/*" {
    BEGIN(MULTI_LINE_COMMENT);
}

<MULTI_LINE_COMMENT>[^*\n]+ {}

<MULTI_LINE_COMMENT>\n {}

<MULTI_LINE_COMMENT>"*" {}

<MULTI_LINE_COMMENT>"*/" {
    printf("MULTI LINE COMMENT");
    BEGIN(INITIAL);
}

%%

int yywrap(void) {return 1;}

int main(void){

    yylex();
    return 0;
}