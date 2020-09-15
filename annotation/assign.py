import sqlite3
from statistics import mean, stdev
from random import choice
from collections import defaultdict as dd
###
### give people more sentences for sentiment
###


db = '/home/bond/papers/HG8011/local/new/eng.db'
conn = sqlite3.connect(db)
c = conn.cursor()

groupsize = 2
##200 for HG8011, 300 for HG2002 
nconcepts = 293


#select min(sid), max(sid) from sent as s join doc as d on s.docid = d.docid where d.doc='houn';
# 45681       49504    for the whole
smin, smax= 48505,  49504
# we did 47488 - 48504 (2019)
# we did 46692 - 47485
# we did 45681-46691
# (- 49504 46692)
# (* 92 300) 

def read_students(file):
    """
    return a dic of stud[sid] = (name, matric, uid)
    """
    stud = {}
    fh = open(file)
    for l in fh:
        if l.startswith('#'):
            continue
        row = l.strip().split('\t')
        #print (row)
        ### from Nura
        #stud[int(row[0])]= row[1], row[2], row[9]
        ### from https://wish.wis.ntu.edu.sg/webexe/owa/aus_class_attendance.main?p1=10002063&p2=
        stud[int(row[0])]= row[1], row[2], row[5]
    return stud

def get_concepts(c):
    concepts = dd(int)
    c.execute("""select sid, count(cid) from concept 
    where sid >= ? and sid <= ? group by sid""",
              (smin, smax))
    for (sid, count) in c:
        #print(sid, count)
        if sid:
            concepts[sid]= int(count)
    return concepts

stud = read_students("students.tsv")

ngroups = int(len(stud)/groupsize)

print ('no of students', len(stud))
print ('no of groups', ngroups)
print ('remainder: add them to the last group', len(stud) % groupsize)
concepts = get_concepts(c)

letter= {0:'A', 1:'B',2:'C',3:'D',4:'E'}

sid = int(smin)
scount = 0
tcount = 0
sents = dict()
for gid in range(1,ngroups+1):
    scount = 0
    sfrom = sid
    while scount < nconcepts:
        #print (sid, scount)
        scount += concepts[sid]
        sid +=1
    sents[gid] = sfrom, sid - 1
    print ('G' + str(gid), sfrom, sid - 1, scount, sid-sfrom, sep='\t')

print ("Total number of sentences:", sid - smin)
print ("Sentences/group:", (sid - smin) / ngroups)


 # (-  49504 47487)

###
### print groups
###
html =open('annotation.html', 'w')

print("""
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html xmlns:xhtml="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Annotation Task</title>
</head>
<body>
<h2><a name='phase1'>Phase 1: Annotation Task</a></h2>

  <p> The format is
<br>
<table>
<tr>
  <td>ID</td> 
  <td>Name</td> 
  <td>UID</td> 
  <td>Corpus</td>
  <td>Sentences</td>
</tr>
<tr>
  <td>s221</td> 
  <td>John Hamish Watson</td> 
  <td>watson001</td> 
  <td>B</td>
  <td>000001-0000016</td>
</tr>
</table>
	<ul>
	  <li> The id is for internal use, please remember it and your password
<li> Clicking on the sentences jumps you to the start sentence (with 4 sentences before and after) 
<li> You will have to log in each time you change to a new browser
	  <li> Don't tag past the end sentence (there will not be a warning)
<li> Sentences vary in length, so some have more, some less, but you all have around {} concepts, with an average of {:.1f} sentences per group.
	</ul>

""".format(nconcepts, (sid - smin) / ngroups), file=html)

url='https://lr.soh.ntu.edu.sg/ntumc/cgi-bin/tag-word.cgi?gridmode=ntumcgrid&corpus=eng'
print("<table>",  file=html)
print ("""<tr>   <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td><td>{}</td></tr>""".format('ID',
                                                                                           'Name', 'UID', 'Corpus',
                                                                              'Sentences'), file=html)
sgroup = dd(list)
corpus = 0
for sid in sorted(stud.keys()):
    gid = sid % ngroups
    if gid == 0:
        gid = ngroups
    sgroup[gid].append(sid)
    (name, matric, uid) = stud[sid]
    print ("""<tr> <td>s{0}</td> <td>{1}</td> <td>{2}</td> <td>{6}</td>
   <td><a href='{5}{6}&sid={3}'>{3} &ndash; {4}</a></td></tr>
    """.format(sid, name.title(), uid,
               sents[gid][0],
               sents[gid][1],
               url,  letter[int((sid-1)/ngroups)]), file=html)
print("</tr>",  file=html)
print("</table>",  file=html)

print("""<hr>
      <p><a href='annotation.html'>Project Guide</a>
      <p><a href='index.html'>Syllabus</a>""",  file=html)
print("<h2><a name='phase2'>Phase 2: Comparison Task</a></h2>", file=html)
url2= "https://lr.soh.ntu.edu.sg/ntumc/cgi-bin/agreement.cgi?lang=eng"#sid_from=45849&sid_to=45870
#https://lr.soh.ntu.edu.sg/ntumc/cgi-bin/agreement.cgi?lang=eng&sid_from=45849&sid_to=45870
for gid in range(1,ngroups+1):
    print("""<h3><a href='{3}&sid_from={1}&sid_to={2}'>Group {0} ({1} &ndash; {2})</a></h3>""".format(gid, sents[gid][0],  sents[gid][1],url2), file=html)
    print("<ol type='A'>",  file=html)
    for sid in sgroup[gid]:
        print ("""  <li> {} (<tt>{}: s{}</tt>)""".format(stud[sid][0].title(), stud[sid][2], sid), file=html)

    print("</ol>",  file=html)

