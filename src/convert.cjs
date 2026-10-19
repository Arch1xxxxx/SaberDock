const {tr}=require('./i18n.cjs');
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),b=require('bsmap');
const job=process.argv[2],configs=JSON.parse(fs.readFileSync(path.join(job,'config.json')));
const settings=JSON.parse(fs.readFileSync(path.join(job,'job.json'))),crypto=require('crypto');
const version=crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex');
function equal(a,z,p){if(typeof a==='number'){assert.ok(Math.abs(a-z)<1e-5,`${p}: ${a} != ${z}`);return;}if(Array.isArray(a)){assert.equal(a.length,z.length,p);a.forEach((v,i)=>equal(v,z[i],`${p}[${i}]`));return;}if(a&&typeof a==='object'){for(const k of Object.keys(a))if(k!=='customData'&&!(p.includes('.bombNotes[')&&['direction','angleOffset'].includes(k)))equal(a[k],z[k],p+'.'+k);return;}assert.equal(a,z,p);}
function local(root,name){const p=path.resolve(root,name);assert(p.startsWith(path.resolve(root)+path.sep),tr('谱面引用了文件夹之外的文件'));return p;}
try {
const reports=[];
for(const c of configs){try{
 const cache=settings.cache&&path.join(settings.cache,'conversion',c.contentKey+'-'+version),cached=cache&&path.join(cache,'report.json');
 if(cached&&fs.existsSync(cached)){const report={...JSON.parse(fs.readFileSync(cached)),...c};const dest=path.join(job,'converted',c.slot);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.cpSync(path.join(cache,'files'),dest,{recursive:true});reports.push(report);console.log(JSON.stringify({event:'progress',message:tr('复用已校验谱面：')+c.label}));continue;}
 const folder=c.folder,raw=JSON.parse(fs.readFileSync(c.infoPath)),info=b.readInfoFileSync(c.infoPath),out=path.join(job,'converted',c.slot);fs.mkdirSync(out,{recursive:true});
 const std=info.difficulties.filter(x=>x.characteristic==='Standard');assert(std.length,tr('仅支持 Standard（标准双剑）谱面'));
 assert(!info.audio.audioOffset&&!info.audio.shuffle,tr('该谱面的音频偏移或 Shuffle 暂不支持'));assert(info.audio.bpm>0,tr('BPM 无效'));
 const v2={_songName:info.song.title,_songSubName:info.song.subTitle,_songAuthorName:info.song.author,_levelAuthorName:[...new Set(std.flatMap(x=>x.authors.mappers))].join(', '),_songFilename:info.audio.filename,_coverImageFilename:info.coverImageFilename,_beatsPerMinute:info.audio.bpm,_previewStartTime:info.audio.previewStartTime,_previewDuration:info.audio.previewDuration||12,_songTimeOffset:0,_environmentName:info.environmentBase.normal||'DefaultEnvironment',_environmentNames:info.environmentNames,_difficultyBeatmapSets:[{_beatmapCharacteristicName:'Standard',_difficultyBeatmaps:[]}]};
 const report={...c,info:v2,difficulties:[],optionalSuggestions:[],bpmEvents:null};
 if(Number(String(raw.version||raw._version).split('.')[0])>=4&&info.audio.audioDataFilename){const file=local(folder,info.audio.audioDataFilename);if(fs.existsSync(file))report.nativeAudioData=JSON.parse(fs.readFileSync(file));}
 for(const m of std){
  const cd=m.customData||{};assert(!(cd._requirements||cd.requirements||[]).length,tr('此谱面需要 Quest 插件，无法直接迁移'));
  const input=local(folder,m.filename),data=JSON.parse(fs.readFileSync(input));assert(!(data._customData?._requirements||data.customData?.requirements||[]).length,tr('此谱面需要 Quest 插件'));
  const src=b.readDifficultyFileSync(input,3),initial=structuredClone(src);
  if(report.nativeAudioData&&m.lightshowFilename&&fs.existsSync(local(folder,m.lightshowFilename))){const lights=b.readLightshowFileSync(local(folder,m.lightshowFilename),3);src.lightshow=lights.lightshow;initial.lightshow=structuredClone(lights.lightshow);}
  if(report.bpmEvents)assert.deepEqual(report.bpmEvents,initial.difficulty.bpmEvents,tr('各难度采用不同变速时间轴，暂不支持'));else report.bpmEvents=initial.difficulty.bpmEvents;
  b.writeDifficultyFileSync(src,4,{directory:out,filename:m.difficulty+'.beatmap.json'});b.writeLightshowFileSync(src,4,{directory:out,filename:m.difficulty+'.lightshow.json'});
  const back=b.readDifficultyFileSync(path.join(out,m.difficulty+'.beatmap.json'),3),light=b.readLightshowFileSync(path.join(out,m.difficulty+'.lightshow.json'),3);
  for(const k of ['colorNotes','bombNotes','obstacles','arcs','chains'])equal(initial.difficulty[k],back.difficulty[k],c.label+'.'+m.difficulty+'.'+k);
  for(const k of ['basicEvents','colorBoostEvents'])equal(initial.lightshow[k],light.lightshow[k],c.label+'.'+m.difficulty+'.'+k);
  const rank={Easy:0,Normal:1,Hard:2,Expert:3,ExpertPlus:4}[m.difficulty];assert(rank!==undefined,tr('未知难度'));
  report.difficulties.push({name:m.difficulty,rank,notes:back.difficulty.colorNotes.length,bombs:back.difficulty.bombNotes.length,obstacles:back.difficulty.obstacles.length,arcs:back.difficulty.arcs.length,chains:back.difficulty.chains.length,basicEvents:light.lightshow.basicEvents.length,njs:m.njs,offset:m.njsOffset,roundTrip:'passed'});
  // Normalize native info color schemes to legacy map custom-data keys used by the builder.
  const normalized={...cd};const cs=info.colorSchemes[m.colorSchemeId];if(cs){for(const [key,name] of Object.entries({_colorLeft:'saberAColor',_colorRight:'saberBColor',_obstacleColor:'obstaclesColor',_envColorLeft:'environmentColor0',_envColorRight:'environmentColor1',_envColorLeftBoost:'environmentColor0Boost',_envColorRightBoost:'environmentColor1Boost'})){const color=cs[name]||cs.colorScheme?.[name];if(color&&!normalized[key])normalized[key]=color;}}
  v2._difficultyBeatmapSets[0]._difficultyBeatmaps.push({_difficulty:m.difficulty,_customData:normalized,_environmentNameIdx:m.environmentId||0});report.optionalSuggestions.push(...cd._suggestions||cd.suggestions||[]);
 }
 report.optionalSuggestions=[...new Set(report.optionalSuggestions)];if(cache){const tmp=cache+'.new';fs.rmSync(tmp,{recursive:true,force:true});fs.mkdirSync(tmp,{recursive:true});fs.cpSync(out,path.join(tmp,'files'),{recursive:true});fs.writeFileSync(path.join(tmp,'report.json'),JSON.stringify(report));fs.rmSync(cache,{recursive:true,force:true});fs.renameSync(tmp,cache);}reports.push(report);console.log(JSON.stringify({event:'progress',message:tr('谱面校验：')+c.label}));
}catch(e){throw new Error(`${c.label}：${e.message}`);}}
fs.writeFileSync(path.join(job,'conversion.json'),JSON.stringify(reports,null,2));

} catch(error) { console.log(JSON.stringify({event:'error',message:error.message}));process.exit(1); }
