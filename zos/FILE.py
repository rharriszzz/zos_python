
class FILE:
    name = None
    mode = None
    amrc = None
    amrc2 = None
    errno = None
    errno2 = False
    error = False
    eof = False
    file = None
    is_readable = False
    is_writable = False

    def close(self):
        """close($self, /)
        --
        
        Close the file.
        
        A closed file cannot be used for further I/O operations.  close() may be
        called more than once without error."""
        
        self.fclose()

    def readable(self, /):
        """readable($self, /)
        --
        
        True if file was opened in a read mode."""
        
        return is_readable

    def writable(self, /):
        """writable($self, /)
        --
        
        True if file was opened in a write mode."""
        
        return is_writable

    def seekable(self, /):
        """seekable($self, /)
        --
         
        True if file supports random-access.
        Always returns False, use fgetpos and fsetpos instead."""

        return False

     def readinto(self, buffer, /):
         """readinto($self, buffer, /)"""
         result = self.fread()
         pass

     def readall(self, /):
         """readall($self, /)
         --
         
         Read all data from the file, returned as bytes.
         
         In non-blocking mode, returns as much as is immediately available,
         or None if no data is available.  Return an empty bytes object at EOF."""

         pass

     def read(self, size=-1, /):
         """read($self, size=-1, /)
         --
         
         Read at most size bytes, returned as bytes.
         
         Only calls fread once, so less data may be returned than requested.
         Return an empty bytes object at EOF."""

         if size < 0:
            return readall(self)

        

         pass

     def write(self, b, /):
         """write($self, b, /)
         --
         
         Write buffer b to file, return number of bytes written.
         
         Only calls fwrite once, so not all of the data may be written.
         The number of bytes actually written is returned."""
         
         pass

     def seek(self, pos, whence, /):
         """seek($self, pos, whence=0, /)
         --
         
         Move to new file position and return the file position.
         Use fsetpos instead."""
         
         raise IOError

     def tell(self, /):
         """tell($self, /)
         --
         
         Current file position.
         Use fgetpos instead."""
         raise OSError

     def isatty(self, /):
         """isatty($self, /)
         --
         
         True if the file is connected to a TTY device."""
         return False

import _FILE
FILE.__init__ = FILE___init__
FILE.fclose = FILE_fclose
FILE.fileno = FILE_fileno
FILE.fflush = FILE_fflush
FILE.fread = FILE_fread
FILE.write = FILE_fwrite
FILE.fwrite = FILE_fwrite
FILE.rewind = FILE_rewind
FILE.fgetpos = FILE_fgetpos
FILE.fsetpos = FILE_fsetpos
FILE.fldata = FILE_fldata
FILE.flocate = FILE_flocate
FILE.fdelrec = FILE_fdelrec
FILE.fupdate = FILE_fupdate
     
