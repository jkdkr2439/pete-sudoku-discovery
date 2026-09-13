const $=id=>document.getElementById(id);
const PHASES=['PHYSICAL_EXPERIMENT','FIELD_COLLAPSE','HELD_OUT_VERIFICATION','SANDBOX','PHYSICAL_COMMIT','SOLVED'];
let nextPollDelay=300;

function drawBoard(target,board,fixed=[],activeCell=null){
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
    const active=activeCell&&activeCell[0]===y&&activeCell[1]===x;
    c.className='cell'+(fixed[y]?.[x]?' fixed':value?' learned':'')+(active?' active':'');
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

function renderCode(code,sandbox){
  if(!code||!code.active)return;
  const route=code.active;
  $('code-phase').textContent=code.phase;
  $('code-function').textContent=route.function;
  $('code-file').textContent=route.file;
  $('code-lines').textContent='L'+route.start_line+'–'+route.end_line;

  const focus=code.active_key==='sandbox'?(sandbox?.focus||''):'';
  const renderKey=code.active_key+'|'+focus;
  const codeEl=$('live-code');
  if(codeEl.dataset.renderKey===renderKey)return;
  codeEl.dataset.renderKey=renderKey;
  const fragment=document.createDocumentFragment();
  let focusElement=null;
  let focusClaimed=false;
  route.source.split('\n').forEach((line,index)=>{
    const row=document.createElement('span');
    const isFocus=Boolean(focus&&!focusClaimed&&line.includes(focus));
    row.className='code-line'+(isFocus?' focus':'');
    if(isFocus)focusClaimed=true;
    row.textContent=String(route.start_line+index).padStart(4,' ')+'  '+line;
    if(isFocus)focusElement=row;
    fragment.appendChild(row);
  });
  codeEl.replaceChildren(fragment);
  if(focusElement){
    const pre=codeEl.parentElement;
    pre.scrollTop=Math.max(0,focusElement.offsetTop-codeEl.offsetTop-pre.clientHeight/2);
  }
}

function renderSandbox(sandbox){
  drawBoard('sandbox-board',sandbox?.board,[],sandbox?.active_cell);
  $('attempts').textContent=sandbox?sandbox.attempts+' TRIES · '+sandbox.sequence+' OPS':'NO PROJECTION';
  $('sandbox-operation').textContent=sandbox?.operation||'WAITING';
  $('sandbox-instruction').textContent=sandbox?.instruction||'No internal operation yet';
  $('sandbox-position').textContent=sandbox?.active_cell?'CELL '+sandbox.active_cell.join(','):'CELL —';
  const latest=sandbox?.recent_ops?.[sandbox.recent_ops.length-1];
  $('sandbox-candidates').textContent=latest?.candidates?'CANDIDATES '+latest.candidates.join(' '):'CANDIDATES —';
  const trace=(sandbox?.recent_ops||[]).slice(-5).reverse();
  const traceEl=$('sandbox-trace');
  traceEl.innerHTML='';
  trace.forEach(op=>{
    const row=document.createElement('div');
    const seq=document.createElement('span');
    const kind=document.createElement('b');
    const instruction=document.createElement('code');
    seq.textContent='#'+op.sequence;
    kind.textContent=op.operation;
    instruction.textContent=op.instruction;
    row.append(seq,kind,instruction);
    traceEl.appendChild(row);
  });
}

function percent(value,max){return Math.max(4,Math.min(100,100*value/max))+'%'}

function render(s){
  $('run-state').textContent=s.running?'RUNNING / '+s.phase:s.phase;
  $('start').disabled=s.running;
  $('pause').disabled=!s.running;
  $('next').disabled=s.running;
  renderPhases(s.phase);
  nextPollDelay=s.phase==='SANDBOX'?80:300;

  const w=s.substrate,n=w.shape[0];
  $('header-world').textContent=n+' × '+n;
  $('header-samples').textContent=s.fieldmap.samples.toLocaleString();
  $('header-solved').textContent=s.worlds_completed;
  $('world-title').textContent='Opaque grid '+n+' × '+n;
  $('difficulty').textContent='TIER '+(w.difficulty_index+1);
  $('action-count').textContent=w.action_index.toLocaleString()+' ACTIONS';
  drawBoard('real-board',w.board,w.fixed);
  renderSandbox(s.sandbox);
  $('sandbox-log-path').textContent=s.sandbox_log?.path||'runtime/logs/sandbox-trace.jsonl';

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
  $('events').innerHTML=s.events.slice().reverse().map(e=>'<div class="event"><b>'+e.kind+'</b><span>'+(e.operation||e.phase||e.status||e.result||'')+(e.completed?' '+e.completed+'/'+e.total:'')+'</span></div>').join('');
}

async function poll(){
  try{
    const [state,code]=await Promise.all([fetch('/api/state').then(r=>r.json()),fetch('/api/code').then(r=>r.json())]);
    render(state);
    renderCode(code,state.sandbox);
  }catch(e){}
  setTimeout(poll,nextPollDelay);
}

$('start').onclick=()=>fetch('/api/start',{method:'POST'});
$('pause').onclick=()=>fetch('/api/pause',{method:'POST'});
$('next').onclick=()=>fetch('/api/new',{method:'POST'}).then(()=>fetch('/api/state')).then(r=>r.json()).then(render);
poll();
