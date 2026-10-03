"""Bounded section interpolation for accepted 1C body and shield silhouettes."""
from pathlib import Path
import json, math
from bisect import bisect_right
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    path=Path(scaffold_path) if scaffold_path else Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/basic-shape-study05/study.json')
    if path.suffix=='.blend':path=path.with_name('study.json')
    shapes=json.loads(path.read_text())['shapes']
    torso=next(q['sections'] for q in shapes if q['part']=='torso')
    wings={q['side']:q['sections'] for q in shapes if q['part']=='shoulder-wing'}
    def profile(rows,z,smooth):
        z=max(rows[0][0],min(rows[-1][0],z));i=min(len(rows)-2,max(0,bisect_right([q[0] for q in rows],z)-1))
        a,b=rows[i],rows[i+1];h=b[0]-a[0];t=(z-a[0])/h;out=[]
        for k in range(1,len(a)):
            slope=(b[k]-a[k])/h
            if not smooth:out.append(a[k]+t*(b[k]-a[k]));continue
            # Monotone cubic Hermite: exact anchors; bounded without overshoot.
            def derivative(j):
                if j==0:return (rows[1][k]-rows[0][k])/(rows[1][0]-rows[0][0])
                if j==len(rows)-1:return (rows[-1][k]-rows[-2][k])/(rows[-1][0]-rows[-2][0])
                left=(rows[j][k]-rows[j-1][k])/(rows[j][0]-rows[j-1][0]);right=(rows[j+1][k]-rows[j][k])/(rows[j+1][0]-rows[j][0])
                return 2*left*right/(left+right) if left*right>0 else 0
            m0,m1=derivative(i),derivative(i+1)
            if slope==0:m0=m1=0
            elif (m0/slope)**2+(m1/slope)**2>9:
                factor=3/math.sqrt((m0/slope)**2+(m1/slope)**2);m0*=factor;m1*=factor
            value=(2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*h*m1
            out.append(max(min(a[k],b[k]),min(max(a[k],b[k]),value)))
        return out
    objects=vertices=0;maxmove=0
    for obj in list(scene.objects):
        region=obj.get('cg1cRegion')
        if region not in ('body','wing') or obj.type!='MESH' or obj.get('cg2ProfileSmoothed'):continue
        side='left' if ('left' in obj.name.lower() or obj.matrix_world.translation.x<0) else 'right'
        rows=torso if region=='body' else wings[side]
        inv=obj.matrix_world.inverted();objects+=1
        for v in obj.data.vertices:
            p=obj.matrix_world@v.co;a=profile(rows,p.z,False);b=profile(rows,p.z,True)
            if region=='body':
                old=Vector((0,a[0],p.z));new=Vector((0,b[0],p.z));rx,ry=a[1:3];nx,ny=b[1:3]
            else:
                sign=-1 if side=='left' else 1;old=Vector((sign*a[0],a[1],p.z));new=Vector((sign*b[0],b[1],p.z));rx,ry=a[2:4];nx,ny=b[2:4]
            # Affine cross-section map keeps the inset backing and raised plate offsets.
            q=Vector((new.x+(p.x-old.x)*nx/max(.005,rx),new.y+(p.y-old.y)*ny/max(.005,ry),p.z))
            maxmove=max(maxmove,(q-p).length);v.co=inv@q;vertices+=1
        obj.data.update();obj['cg2ProfileSmoothed']=True
    return {'module':'cg2-body','objects':objects,'vertices':vertices,'maximumVertexDisplacement':maxmove,'anchorDeviation':0,'change':'Monotone bounded section interpolation of accepted body and folded shield masses; mapped backing, plates and rolled edges together','limits':'Existing circumferential tessellation retained; no proportion, joint anchor, stance or material change'}
