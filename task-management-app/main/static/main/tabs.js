// Tabs navigation script: show/hide panels and manage history
(function(){
    function qs(sel, root){ return (root||document).querySelector(sel); }
    function qsa(sel, root){ return Array.from((root||document).querySelectorAll(sel)); }

    const TAB_PATHS = {
        'dashboard': '/dashboard/',
        'tasks': '/pages/tasks/',
        'users': '/pages/users/',
        'reports': '/pages/reports/',
        'settings': '/pages/settings/'
    };

    function activateTab(name, push){
        qsa('.tab-btn').forEach(btn=>{
            const active = btn.dataset.tab === name;
            btn.setAttribute('aria-selected', active? 'true':'false');
            btn.classList.toggle('active', active);
            // manage focusability
            btn.tabIndex = active ? 0 : -1;
        });
        qsa('.tab-panel').forEach(p=>{
            if(p.id === 'tab-'+name){ p.hidden = false; } else { p.hidden = true; }
            // set aria-hidden
            p.setAttribute('aria-hidden', p.id === 'tab-'+name ? 'false' : 'true');
        });
        if(push){
            try{
                const path = TAB_PATHS[name] || '#'+name;
                history.pushState({tab:name}, '', path);
                // trigger progressive load for server path
                loadTabContent(name, path);
            }catch(e){}
        }
    }

    function loadTabContent(name, path){
        const panel = document.getElementById('tab-'+name);
        if(!panel) return;
        // if already loaded, skip
        if(panel.dataset.loaded === '1') return;
        fetch(path, {headers: {'x-requested-with': 'XMLHttpRequest'}})
            .then(r=>{ if(!r.ok) throw new Error('Network'); return r.text(); })
            .then(html=>{
                panel.innerHTML = html;
                panel.dataset.loaded = '1';
                if(name === 'dashboard'){
                    initDashboard(panel);
                    try{ if(localStorage.getItem('simulateLive') === '1'){ if(typeof startSimulation === 'function') startSimulation(panel); } }catch(e){}
                }
                // Announce load to assistive tech
                try{ const live = document.getElementById('tab-live'); if(live) live.textContent = name.charAt(0).toUpperCase()+name.slice(1)+ ' content loaded.'; }catch(e){}
            }).catch(()=>{});
    }

    document.addEventListener('click', function(e){
        const btn = e.target.closest('.tab-btn');
        if(!btn) return;
        // Ignore disabled tabs
        if(btn.getAttribute('aria-disabled') === 'true' || btn.disabled) return;
        const tab = btn.dataset.tab;
        activateTab(tab, true);
    });

    // Keyboard navigation for tabs: Left/Right/Home/End, Enter/Space to activate
    document.addEventListener('keydown', function(e){
        const el = document.activeElement;
        if(!el || !el.classList.contains('tab-btn')) return;
        const tabs = qsa('.tab-btn');
        const idx = tabs.indexOf(el);
        if(idx === -1) return;
        if(e.key === 'ArrowRight' || e.key === 'Right'){
            e.preventDefault();
            const next = tabs[(idx+1)%tabs.length]; next.focus();
        } else if(e.key === 'ArrowLeft' || e.key === 'Left'){
            e.preventDefault();
            const prev = tabs[(idx-1+tabs.length)%tabs.length]; prev.focus();
        } else if(e.key === 'Home'){
            e.preventDefault(); tabs[0].focus();
        } else if(e.key === 'End'){
            e.preventDefault(); tabs[tabs.length-1].focus();
        } else if(e.key === 'Enter' || e.key === ' '){
            e.preventDefault(); const tab = el.dataset.tab; activateTab(tab, true);
        }
    });

    window.addEventListener('popstate', function(e){
        const t = (e.state && e.state.tab) || location.pathname.replace(/^\/+|\/+$/g,'') || location.hash.replace('#','') || 'dashboard';
        // normalize when path is like 'dashboard' or 'pages/tasks'
        let name = t.split('/').pop() || 'dashboard';
        if(name === 'tasks' && location.pathname.indexOf('/pages/')===-1) name = 'dashboard';
        activateTab(name, false);
    });

    document.addEventListener('DOMContentLoaded', function(){
        // initialize from hash
        const start = location.hash.replace('#','') || 'dashboard';
        activateTab(start, false);
        // expose for debugging
        window.activateTab = activateTab;
    });
})();

