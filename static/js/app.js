(() => {
const tg = window.Telegram?.WebApp;
const initData = tg?.initData || "";
tg?.ready(); tg?.expand();
const headers = () => ({'Content-Type':'application/json', ...(initData ? {'X-Telegram-Init-Data':initData} : {})});
const $ = s => document.querySelector(s);
const toast = message => {const el=$('#toast');el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),3200)};
async function api(path, options={}) {
 const response=await fetch(path,{...options,headers:{...headers(),...(options.headers||{})}});
 let data={};try{data=await response.json()}catch{}
 if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:(data.detail?.message||'So‘rov bajarilmadi'));
 return data;
}
function card(t){const status={open:'Ro‘yxat ochiq',live:'Jonli',full:'Joylar to‘ldi',finished:'Yakunlangan',draft:'Tayyorlanmoqda',cancelled:'Bekor qilingan'}[t.status]||t.status;
 return `<article class="tournament-card"><span class="chip">${status}</span><h3>${escapeHtml(t.title)}</h3><p>${escapeHtml(t.description||'Turnir tafsilotlari')}</p><div class="card-meta"><span class="chip">${escapeHtml(t.mode)}</span><span class="chip">${t.registered_teams}/${t.max_teams} jamoa</span></div><div class="prize">${Number(t.prize_pool||0).toLocaleString('uz-UZ')} so‘m</div>${t.status==='open'?`<button class="primary-btn register" data-id="${t.id}">Jamoani ro‘yxatdan o‘tkazish</button>`:''}</article>`;
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function loadTournaments(){try{const data=await api('/api/tournaments',{headers:{}});$('#active-count').textContent=data.filter(x=>['open','live'].includes(x.status)).length;const html=data.length?data.map(card).join(''):'<div class="empty">Hozircha turnir yo‘q. Keyinroq qayta tekshiring.</div>';$('#featured').innerHTML=html;$('#all-tournaments').innerHTML=html;}catch(e){$('#featured').innerHTML='<div class="empty">Turnirlarni olish imkoni bo‘lmadi. Backendni tekshiring.</div>';$('#all-tournaments').innerHTML=$('#featured').innerHTML;}}
document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===btn));document.querySelectorAll('.view').forEach(x=>x.classList.toggle('hidden',x.id!==btn.dataset.section));}));
document.addEventListener('click',async e=>{const btn=e.target.closest('.register');if(!btn)return;try{const out=await api(`/api/tournaments/${btn.dataset.id}/register`,{method:'POST'});toast(`Ariza yuborildi: ${out.status}`);}catch(err){toast(err.message);}});
$('#player-form').addEventListener('submit',async e=>{e.preventDefault();const form=Object.fromEntries(new FormData(e.target));try{const out=await api('/api/player/verify',{method:'POST',body:JSON.stringify(form)});toast(`Tekshiruv holati: ${out.status}`);}catch(err){toast(err.message);}});
$('#team-form').addEventListener('submit',async e=>{e.preventDefault();const form=Object.fromEntries(new FormData(e.target));try{const out=await api('/api/teams',{method:'POST',body:JSON.stringify(form)});toast(`Jamoa yaratildi: ${out.name}`);e.target.reset();}catch(err){toast(err.message);}});
$('#lang').addEventListener('click',()=>toast('Tilni tanlash API orqali saqlanadi; tarjimalar bosqichma-bosqich kengaytiriladi.'));
async function loadProfile(){if(!initData){$('#profile-status').textContent='Profilni tekshirish uchun Mini App’ni Telegram bot ichidan oching.';return;}try{const me=await api('/api/me');$('#profile-status').textContent=`Xush kelibsiz, ${me.display_name}. Telegram ID: ${me.telegram_id}. ${me.profile?`MLBB: ${me.profile.mlbb_id} (${me.profile.verification_status})`:'MLBB profilingizni to‘ldiring.'}`;}catch(e){$('#profile-status').textContent=`Autentifikatsiya xatosi: ${e.message}`;}}
loadTournaments();loadProfile();
})();
