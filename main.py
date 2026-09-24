from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json, time
from datetime import datetime

app = FastAPI()
users = {}
msgs = []
pinned_id = None

HTML_PAGE = """
<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Adegram</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui}
body{display:flex;height:100vh;background:#0e1621;color:#fff;overflow:hidden}
.side{width:380px;background:#17212b;display:flex;flex-direction:column;border-right:1px solid #2b5278}
@media(max-width:700px){.side{width:100%}.chat{display:none}.chat.on{display:flex;width:100%}.side.hide{display:none}}
.top{padding:12px;background:#17212b;display:flex;gap:8px;align-items:center}
.top b{color:#5288c1}
.top input{flex:1;padding:8px 12px;border-radius:20px;border:none;background:#242f3d;color:#fff;outline:none}
.list{flex:1;overflow-y:auto}
.item{padding:10px 12px;display:flex;gap:10px;align-items:center;cursor:pointer}
.item:hover,.item.act{background:#2b5278}
.ava{width:46px;height:46px;border-radius:50%;background:#5288c1;display:grid;place-items:center;font-weight:700}
.chat{flex:1;display:flex;flex-direction:column;background:#0e1621}
.head{height:54px;background:#17212b;display:flex;align-items:center;padding:0 10px;gap:10px}
.mbox{flex:1;overflow-y:auto;padding:10px 10%;display:flex;flex-direction:column;gap:4px}
.bub{max-width:68%;padding:6px 10px;border-radius:12px;font-size:14px;word-break:break-word}
.bub.me{align-self:flex-end;background:#2b5278}
.bub.you{align-self:flex-start;background:#182533}
.bub img{max-width:200px;border-radius:8px;display:block;margin-top:4px}
.bub audio{width:200px}
.meta{font-size:10px;color:#7d8b99;text-align:right;margin-top:3px}
.react{font-size:11px;background:#242f3d;border-radius:10px;padding:1px 6px;margin-top:2px;display:inline-block}
.menu{position:fixed;background:#17212b;border-radius:8px;box-shadow:0 4px 20px #0008;z-index:200;display:none;min-width:150px}
.menu div{padding:10px 14px;font-size:13px;cursor:pointer}
.menu div:hover{background:#2b5278}
.input{padding:8px;background:#17212b;display:flex;gap:6px;align-items:flex-end}
.rBar{display:none;background:#182533;padding:6px 12px;border-left:2px solid #5288c1;margin:0 8px;font-size:12px;justify-content:space-between}
.rBar.on{display:flex}
.input textarea{flex:1;background:#242f3d;border:none;border-radius:20px;padding:10px 14px;color:#fff;outline:none;resize:none}
.icon{width:42px;height:42px;border-radius:50%;border:none;background:#242f3d;color:#fff;display:grid;place-items:center;cursor:pointer}
.send{background:#5288c1}
.typ{height:16px;font-size:11px;color:#7d8b99;padding:0 12px}
.login{position:fixed;inset:0;background:#17212b;z-index:99;display:flex;align-items:center;justify-content:center}
.lbox{background:#0e1621;padding:26px;border-radius:12px;width:92%;max-width:340px;text-align:center}
.lbox input{width:100%;padding:11px;margin:8px 0;border-radius:8px;border:none;background:#242f3d;color:#fff;outline:none}
.lbox button{width:100%;padding:11px;background:#5288c1;border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer}
#fileIn{display:none}
.pin{padding:6px 12px;background:#182533;font-size:12px;display:none;gap:8px}
.pin.on{display:flex}
</style>
</head><body>
<div class="login" id="log"><div class="lbox"><h2 style="color:#5288c1">ADEGRAM ULTIMATE</h2><input id="n" placeholder="Your name"><button onclick="join()">JOIN</button></div></div>
<div class="side" id="side"><div class="top"><b>Adegram</b><input id="s" placeholder="Search" oninput="filt()"></div><div class="list" id="list"></div></div>
<div class="chat" id="chat">
<div class="head"><span id="back" style="display:none;cursor:pointer" onclick="showSide()">←</span><div class="ava" id="cAva">G</div><div style="flex:1"><div id="cName">General</div><div id="cStat" style="font-size:11px;color:#7d8b99">real-time</div></div><div id="oCnt" style="font-size:11px"></div></div>
<div class="pin" id="pinBar"><span>📌</span><span id="pinTxt" style="flex:1"></span><span onclick="unpin()" style="cursor:pointer">✕</span></div>
<div class="mbox" id="mbox"></div>
<div class="typ" id="typ"></div>
<div class="rBar" id="rBar"><div><div id="rWho" style="color:#5288c1"></div><div id="rTxt"></div></div><span onclick="cancelR()" style="cursor:pointer">✕</span></div>
<div class="input">
<button class="icon" onclick="document.getElementById('fileIn').click()">📎</button>
<input type="file" id="fileIn" onchange="sendFile(this)">
<button class="icon" id="rec" onmousedown="sRec()" onmouseup="eRec()" ontouchstart="sRec()" ontouchend="eRec()">🎤</button>
<textarea id="t" rows="1" placeholder="Message" oninput="grow(this);typing()" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
<button class="icon send" onclick="send()">➤</button>
</div>
</div>
<div class="menu" id="menu">
<div onclick="doReply()">↩ Reply</div>
<div onclick="doReact('❤️')">❤️</div>
<div onclick="doReact('😂')">😂</div>
<div onclick="doReact('🔥')">🔥</div>
<div onclick="doPin()">📌 Pin</div>
<div onclick="doEdit()">✏ Edit</div>
<div onclick="doDel()" style="color:#ff5a5a">🗑 Delete</div>
</div>
<script>
let ws, myName, cur='General', curType='group', allUsers=[], allMsgs=[], replyTo=null, selMsg=null, mRec, chunks=[];
function join(){
 myName=document.getElementById('n').value.trim(); if(!myName)return alert('name');
 document.getElementById('log').style.display='none';
 if(innerWidth<=700) document.getElementById('back').style.display='block';
 let p=location.protocol==='https:'?'wss://':'ws://';
 ws=new WebSocket(p+location.host+'/ws/'+encodeURIComponent(myName));
 ws.onmessage=e=>{
  let d=JSON.parse(e.data);
  if(d.type==='init'){allUsers=d.users; allMsgs=d.msgs; render(); allMsgs.forEach(m=>{if(ok(m)) draw(m)}); upd(d.users); if(d.pinned) showPin(d.pinned)}
  else if(d.type==='msg'){allMsgs.push(d); if(ok(d)) draw(d)}
  else if(d.type==='users'){allUsers=d.users; render(); upd(d.users)}
  else if(d.type==='typing'){if(d.from!==myName){document.getElementById('typ').innerText=d.from+' typing...'; setTimeout(()=>document.getElementById('typ').innerText='',1200)}}
  else if(d.type==='delete'){allMsgs=allMsgs.filter(m=>m.id!==d.id); refresh()}
  else if(d.type==='edit'){let m=allMsgs.find(x=>x.id===d.id); if(m){m.text=d.text; m.edited=true; refresh()}}
  else if(d.type==='react'){let m=allMsgs.find(x=>x.id===d.id); if(m){m.reacts=m.reacts||{}; m.reacts[d.from]=d.emoji; refresh()}}
  else if(d.type==='pin'){showPin(d.msg)} else if(d.type==='unpin'){document.getElementById('pinBar').classList.remove('on')}
 };
}
function ok(m){ if(curType==='group') return m.to==='General'; return (m.sender===myName&&m.to===cur)||(m.sender===cur&&m.to===myName); }
function upd(u){document.getElementById('oCnt').innerText=u.length+' online'}
function render(f=''){ let l=document.getElementById('list'); l.innerHTML=''; let add=(name,sub,ico)=>{ if(f&&!name.toLowerCase().includes(f))return; let d=document.createElement('div'); d.className='item'+(cur===name?' act':''); d.innerHTML=`<div class="ava">${ico}</div><div style="flex:1"><div>${name}</div><div style="font-size:11px;color:#7d8b99">${sub}</div></div>`; d.onclick=()=>openC(name); l.appendChild(d); }; add('General','Group chat','G'); allUsers.forEach(u=>{ if(u.name!==myName) add(u.name,u.online?'online':'offline',u.name[0].toUpperCase()) }); }
function openC(name){ cur=name; curType=name==='General'?'group':'private'; document.getElementById('cName').innerText=name; document.getElementById('cAva').innerText=name[0].toUpperCase(); refresh(); if(innerWidth<=700){document.getElementById('side').classList.add('hide');document.getElementById('chat').classList.add('on')} }
function showSide(){document.getElementById('side').classList.remove('hide');document.getElementById('chat').classList.remove('on')}
function refresh(){ document.getElementById('mbox').innerHTML=''; allMsgs.forEach(m=>{ if(ok(m)) draw(m) }); }
function draw(m){
 let b=document.getElementById('mbox'); let div=document.createElement('div'); div.className='bub '+(m.sender===myName?'me':'you');
 let rep=''; if(m.replyTo){ let rm=allMsgs.find(x=>x.id===m.replyTo); if(rm) rep=`<div style="border-left:2px solid #5288c1;background:#0004;padding:3px 6px;font-size:11px;margin-bottom:3px">${rm.sender}: ${(rm.text||'media').slice(0,30)}</div>`; }
 let ct=rep; if(m.sender!==myName && curType==='group') ct+=`<div style="font-size:11px;color:#7fc0ff">${m.sender}</div>`;
 if(m.deleted) ct+='<i>deleted</i>';
 else if(m.mtype==='text') ct+=`<div>${esc(m.text)}${m.edited?' (edited)':''}</div>`;
 else if(m.mtype==='image') ct+=`<img src="${m.data}"><div>${esc(m.text||'')}</div>`;
 else if(m.mtype==='audio') ct+=`<audio controls src="${m.data}"></audio>`;
 else ct+=`<a href="${m.data}" download="${m.fname}" style="color:#7fc0ff">${m.fname||'file'}</a>`;
 if(m.reacts){ let r=Object.values(m.reacts).join(' '); if(r) ct+=`<div class="react">${r}</div>`; }
 ct+=`<div class="meta">${m.time} ${m.sender===myName?'✓✓':''}</div>`;
 div.innerHTML=ct; div.oncontextmenu=e=>{e.preventDefault(); openM(e,m)}; let pr; div.ontouchstart=e=>{pr=setTimeout(()=>openM(e,m),600)}; div.ontouchend=()=>clearTimeout(pr);
 b.appendChild(div); b.scrollTop=b.scrollHeight;
}
function esc(s){ let d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }
function grow(el){ el.style.height=''; el.style.height=Math.min(el.scrollHeight,110)+'px'; }
function typing(){ ws.send(JSON.stringify({type:'typing',to:cur})); }
function send(){ let el=document.getElementById('t'); let txt=el.value.trim(); if(!txt)return; if(selMsg&&selMsg._edit){ ws.send(JSON.stringify({type:'edit',id:selMsg.id,text:txt})); selMsg=null; el.value=''; cancelR(); return; } ws.send(JSON.stringify({type:'msg',mtype:'text',text:txt,to:cur,replyTo:replyTo})); el.value=''; cancelR(); }
function sendFile(inp){ let f=inp.files[0]; if(!f)return; if(f.size>8000000)return alert('Max 8MB'); let r=new FileReader(); r.onload=e=>{ let mt=f.type.startsWith('image/')?'image':f.type.startsWith('audio/')?'audio':'file'; ws.send(JSON.stringify({type:'msg',mtype:mt,data:e.target.result,fname:f.name,to:cur,replyTo:replyTo})); }; r.readAsDataURL(f); inp.value=''; cancelR(); }
function openM(e,m){ selMsg=m; let menu=document.getElementById('menu'); let x=e.touches?e.touches[0].clientX:e.clientX; let y=e.touches?e.touches[0].clientY:e.clientY; menu.style.left=x+'px'; menu.style.top=y+'px'; menu.style.display='block'; }
document.addEventListener('click',()=>document.getElementById('menu').style.display='none');
function doReply(){ replyTo=selMsg.id; document.getElementById('rBar').classList.add('on'); document.getElementById('rWho').innerText=selMsg.sender; document.getElementById('rTxt').innerText=(selMsg.text||'media').slice(0,30); }
function cancelR(){ replyTo=null; document.getElementById('rBar').classList.remove('on'); }
function doDel(){ ws.send(JSON.stringify({type:'delete',id:selMsg.id})); }
function doEdit(){ if(selMsg.sender!==myName)return alert('Only yours'); selMsg._edit=true; document.getElementById('t').value=selMsg.text; document.getElementById('rBar').classList.add('on'); document.getElementById('rWho').innerText='Editing'; }
function doReact(em){ ws.send(JSON.stringify({type:'react',id:selMsg.id,emoji:em})); }
function doPin(){ ws.send(JSON.stringify({type:'pin',id:selMsg.id})); }
function unpin(){ ws.send(JSON.stringify({type:'unpin'})); }
function showPin(m){ document.getElementById('pinBar').classList.add('on'); document.getElementById('pinTxt').innerText=m?m.sender+': '+(m.text||'media'):'Pinned'; }
function filt(){ render(document.getElementById('s').value.toLowerCase()); }
async function sRec(){ try{ let st=await navigator.mediaDevices.getUserMedia({audio:true}); mRec=new MediaRecorder(st); chunks=[]; mRec.ondataavailable=e=>chunks.push(e.data); mRec.onstop=()=>{ let bl=new Blob(chunks,{type:'audio/webm'}); let r=new FileReader(); r.onload=e=>ws.send(JSON.stringify({type:'msg',mtype:'audio',data:e.target.result,fname:'voice.webm',to:cur})); r.readAsDataURL(bl); st.getTracks().forEach(t=>t.stop()); }; mRec.start(); document.getElementById('rec').style.background='#ff3b30'; }catch{} }
function eRec(){ if(mRec&&mRec.state==='recording'){ mRec.stop(); document.getElementById('rec').style.background='#242f3d'; } }
</script>
</body></html>
"""

