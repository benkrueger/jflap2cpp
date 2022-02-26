import os
import sys
import xml.etree.ElementTree as ET

#to make state machines a little less redundant you can use these special chars to shorthand entire sets of input
charsets = {
    #any number
    "\\d":['0','1','2','3','4','5','6','7','8','9'],
    #whitespace
    "\\s":['\\n','\\t',' '],
    #lowercase
    "\\c":['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
    "\\C":['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'],
    #alphabet
    "\\a":['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
}
def scannersrc():
    # Order of format strings 
    # table declaration string 
    # initial state id
    # transition table value initialization
    # newline identifier
    # accepting state conditional string
    # error state identifier
    src = '''
#ifndef SCANNER_H
#define SCANNER_H
#include <iostream>
#include "token.hpp"
#include <vector>
using namespace std;
int NumLines = 0;
int NumChars = 0;
class Scanner {{
    private:
        {}
        TokenID state;
        int numlines;
        vector<Token> tokens;
    public:
        Scanner();
        void init_statemachine();
        void getToken(istream &input);
        void printTokens();
}};
Scanner::Scanner(){{
    state = {};
    init_statemachine();
}}

void Scanner::init_statemachine(){{
{}
}}


void Scanner::printTokens() {{
    for(auto t:tokens){{
        t.printToken();
    }}
}}

void Scanner::getToken(istream &input) {{
    cout<<"State "<<TokenTypeStr[state]<<endl;
    char nextchar;
    string currentTokenContents = "";
    while (input.get(nextchar))
    {{
        InputID next_i = inputMap[nextchar];
        NumChars++;
        //Newline identifier
        if(next_i == NEWLINE){{
            NumLines++;
        }}
        cout<<"Input ID "<<next_i<<endl;
        state = transition_table[state][next_i];
        cout<<"State "<<state<<" "<<TokenTypeStr[state]<<endl;
        if(state != ERROR_tok){{
            currentTokenContents += nextchar;
        }}
        //Accepting state conditional
        if({}){{
            Token* t = new Token(state,currentTokenContents,NumLines,NumChars);
            t->printToken();
            currentTokenContents = "";
        }}
        //Error state exit
        if(state == {}){{
            return;
        }}
    }}
   
}}
#endif
'''
    return src
def build_scanner_src(tabledec,init_id,ttable_init,accept_cond):
    src = scannersrc()
    return src.format(tabledec,init_id,ttable_init,accept_cond,"ERROR_tok")
def tokensrc():
    #order of format string content:
    # InputEnum
    # InputMap
    # tokenEnum
    # tokentypeStr
    src = '''
#ifndef TOKEN_H
#define TOKEN_H
#include <vector>
#include <iostream>
#include <map>
using namespace std;
    
{}

{}

{}

{}

class Token {{
    private:
        TokenID tokenID;
        string tokenTypeStr;
        string tokenInstance;
        int line;
        int tbegin;
    public:
        Token(TokenID t_id, string typestr,int line, int tbegin);
        void printToken();

}};

Token::Token(TokenID t_id,string instanceStr ,int t_line, int t_begin){{
    tokenID= t_id;
    tokenTypeStr = TokenTypeStr[tokenID];
    tokenInstance = instanceStr;
    line = t_line;
    tbegin = t_begin;
}}

void Token::printToken(){{
    cout<<"Token "<<tokenInstance <<" Of Type: "<<tokenTypeStr << " detected At Line" <<line << "Column " << tbegin<<endl;
}}

#endif
'''
    return src
def build_accept_conditional(acceptingstates,token_lt_table):
    condfmt = "state == {}"
    condstr = ""
    if len(acceptingstates) == 1:
        return condfmt.format(token_lt_table[acceptingstates[0]])
    for s in range(len(acceptingstates) - 1):
        condstr = condstr+condfmt.format(token_lt_table[acceptingstates[s]])+"||"
    condstr = condstr + condfmt.format(token_lt_table[acceptingstates[-1]])
    return condstr
        
def build_token_src(inputenum,inputmap,inputtypstr,tokentypstr):
    src = tokensrc()
    return src.format(inputenum,inputmap,inputtypstr,tokentypstr)

def build_tokentypstr(states):
    tokentypeStr = "const string TokenTypeStr[] = {{{}}};"
    innerstr = ""
    for i in range(len(states) -1):
        innerstr = innerstr + "\"{}\",".format(states[i])
    innerstr = innerstr + "\"{}\"".format(states[-1])
    return tokentypeStr.format(innerstr)

def build_token_enum(states):
    enum_strs = []
    token_lt_table = {}
    enum_fmt = "{}_tok"
    inenm= "enum TokenID {\n"
    for i in range(len(states) -1):
        enistr = enum_fmt.format(states[i])
        token_lt_table[states[i]] = enistr
        enum_strs.append(enistr)
        inenm = inenm + "\t{},\n".format(enistr)
    enum_strs.append(enum_fmt.format(states[-1]))
    inenm = inenm +"\t{}_tok\n".format(states[-1])
    inenm = inenm + "};"
    return inenm,enum_strs,token_lt_table

def build_input_enum(inputs):
    input_identifiers = []
    in_lt_table = {}
    inenm= "enum InputID {\n"
    for i in range(len(inputs) -1):
        if(inputs[i] == "\\n"):
            input_ident =  "NEWLINE"
        else:
            input_ident = "INPUT_{}".format(i)
        in_lt_table[inputs[i]] = input_ident
        input_identifiers.append(input_ident)
        inenm = inenm + "\t{},\n".format(input_ident)
    
    if(inputs[i] == "\\n"):
        input_ident =  "NEWLINE"
    else:
        input_ident = "INPUT_{}".format(len(inputs)-1)
    in_lt_table[inputs[-1]] = input_ident
    inenm = inenm +"\t{}\n".format(input_ident)
    input_identifiers.append(input_ident)
    inenm = inenm + "};"
    return inenm,input_identifiers,in_lt_table

def build_inputmap(inputs,input_enumstrs):
    inmap = "map<int,InputID> inputMap = {\n"
    for i in range(len(inputs) -1):
        inmap = inmap + "\t{{\'{}\',{}}},\n".format(inputs[i],input_enumstrs[i])
    inmap = inmap + "\t{{\'{}\',{}}}\n".format(inputs[-1],input_enumstrs[-1])
    inmap = inmap + "\n};"
    return inmap
def build_table_declaration(states,inputs):
    return "TokenID transition_table[{}][{}];".format(states[-1],inputs[-1])

def build_transition_table_init(states,inputs,transitions,t_lt,in_lt):
    table = {}
    table_str = ""
    dec_string = "\ttransition_table[{}][{}] = {};"
    for s in states:
        for i in inputs:
            table_str= table_str +"{}\n".format(dec_string.format(s,i,states[-1]))
    for toState,fromState,onEvent in transitions:
        t_line = dec_string.format(t_lt[fromState],in_lt[onEvent],t_lt[toState])
        table_str = table_str + "{}\n".format(t_line)
    return table_str

def main():
    if(len(sys.argv) != 2):
        print("usage is jflap2cpp.py <.jff file>")
        exit(-1)
    inputpath = sys.argv[1]
    if(not os.path.exists(inputpath)):
        print("{} file does not exist. exiting.".format(sys.argv[1]))
        exit(-1)
    jfftree = ET.parse(inputpath)
    jffroot = jfftree.getroot()
    states = {}
    if(jffroot.find('type').text != 'fa'):
        print(jffroot.findall('type'))
        print("Input type must be a jflap finite automata. Exiting")
        exit(-1)
    states = []
    inputs = []
    state_table = {}
    transitions = []
    initial = ""
    final = {}
    final_states = []
    for state in jffroot.find('automaton').findall('state'):
        isInitial = state.find('initial') != None
        isFinal = state.find('final') != None
        stateName = state.attrib['name']
        stateId = state.attrib['id']
        states.append(stateName)
        state_table[stateId] = stateName
        if isInitial:
            initial = stateName
        if isFinal:
            final[stateName] = stateName
            final_states.append(stateName)

    for t in jffroot.find('automaton').findall('transition'):
        transitionTo = t.find('to').text
        transitionFrom = t.find('from').text
        onEvent = t.find('read').text
        if onEvent in charsets:
            for c in charsets[onEvent]:
                inputs.append(c)
                transitions.append((state_table[transitionTo],state_table[transitionFrom],c))
        else:
            inputs.append(onEvent)
            transitions.append((state_table[transitionTo],state_table[transitionFrom],onEvent))
    #last state defined in enumeration will be the error state

    states.append("ERROR")
    #print(transitions)
    

    #scanner_src = scannersrc()
    input_enum,input_enum_strs,input_lt_table = build_input_enum(inputs)
    token_enum,token_enum_strs,token_lt_table = build_token_enum(states)
    input_map = build_inputmap(inputs,input_enum_strs)
    toke_ts = build_tokentypstr(token_enum_strs)

    accept_condition = build_accept_conditional(final_states,token_lt_table)

    tabledec = build_table_declaration(token_enum_strs,input_enum_strs)
    ttable_init = build_transition_table_init(token_enum_strs,input_enum_strs,transitions,token_lt_table,input_lt_table)

    token_src = build_token_src(input_enum,input_map,token_enum,toke_ts)
    scanner_src = build_scanner_src(tabledec,token_enum_strs[0],ttable_init,accept_condition)
    with open("token.hpp","x") as f:
        f.write(token_src)
    with open("scanner.hpp","x") as f:
        f.write(scanner_src)

if __name__ == "__main__":
    main()