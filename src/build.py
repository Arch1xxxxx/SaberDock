import sys,json
def main():
    from pathlib import Path
    import ctypes,base64,copy,gzip,hashlib,json,struct,zipfile,zlib,shutil
    import UnityPy,soundfile as sf
    import numpy as np
    from UnityPy.streams import EndianBinaryReader
    
    import sys
    BASE=Path(sys.argv[1]).resolve()
    SETTINGS=json.loads((BASE/'job.json').read_text())
    SOURCE=Path(SETTINGS['sourceObb'])
    OUT=BASE/'payload';OUT.mkdir(exist_ok=True)
    configs=json.loads((BASE/'conversion.json').read_text())
    archive=zipfile.ZipFile(SOURCE)
    patch={};report={'songs':[],'checks':[]}
    def pcm_bytes(env,clip):
        r=clip['m_Resource'];raw=env.file.files[r['m_Source'].rsplit('/',1)[-1]].bytes;encoded=raw[r['m_Offset']:r['m_Offset']+r['m_Size']]
        magic,version,count,headers,names,size,mode=struct.unpack_from('<4s6I',encoded)
        assert magic==b'FSB5' and version==1 and count==1 and headers==8 and mode==2,'FSB PCM 格式无效'
        sample=struct.unpack_from('<Q',encoded,60)[0];channels=((sample>>5)&1)+1;frames=sample>>34
        assert frames*channels*2==size and len(encoded)==60+headers+names+size,'FSB 音频长度不一致'
        return encoded[60+headers+names:]
    
    def fsb(data,rate):
        n,ch=data.shape;assert ch in [1,2]
        pcm=data.astype('<i2').tobytes();names=struct.pack('<I',4)+b'CustomSong\0';names+=b'\0'*((-(68+len(names)))%32)
        return struct.pack('<4s6I8s16s8s',b'FSB5',1,1,8,len(names),len(pcm),2,b'\0'*8,b'\0'*16,b'\0'*8)+struct.pack('<Q',({4000:0,8000:1,11000:2,11025:3,16000:4,22050:5,24000:6,32000:7,44100:8,48000:9,96000:10}[rate]<<1)|((ch-1)<<5)|(n<<34))+names+pcm
    
    def put_audio(env,obj,data,rate,append=False):
        encoded=fsb(data,rate)
        d=obj.read_typetree();key=d['m_Resource']['m_Source'].rsplit('/',1)[-1];old=env.file.files[key]
        raw=old.bytes if append else b'';offset=(len(raw)+15)&~15
        reader=EndianBinaryReader(raw+b'\0'*(offset-len(raw))+encoded);reader.flags=old.flags;env.file.files[key]=reader
        d.update(m_Channels=data.shape[1],m_Frequency=rate,m_BitsPerSample=16,m_Length=len(data)/rate,m_CompressionFormat=0)
        d['m_Resource'].update(m_Offset=offset,m_Size=len(encoded));obj.save_typetree(d)
    
    def put_json(obj,data,name=None):
        d=obj.read_typetree()
        if name:d['m_Name']=name
        d['m_Script']=gzip.compress(json.dumps(data,separators=(',',':'),ensure_ascii=False).encode(),mtime=0).decode('utf-8','surrogateescape')
        obj.save_typetree(d)
    
    def bundle_crc(env):
        return zlib.crc32(b''.join(f.reader.bytes if hasattr(f,'reader') else f.bytes for f in env.file.files.values()))
    
    def write_bundle(env,path):
        data=env.file.save(packer='lz4');p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        check=UnityPy.load(data)
        patch[path]={'originalSha256':hashlib.sha256(archive.read(path)).hexdigest() if path in archive.namelist() else None,'patchedSha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'crc':bundle_crc(check)}
        return check
    
    
    from PIL import Image,ImageOps
    def color_scheme(cd,ident):
        rgba=lambda k,default:dict(zip('rgba',[*([cd[k][v] for v in 'rgb'] if k in cd else default),1.0]))
        return {'_colorSchemeId':ident,'_overrideNotes':int('_colorLeft' in cd or '_colorRight' in cd),
        '_saberAColor':rgba('_colorLeft',[0.75,0,0]),'_saberBColor':rgba('_colorRight',[0,0.5,1]),
        '_obstaclesColor':rgba('_obstacleColor',[1,0,0]),'_overrideLights':int('_envColorLeft' in cd and '_envColorRight' in cd),
        '_environmentColor0':rgba('_envColorLeft',[0.75,0,0]),'_environmentColor1':rgba('_envColorRight',[0,0.5,1]),
        '_environmentColor0Boost':rgba('_envColorLeftBoost',[0.75,0,0]),'_environmentColor1Boost':rgba('_envColorRightBoost',[0,0.5,1])}
    
    def progress(message):print(json.dumps({'event':'progress','message':message},ensure_ascii=False),flush=True)
    def clone(obj,name):
        ident=int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'little')&0x7fffffffffffffff
        while ident in obj.assets_file.objects:ident+=1
        new=copy.copy(obj);new.path_id=ident;new.data=obj.get_raw_data();new._read_until=None
        obj.assets_file.objects[ident]=new;return new
    
    def ptr(obj):return {'m_FileID':0,'m_PathID':obj.path_id}
    def unique_names(env,level_id):
        old=next(f.name for f in env.file.files.values() if hasattr(f,'objects'));new='CAB-'+hashlib.md5(('BeatSaberLibrary:'+level_id).encode()).hexdigest()
        for o in env.objects:
            if o.type.name=='AudioClip':
                d=o.read_typetree();d['m_Name']=level_id;d['m_Resource']['m_Source']=d['m_Resource']['m_Source'].replace(old,new);o.save_typetree(d)
            elif o.type.name=='AssetBundle':
                d=o.read_typetree();d['m_Name']=d['m_AssetBundleName']=level_id.lower()+'.1'
                d['m_Container']=[(p.replace('fitbeat',level_id.lower()),v) for p,v in d['m_Container']];o.save_typetree(d)
        files={}
        for key,f in env.file.files.items():
            key=key.replace(old,new)
            if hasattr(f,'objects'):f.name=key
            files[key]=f
        env.file.files=files
    
    packs={};known_envs={'DefaultEnvironment','GlassDesertEnvironment','BigMirrorEnvironment','NiceEnvironment','TriangleEnvironment','FitBeatEnvironment','KDAEnvironment'}
    playlist_names={g['pack']:g['name'] for g in SETTINGS['playlists']}
    for key in playlist_names:
        path=next(n for n in archive.namelist() if f'/{key}_pack_assets_all_' in n);env=UnityPy.load(archive.read(path));objs={o.path_id:o for o in env.objects}
        previews=[o for o in env.objects if o.type.name=='MonoBehaviour' and '_levelID' in o.read_typetree()]
        assert previews,'曲包模板没有歌曲'
        template=previews[0];pd=template.read_typetree();pack=next(o for o in env.objects if o.type.name=='MonoBehaviour' and '_packID' in o.read_typetree());packdata=pack.read_typetree()
        sprite=objs[packdata['_coverImage']['m_PathID']];sd=sprite.read_typetree();assert sprite.type.name=='Sprite' and sd['m_RD']['texture']['m_FileID']==0
        tex=objs[sd['m_RD']['texture']['m_PathID']]
        packs[key]={'path':path,'env':env,'template':template,'audio':objs[pd['_previewAudioClip']['m_PathID']],'sprite':sprite,'texture':tex,'levels':[],'clones':[],'covers':[],'audio_checks':[],'name':playlist_names[key]}
        for p in previews:
            d=p.read_typetree();known_envs.add(d['_environmentName']['_environmentName']);known_envs.update(v['_environmentName'] for v in d['_environmentNames'])
    
    def has_env(name):return name in known_envs or any('/'+name.lower()+'_assets_all_' in p for p in archive.namelist())
    built=set();cache_root=Path(SETTINGS.get('cache',BASE/'cache'))/'assets';cache_version=hashlib.sha256(Path(__file__).read_bytes()+json.dumps(SETTINGS.get('sourceStamp',[])).encode()+Path(__file__).with_name('convert.cjs').read_bytes()).hexdigest()
    for c in configs:
        try:
            info=c['info'];folder=Path(c['folder']);state=packs[c['pack']];env=state['env'];level_id=c['levelId']
            def local(name):
                path=(folder/name).resolve();assert path.is_relative_to(folder.resolve()),'歌曲文件路径越界';return path
            cache=cache_root/(c['contentKey']+'-'+level_id+'-'+cache_version);meta_path=cache/'meta.json';cache_hit=False
            path='assets/BeatmapLevelsData/'+c['slot']
            if meta_path.is_file():
                try:
                    meta=json.loads(meta_path.read_text());cached_bundle=cache/'bundle'
                    if cached_bundle.stat().st_size!=meta['patch']['bytes']:raise ValueError('缓存不完整')
                    audio=np.load(cache/'preview.npy',allow_pickle=False);rate=meta['rate'];n=meta['n'];duration=meta['duration'];gain=meta['gain'];peak_db=meta['peakDbFS'];cache_hit=True
                    dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(cached_bundle,dest);patch[path]=meta['patch'];built.add(path)
                except (OSError,ValueError,KeyError):cache_hit=False;shutil.rmtree(cache,ignore_errors=True)
            if not cache_hit:
                source_float,rate=sf.read(local(info['_songFilename']),dtype='float64',always_2d=True)
                assert rate in [4000,8000,11000,11025,16000,22050,24000,32000,44100,48000,96000],'不支持的音频采样率'
                assert source_float.shape[1] in [1,2] and np.isfinite(source_float).all() and len(source_float)>0,'音频必须为单声道或双声道'
                peak=float(np.abs(source_float).max());gain=min(1.,10**(-3/20)/max(peak,1e-12));audio=np.rint(source_float*gain*32767).astype('<i2');n,ch=audio.shape;duration=n/rate
                assert np.abs(audio.astype('int32')).max()<32767
                significant=np.abs(source_float*gain)>1/32767;assert np.array_equal(source_float[significant]>0,audio[significant]>0)
                songenv=UnityPy.load(archive.read('assets/BeatmapLevelsData/fitbeat'));unique_names(songenv,level_id);songenv=UnityPy.load(songenv.file.save(packer='lz4'));objects={o.path_id:o for o in songenv.objects};model=next(o for o in songenv.objects if o.type.name=='MonoBehaviour');d=model.read_typetree();d['m_Name']=level_id+'BeatmapLevelData'
                std=next(s for s in d['_difficultyBeatmapSets'] if s['_beatmapCharacteristicSerializedName']=='Standard')
                ranks={v['rank'] for v in c['difficulties']};used={v['_beatmapAsset']['m_PathID'] for v in std['_difficultyBeatmaps'] if v['_difficulty'] in ranks}
                pool=[o for o in songenv.objects if o.type.name=='TextAsset' and o.path_id not in used and o.path_id!=d['_audioDataAsset']['m_PathID']];pool.sort(key=lambda o:not o.read_typetree()['m_Name'].endswith('.lightshow.gz'));assert len(pool)>=len(ranks)
                selected=[]
                for stat,light in zip(c['difficulties'],pool):
                    item=copy.deepcopy(next(v for v in std['_difficultyBeatmaps'] if v['_difficulty']==stat['rank']));bm=json.loads((BASE/f"converted/{c['slot']}/{stat['name']}.beatmap.json").read_text());ls=json.loads((BASE/f"converted/{c['slot']}/{stat['name']}.lightshow.json").read_text())
                    put_json(objects[item['_beatmapAsset']['m_PathID']],bm);put_json(light,ls,level_id+stat['name']+'.lightshow.gz');item['_lightshowAsset']=ptr(light);selected.append(item)
                d['_difficultyBeatmapSets']=[{'_beatmapCharacteristicSerializedName':'Standard','_difficultyBeatmaps':selected}];model.save_typetree(d)
                if c.get('nativeAudioData'):
                    ad=c['nativeAudioData'];assert ad['songFrequency']==rate and ad['songSampleCount']==n,'原谱面 AudioData 与音频长度不匹配';timeline=ad['bpmData']
                else:
                    timeline=[];beat=0.;seconds=0.;bpm=info['_beatsPerMinute']
                    for event in c.get('bpmEvents') or []:
                        assert event['time']>=beat and event['bpm']>0
                        if event['time']>beat:
                            end=seconds+(event['time']-beat)*60/bpm;timeline.append({'si':round(seconds*rate),'ei':round(end*rate),'sb':beat,'eb':event['time']});seconds=end;beat=event['time']
                        bpm=event['bpm']
                    assert seconds<duration
                    timeline.append({'si':round(seconds*rate),'ei':n,'sb':beat,'eb':beat+(duration-seconds)*bpm/60})
                assert timeline[0]['si']==0 and timeline[-1]['ei']==n and all(v['ei']>v['si'] for v in timeline)
                assert all(a['ei']==b['si'] and abs(a['eb']-b['sb'])<1e-5 for a,b in zip(timeline,timeline[1:]))
                put_json(objects[d['_audioDataAsset']['m_PathID']],{'version':'4.0.0','songChecksum':base64.b64encode(hashlib.sha1(local(info['_songFilename']).read_bytes()).digest()).decode(),'songSampleCount':n,'songFrequency':rate,'bpmData':timeline,'lufsData':[]})
                put_audio(songenv,objects[d['_audioClip']['m_PathID']],audio,rate);checked=write_bundle(songenv,path);co={o.path_id:o for o in checked.objects}
                for item,stat in zip(selected,c['difficulties']):
                    bm=json.loads(gzip.decompress(co[item['_beatmapAsset']['m_PathID']].read_typetree()['m_Script'].encode('utf-8','surrogateescape')));assert len(bm['colorNotes'])==stat['notes'] and len(bm['bombNotes'])==stat['bombs'] and len(bm['obstacles'])==stat['obstacles']
                assert pcm_bytes(checked,co[d['_audioClip']['m_PathID']].read_typetree())==audio.tobytes(),'整曲音频校验失败';built.add(path)
                peak_db=float(20*np.log10(max(float(np.abs(audio.astype('float64')).max())/32768,1e-12)))
            tag=c['pack']+':'+level_id
            preview=clone(state['template'],tag+':preview');clip=clone(state['audio'],tag+':audio');sprite=clone(state['sprite'],tag+':sprite');texture=clone(state['texture'],tag+':texture');state['clones'] += [preview,clip,sprite,texture]
            expected=ImageOps.fit(Image.open(local(info['_coverImageFilename'])).convert('RGBA'),(256,256),method=Image.Resampling.LANCZOS);t=texture.read();t.m_Name=level_id+'Cover';t.set_image(expected,target_format=4,mipmap_count=1);t.save()
            sd=sprite.read_typetree();sd.update(m_Name=level_id+'Cover',m_Rect={'x':0.,'y':0.,'width':256.,'height':256.},m_PixelsToUnits=256.,m_AtlasTags=[],m_SpriteAtlas={'m_FileID':0,'m_PathID':0});sd['m_RD']['texture']=ptr(texture);sd['m_RD']['textureRect']={'x':0.,'y':0.,'width':256.,'height':256.};sd['m_RD']['uvTransform']={'x':256.,'y':128.,'z':256.,'w':128.};sprite.save_typetree(sd);state['covers'].append((sprite.path_id,expected,c['label']))
            pd=preview.read_typetree();template=copy.deepcopy(next(v for v in pd['_previewDifficultyBeatmapSets'] if v['_beatmapCharacteristic']['m_PathID']==-7286399427822119286));p0=0 if cache_hit else min(n-1,max(0,round(info['_previewStartTime']*rate)));p1=len(audio) if cache_hit else min(n,p0+max(1,round(info['_previewDuration']*rate)));put_audio(env,clip,audio[p0:p1],rate,append=True);state['audio_checks'].append((clip.path_id,hashlib.sha256(audio[p0:p1].tobytes()).hexdigest(),c['label'])) if not cache_hit else None
            pd.update(m_Name=level_id+'BeatmapLevel',_levelID=level_id,_songName=info['_songName'],_songSubName=info['_songSubName'],_songAuthorName=info['_songAuthorName'],_levelAuthorName=info['_levelAuthorName'],_beatsPerMinute=info['_beatsPerMinute'],_songTimeOffset=0.,_previewStartTime=0.,_previewDuration=(p1-p0)/rate,_songDuration=duration,_previewAudioClip=ptr(clip),_coverImage=ptr(sprite),_colorSchemes=[])
            wanted=info['_environmentName'];scene=wanted if has_env(wanted) else 'DefaultEnvironment';pd['_environmentName']={'_environmentName':scene};pd['_environmentNames']=[{'_environmentName':v if has_env(v) else 'DefaultEnvironment'} for v in info['_environmentNames']]
            diffs=[]
            for stat in c['difficulties']:
                source=next(v for v in info['_difficultyBeatmapSets'][0]['_difficultyBeatmaps'] if v['_difficulty']==stat['name']);cd=source.get('_customData',{});v=copy.deepcopy(template['_previewDifficultyBeatmaps'][0]);v.update(_difficulty=stat['rank'],_notesCount=stat['notes'],_bombsCount=stat['bombs'],_obstaclesCount=stat['obstacles'],_cuttableBeatmapObjectsCount=stat['notes']+stat['chains'],_noteJumpMovementSpeed=stat['njs'],_noteJumpStartBeatOffset=stat['offset'],_environmentNameIdx=source.get('_environmentNameIdx',0),_beatmapColorSchemeIdx=-1)
                if any(k in cd for k in ['_colorLeft','_colorRight','_obstacleColor','_envColorLeft']):v['_beatmapColorSchemeIdx']=len(pd['_colorSchemes']);pd['_colorSchemes'].append(color_scheme(cd,'Custom-'+level_id+stat['name']))
                diffs.append(v)
            template['_previewDifficultyBeatmaps']=diffs;pd['_previewDifficultyBeatmapSets']=[template];preview.save_typetree(pd);state['levels'].append(preview)
            report['songs'].append({'label':c['label'],'id':level_id,'playlist':c['playlistName'],'difficulties':c['difficulties'],'gainDb':float(20*np.log10(gain)),'peakDbFS':peak_db,'cached':cache_hit,'warnings':(['环境 '+wanted+' 不可用，已使用默认环境'] if scene!=wanted else []),'optionalSuggestions':c['optionalSuggestions']})
            if not cache_hit:
                tmp=cache.with_name(cache.name+'.new');shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(OUT/path,tmp/'bundle');np.save(tmp/'preview.npy',audio[p0:p1],allow_pickle=False)
                (tmp/'meta.json').write_text(json.dumps({'rate':rate,'n':n,'duration':duration,'gain':gain,'peakDbFS':peak_db,'patch':patch[path]}))
                shutil.rmtree(cache,ignore_errors=True);tmp.replace(cache)
            progress(('复用已处理歌曲：' if cache_hit else '音频、封面和配色：')+c['label'])
        except Exception as e:raise RuntimeError(c['label']+'：'+(str(e) or '歌曲资源校验失败')) from e
    for key,state in packs.items():
        env=state['env'];refs=[ptr(o) for o in state['levels']];allrefs=[ptr(o) for o in state['clones']]
        for o in list(env.objects):
            if o.type.name=='MonoBehaviour':
                d=o.read_typetree()
                if '_beatmapLevels' in d:d['_beatmapLevels']=refs;o.save_typetree(d)
                elif '_packID' in d:
                    d.update(_packName=state['name'],_shortPackName=state['name'],_coverImage=ptr(state['clones'][2] if state['clones'] else state['sprite']),_smallCoverImage=ptr(state['clones'][2] if state['clones'] else state['sprite']),_packBuyOption=0);o.save_typetree(d)
                elif '_beatmapLevelPack' in d and '_order' in d:
                    d['_tags']=1;d['_order']=(list(packs).index(key)+1)*10
                    for field in d['_levelProductPacks']:d['_levelProductPacks'][field]={'m_FileID':0,'m_PathID':0}
                    d['_packPromoInfoReference']={'m_AssetGUID':'','m_SubObjectName':'','m_SubObjectType':''};o.save_typetree(d)
            elif o.type.name=='AssetBundle':
                d=o.read_typetree();original=list(d['m_PreloadTable'])
                for name,item in d['m_Container']:
                    start=item['preloadIndex'];count=item['preloadSize'];item['preloadIndex']=len(d['m_PreloadTable']);d['m_PreloadTable'].extend(original[start:start+count]+allrefs);item['preloadSize']=count+len(allrefs)
                o.save_typetree(d)
        checked=write_bundle(env,state['path']);co={o.path_id:o for o in checked.objects}
        for ident,expected_hash,label in state['audio_checks']:
            assert hashlib.sha256(pcm_bytes(checked,co[ident].read_typetree())).hexdigest()==expected_hash,label+'：试听音频校验失败'
        for ident,expected,label in state['covers']:assert co[ident].read().image.convert('RGBA').tobytes()==expected.tobytes(),label+'：封面回读不一致'
        assert next(o.read_typetree() for o in checked.objects if o.type.name=='MonoBehaviour' and '_beatmapLevels' in o.read_typetree())['_beatmapLevels']==refs
    
    catalog=json.loads(archive.read('assets/aa/catalog.json'));entries=bytearray(base64.b64decode(catalog['m_EntryDataString']));extra=bytearray(base64.b64decode(catalog['m_ExtraDataString']));rows=struct.unpack_from('<I',entries)[0]
    for path,v in list(patch.items()):
        if not path.endswith('.bundle'):continue
        idx=next(i for i,n in enumerate(catalog['m_InternalIds']) if Path(path).name in n);row=next(struct.unpack_from('<7i',entries,4+i*28) for i in range(rows) if struct.unpack_from('<i',entries,4+i*28)[0]==idx)
        start=extra.find(b'{\0',row[4]);size=struct.unpack_from('<I',extra,start-4)[0];opts=json.loads(extra[start:start+size].decode('utf-16le'));assert bundle_crc(UnityPy.load(archive.read(path)))==opts['m_Crc']
        opts.update(m_Hash=hashlib.md5((OUT/path).read_bytes()).hexdigest(),m_Crc=v['crc'],m_BundleSize=v['bytes']);encoded=json.dumps(opts,separators=(',',':')).encode('utf-16le');delta=len(encoded)-size
        if delta>0:
            extra[start:start+size]=encoded;struct.pack_into('<I',extra,start-4,len(encoded))
            for i in range(rows):
                pos=4+i*28+16;off=struct.unpack_from('<i',entries,pos)[0]
                if off>row[4]:struct.pack_into('<i',entries,pos,off+delta)
        else:extra[start:start+size]=encoded+b' \0'*((-delta)//2)
    catalog['m_EntryDataString']=base64.b64encode(entries).decode();catalog['m_ExtraDataString']=base64.b64encode(extra).decode()
    keys=base64.b64decode(catalog['m_KeyDataString']);buckets=base64.b64decode(catalog['m_BucketDataString']);count=struct.unpack_from('<i',buckets)[0];pos=4;new=bytearray(struct.pack('<i',count));pack_rows=[]
    # Addressable internal paths identify the reused pack definitions.
    pack_prefixes={'ostvol1':'ost1','ostvol2':'ost2','ostvol3':'ost3','ostvol4':'ost4','ostvol5':'ost5','ostvol6':'ost6','ostvol7':'ost7'}
    for i in range(count):
        off,num=struct.unpack_from('<2i',buckets,pos);pos+=8;locs=list(struct.unpack_from(f'<{num}i',buckets,pos));pos+=4*num;tag=keys[off];key=None
        if tag in [0,1]:length=struct.unpack_from('<i',keys,off+1)[0];key=keys[off+5:off+5+length].decode('utf-8' if tag==0 else 'utf-16le')
        if key=='PackDefinition':
            def belongs(loc):
                internal=catalog['m_InternalIds'][struct.unpack_from('<i',entries,4+28*loc)[0]].lower()
                return any('/'+Path(s['path']).name in internal or f'packs.{pack_prefixes.get(p,p)}/' in internal or ('packdefinition' in internal and p.replace('_','') in internal.replace('-','').replace('_','')) for p,s in packs.items())
            locs=[loc for loc in locs if belongs(loc)];pack_rows=locs;assert len(locs)==len(packs),(len(locs),list(packs))
        new+=struct.pack('<2i',off,len(locs))+(struct.pack(f'<{len(locs)}i',*locs) if locs else b'')
    assert pack_rows and pos==len(buckets);catalog['m_BucketDataString']=base64.b64encode(new).decode();cat=json.dumps(catalog,separators=(',',':')).encode();(OUT/'assets/aa/catalog.json').write_bytes(cat);patch['assets/aa/catalog.json']={'patchedSha256':hashlib.sha256(cat).hexdigest(),'bytes':len(cat)}
    report.update(patches=patch,playlists=[{'name':s['name'],'songs':len(s['levels'])} for s in packs.values()],checks=['core beatmap round-trip','FSB PCM byte comparison','audio peaks below -3 dBFS','cover pixels after serialization','unique bundle names per song','addressable CRC and pack count','original playable songs removed'])
    progress('正在生成头显曲库文件…')
    out=BASE/'main.1716.com.beatgames.beatsaber.obb'
    with zipfile.ZipFile(out,'w',allowZip64=True) as z:
        for info in archive.infolist():
            if info.filename.startswith('assets/BeatmapLevelsData/'):continue
            if info.filename in patch:z.writestr(info,(OUT/info.filename).read_bytes())
            else:
                with archive.open(info) as a,z.open(info,'w') as dst:shutil.copyfileobj(a,dst,1024*1024)
        for path in sorted(built):z.write(OUT/path,path,compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for path,v in patch.items():
            label=next((c['label'] for c in configs if path=='assets/BeatmapLevelsData/'+c['slot']),path)
            assert hashlib.sha256(z.read(path)).hexdigest()==v['patchedSha256'],label+'：资源完整性校验失败，请重试'
    report['resourceBytes']=out.stat().st_size;report['resourceSha256']=hashlib.sha256(out.read_bytes()).hexdigest();(BASE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));progress('曲库生成并校验完成')

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'event':'error','message':'曲库处理未完成：'+(str(error) or '资源结构校验失败')},ensure_ascii=False),flush=True)
        sys.exit(1)
