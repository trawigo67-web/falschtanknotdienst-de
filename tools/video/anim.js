const $=id=>document.getElementById(id), NS='http://www.w3.org/2000/svg';
const cl=x=>Math.max(0,Math.min(1,x)), p=(t,a,b)=>cl((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3), ei=x=>x*x*x, eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const back=x=>{const c=1.70158,c3=c+1;return 1+c3*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const pop=(el,x,cx,cy)=>{const s=x<=0?0:back(cl(x));el.setAttribute('transform',`translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})`);el.style.opacity=x<=0?0:1};
const popg=(el,x,cx,cy)=>{const s=x<=0?0:back(cl(x));el.setAttribute('transform',`translate(${cx} ${cy}) scale(${s})`);el.style.opacity=x<=0?0:1};
const lerp=(a,b,x)=>a+(b-a)*x;

const QS=new URLSearchParams(location.search);
const LANG=QS.get('lang')||'de', V=QS.get('fmt')==='v', BRAND=QS.get('brand')||'nd';
const W=V?1080:1920, H=V?1920:1080;
const root=$('root');root.setAttribute('width',W);root.setAttribute('height',H);root.setAttribute('viewBox',`0 0 ${W} ${H}`);
$('bg').setAttribute('width',W);$('bg').setAttribute('height',H);

const BR={
 nd:{w:['falschtank','not','dienst','.de'],van:['Falschtank-','Notdienst'],name:'Falschtank-Notdienst'},
 td:{w:['Tankdoktor','','','.de'],van:['Tankdoktor','Soforthilfe'],name:'Tankdoktor'}
}[BRAND];
// Grundzeiten (deutsche Aufnahme): daran sind die Bewegungen ausgerichtet
const DB=[7.08,7.66,7.93,6.91,11.17,5.65,4.5];
const L={
 de:{B:[0,7.08,14.74,22.67,29.58,40.75,46.40,50.90,57.80],
  T:[['KEINE PANIK','Falsch getankt?','Keine Panik. Das lässt sich|meist schnell beheben.'],
     ['SCHRITT 1','Motor nicht|starten.','Auch die Zündung aus lassen,|selbst zum Umparken.'],
     ['SCHON GEFAHREN?','Sofort sicher|anhalten.','Motor abstellen und|nicht erneut starten.'],
     ['SCHRITT 2','Auto zur Seite|schieben.','Gang raus, Warnblinker an.'],
     ['SCHRITT 3','Rufen Sie|uns an.','Was getankt? Wie viel?|Welches Fahrzeug? Wo stehen Sie?'],
     ['SCHRITT 4','Wir kommen|zu Ihnen.','Abpumpen und spülen,|direkt vor Ort.'],
     ['GESCHAFFT','Einfach|weiterfahren.','In den meisten Fällen|direkt nach dem Einsatz.']],
  pump:'DIESEL',tag:'Benziner',chip1:'Sicher anhalten',chip2:'Motor aus',call:'Jetzt anrufen',price:'Festpreis direkt am Telefon',
  gauge:'Falscher Kraftstoff im Tank',done:'Abgepumpt und gespült',
  Q:['Was haben Sie getankt?','Wie viel?','Welches Fahrzeug?','Wo stehen Sie?'],
  tagline:['Falsch getankt?','Wir pumpen vor Ort ab.'],
  N:[['NRW, Hessen, Rheinland-Pfalz','0174 243 22 22'],['Bayern','0170 404 45 55'],['Frankfurt und Rhein-Main','01521 130 35 70']],
  open:['Rund um die Uhr erreichbar,','auch sonn- und feiertags'],openShort:'Rund um die Uhr erreichbar'},
 tr:{B:[0,6.25,12.59,18.75,24.13,33.35,39.40,42.50,49.70],
  T:[['PANİK YOK','Yanlış yakıt mı?','Panik yapmayın. Çoğu zaman|hızlıca çözülür.'],
     ['1. ADIM','Motoru|çalıştırmayın.','Kontağı da açmayın,|kısa bir mesafe için bile.'],
     ['YOLA ÇIKTINIZ MI?','Hemen güvenle|durun.','Motoru kapatın ve|tekrar çalıştırmayın.'],
     ['2. ADIM','Aracı kenara|itin.','Vites boşta, dörtlüler açık.'],
     ['3. ADIM','Bizi arayın.','Ne doldurdunuz? Kaç litre?|Hangi araç? Neredesiniz?'],
     ['4. ADIM','Yanınıza|geliyoruz.','Boşaltma ve temizleme,|hepsi yerinde.'],
     ['TAMAM','Yolunuza|devam edin.','Çoğu durumda işlemden|hemen sonra.']],
  pump:'DİZEL',tag:'Benzinli araç',chip1:'Güvenli durun',chip2:'Motor kapalı',call:'Hemen arayın',price:'Sabit fiyat hemen telefonda',
  gauge:'Depoda yanlış yakıt',done:'Boşaltıldı ve temizlendi',
  Q:['Ne doldurdunuz?','Kaç litre?','Hangi araç?','Neredesiniz?'],
  tagline:['Yanlış yakıt mı?','Yerinde boşaltıyoruz.'],
  N:[['NRW, Hessen, Rheinland-Pfalz','0174 243 22 22'],['Bavyera','0170 404 45 55'],['Frankfurt ve Rhein-Main','01521 130 35 70']],
  open:['7/24 ulaşabilirsiniz,','pazar ve tatil günleri de'],openShort:'7/24 ulaşabilirsiniz'}
}[LANG];
if(QS.get('end'))L.B[8]=+QS.get('end');
const B=L.B,T=L.T;
const TD=BRAND=='td', WF=TD?' style="font-family:SSC" ':'';
if(TD){$('mark').innerHTML='<path d="M105 31.8L143.7 91.8Q148.8 99.7 150.8 108.9Q151.7 112.9 151.9 117L126.3 117L120.8 107.5Q119.5 105.4 117.2 104.7Q114.8 104.1 112.6 105.3Q110.4 106.6 109.8 109L104.5 128.9L94.4 87.3Q93.6 84.1 90.6 83Q88.3 82.2 86 83.2Q83.8 84.3 82.9 86.6L71.9 117L48.1 117Q48.3 112.9 49.2 108.9Q51.2 99.7 56.3 91.8L95 31.8Q95.8 30.5 97.1 29.8Q98.5 29.1 100 29.1Q101.5 29.1 102.9 29.8Q104.2 30.5 105 31.8ZM151.2 129Q149.7 137.4 145.7 144.9Q141.2 153.1 134.1 159.3Q127 165.4 118.2 168.7Q109.4 172 100 172Q90.6 172 81.8 168.7Q73 165.4 65.9 159.3Q58.8 153.1 54.3 144.9Q50.3 137.4 48.8 129L76.1 129Q80.3 129 81.7 125.1L87.4 109.4L98.3 154.6Q98.9 157 101 158.3Q103.2 159.6 105.6 159Q109 158.2 110 154.7L117.7 126Q119.4 129 122.9 129L151.2 129Z" fill="#FF8A1F"/>';$('tWord').style.fontFamily='SSC';$('tWord').setAttribute('font-size',48);$('tWord').setAttribute('y',96);$('tVan1').style.fontFamily='SSC';$('tVan1').setAttribute('font-size',36);$('tVan2').setAttribute('font-size',22);$('tVan2').setAttribute('y',114);}
const wm=(c1,c2,c3)=>`<tspan fill="${c1}">${BR.w[0]}</tspan><tspan fill="${c2}">${BR.w[1]}</tspan><tspan fill="${c1}">${BR.w[2]}</tspan><tspan fill="${c3}" font-weight="600">${BR.w[3]}</tspan>`;

// Texte in den Bildern
$('tPump').textContent=L.pump;$('tTag').textContent=L.tag;$('tChip1').textContent=L.chip1;$('tChip2').textContent=L.chip2;
$('tCall').textContent=L.call;$('tPrice').textContent=L.price;$('s6gt').textContent=L.gauge;$('tDone').textContent=L.done;
$('tVan1').textContent=BR.van[0];$('tVan2').textContent=BR.van[1];$('tCallSub').textContent=BR.name;
$('tWord').innerHTML=wm('#1F1620','#C8146F','#8A7C85');

for(let i=0;i<7;i++){const c=document.createElementNS(NS,'circle');c.setAttribute('cx',i*38);c.setAttribute('r',10);c.id='dot'+i;$('dots').appendChild(c)}
for(let i=0;i<24;i++){const r=document.createElementNS(NS,'rect');r.setAttribute('y',783);r.setAttribute('width',90);r.setAttribute('height',8);r.setAttribute('rx',4);r.setAttribute('fill','#F7F3F6');r.id='ln'+i;$('s3lane').appendChild(r)}
L.Q.forEach((q,i)=>{const g=document.createElementNS(NS,'g');g.id='q'+i;const y=230+i*100;
 g.innerHTML=`<rect x="900" y="${y-42}" width="640" height="84" rx="42" fill="#fff" stroke="#E7DCE3" stroke-width="3"/><circle cx="944" cy="${y}" r="28" fill="#FF8A1F"/><text x="944" y="${y+13}" text-anchor="middle" font-size="34" font-weight="800" fill="#1C1305">${i+1}</text><text x="996" y="${y+14}" font-size="40" font-weight="700" fill="#1F1620">${q}</text>`;$('s5list').appendChild(g)});

// Abspann
{let h=`<rect width="${W}" height="${H}" fill="url(#end)"/>`;
 if(!V){
  h+=`<g id="e1"><g transform="translate(860 90)"><rect width="200" height="200" rx="44" fill="#fff" opacity=".14"/><use href="#mark"/></g>
  <text x="960" y="408" text-anchor="middle" ${WF} font-size="${TD?136:104}" font-weight="800" letter-spacing="${TD?0:-2}">${wm('#fff','#FFA94A','#F3C9DE')}</text>
  <text x="960" y="482" text-anchor="middle" font-size="44" font-weight="500" fill="#fff" opacity=".92">${L.tagline.join(' ')}</text></g><g id="cards">`;
  L.N.forEach((n,i)=>{const x=120+i*573;h+=`<g id="card${i}"><rect x="${x}" y="580" width="533" height="290" rx="36" fill="#1F1620"/><text x="${x+266}" y="660" text-anchor="middle" font-size="33" font-weight="600" fill="#fff" opacity=".85">${n[0]}</text><text x="${x+266}" y="762" text-anchor="middle" font-size="64" font-weight="800" fill="#FF8A1F" letter-spacing="-1">${n[1]}</text><text x="${x+266}" y="826" text-anchor="middle" font-size="30" font-weight="700" fill="#fff">${L.call}</text></g>`});
  h+=`</g><g id="e3"><rect x="390" y="930" width="1140" height="80" rx="40" fill="#fff" opacity=".14"/><text x="960" y="983" text-anchor="middle" font-size="38" font-weight="700" fill="#fff">${L.open.join(' ')}</text></g>`;
 }else{
  h+=`<g id="e1"><g transform="translate(440 230)"><rect width="200" height="200" rx="44" fill="#fff" opacity=".14"/><use href="#mark"/></g>
  <text x="540" y="548" text-anchor="middle" ${WF} font-size="${TD?140:80}" font-weight="800" letter-spacing="${TD?0:-2}">${wm('#fff','#FFA94A','#F3C9DE')}</text>
  <text x="540" y="630" text-anchor="middle" font-size="46" font-weight="500" fill="#fff" opacity=".92">${L.tagline[0]}</text>
  <text x="540" y="690" text-anchor="middle" font-size="46" font-weight="500" fill="#fff" opacity=".92">${L.tagline[1]}</text></g><g id="cards">`;
  L.N.forEach((n,i)=>{const y=790+i*250;h+=`<g id="card${i}"><rect x="90" y="${y}" width="900" height="220" rx="40" fill="#1F1620"/><text x="540" y="${y+62}" text-anchor="middle" font-size="36" font-weight="600" fill="#fff" opacity=".85">${n[0]}</text><text x="540" y="${y+152}" text-anchor="middle" font-size="88" font-weight="800" fill="#FF8A1F" letter-spacing="-1">${n[1]}</text><text x="540" y="${y+198}" text-anchor="middle" font-size="28" font-weight="700" fill="#fff">${L.call}</text></g>`});
  h+=`</g><g id="e3"><rect x="150" y="1570" width="780" height="140" rx="50" fill="#fff" opacity=".14"/><text x="540" y="1630" text-anchor="middle" font-size="40" font-weight="700" fill="#fff">${L.open[0]}</text><text x="540" y="1682" text-anchor="middle" font-size="40" font-weight="700" fill="#fff">${L.open[1]}</text></g>`;
 }
 $('endc').innerHTML=h;}

// Hochformat: Kopf, Fußzeile, Textstil
if(V){
 $('top').setAttribute('transform',`translate(${540-1.35*372} 90) scale(1.35)`);
 $('dots').setAttribute('transform','translate(426 300)');
 $('foot').innerHTML=`<rect x="130" y="1590" width="820" height="124" rx="62" fill="#1F1620"/><circle cx="200" cy="1652" r="44" fill="#FF8A1F"/><g transform="translate(173 1625) scale(2.25)"><path d="M8.4 3.4 5.3 4.3c-.9 6 5.2 14.7 13.4 15.4l1.1-3-3.7-2.3-1.9 1.7c-2.2-1.1-4.2-3.5-5-5.7l1.8-1.7z" fill="#1C1305"/></g><text x="${BRAND=='nd'?585:585}" y="${TD?1674:1669}" text-anchor="middle" ${WF} font-size="${TD?72:50}" font-weight="800">${wm('#fff','#FFA94A','#BCBEC3')}</text><text x="540" y="1790" text-anchor="middle" font-size="38" font-weight="600" fill="#5C4E57">${L.openShort}</text>`;
 $('head').style.fontSize='98px';$('sub').style.fontSize='46px';$('chipt').style.fontSize='32px';
 $('chipr').setAttribute('height',60);$('chipr').setAttribute('rx',30);
}
const lines=(el,str,x,y,lh,anchor)=>{el.innerHTML=str.split('|').map((l,i)=>`<tspan x="${x}" y="${y+i*lh}">${l}</tspan>`).join('');el.setAttribute('text-anchor',anchor)};

let curTxt=-1;
function setTime(t){
  let si=0;for(let i=0;i<7;i++)if(t>=B[i])si=i;
  const scenes=['s1','s2','s3','s4','s5','s6','s7'];
  scenes.forEach((id,i)=>{const a=B[i],b=i==6?B[8]:B[i+1];
    let o=Math.min(p(t,a,a+.35),1-p(t,b-.3,b)); if(i==0)o=1-p(t,b-.3,b); if(i==6)o=p(t,a,a+.35);
    const el=$(id);el.style.opacity=o;el.style.display=(t>=a-.01&&t<b+.01)?'':'none'});
  if(si!==curTxt){curTxt=si;$('chipt').textContent=T[si][0];
    if(V){lines($('head'),T[si][1],540,570,106,'middle');lines($('sub'),T[si][2],540,790,60,'middle');
      $('chipt').setAttribute('x',540);$('chipt').setAttribute('y',441);$('chipt').setAttribute('text-anchor','middle');
      const w=$('chipt').getComputedTextLength()+64;$('chipr').setAttribute('width',w);$('chipr').setAttribute('x',540-w/2);$('chipr').setAttribute('y',400);
    }else{lines($('head'),T[si][1].replace('|',' '),118,952,0,'start');lines($('sub'),T[si][2].replace('|',' '),120,1022,0,'start');
      $('chipt').setAttribute('x',146);$('chipt').setAttribute('y',847);
      const w=$('chipt').getComputedTextLength()+52;$('chipr').setAttribute('width',w);$('chipr').setAttribute('x',120);$('chipr').setAttribute('y',812);}}
  const a=B[si],b=B[si+1],lt0=t-a,d0=b-a;
  const lt=lt0*DB[si]/d0, d=DB[si];           // auf die Grundzeiten umgerechnet
  const out=si<6?1-p(t,b-.3,b):1;
  const k1=eo(p(lt0,.15,.6)),k2=eo(p(lt0,.3,.8));
  const subAt={0:1.6,1:3.6,2:3.4,3:3.0,4:1.9,5:2.4,6:1.4}[si]; const k3=eo(p(lt,subAt,subAt+.5));
  $('chipg').style.opacity=k1*out;$('chipg').setAttribute('transform',`translate(0 ${(1-k1)*24})`);
  $('head').style.opacity=k2*out;$('head').setAttribute('transform',`translate(0 ${(1-k2)*30})`);
  $('sub').style.opacity=k3*out;$('sub').setAttribute('transform',`translate(0 ${(1-k3)*20})`);
  for(let i=0;i<7;i++)$('dot'+i).setAttribute('fill',i<=si?'#C8146F':'#DCCFD7');
  const blinkOn=(tt)=>Math.floor(tt*2.6)%2==0;
  let cx=960,z=.75;

  if(si==0){ cx=905; pop($('s1tag'),p(lt,.7,1.1),1095,366); pop($('s1bang'),p(lt,1.0,1.45),1480,400);
    if(lt>1.45){const w=1+0.05*Math.sin(lt*7);$('s1bang').setAttribute('transform',`translate(1480 400) scale(${w}) translate(-1480 -400)`);}}
  if(si==1){ cx=970; const pu=1+0.02*Math.sin(lt*4);$('s2btn').setAttribute('transform',`translate(640 440) scale(${pu})`);
    const x1=p(lt,1.9,2.4);$('s2ban1').setAttribute('transform',`translate(640 440) scale(${x1<=0?0:(2-back(x1))})`);$('s2ban1').style.opacity=x1;
    const kx=eo(p(lt,.5,1.1));$('s2key').style.opacity=kx;$('s2key').setAttribute('transform',`translate(${1280+(1-kx)*80} 440)`);
    const x2=p(lt,4.1,4.6);$('s2ban2').setAttribute('transform',`translate(1300 440) scale(${x2<=0?0:(2-back(x2))*.86})`);$('s2ban2').style.opacity=x2;}
  if(si==2){ cx=965; const m=eo(p(lt,0,4.0)); const x=-900+m*(560+900);
    $('s3car').setAttribute('transform',`translate(${x} 444)`);
    const off=(m*2600)%240; for(let i=0;i<24;i++)$('ln'+i).setAttribute('x',(i-5)*240-off);
    $('s3blink').style.opacity=(lt>1.2&&blinkOn(lt))?1:0;
    popg($('s3chip1'),p(lt,3.3,3.7),735,300); popg($('s3chip2'),p(lt,5.0,5.4),1230,300);}
  if(si==3){ const m=eio(p(lt,.8,d-.6)); const x=560+m*(V?520:440); cx=lerp(780,1290,m);
    $('s4grp').setAttribute('transform',`translate(${x} 760)`);
    const ph=m*26, s1=Math.sin(ph), s2=Math.sin(ph+Math.PI);
    $('s4leg1').setAttribute('d',`M-70 -150L${-110+s1*46} -12`);$('s4leg2').setAttribute('d',`M-70 -150L${-110+s2*46} -12`);
    $('s4blink').style.opacity=blinkOn(lt)?1:0;
    const ax=p(lt,1.0,1.5);$('s4arrow').style.opacity=ax*(0.6+0.4*Math.sin(lt*5));$('s4arrow').setAttribute('transform',`translate(${(V?1380:1560)+m*(V?330:0)+Math.sin(lt*5)*14} ${V?300:360}) scale(1.2)`);}
  if(si==4){ cx=920; const ring=(el,ph)=>{const r=((lt*0.9+ph)%1);el.setAttribute('r',80+r*110);el.style.opacity=(1-r)*.9}; ring($('s5r1'),0);ring($('s5r2'),.5);
    const sh=lt<1.6?Math.sin(lt*38)*3*(1-lt/1.6):0;$('s5phone').setAttribute('transform',`translate(470 440) rotate(${sh})`);
    const at=[2.4,4.3,5.2,6.8];
    for(let i=0;i<4;i++){const k=eo(p(lt,at[i],at[i]+.4));const g=$('q'+i);g.style.opacity=k;g.setAttribute('transform',`translate(${(1-k)*70} 0)`)}
    pop($('s5price'),p(lt,8.4,8.85),1220,686);}
  if(si==5){ const m=eo(p(lt,0,1.5)); const x=-900+m*(900+20); {const zz=eio(p(lt,1.3,2.5));cx=lerp(760,945,zz);z=lerp(.75,.585,zz);}
    $('s6van').setAttribute('transform',`translate(${x} 418)`);
    $('s6glow').style.opacity=blinkOn(lt*1.3)?.34:0;
    $('s6hose').style.opacity=p(lt,1.5,2.0);
    $('s6flow').setAttribute('stroke-dashoffset',-lt*120);
    $('s6gauge').style.opacity=eo(p(lt,1.3,1.7))*(1-p(lt,4.2,4.4));
    const dr=eio(p(lt,2.0,4.2));$('s6bar').setAttribute('width',Math.max(0,464*(1-dr)));$('s6bar').style.opacity=dr>=1?0:1;
    $('s6flow').style.opacity=dr>=1?0:1;
    popg($('s6done'),p(lt,4.35,4.75),1390,315);}
  if(si==6){ const m=ei(p(lt,.5,3.6)); const x=1060+m*1300; cx=945;z=.585;
    $('s7car').setAttribute('transform',`translate(${x} 434)`);
    $('s7lines').setAttribute('transform',`translate(${x} 434)`);$('s7lines').style.opacity=.5*p(lt,.9,1.6);}
  $('stage').setAttribute('transform',V?`translate(${540-cx*z} ${1460-760*z}) scale(${z})`:'');
  // Abspann
  const e=p(t,B[7]-.25,B[7]+.35);$('endc').style.opacity=e;$('endc').style.display=e>0?'':'none';
  const et=t-B[7];
  const a1=eo(p(et,.2,.8));$('e1').style.opacity=a1;$('e1').setAttribute('transform',`translate(0 ${(1-a1)*30})`);
  for(let i=0;i<3;i++){const k=eo(p(et,.9+i*.22,1.4+i*.22));const g=$('card'+i);g.style.opacity=k;g.setAttribute('transform',`translate(0 ${(1-k)*50})`)}
  $('e3').style.opacity=eo(p(et,2.5,3.0));
}
window.setTime=setTime;window.DUR=B[8];setTime(0);
