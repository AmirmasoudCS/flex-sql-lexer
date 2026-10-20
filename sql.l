%{
    #include <stdio.h>    
%}

identifier [a-zA-Z_][a-zA-Z0-9_]*

%%

{identifier}                                    { printf("IDENTIFIER";) }

%%

yywrap(void) {return 1;}

int main(void){

    yylex();
    return 0;
}