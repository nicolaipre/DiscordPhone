    async def set_caller_id(self, caller_id):
        pass
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # conn = sock.connect(('127.0.0.1', '5038'))
        #        sock.send("""
        # action:updateconfig
        # 
        # """)
        #        sock.send("\r\n")
        # data = sock.recv()
        # sock.close()
        # netcat connection to 5038, username + password -> action:updateconfig
        # https://gist.github.com/jfinstrom/4227521
        # https://pypi.org/project/asterisk-ami/
        # https://www.voip-info.org/asterisk-manager-api-action-updateconfig/
        # https://community.asterisk.org/t/persuade-asterisk-to-reload-config-files-from-python/20056
        # https://stackoverflow.com/questions/32781655/asterisk-ami-deleting-of-certain-extension
        # https://stackoverflow.com/questions/47938769/updateconfig-asterisk-extensions-conf
        """
        Action: updateconfig
        Reload: yes
        Srcfilename: extensions.conf
        Dstfilename: extensions.conf
        Action-000000: delete
        Cat-000000: test
        Var-000000: exten
        Match-000000: Bob


        action:updateconfig
        srcfilename:extensions.conf
        dstfilename:extensions.conf
        Action-000000: update
        Cat-000000: stdexten
        Var-000000: exten
        Match-000000: _X.,50005,Dial(${dev},20)
        Value-000000:>_X.,50005,Dial(${dev},30)
        """
