#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import json
import os
from fileinput import close
import zipfile



class JsonInoConvertor( object ) :

    instructions = dict()
    booleanTests = dict()
    setupFunctionStr = str()
    loopFunctionStr = str()
    functionNameStr = str()
    nb_block = 0
    #nbBlockStr = str()
    pins = dict()
    var = []
    indentation = str()
    incr = "j"
    typeArduino = 0
    sleep_var = False

    def __init__( self, indentation = "   ", typeArduino = 0 ) :

        super( JsonInoConvertor, self ).__init__()
        
        self.instructions = {
            
            'A4S (Arduino For Scratch).digitalWrite' : self.digitalWriteConvertion,
            'doIf' : self.doIfConvertion,
            'doIfElse' : self.doIfElseConvertion,
            'readVariable': self.doReadVariable,
            'setVar:to:' : self.ChangeVar,
            'changeVar:by:' : self.ChangeVar,
            'A4S (Arduino For Scratch).analogRead' : self.AnalogReadingConvertion,
            'A4S (Arduino For Scratch).analogWrite' : self.AnalogWriteConvertion,
            '*' : self.OpertationConvertion,
            '+' : self.OpertationConvertion,
            '-' : self.OpertationConvertion,
            '/' : self.OpertationConvertion,
            'doRepeat' : self.doRepeatConvertion,
            'doUntil' : self.doUntilConvertion,
            'wait:elapsed:from:' : self.doWaitConvertion,
            'doWaitUntil' : self.doWaitUntilConvertion,

        }

        self.booleanTests = {
            
            '&' : self.reportAndConvertion,
            '|' : self.reportOrConvertion,
            '=' : self.reportEqualConvertion,
            'A4S (Arduino For Scratch).digitalRead' : self.reportDigitalReadingConvertion,
            'low' : self.reportFalseConvertion,
            'high' : self.reportTrueConvertion,
            'not' : self.reportNot,
            '<' : self.reportCompareConvertion,
            '>' : self.reportCompareConvertion,
        }
        
        self.functionNameStr = "void consumer"
        #self.nbBlockStr = "#define MAX_THREAD_LIST "
        self.setupFunctionStr = "void Setup() {\n"
        #self.loopFunctionStr = "void consumer1() {\n  while(1){\n"
        #Voir pour incrémentation des consumer : créer à chaque fois l'objet loopfunction différent pour chaque groupe de blocs
        
        self.indentation = indentation
        self.typeArduino = typeArduino

    
    def doIfConvertion( self, block, i ) :
        self.loopFunctionStr += i + "if ( "
        self.booleanTests[block[1][0]](block[1])
        #self.convertBooleanTestBlock( block[0] )
        self.loopFunctionStr += " ) {\n"
        self.convertScript(block[2],i)
        #self.convertScript( block[1], i + self.indentation )
        self.loopFunctionStr += i + "}\n"
        
    def doUntilConvertion( self, block, i ) :
        #print block
        self.loopFunctionStr += i + "while ( "
        self.booleanTests[block[1][0]](block[1])
        self.loopFunctionStr += " ) {\n"
        self.loopFunctionStr += i + self.indentation + "Printf(\"0 x DEADBEEF\\n\");\n"
        self.convertScript(block[2],i )
        #self.convertScript( block[1], i + self.indentation )
        if (not (self.sleep_var)):
            self.loopFunctionStr += i + self.indentation + "ARTK_yield();\n"
        self.sleep_var = False;
        self.loopFunctionStr += i+"}\n"
        
    def doWaitConvertion( self, block, i ) :
        x = float(block[1]) * 100
        self.loopFunctionStr += i + "ARTK_Sleep("
        self.loopFunctionStr += str(x)
        self.loopFunctionStr += ");\n"
        self.sleep_var = True;
        
    def doWaitUntilConvertion( self, block, i ) :
        #print "lolilol"
        #print block
        self.loopFunctionStr += i + "while ( "
        self.booleanTests[block[1][0]](block[1])
        #self.convertBooleanTestBlock( block[0] )
        self.loopFunctionStr += " ) {\n"
        self.loopFunctionStr += i + self.indentation + "Printf(\"0 x DEADBEEF\\n\");\n"
        self.loopFunctionStr += i + self.indentation + "ARTK_Sleep(50);\n"
        self.loopFunctionStr += i + "}\n"
    
    def doRepeatConvertion(self, block, i):
        #à revoir : tester si non à l'intérieur d'un autre dorepeat (changer la variable d'incrémentation)
        this_incr = self.incr
        self.incr += "j"
        self.loopFunctionStr += i + "for (int "+this_incr+"=0; "+this_incr+"< "
        
        self.loopFunctionStr += str(block[1])
        self.loopFunctionStr += "; "+this_incr+"++) {\n"
        self.convertScript(block[2],i + self.indentation)
        #self.convertScript( block[1], i + self.indentation )
        if (not (self.sleep_var)):
            self.loopFunctionStr += i + i + "ARTK_yield();\n"
        self.sleep_var = False;
        self.loopFunctionStr += i+"}\n"
    
    def digitalWriteConvertion( self, block, i ) :

        pin = block[1]
        if not ( pin in self.pins ) :
            self.pins[pin] = 'OUTPUT'
            self.setupFunctionStr += self.indentation + "pinMode( " + str(pin) + ", OUTPUT );\n"

        elif self.pins[pin] != 'OUTPUT' :
            print "Warning reportDigitalReadingConvertion : pin", pin, "already use in", pins[pin], "status"
        
        self.loopFunctionStr += i + "digitalWrite( " + str(pin) + ", "
        self.booleanTests[block[2]](block[2])
        #self.convertBooleanTestBlock( block[1] )
        self.loopFunctionStr += " );\n"
        
    def AnalogWriteConvertion(self,block,i):
        pin = block[1]
        if not ( pin in self.pins ) :
            self.pins[pin] = 'OUTPUT'
            self.setupFunctionStr += self.indentation + "pinMode( " + str(pin) + ", OUTPUT );\n"

        elif self.pins[pin] != 'OUTPUT' :
            print "Warning reportDigitalReadingConvertion : pin", pin, "already use in", pins[pin], "status"
        
        self.loopFunctionStr += i + "AnalogWrite( " + str(pin) + ", "
        if ((not isinstance(block[1], basestring)) &  (not isinstance(block[1], int))):
            self.instructions[block[1][0]](block[1],"")
        else :
            #print block[1]
            self.loopFunctionStr += str(block[1])
        self.loopFunctionStr += " );\n"
        
    def doIfElseConvertion( self, block, i ) :
        
        self.loopFunctionStr += "if ( "
        self.booleanTests[block[1][0]](block[1])
        self.loopFunctionStr += " ) {\n"
        self.convertScript(block[2],i + self.indentation)
        #self.instructions[block[2][0]](block[2],i)
        self.loopFunctionStr += i + "}\n" + i + "else {\n"
        self.convertScript(block[3],i + self.indentation)
        #self.instructions[block[3][0]](block[3],i)
        self.loopFunctionStr += i + "}\n"

    def reportDigitalReadingConvertion( self, block ) :

        pin = block[1]
        if not ( pin in self.pins ) :
            self.pins[pin] = 'INPUT'
            self.setupFunctionStr += self.indentation + "pinMode( " + str(pin) + ", INPUT );\n"

        elif self.pins[pin] != 'INPUT' :
            print "Warning reportDigitalReadingConvertion : pin", pin, "already use in", pins[pin], "status"
        
        #print "digitalRead( "
        self.loopFunctionStr += "digitalRead( "
        #print pin
        self.loopFunctionStr += str(pin)
        #print " )"
        self.loopFunctionStr += " )"
        
    def AnalogReadingConvertion( self, block, i ) :
        
        pin = block[1]

        self.loopFunctionStr += i+"analogRead( "
        self.loopFunctionStr += str(pin)
        self.loopFunctionStr += " )"
            
    def reportAndConvertion( self, block ) :
        #print "( "
        self.loopFunctionStr += "( "
        self.booleanTests[block[1][0]](block[1])
        #self.convertBooleanTestBlock( block[0] )
        #print " ) && ( "
        self.loopFunctionStr += " ) && ( "
        self.booleanTests[block[2][0]](block[2])
        
        self.loopFunctionStr += " )"

    
    def reportCompareConvertion(self, block):
        #print block
        if (not isinstance(block[1], basestring)):
            self.instructions[block[1][0]](block[1],"")
        else :
            #print block[1]
            self.loopFunctionStr += str(block[1])
        
        #print " == "
        self.loopFunctionStr += block[0]
        
        if (not isinstance(block[2], basestring)):
            self.instructions[block[2][0]](block[2],"")
        else :
            #print block[2]
            self.loopFunctionStr += str(block[2])
            
    def OpertationConvertion(self,block,i):
        #print block
        if ((not isinstance(block[1], basestring)) &  (not isinstance(block[1], int))):
            self.instructions[block[1][0]](block[1],"")
        else :
            #print block[1]
            self.loopFunctionStr += str(block[1])
        
        #print " == "
        self.loopFunctionStr += block[0]
        
        if ((not isinstance(block[2], basestring)) &  (not isinstance(block[2], int))):
            self.instructions[block[2][0]](block[2],"")
        else :
            #print block[2]
            self.loopFunctionStr += str(block[2])
    
    def reportEqualConvertion(self,block):
        #print block
        if (not isinstance(block[1], basestring) &  (not isinstance(block[1], int))):
            self.instructions[block[1][0]](block[1],"")
        else :
            #print block[1]
            self.loopFunctionStr += str(block[1])
        
        #print " == "
        self.loopFunctionStr += " == "
        
        if (not isinstance(block[2], basestring) & (not isinstance(block[2], int))):
            self.instructions[block[2][0]](block[2],"")
        else :
            #print block[2]
            self.loopFunctionStr += str(block[2])
            
    def ChangeVar(self, block, i):
        #print block
        if (not (block[1] in self.var)):
            self.var.append(block[1])
            self.setupFunctionStr += self.indentation + "int "+block[1]+";\n"
        
        #print block[1]
        #print "="
        self.loopFunctionStr += i + str(block[1])
        self.loopFunctionStr += "="
        
        
        if ( (not isinstance(block[2], basestring)) & (not isinstance(block[2], int))):
            #print "c'est un bloc"
            #print block[2]
            self.instructions[block[2][0]](block[2],"")
            self.loopFunctionStr += ";\n"
        else :
            #print "c'est pas un bloc"
            #print block[2]
            self.loopFunctionStr += str(block[2])
            self.loopFunctionStr += ";\n"
        
    def reportOrConvertion(self, block):
        self.loopFunctionStr += "( "
        self.booleanTests[block[1][0]](block[1])
        #self.convertBooleanTestBlock( block[0] )
        #print " ) && ( "
        self.loopFunctionStr += " ) || ( "
        self.booleanTests[block[2][0]](block[2])
        
        self.loopFunctionStr += " )"
    
    def reportNot(self,block):
        self.loopFunctionStr += "! ("
        if block[1][0] in  self.instructions:
            #print "c'est une instruction :"
            #print element
            self.instructions[block[1][0]](block[1],"")
        elif block[1][0] in  self.booleanTests:
            #print "c'est un test booleen :"
            #print element
            self.booleanTests[block[1][0]](block[1])
        else :
            print "Warning script : bloc", element[0], "non géré..."
        self.loopFunctionStr += ")"
    
    def doReadVariable(self, block,i):
        #print block
        self.loopFunctionStr += i + block[1]
        
    def reportFalseConvertion( self, block ):
        
        self.loopFunctionStr += "LOW"

    def reportTrueConvertion( self, block ):
        
        self.loopFunctionStr += "HIGH"

    def convertSpriteScripts( self, fileINName, fileOUTName ) :
    
        fileOUT = open( fileOUTName, "w" )
        
        archive = zipfile.ZipFile(fileINName, 'r')
        json_data = archive.read('project.json')
        
        #json_data=open(jsondata)

        data = json.loads(json_data)
        for threadScript in data['children'][0]['scripts'] :
            print threadScript[2]
            self.convertThreadScript( threadScript[2], self.indentation )
        
        self.setupFunctionStr += self.indentation + "ARTK_SetOptions(" + str(self.typeArduino) + ", 10) ;\n"
        for i in range(1,self.nb_block + 1):
            self.setupFunctionStr += self.indentation + "ARTK_CreateTask(consumer" + str(i) + ");\n"
        self.setupFunctionStr += "}\n"
        #self.loopFunctionStr += "ARTK_Yield();\n}\n}\n"
        
        print "#include <ARTK.h>\n"+ self.loopFunctionStr + self.setupFunctionStr
        #fileOUT.write( self.nbBlockStr + str(self.nb_block) + "\n\n")
        fileOUT.write("#include <ARTK.h>\n")
        fileOUT.write( self.loopFunctionStr )
        fileOUT.write( self.setupFunctionStr )
        fileOUT.close()   
        #print data

        #json_data.close()
        #print self.loopFunctionStr
        
    def convertThreadScript( self, threadScript, i ) :
        #print "on m'appelle"
        #print threadScript
        if (len(threadScript)>= 2):
            receiveGoBlock = threadScript[0]
            doForeverBlock = threadScript[1]
            #print receiveGoBlock[0]
            #print doForeverBlock[1]
            if receiveGoBlock[0] != "whenGreenFlag" or ( not receiveGoBlock[0] ) :
                print "Warning convertThreadScript : expected block receiveGo"

            elif doForeverBlock[0] != 'doForever' or ( not doForeverBlock[0] ):
                print "Warning convertThreadScript : expected block doForever"

            else :
                self.nb_block = self.nb_block + 1
                self.loopFunctionStr += "void consumer" + str(self.nb_block) + "() {\n"
                self.loopFunctionStr += i + "while(1){\n"
                self.loopFunctionStr += i+i +"Printf(\"0 x DEADBEEF\\n\");\n"
                self.convertScript( doForeverBlock[1], i )
                if (not (self.sleep_var)):
                    self.loopFunctionStr += i + self.indentation + "ARTK_Yield();\n"

                self.sleep_var = False;
                self.loopFunctionStr += i + "}\n}\n"

    def convertScript( self, script, i ) :
        for element in script :
            #print element
            if element[0] in  self.instructions:
                #print "c'est une instruction :"
                #print element
                self.instructions[element[0]](element,i + self.indentation)
            elif element[0] in  self.booleanTests:
                #print "c'est un test booleen :"
                #print element
                self.booleanTests[element[0]](element)
            else :
                print "Warning script : bloc", element[0], "non géré..."
                
