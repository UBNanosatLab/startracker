from startracker import *
import rst
rst.load_db()
query=rst.star_query()
for s in extract_stars(cv2.imread(sys.argv[1])):
    query.add_star(s[0],s[1],s[2],0)

for s in extract_stars(cv2.imread(sys.argv[2])):
    query.add_star(s[0],s[1],s[2],1)
print query.search_rel()
print [i for i in query.winner_id_map]

