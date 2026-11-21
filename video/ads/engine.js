// Motor de animacao dos criativos Corte Pronto (renderizado quadro a quadro pelo Playwright)
(function(){
const A=window.AD;
const $=id=>document.getElementById(id);
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>1-Math.pow(1-cl(x),3);
const eio=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
window.U={$,cl,ease,eio};
// fundo
document.body.insertAdjacentHTML('afterbegin','<div id="glow"></div><div id="dots"></div><canvas id="fx" width="720" height="1280"></canvas><div id="flash"></div><div id="vig"></div>');
document.body.insertAdjacentHTML('beforeend','<div id="cap"></div>');
// palavras e legenda
const W=[];
A.LN.forEach(([st,du,tx],li)=>{st+=A.OFF;let key=false;const toks=[];
  tx.split(' ').forEach(w=>{let k=key;if(w.startsWith('[')){k=true;key=true;w=w.slice(1)}
    if(/\][,.?]?$/.test(w)){w=w.replace(/\]([,.?]?)$/,'$1');toks.push({w,k:true});key=false;return}toks.push({w,k})});
  const end=st+du*0.92;const wt=toks.map(x=>x.w.length+2);const tot=wt.reduce((a,b)=>a+b,0);let a=st;
  toks.forEach((x,i)=>{x.s=a;a+=(end-st)*wt[i]/tot;x.line=li;W.push(x)})});
const CH=[];let g=[];
W.forEach((x,i)=>{g.push(x);const nx=W[i+1];if(!nx||nx.line!==x.line||g.length>=6&&/[,.?]$/.test(x.w)||g.length>=7){CH.push(g);g=[]}});
window.W=W;window.L=i=>A.LN[i][0]+A.OFF;
const KEYS=W.filter((x,i)=>x.k&&!(W[i-1]&&W[i-1].k));
// imagens quadro a quadro
const CF='file:///tmp/claude-0/-home-user-P-gina-de-vendas-GGG/482a6202-3c7c-579d-a01d-3a24b350b15a/scratchpad/vid/cf/';
window.TH=n=>`url(${CF}th/t${n}.jpg)`;
window.setImg=function(id,dir,t0,t,max){const el=$(id);const f=Math.max(1,Math.min(max,Math.floor((t-t0)*30)+1));const src=CF+dir+'/'+String(f).padStart(5,'0')+'.jpg';if(el.dataset.s!==src){el.dataset.s=src;el.src=src;return Promise.race([el.decode().catch(()=>{}),new Promise(r=>setTimeout(r,2000))])}return null};
// particulas deterministicas
const P=[];let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647};
for(let i=0;i<55;i++)P.push({x:rnd()*720,y:rnd()*1280,r:0.6+rnd()*1.8,v:8+rnd()*26,a:0.15+rnd()*0.45,ph:rnd()*6.28});
const fx=$('fx').getContext('2d');
// sfx
const SC=A.SCN.map(s=>({...s,a:typeof s.a==='function'?s.a():s.a,b:typeof s.b==='function'?s.b():s.b}));
window.SFX={whoosh:SC.slice(1).map(s=>+(s.a-0.18).toFixed(3)),boom:SC.filter(s=>s.boom).map(s=>+s.a.toFixed(3))};
window.END=A.END;
window.render=function(t){const waits=[];
  // brilho que muda de cor e respira
  let gc=A.GLOW[0][1];A.GLOW.forEach(([s,c])=>{if(t>=s)gc=c});
  const br=0.30+0.05*Math.sin(t*1.7);
  $('glow').style.background=`radial-gradient(closest-side,rgba(${gc},${br.toFixed(3)}),rgba(${gc},.09) 55%,transparent 80%)`;
  // flash nas palavras-chave
  let fl=0;KEYS.forEach(k=>{const d=t-k.s;if(d>=0&&d<0.6)fl=Math.max(fl,(1-d/0.6)*0.28)});$('flash').style.opacity=fl.toFixed(3);
  // particulas
  fx.clearRect(0,0,720,1280);P.forEach(p=>{const y=((p.y-t*p.v)%1280+1280)%1280;const x=p.x+Math.sin(t*0.6+p.ph)*10;fx.globalAlpha=p.a*(0.6+0.4*Math.sin(t*2+p.ph));fx.fillStyle=p.r>1.6?'#FFB070':'#FFFFFF';fx.beginPath();fx.arc(x,y,p.r,0,6.283);fx.fill()});fx.globalAlpha=1;
  // camera
  $('cam').style.transform=`rotateX(${(5+2*Math.sin(t*0.45)).toFixed(2)}deg) rotateY(${(-7+7*Math.sin(t*0.32)).toFixed(2)}deg)`;
  // cenas
  SC.forEach((s,i)=>{const el=$(s.id);const inD=s.inD||0.55,outD=0.38;
    if(t<s.a-0.02||t>s.b+outD){el.style.display='none';return}
    const lt=t-s.a;const ki=ease(lt/inD),ko=ease((t-s.b)/outD);
    const z=-380*(1-ki)+320*ko+lt*14;const blur=14*(1-ki)+12*ko;const op=Math.min(ki,1-ko);
    el.style.display='block';el.style.opacity=op.toFixed(3);el.style.filter=blur>0.3?`blur(${blur.toFixed(1)}px)`:'none';
    el.style.transform=`translate3d(0,${Math.round(40*(1-ki)-30*ko)}px,${Math.round(z)}px) rotateY(${(8*(1-ki)).toFixed(2)}deg)`;
    el.querySelectorAll('.sheen').forEach(sh=>{sh.style.left=(-60+cl((lt-0.35)/0.7)*220)+'%'});
    if(s.upd){const w=s.upd(lt,t);if(w)[].concat(w).forEach(x=>x&&waits.push(x))}});
  // legenda
  let ci=-1;for(let i=0;i<CH.length;i++)if(t>=CH[i][0].s-0.02)ci=i;
  const cap=$('cap');if(cap.dataset.c!=ci){cap.dataset.c=ci;cap.innerHTML=ci<0?'':CH[ci].map(x=>'<span'+(x.k?' class="k"':'')+'>'+x.w+'</span>').join('')}
  if(ci>=0){const c=CH[ci];const sp=cap.children;const last=c[c.length-1].s;const fade=t>last+1.3?1-cl((t-last-1.3)/0.2):1;
    c.forEach((x,i)=>{const k=cl((t-x.s)/0.12);sp[i].style.opacity=(k*fade).toFixed(3);sp[i].style.transform=`translate3d(0,${Math.round((1-k)*8)}px,0)`;if(x.k)sp[i].style.setProperty('--u',cl((t-x.s-0.08)/0.25))})}
  return Promise.all(waits)};
render(0);
})();
