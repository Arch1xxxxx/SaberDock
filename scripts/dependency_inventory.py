import importlib.metadata,json,sys
from pathlib import Path
entries=[]
for d in importlib.metadata.distributions(path=[sys.argv[1]]):
 entries.append({'name':d.metadata['Name'],'version':d.version,'licenseExpression':d.metadata.get('License-Expression'),'license':d.metadata.get('License'),'projectURLs':d.metadata.get_all('Project-URL',[])})
Path(sys.argv[2]).write_text(json.dumps(sorted(entries,key=lambda d:d['name'].lower()),indent=2))