def ExtractionDuNom(lien):
    ind = 0
    taille = len(lien)-1
    nomFile = ""
    
    while taille > 0:
        if lien[taille] == "/":          
            break
        taille = taille-1    
        
    while taille < len(lien)-5:
        nomFile = nomFile + lien[taille+1] 
        taille = taille+1
        print (taille)
        
    return nomFile  

def main() :

    args = sys.argv[1:]
    argc = len( args )

    #if argc < 1 :
    #    print "Use error :", sys.argv[0], "fileIN.xml [fileOUT.ino]"
     #   exit( 1 )


    #fileINName = args[0]
    #fileOUTName = args[0] + ".ino"

    #if argc > 1 :
     #   fileOUTName = args[1]
    fileName = ExtractionDuNom(sys.argv[1].decode('utf8'))
    convertor = JsonInoConvertor(typeArduino=sys.argv[2])
    #controls_scratch/controls.sb2
    #print ExtractionDuNom(sys.argv[1].decode('utf8'))
    if not os.path.exists("sketch/" + fileName):
        os.makedirs("sketch/" + fileName)
    
    convertor.convertSpriteScripts( sys.argv[1].decode('utf8'), "sketch/" + fileName + "/" + fileName + ".ino" )
    os.chdir("sketch")
    os.chdir(fileName)
    os.startfile(fileName + ".ino")
    #convertor.convertSpriteScripts( "controls.sb2", "test/testcontrols.ino" )



if __name__ == '__main__':
    main()