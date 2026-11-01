#!/usr/bin/env python3
"""Exact k-NN inference audit for ai_patrol.py (no ROS dependencies).
Execute: python3 knn_audit.py
Outputs: knn_neighbors.csv and knn_summary.csv in current directory.
"""
import csv, math

samples=[]
for urgency in range(1,6):
    for distance in (0.25,0.5,0.75,1.0,1.25,1.5):
        score=2.0*urgency-2.0*distance
        if urgency==5:score+=1.5
        samples.append((urgency,distance,score))

cases={
    'case1': [('A',.8,0.,2),('B',.8,.8,5),('C',0.,.8,3)],
    'case2': [('A',.8,0.,5),('B',.8,.8,2),('C',0.,.8,3)],
}
audit=[];summary=[]
for case,points in cases.items():
    rankings=[]
    for name,x,y,urgency in points:
        distance=math.hypot(x,y)
        neighbors=[]
        for su,sd,score in samples:
            D=math.sqrt(((urgency-su)/5.0)**2+((distance-sd)/1.5)**2)
            neighbors.append((D,score,su,sd))
        neighbors.sort(key=lambda item:item[0])
        closest=neighbors[:5]
        weights=[1.0/(D+.001) for D,_,_,_ in closest]
        prediction=sum(w*p[1] for w,p in zip(weights,closest))/sum(weights)
        rankings.append((prediction,name))
        summary.append([case,name,urgency,distance,prediction])
        for rank,((D,score,su,sd),weight) in enumerate(zip(closest,weights),1):
            audit.append([case,name,rank,su,sd,score,D,weight,prediction])
    print(case, ' -> '.join(name for _,name in sorted(rankings,reverse=True)), '-> START')
    for score,name in sorted(rankings,reverse=True):print(' ',name,f'{score:.2f}')

for filename,header,rows in [
    ('knn_neighbors.csv',['case','target','rank','sample_urgency','sample_distance','sample_score','feature_distance','weight','prediction'],audit),
    ('knn_summary.csv',['case','target','urgency','distance','prediction'],summary),
]:
    with open(filename,'w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f);wr.writerow(header);wr.writerows(rows)
    print('Saved',filename)
