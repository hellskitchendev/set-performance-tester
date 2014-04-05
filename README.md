This is a simple class for testing performance of comparing sets, called parts, of objects, called nodes. It can be used with a file containing the node/part data or can generate it's own random data from provided node and part numbers or defaults.

File should be in the format: [node_id as integer][delimiter][part_id as integer]

The delimiter can be either  "," or  "\t" (tab) or " "(space) or "|" and after the part_id there can be anything else on the same line.

Keyword arguments:
* filename -- path to the file with the input information
* parts -- the number of nodes to use (default 50)
* nodes -- the imaginary part (default 1000)
* maxNodes -- the max number of nodes in each part (default # of nodes)
* verbose -- write out debug information to system (default False)
* skipTests -- skip the tests and create part intersection report (default False)
* fileOut -- write out intersection report to a file (default False)


NOTE: This was developed for a friend trying to crunch some data and who wants to get more into programming/Python. The pandas stuff is commented out so you can run on base python and because it was not well implemented. I might update with new stuff from time to time....


