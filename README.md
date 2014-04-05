This is a simple class for testing performance of comparing sets, called parts, of objects, called nodes. It can be used with a file containing the node/part data or can generate it's own random data from provided node and part numbers or defaults.

The class and script are in src/SetPerformanceTester.py

The Vagrant file can be used with [Vagrant](http://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) to set up an environment to run the code.

Keyword arguments:
* -filename [path] -- path to the file with the input information
* -parts [parts] -- the number of nodes to use (default 200)
* -nodes [nodes] -- the imaginary part (default 3000)
* -maxNodes [maxNodes] -- the max number of nodes in each part (default # of nodes)
* -v -- write out debug information to system (default False)
* -skipTests -- skip the tests and create part intersection report (default False)
* -fileOut -- write out intersection report to a file (default False)

The input file should be in the format: [node_id as integer][delimiter][part_id as integer]

The delimiter can be either:
* ","  
* "\t" (tab) 
* " "(space) 
* "|"

After the part_id there can be anything else on the same line.


NOTE: This was developed for a friend trying to crunch some data and who wants to get more into programming/Python. The pandas stuff is commented out so you can run on base python and because it was not well implemented. I might update with new stuff from time to time....