print("""<hr>
      <p><a href='annotation.html'>Project Guide</a>
      <p><a href='index.html'>Syllabus</a>
</body>
</html>
      """,  file=html)


# steps = [0,1,1,2]

# print('Sentences:', smax-smin)
# maxstudent=204
# print('Students:', maxstudent)
# students=range(1,maxstudent+1)
# overlap = 4

# groups = int(maxstudent / overlap)
# if maxstudent % overlap:
#     groups +=1
# print('Groups:', groups)
# print('Sent/stud = ', (smax-smin) / groups)
# startlength= int((smax-smin) / groups) 

# studs = list() # stud[s] = [(sfrom, sto), ...]

# start = smin
# for s in range(groups):
#     studs.append((start,start+startlength))
#     start = start + startlength + 1
# studs[groups-1] = (studs[groups-1][0],smax)
    
# print (len(studs), studs)
# load=list()
# for f,t in studs:
#     l = sum(concepts[s] for s in range(f,t+1))
#     load.append(l)


# def loadat(pos, studs, concepts):
#     "load at a particular position"
#     return sum(concepts[s] for s in range(studs[pos][0], studs[pos][1] +1))

# def lengthen(studs,pos,load):
#     "lengthen the passage at position pos"
#     #choose to take from left or right
#     if pos==1: # at the start
#         dir = +1
#     elif pos == len(studs)-1: # at the end
#         dir = -1
#     ### calculate the effect at left and right, chose the best 
#     elif abs(sum(concepts[s] for s in
#                  range(studs[pos -1][0], studs[pos -1][1]))
#              - mean(load)) < \
#              abs(sum(concepts[s] for s in
#                      range(studs[pos +1][0] +1, studs[pos +1][1]))
#                  - mean(load) +1):
#         dir = -1
#     else:
#         dir = +1
#     step=choice(steps)
#     #print("lengthen: ", pos, dir,step)
#     if dir == -1: #expand left
#         studs[pos] = (studs[pos][0] -step, studs[pos][1])
#         studs[pos -1] = (studs[pos-1][0], studs[pos-1][1] -step)
#         load[pos]=loadat(pos, studs, concepts)
#         load[pos-1]=loadat(pos-1, studs, concepts)
#     elif dir == +1:  # expand right
#         studs[pos] = (studs[pos][0], studs[pos][1] +step)
#         studs[pos +1] = (studs[pos+1][0] +step, studs[pos+1][1])
#         load[pos]=loadat(pos, studs, concepts)
#         load[pos+1]=loadat(pos+1, studs, concepts)

# def shorten(studs,pos,load):
#     "shorten the passage at position pos"
#     #choose to take from left or right
#     if pos==1: # at the start
#         dir = +1
#     elif pos == len(studs)-1: # at the end
#         dir = -1
#     ### calculate the effect at left and right, chose the best 
#     elif abs(sum(concepts[s] for s in
#                  range(studs[pos -1][0], studs[pos -1][1]+1))
#              - mean(load)) < \
#              abs(sum(concepts[s] for s in
#                      range(studs[pos+1][0] +1, studs[pos +1][1]))
#                  - mean(load) +1):
#         dir = -1
#     else:
#         dir = +1
#     step=choice(steps)
#     #print("shorten: ", pos, dir, step)
#     if dir == -1: #shrink from left
#         studs[pos] = (studs[pos][0] +step, studs[pos][1])
#         studs[pos -1] = (studs[pos-1][0], studs[pos-1][1] +step)
#         load[pos]=loadat(pos, studs, concepts)
#         load[pos-1]=loadat(pos-1, studs, concepts)
#     elif dir == +1:  # shrink from right
#         studs[pos] = (studs[pos][0], studs[pos][1] -step)
#         studs[pos +1] = (studs[pos+1][0] -step, studs[pos+1][1])
#         load[pos]=loadat(pos, studs, concepts)
#         load[pos+1]=loadat(pos+1, studs, concepts)

        
# print('Min: ', min(load))
# print('Max: ', max(load))
# print('Mean: ', mean(load))
# print('SD: ', stdev(load))

# outer = 25
# iterations = 50000
# initial = studs
# trials = []
# for o in range(outer):
#     studs = initial
#     load=list()
#     for f,t in studs:
#         l = sum(concepts[s] for s in range(f,t+1))
#         load.append(l)
#     for i in range(iterations):
#         # add some noise, but not at the end
#         if i <= iterations - 100:
#             m = choice(range(1, len(studs)-2))
#             lengthen(studs,m,load)
#             m= choice(range(1, len(studs)-2))
#             shorten(studs,m,load)
#             m = choice(range(1, len(studs)-2))
#             lengthen(studs,m,load)
#             m= choice(range(1, len(studs)-2))
#             shorten(studs,m,load)
#             ## clean up
#             mins = [m for m in range(len(load))
#                     if loadat(m, studs, concepts) == min(load)]
#             for m in mins:
#                 lengthen(studs,m,load)
#             maxs = [m for m in range(len(load))
#                     if loadat(m, studs, concepts) == max(load)]
#             for m in maxs:
#                 shorten(studs,m,load)
#     # print('Min: ', min(load))
#     # print('Max: ', max(load))
#     # print('Mean: ', mean(load))
#     # print('SD: ', stdev(load))
#     #print (studs)
#     trials.append([stdev(load),load,studs])
#     print("Trial:", o, stdev(load))


# for (s,l,ss) in sorted(trials,reverse=True):
#     print(s,min(l),max(l))

# for i, (sfrom, sto) in enumerate(ss):
#     print ("{:d}\t{:d}\t{:d}\t{:d}\t{:d}".format(i+1, sfrom, sto,
#                                             sto-sfrom,
#                                             l[i]))
        
        
    
    
    