function initDashboard(panel){
    try{
        const card = panel.querySelector('.chart-card');
        if(!card) return;
        const pending = parseInt(card.dataset.pending||0,10);
        const running = parseInt(card.dataset.running||0,10);
        const completed = parseInt(card.dataset.completed||0,10);
        const cancelled = parseInt(card.dataset.cancelled||0,10);
        const canvas = panel.querySelector('canvas');
        if(!canvas) return;
        // load Chart.js dynamically if needed
        function createChart(){
            const ctx = canvas.getContext('2d');
            // eslint-disable-next-line no-undef
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Pending','Running','Completed','Cancelled'],
                    datasets: [{ data: [pending,running,completed,cancelled], backgroundColor: ['#f59e0b','#0ea5e9','#10b981','#dc2626'] }]
                }, options: {plugins:{legend:{position:'bottom'}},maintainAspectRatio:false}
            });
        }
        if(typeof Chart === 'undefined'){
            const s = document.createElement('script'); s.src='https://cdn.jsdelivr.net/npm/chart.js'; s.onload=createChart; document.head.appendChild(s);
        } else { createChart(); }
    }catch(e){}
}

// Simulation functions (start/stop) exposed globally for settings toggle
function startSimulation(panel){
    try{
        if(!panel) panel = document.getElementById('tab-dashboard');
        if(!panel) return;
        if(panel.dataset.simRunning === '1') return;
        panel.dataset.simRunning = '1';
        const chartCanvas = panel.querySelector('canvas');
        let chartObj = null;
        if(chartCanvas && typeof Chart !== 'undefined'){
            try{ chartObj = Chart.getChart(chartCanvas) || null; }catch(e){}
        }
        const intervalId = setInterval(()=>{
            const statTotalEl = panel.querySelector('#stat-total');
            const statPendingEl = panel.querySelector('#stat-pending');
            const statRunningEl = panel.querySelector('#stat-running');
            const statCompletedEl = panel.querySelector('#stat-completed');
            if(!statTotalEl || !statPendingEl || !statRunningEl || !statCompletedEl) return;
            let total = parseInt(statTotalEl.textContent||'0',10);
            let pending = parseInt(statPendingEl.textContent||'0',10);
            let running = parseInt(statRunningEl.textContent||'0',10);
            let completed = parseInt(statCompletedEl.textContent||'0',10);
            if(pending>0 && Math.random()<0.6){ pending--; running++; }
            if(running>0 && Math.random()<0.35){ running--; completed++; }
            if(Math.random()<0.15){ pending++; total++; }
            statTotalEl.textContent = total;
            statPendingEl.textContent = pending;
            statRunningEl.textContent = running;
            statCompletedEl.textContent = completed;
            if(chartObj){ chartObj.data.datasets[0].data = [pending, running, completed, 0]; chartObj.update(); }
        }, 2500);
        panel.dataset.simInterval = intervalId;
    }catch(e){}
}

function stopSimulation(panel){
    try{
        if(!panel) panel = document.getElementById('tab-dashboard');
        if(!panel) return;
        const id = panel.dataset.simInterval;
        if(id){ clearInterval(id); panel.dataset.simInterval = ''; panel.dataset.simRunning = '0'; }
    }catch(e){}
}

// Adjust task counts and chart after local CRUD changes
function adjustTaskCounts(deltaTotal, deltaByStatus){
    try{
        const totalEl = document.getElementById('stat-total');
        const pendingEl = document.getElementById('stat-pending');
        const runningEl = document.getElementById('stat-running');
        const completedEl = document.getElementById('stat-completed');
        if(totalEl) totalEl.textContent = Math.max(0, (parseInt(totalEl.textContent||'0',10) + (deltaTotal||0)));
        if(pendingEl && deltaByStatus && deltaByStatus.Pending) pendingEl.textContent = Math.max(0, parseInt(pendingEl.textContent||'0',10) + deltaByStatus.Pending);
        if(runningEl && deltaByStatus && deltaByStatus.Running) runningEl.textContent = Math.max(0, parseInt(runningEl.textContent||'0',10) + deltaByStatus.Running);
        if(completedEl && deltaByStatus && deltaByStatus.Completed) completedEl.textContent = Math.max(0, parseInt(completedEl.textContent||'0',10) + deltaByStatus.Completed);
        // update chart if present
        const canvas = document.querySelector('#tab-dashboard canvas');
        if(canvas && typeof Chart !== 'undefined'){
            try{
                const ch = Chart.getChart(canvas);
                if(ch && ch.data && ch.data.datasets && ch.data.datasets[0]){
                    const map = {Pending:0, Running:1, Completed:2, Cancelled:3};
                    const ds = ch.data.datasets[0].data;
                    for(const k in (deltaByStatus||{})){
                        if(Object.prototype.hasOwnProperty.call(map,k)){
                            ds[map[k]] = Math.max(0, (ds[map[k]]||0) + deltaByStatus[k]);
                        }
                    }
                    if(typeof ch.update === 'function') ch.update();
                }
            }catch(e){}
        }
    }catch(e){}
}
