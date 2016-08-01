#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author : Jean-Philippe Beaudet@s3r3nity

Server to run python command in threads

Wrapper to start any new comand in python threads
​
"""

import argparse
import zmq
import thread
import time
import datetime
import subprocess
from subprocess import Popen, PIPE
import threading
import Queue
import ConfigParser
import traceback

# load configs
Config = ConfigParser.ConfigParser()
Config.read("config.ini")
section = Config.sections()
_HOST=Config.get("Default",'Host')
_PORT=Config.get("Default",'Port')
_INIT= []
for (each_key, each_val) in Config.items("Init"):
    _INIT.append([ each_key, each_val])
    print(str(timenow())+' ZeroPh() CONFIG | Init key : '+str(each_key)+ ' val:' + str(each_val))

class ZeroPh(object):
    
    def __init__(self, verbose):
        self.verbose = verbose
        self.host=_HOST
        self.port=_PORT
        self.init()
        
    def init(self):
        """
        Start the base services described in config.ini in [Init] section
        
        If nothing then continue on listening. 
        if key is a number then wait the number of seconds
        @params: {file} config.ini
        @rtype:{}
        
        """
        if len(_INIT) >0:
            return self.parse_commands(_INIT)
        else:
            pass
        
        
    def run_server(self):
        """
        Start the server. Listen for cmd call
        
        """
        # server
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(self.host+':'+self.port)
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | socket now listen on port: ' + str(self.port))
            
        while True:
            msg = socket.recv()
            if isinstance(msg, str):
                # Create two threads as follows
                q1 = enthread(cmd, (msg, self.verbose))
                socket.send(str(q1.get()))
            else:
                print(str(timenow())+' ZeroPh() WARNING | Error: cmd was not converted to list ')
                
    def send(self, _type, _file, _cmd):
        """
        Send a cmd to the server to be run in a thread
        
        @params: {str} _type: type of comand ex: python, node, sh
        @params: {str} _file: filename to be called
        @params: {str} _cmd: the actual cmd and args that will be apllied to the cmd
        @rtype: {} get the rsponse form the server which should be stdout of the called process
        
        """

        # client
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.host+':'+self.port)
        
        s =","
        cmd = s.join((_type,_file))
        for arg in _cmd:
            if arg != ",":
                cmd= cmd+","
                if self.verbose:
                    print(str(timenow())+' ZeroPh() INFO | arg in _cmd: ' + str(arg)) 

                cmd = cmd + arg.replace("[","").replace("]","") 

        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | cmd sent to server: ' + str(cmd))
        socket.send(cmd)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | server returned response: ' + str(msg))
            
    def call(self, method):
        """
        Send a cmd to the server to be run in a thread
        
        @params: {str} _type: type of comand ex: python, node, sh
        @params: {str} _file: filename to be called
        @params: {str} _cmd: the actual cmd and args that will be apllied to the cmd
        @rtype: {} get the rsponse form the server which should be stdout of the called process
        
        """
        # client
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.host+':'+self.port)
        try:
            cmd= Config.get("Cmd", method)
        except:
            print(str(timenow())+' ZeroPh() Warning | method does NOT exist in [Cmd] config.ini : ' + str(method))
            cmd=str(timenow())+' ZeroPh() Warning | method does NOT exist in [Cmd] config.ini : ' + str(method)
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | cmd sent to server: ' + str(cmd))
        socket.send(cmd)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | server returned response: ' + str(msg))     
        return msg

    def parse_command_group(self, section):
        """
        Parse the group of command and store in into a list
        
        @params: {str} Section name to get list from
        @rtype: {list} List of key,value to be parsed as commands
        
        """
        result =[]
        for (each_key, each_val) in Config.items(section):
            result.append([ each_key, each_val])
        return result
        
    def parse_commands(self, commands):
        """
        Parse commands
        
        Will read the key and determine if it is a wait call or a cascade list
        (number can be contained in the list and will trigger a wait_and_call)
        
        @params:{list} list of commands (format: [[key,value],[key,value]] )
        
        """
        if len(commands) >0:
            for cmds in commands:
                if is_number(cmds[0]):
                    if self.verbose:
                        print(str(timenow())+' ZeroPh() INFO | Init process: '+str(cmds[1])+': waiting ' + str(cmds[0])+' seconds')
                    self.wait_and_call(cmds[0],cmds[1])
                elif isinstance(cmds[0], str):
                    commands=[]
                    if cmds[1].split(",") > 0:
                        for command in cmds[1].split(","):
                            commands.append(command)
                    else:
                        commands.append(cmds[1])
                    self.wait_cascade(commands)
        else:
            return self.onError("ERROR in parse_commands: ", "commands was empty")
            
        return True
        
    def wait_and_call(self, seconds, command):
        """
        wait number of seconds before lunching command
        @params:{int} number of seconds
        @params:{str} command
        @rtype{func} call the command
        
        """
        time.sleep(seconds)
        return self.call(command)
        
    def wait_cascade(self, commands):
        """
        wait on a return value before calling next command. Here will
        go the onReturn, onError, strategy.
        
        If cmd is a number , wait and call the enxt command in (number) seconds
        
        Here will also go the custom strategy(set at onReturn event)
        
        @params:{list} list of commands
        @rtype{func} call the command
        
        """
        for cmd, index in commands:
            if is_number(cmd):
                try:
                    result= self.wait_and_call(cmd, commands[index+1] 
                    command.pop(index+1)
                except:
                    text = traceback.format_exc()
                    exc_value = sys.exc_info()[
                    self.onError(text, exc_value, str(cmd) )
            else:
                try:
                    result = self.call(cmd)
                    ok = self.onReturn(result, str(cmd))
                    if ok:
                        continue
                    else:
                        raise except
                except:
                    text = traceback.format_exc()
                    exc_value = sys.exc_info()[
                    self.onError(text, exc_value, str(cmd) )
                
         

    def onError(self, error, message, _id):
        """
        onError return a print message with the stacktrace or message
        
        @params:{str} error
        @params: {str} message
        @params: {str} id for following (to be implemented)
        
        """
        if self.verbose:
            print(str(timenow())+' ZeroPh() ERROR | server returned error: '+str(error)+' message: ' + str(message))  
        return True
        
    def onReturn(self, value, _id)):
        """
        onReturn value strategy
        Here will be run the strategy
        
        @params:{str} return value

        """
        # put the strategy
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | server returned return value: '+str(value)+' for: ' + str(_id)) 
        if value != null:
            return True
        else:
            return False
        
def cmd(cmd, verbose):
    """
    Run the actual command in thread
        
    @params: {str} cmd: the command to run
    @rtype: {} return value
        
    """

    if verbose:
        print(str(timenow())+' ZeroPh() INFO | Thread started for : ' + str(cmd))
    query= cmd.split(",")
    if verbose:
        print(str(timenow())+' ZeroPh) INFO | query : ' + str(query))
    process = Popen(query, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(str(timenow())+' ZeroPh() WARNING | cmd returned error: ' + str(stderr))
    else:
        if verbose:
            print(str(timenow())+' ZeroPh() INFO | cmd returned stdout: ' + str(stdout))
        return stdout
        
        
def enthread(target, args):
    q = Queue.Queue()
    def wrapper():
        q.put(target(*args))
    t = threading.Thread(target=wrapper)
    t.start()
    return q

def timenow():
    return datetime.datetime.now().time()

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description='zeromq server/client for CmdToThread()')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag to verbose')
    parser.add_argument('-t', '--_type', help='{string} type of file to be called, ex: python , node, sh, ./')
    parser.add_argument('-f', '--_file', help='{string} filename to be called, ex: example.py, do.sh, index.js')
    parser.add_argument('-c', '--cmd', nargs='+', help='{list} cmd args and parameters')
    parser.add_argument('-s', '--start', action='store_true', help='start the server')
    parser.add_argument('-n', '--name',  help='{string} Name of the method to fetch in config')
    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True
    zeroph = ZeroPh(verbose)
    
    if args._type and args._file and args.cmd:
        zeroph.send(args._type, args._file, args.cmd)
    elif args.start:
        zeroph.run_server()
    elif args.name:
        result = zeroph.call(args.name)
    else:
        print(str(timenow())+' ZeroPh() WARNING | missing argument, need a _type, _file and cmd, start the server with -s')

if __name__ == "__main__":
    main()
