#   Copyright 2009 Aaron Barnes
#
#   This file is part of the FreeEMS project.
#
#   FreeEMS software is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   FreeEMS software is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with any FreeEMS software.  If not, see <http://www.gnu.org/licenses/>.
#
#   We ask that if you make any changes to this file you send them upstream to us at admin@diyefi.org


import os
import libs.config as config, comms.interface, libs.data


class connection(comms.interface.interface):
    '''
    Fake comms interface for loading input from file
    '''

    # Fake receive buffer
    _buffer = ''


    def __init__(self, name, controller):
        '''
        Initialise comms thread
        '''
        comms.interface.interface.__init__(self, name, controller)

        # Load protocol
        self.getProtocol()

        self.start()


    def _connect(self):
        '''
        "Connect" to fake serial connection
        '''
        self._connWanted = False
        
        if self.isConnected():
            return

        self._connected = True
        self._debug('Test comms connection connected')
        
        # Get complete file path
        path = libs.data.getPath() + config.get('Comms_File', 'path')
    
        # Check to see if file exists
        if not os.path.exists(path) or not os.path.isfile(path):
            self._error('Comms input file does not exist (%s)' % path)
            return

        # Load file into buffer
        fd = open(path, 'r')
        self._buffer = ''.join(fd.readlines())
        fd.close()


    def _disconnect(self):
        '''
        "Disconnect" from fake serial connection
        '''
        self._disconnWanted = False

        if not self.isConnected():
            return

        self._connected = False
        self._debug('Test comms connection disconnected')


    def _send(self, packet):
        '''
        Drops any sent packets.
        '''
        # Log packet hex
        self._debug('Packet sent to File comms connection dropped')


    def run(self):
        '''
        Check for and receive packets waiting in the connection
        '''
        # Get protocol
        protocol = self.getProtocol()

        # Create send and receive threads
        self._createSendThread()
        self._createReceiveThread()

        while self.isConnected() or self._alive:

            # If not connected, block until we are ready to
            if not self.isConnected():

                # If told to connect
                if self._connWanted:
                    self._connect()
                else:
                    self._checkBlock()
                    continue

            # If connected, see if we want to disconnect
            if self.isConnected() and self._disconnWanted:
                self._disconnect()
                continue

            # If stuff in receive buffer
            if len(self._buffer):
                self._receive(self._buffer)
                self._buffer = ''

            # If stuff in send buffer
            while len(self._queue):
                self._send(self._queue.pop(0))

            self._checkBlock()

        self._final()
