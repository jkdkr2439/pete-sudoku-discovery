const $=id=>document.getElementById(id);

function drawBoard(target,board,fixed=[]){
  const el=$(target);
  if(!board){
    el.innerHTML='<p class="muted">No sandbox projection yet.</p>';
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

function renderCode(code){
  if(!code||!code.active)return;
  const route=code.active;
  $('code-phase').textContent=code.phase;
  $('code-function').textContent=route.function;
  $('code-file').textContent=route.file;
  $('code-lines').textContent='lines '+route.start_line+'-'+route.end_line;
  const numbered=route.source.split('\n').map((line,index)=>String(route.start_line+index).padStart(4,' ')+'  '+line).join('\n');
  if($('live-code').textContent!==numbered)$('live-code').textContent=numbered;
}

function render(s){
  $('run-state').textContent=s.phase;
  $('start').disabled=s.running;
  $('pause').disabled=!s.running;
  $('next').disabled=s.running;
  const w=s.substrate,n=w.shape[0];
  $('world-title').textContent='Opaque grid '+n+' x '+n;
  $('difficulty').textContent='tier '+(w.difficulty_index+1);
  drawBoard('real-board',w.board,w.fixed);
  drawBoard('sandbox-board',s.sandbox?.board);
  $('attempts').textContent=s.sandbox?s.sandbox.attempts+' sandbox steps':'-';
  $('samples').textContent=s.fieldmap.samples;
  $('accuracy').textContent=s.metrics.verification?(100*s.metrics.verification.accuracy).toFixed(1)+'%':'-';
  $('baseline').textContent=s.metrics.verification?(100*s.metrics.verification.empty_model_baseline).toFixed(1)+'%':'-';
  $('journal').textContent=s.journal.events;
  $('worlds').textContent=s.worlds_completed;
  $('reactions').textContent=s.fieldmap.reaction_shapes;
  $('structure').textContent=s.fieldmap.structure_hash.slice(0,8);
  $('clauses').innerHTML=s.fieldmap.clauses.length?s.fieldmap.clauses.map(c=>'<div class="clause">'+c.terms.join(' AND ')+'<b>w='+c.dynamic_weight.toFixed(2)+'</b></div>').join(''):'<p class="muted">Fieldmap is empty.</p>';
  $('events').innerHTML=s.events.slice().reverse().map(e=>'<div class="event"><b>'+e.kind+'</b> '+(e.phase||e.status||e.result||'')+(e.completed?' '+e.completed+'/'+e.total:'')+'</div>').join('');
}

async function poll(){
  try{
    const [state,code]=await Promise.all([
      fetch('/api/state').then(r=>r.json()),
      fetch('/api/code').then(r=>r.json())
    ]);
    render(state);
    renderCode(code);
  }catch(e){}
  setTimeout(poll,400);
}

$('start').onclick=()=>fetch('/api/start',{method:'POST'});
$('pause').onclick=()=>fetch('/api/pause',{method:'POST'});
$('next').onclick=()=>fetch('/api/new',{method:'POST'}).then(()=>fetch('/api/state')).then(r=>r.json()).then(render);
poll();
