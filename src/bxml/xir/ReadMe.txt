This is a rapid prototype of XIR.

To get started, do the following:

1. From the 'xir/src' directory, source set_pythonpath.sh:
   $ cd ..
   $ . set_pythonpath.sh
   --- or ---
   $ source set_pythonpath.sh
   
2. $ python xml2xir.py simple.xml > simple.xir

3. Go ahead and examine the simple.xir file. It's a non-tree representation of the XML document. 
   Think of it as a "compiled" version of the simple.xml file.
   
4. $ python xirecho.py simple.xir
   This will show you the XIR event stream. I will be extending this example to reconstruct the
   original XML document (or one very similar to it).
   
More to come soon, including a Java writer/reader!