@app.get("/")
async def home():
    return HTMLResponse(HTML_PAGE)

@app.websocket("/ws/{name}")
async def ws_ep(websocket: WebSocket, name: str):
    await websocket.accept()
    users[name] = {"ws": websocket, "name": name, "online": True, "last_seen": datetime.now().strftime("%H:%M")}
    await websocket.send_text(json.dumps({
        "type": "init",
        "users": [{"name": u, "online": v["online"], "last_seen": v["last_seen"]} for u,v in users.items()],
        "msgs": msgs[-200:],
        "pinned": next((m for m in msgs if m["id"] == pinned_id), None)
    }))
    for u,v in users.items():
        if u != name:
            try:
                await v["ws"].send_text(json.dumps({"type":"users","users":[{"name": x, "online": y["online"], "last_seen": y["last_seen"]} for x,y in users.items()]}))
            except:
                pass
    try:
        while True:
            raw = await websocket.receive_text()
            obj = json.loads(raw)
            t = obj.get("type")
            if t == "typing":
                for uname, udata in users.items():
                    if uname == name: continue
                    try:
                        await udata["ws"].send_text(json.dumps({"type":"typing","from":name,"to":obj.get("to","General")}))
                    except:
                        pass
                continue
            if t == "delete":
                mid = obj.get("id")
                m = next((x for x in msgs if x["id"]==mid), None)
                if m and m["sender"]==name:
                    m["deleted"]=True
                    for ud in users.values():
                        try: await ud["ws"].send_text(json.dumps({"type":"delete","id":mid}))
                        except: pass
                continue
            if t == "edit":
                mid = obj.get("id")
                m = next((x for x in msgs if x["id"]==mid), None)
                if m and m["sender"]==name:
                    m["text"]=obj.get("text","")[:1000]
                    m["edited"]=True
                    for ud in users.values():
                        try: await ud["ws"].send_text(json.dumps({"type":"edit","id":mid,"text":m["text"]}))
                        except: pass
                continue
            if t == "react":
                mid = obj.get("id")
                m = next((x for x in msgs if x["id"]==mid), None)
                if m:
                    m.setdefault("reacts",{})[name]=obj.get("emoji","❤️")
                    for ud in users.values():
                        try: await ud["ws"].send_text(json.dumps({"type":"react","id":mid,"emoji":obj.get("emoji"),"from":name}))
                        except: pass
                continue
            if t == "pin":
                global pinned_id
                pinned_id = obj.get("id")
                pm = next((x for x in msgs if x["id"]==pinned_id), None)
                for ud in users.values():
                    try: await ud["ws"].send_text(json.dumps({"type":"pin","msg":pm}))
                    except: pass
                continue
            if t == "unpin":
                pinned_id = None
                for ud in users.values():
                    try: await ud["ws"].send_text(json.dumps({"type":"unpin"}))
                    except: pass
                continue
            if t == "msg":
                msg = {
                    "id": int(time.time()*1000),
                    "type": "msg",
                    "sender": name,
                    "to": obj.get("to","General"),
                    "mtype": obj.get("mtype","text"),
                    "text": obj.get("text","")[:1000],
                    "data": obj.get("data",""),
                    "fname": obj.get("fname",""),
                    "replyTo": obj.get("replyTo"),
                    "time": datetime.now().strftime("%H:%M"),
                    "reacts": {}
                }
                msgs.append(msg)
                if len(msgs)>500: msgs.pop(0)
                if msg["to"]=="General":
                    for ud in users.values():
                        try: await ud["ws"].send_text(json.dumps(msg))
                        except: pass
                else:
                    for target in [msg["to"], name]:
                        if target in users:
                            try: await users[target]["ws"].send_text(json.dumps(msg))
                            except: pass
    except WebSocketDisconnect:
        if name in users:
            users[name]["online"]=False
            users[name]["last_seen"]=datetime.now().strftime("%H:%M")
        for ud in users.values():
            try:
                await ud["ws"].send_text(json.dumps({"type":"users","users":[{"name":x,"online":y["online"],"last_seen":y["last_seen"]} for x,y in users.items()]}))
            except:
                pass
