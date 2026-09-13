const $=id=>document.getElementById(id);
const PHASES=['PHYSICAL_EXPERIMENT','FIELD_COLLAPSE','HELD_OUT_VERIFICATION','SANDBOX','PHYSICAL_COMMIT','SOLVED'];

function drawBoard(target,board,fixed=[]){
  const el=$(target);
  if(!board){
    el.innerHTML='<p class="muted">No projection yet.</p>';
    el.style.removeProperty('--n');
    return;
  }
  el.style.setProperty('--n',board.length);
  el.innerHTML='';
  board.forEach((line,y)=>line.forEach((value,x)=>{
    const c=document.createElement('div');
    c.className='cell'+(fixed[y]?.[x]?' fixed':value?' learned':'');
    c.textContent=value||'';
    el.appendChild(c);
  }));
}

function renderPhases(phase){
  const active=PHASES.indexOf(phase);
  document.querySelectorAll('.phase-step').forEach((step,index)=>{
    step.classList.toggle('is-active',index===active);
    step.classList.toggle('is-done',phase==='SOLVED'||(active>=0&&index<active));
  });
}

function renderCode(code){
  if(!code||!code.active)return;
  const route=code.active;
  $('code-phase').textContent=code.phase;
  $('code-function').textContent=route.function;
  $('code-file').textContent=route.file;
  $('code-lines').textContent='L'+route.start_line+'–'+route.end_line;
  const numbered=route.source.split('\n').map((line,index)=>String(route.start_line+index).padStart(4,' ')+'  '+line).join('\n');
  if($('live-code').textContent!==numbered)$('live-code').textContent=numbered;
}

function percent(value,max){return Math.max(4,Math.min(100,100*value/max))+'%'}

function render(s){
  $('run-state').textContent=s.running?'RUNNING / '+s.phase:s.phase;
  $('start').disabled=s.running;
  $('pause').disabled=!s.running;
  $('next').disabled=s.running;
  renderPhases(s.phase);

  const w=s.substrate,n=w.shape[0];
  $('header-world').textContent=n+' × '+n;
  $('header-samples').textContent=s.fieldmap.samples.toLocaleString();
  $('header-solved').textContent=s.worlds_completed;
  $('world-title').textContent='Opaque grid '+n+' × '+n;
  $('difficulty').textContent='TIER '+(w.difficulty_index+1);
  $('action-count').textContent=w.action_index.toLocaleString()+' ACTIONS';
  drawBoard('real-board',w.board,w.fixed);
  drawBoard('sandbox-board',s.sandbox?.board);
  $('attempts').textContent=s.sandbox?s.sandbox.attempts+' STEPS':'NO PROJECTION';

  $('life').textContent=s.body.life.toLocaleString();
  $('energy').textContent=s.body.energy.toLocaleString();
  $('life-bar').style.width=percent(s.body.life,100000);
  $('energy-bar').style.width=percent(s.body.energy,100000);
  $('samples').textContent=s.fieldmap.samples.toLocaleString();
  $('accuracy').textContent=s.metrics.verification?(100*s.metrics.verification.accuracy).toFixed(1)+'%':'—';
  $('baseline').textContent=s.metrics.verification?(100*s.metrics.verification.empty_model_baseline).toFixed(1)+'%':'—';
  $('journal').textContent=s.journal.events.toLocaleString();
  $('reactions').textContent=s.fieldmap.reaction_shapes;
  $('structure').textContent=s.fieldmap.structure_hash.slice(0,8).toUpperCase();
  $('clause-count').textContent=s.fieldmap.clauses.length+' CLAUSES';
  $('clauses').innerHTML=s.fieldmap.clauses.length?s.fieldmap.clauses.map(c=>'<div class="clause">'+c.terms.join(' AND ')+'<b>dynamic weight '+c.dynamic_weight.toFixed(2)+'</b></div>').join(''):'<p class="muted">Fieldmap is empty.</p>';
  $('events').innerHTML=s.events.slice().reverse().map(e=>'<div class="event"><b>'+e.kind+'</b><span>'+(e.phase||e.status||e.result||'')+(e.completed?' '+e.completed+'/'+e.total:'')+'</span></div>').join('');
}

async function poll(){
  try{
    const [state,code]=await Promise.all([fetch('/api/state').then(r=>r.json()),fetch('/api/code').then(r=>r.json())]);
    render(state);renderCode(code);
  }catch(e){}
  setTimeout(poll,400);
}

$('start').onclick=()=>fetch('/api/start',{method:'POST'});
$('pause').onclick=()=>fetch('/api/pause',{method:'POST'});
$('next').onclick=()=>fetch('/api/new',{method:'POST'}).then(()=>fetch('/api/state')).then(r=>r.json()).then(render);
poll();