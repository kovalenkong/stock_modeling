from enum import Enum


class TokenType(Enum):
    EOF = 'EOF'
    INVALID = 'INVALID'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'

    IDENT = 'IDENT'
    DELIMITER = 'DELIMITER'

    DIGIT = 'DIGIT'
    STRING = 'STRING'

    ADD = 'ADD'
    SUB = 'SUB'
    MUL = 'MUL'
    DIV = 'DIV'
    EXP = 'EXP'

    EQ = 'EQ'
    LT = 'LT'
    GT = 'GT'
    LTE = 'LTE'
    GTE = 'GTE'
