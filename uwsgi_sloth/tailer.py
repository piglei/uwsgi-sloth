# -*- coding: utf-8 -*-
"""File tailer, Based on: https://github.com/six8/pytailer"""
import os
import re
import time
import logging

logger = logging.getLogger(__name__)


class NoNewLine(object):
    pass

no_new_line = NoNewLine()


class Tailer(object):
    """Implements tailing and heading functionality like GNU tail and head
    commands.
    """
    line_terminators = ('\r\n', '\n', '\r')
    DEFAULT_BLOCK_SIZE = 4096
    MAX_UNCHANGED_STATS = 5

    def __init__(self, file, read_size=DEFAULT_BLOCK_SIZE, end=False):
        if isinstance(file, str):
            file = open(file, 'r')

        self.should_stop_follow = False
        self.read_size = read_size
        self.file = file
        self.start_pos = self.file.tell()
        if end:
            self.seek_end()
    
    def splitlines(self, data):
        return re.split('|'.join(self.line_terminators), data)

    def seek_end(self):
        self.seek(0, 2)

    def seek(self, pos, whence=0):
        self.file.seek(pos, whence)

    def read(self, read_size=None):
        if read_size:
            read_str = self.file.read(read_size)
        else:
            read_str = self.file.read()

        return len(read_str), read_str

    def seek_line_forward(self):
        """\
        Searches forward from the current file position for a line terminator
        and seeks to the charachter after it.
        """
        pos = start_pos = self.file.tell()

        bytes_read, read_str = self.read(self.read_size)

        start = 0
        if bytes_read and read_str[0] in self.line_terminators:
            # The first charachter is a line terminator, don't count this one
            start += 1

        while bytes_read > 0:          
            # Scan forwards, counting the newlines in this bufferfull
            i = start
            while i < bytes_read:
                if read_str[i] in self.line_terminators:
                    self.seek(pos + i + 1)
                    return self.file.tell()
                i += 1

            pos += self.read_size
            self.seek(pos)

            bytes_read, read_str = self.read(self.read_size)

        return None

    def seek_line(self):
        """\
        Searches backwards from the current file position for a line terminator
        and seeks to the charachter after it.
        """
        pos = end_pos = self.file.tell()

        read_size = self.read_size
        if pos > read_size:
            pos -= read_size
        else:
            pos = 0
            read_size = end_pos

        self.seek(pos)

        bytes_read, read_str = self.read(read_size)

        if bytes_read and read_str[-1] in self.line_terminators:
            # The last charachter is a line terminator, don't count this one
            bytes_read -= 1

            if read_str[-2:] == '\r\n' and '\r\n' in self.line_terminators:
                # found crlf
                bytes_read -= 1

        while bytes_read > 0:          
            # Scan backward, counting the newlines in this bufferfull
            i = bytes_read - 1
            while i >= 0:
                if read_str[i] in self.line_terminators:
                    self.seek(pos + i + 1)
                    return self.file.tell()
                i -= 1

            if pos == 0 or pos - self.read_size < 0:
                # Not enought lines in the buffer, send the whole file
                self.seek(0)
                return None

            pos -= self.read_size
            self.seek(pos)

            bytes_read, read_str = self.read(self.read_size)

        return None
  
    def tail(self, lines=10):
        """\
        Return the last lines of the file.
        """
        self.seek_end()
        end_pos = self.file.tell()

        for i in range(lines):
            if not self.seek_line():
                break

        data = self.file.read(end_pos - self.file.tell() - 1)
        if data:
            return self.splitlines(data)
        else:
            return []
               
    def head(self, lines=10):
        """\
        Return the top lines of the file.
        """
        self.seek(0)

        for i in range(lines):
            if not self.seek_line_forward():
                break
    
        end_pos = self.file.tell()
        
        self.seek(0)
        data = self.file.read(end_pos - 1)

        if data:
            return self.splitlines(data)
        else:
            return []

    def follow(self, delay=1.0):
        """\
        Iterator generator that returns lines as data is added to the file.

        Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        """
        # TODO: Handle log file rotation
        self.trailing = True
        unchanged_stats = 0
        
        while not self.should_stop_follow:
            where = self.file.tell()
            line = self.file.readline()
            if line:    
                if self.trailing and line in self.line_terminators:
                    # This is just the line terminator added to the end of the file
                    # before a new line, ignore.
                    self.trailing = False
                    continue

                if line[-1] in self.line_terminators:
                    line = line[:-1]
                    if line[-1:] == '\r\n' and '\r\n' in self.line_terminators:
                        # found crlf
                        line = line[:-1]

                self.trailing = False
                unchanged_stats = 0
                yield line
            else:
                self.trailing = True
                self.seek(where)
                yield no_new_line
                # Try to catch up rotated log file
                unchanged_stats += 1
                if unchanged_stats >= self.MAX_UNCHANGED_STATS and \
                        where != os.stat(self.file.name).st_size:
                    logger.info('Reopen log file because file may has been rotated.')
                    self.reopen_file()

                time.sleep(delay)

    def reopen_file(self):
        self.file = open(self.file.name, 'r')

    def stop_follow(self):
        self.should_stop_follow = True

    def __iter__(self):
        return self.follow()

    def close(self):
        self.file.close()


