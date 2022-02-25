import os
import sys
import xml.etree.ElementTree as ET

#to make state machines a little less redundant you can use these special chars to shorthand entire sets of input
charsets = {
    "\\d":['0','1','2','3','4','5','6','7','8','9'],
    "\\s":['\n','\t',' '],
    "\\c":['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
    "\\C":['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
}
def scannersrc():
    # Order of format strings 
    # final state id
    # final input id

    src = '''
#ifndef SCANNER_H
#define SCANNER_H
#include <iostream>
#include "token.hpp"
#include <vector>
using namespace std;
class Scanner {{
    private:
        int transition_table[{}][{}];
        int state;
        int numlines;
        vector<Token> tokens;
    public:
        Scanner();
        void init_statemachine();
        bool getToken(istream &input);
        void printTokens();
}};
void Scanner::init_statemachine(){{
    
}}
void Scanner::printTokens() {{
    for(auto t:tokens){{
        t.printToken();
    }}
}}

bool Scanner::getToken(istream &input) {

}
#endif
'''
    return src
def tokensrc():
    #order of format string content:
    # InputEnum
    # InputMap
    # inputTypestr
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
def build_tokentypstr(final_states):
    tokentypeStr = "const string TokenTypeStr[] = {{{}}};"
    innerstr = ""
    for i in range(len(final_states) -1):
        innerstr = innerstr + "\"{}\",".format(final_states[i])
    innerstr = innerstr + "\"{}\"".format(final_states[-1])
    return tokentypeStr.format(innerstr)

def build_token_enum(final_states):
    inenm= "enum TokenID {\n"
    for i in range(len(final_states) -1):
        inenm = inenm + "\t{}_tok,\n".format(final_states[i])
    inenm = inenm +"\t{}_tok\n".format(final_states[-1])
    inenm = inenm + "};"
    return inenm,"{}_tok".format(final_states[-1])

def build_input_enum(inputs):
    inenm= "enum InputID {\n"
    for i in range(len(inputs) -1):
        inenm = inenm + "\tINPUT_{},\n".format(i)
    inenm = inenm +"\tINPUT_{}\n".format(len(inputs)-1)
    inenm = inenm + "};"
    return inenm,"INPUT_{}".format(len(inputs)- 1)

def build_inputmap(inputs):
    inmap = "const map<int,InputID> inputMap = {\n"
    for i in range(len(inputs) -1):
        inmap = inmap + "\t{{\'{}\',INPUT_{}}},\n".format(inputs[i],i)
    inmap = inmap + "\t{{\'{}\',INPUT_{}}}\n".format(inputs[-1],len(inputs) -1 )
    inmap = inmap + "\n};"
    return inmap

def build_transition_table(states,inputs,transitions):
    table = {}
    for s in states:
        table[s] = {}
        for i in inputs:
            table[s][i] = {}
        for t in transitions:
            toState,fromState,event = t[0],t[1],t[2]
            table[fromState][event] = toState
    return table

def evaluate_statemachine(initial,final,table,inputStr):
    state=initial
    for c in inputStr:
        print(state)
        print(c) 
        state = table[state][c]
    if state in final:
            print("{} is final state".format(state))
    else:
        print("Error, {} string not accepted".format(inputStr))

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
    inputs = ["LAMBDA"]
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
        if onEvent is None and transitionTo is not None and transitionFrom is not None:
            transitions.append((state_table[transitionTo],state_table[transitionFrom],"LAMBDA"))
            continue
        if onEvent in charsets:
            inputs.append(charsets[onEvent])
        else:
            inputs.append(onEvent)
        transitions.append((state_table[transitionTo],state_table[transitionFrom],onEvent))
    print(transitions)
    print(build_transition_table(states,inputs,transitions))

    #scanner_src = scannersrc()
    #input_enum,last_input_id = build_input_enum(inputs)
    #input_map = build_inputmap(inputs)
    #toke_ts = build_tokentypstr(final_states)
    #token_enum,last_token_id = build_token_enum(final_states)
    #print(src.format(input_enum,input_map,toke_ts,token_enum))
    #print(last_input_id)
    #print(last_token_id)
    #print(scanner_src.format(last_input_id,last_token_id))
if __name__ == "__main__":
    main()