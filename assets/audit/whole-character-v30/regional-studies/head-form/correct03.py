from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/scripts/regions/whole-character-v30-head-form.py');s=p.read_text()
s=s.replace("capnames=['V27 fixed frontal cranial receiving return','V27 dorsal swept cranial course 0','V27 dorsal swept cranial course 1','V27 dorsal swept cranial course 2']", "capnames=['V27 fixed frontal cranial receiving return','V27 dorsal swept cranial course 0']")
s=s.replace("v,f=crown_sheet([(-.597,1.633,.028),(-.603,1.626,.024),(-.607,1.620,.020)]);install('Distal mandible bridge',v,f)", "# Seat the transverse jaw bridge on the actual paired midspan returns,\n # posterior to the hook cutting envelope; distal rails retain their seam.\n v,f=crown_sheet([(-.551,1.679,.059),(-.555,1.678,.060),(-.559,1.676,.058)]);install('Distal mandible bridge',v,f)")
s=s.replace(",('V27 dorsal swept cranial course 1',(-.491,-.286,.82,1.41,.017,.40,-.08,.91,None)),('V27 dorsal swept cranial course 2',(-.495,-.295,1.73,2.32,.017,.34,.10,.91,None))", "")
s=s.replace("'primaryPivotChanges':[]", "'primaryPivotChanges':[],'technicalFitRepair':{'bridge':'Finite transverse connector reseated at actual paired jaw midspan, posterior to distal hook swept envelope; paired distal cutting rails retained.','originalDorsalCoursesRetainedExact':[1,2]}")
p.write_text(s)
s=Path('/tmp/v30-head-form/study02.py').read_text().replace('/tmp/v30-head-form/attempt02','/tmp/v30-head-form/attempt03');Path('/tmp/v30-head-form/study03.py').write_text(s)
