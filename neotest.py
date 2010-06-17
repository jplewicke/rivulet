from __future__ import with_statement
import neo4j

gdb = neo4j.GraphDatabase("./nt")

index = gdb.index("cat_names", create=True)

cats = ["Pookie","Oliver","Blu","George","Ringo","Paul","John"]

bad_smells = {"Pookie":3 , "Oliver":6 , "Blu":900, "George":8, "Ringo":4, "Paul":2, "John":7}

print dir(neo4j)
print cats

with gdb.transaction:
    #ref_node = gdb.reference_node
    #for c in cats:
    #    node = gdb.node(name=c, bad_smells=bad_smells[c])
    #    index[c] = node
    print index["Blu"]["bad_smells"]

    
gdb.shutdown()