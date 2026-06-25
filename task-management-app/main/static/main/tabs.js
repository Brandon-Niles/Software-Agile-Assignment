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
                if(name === 'dashboard') initDashboard(panel);
                // Announce load to assistive tech
                try{ const live = document.getElementById('tab-live'); if(live) live.textContent = name.charAt(0).toUpperCase()+name.slice(1)+ ' content loaded.'; }catch(e){}
            }).catch(()=>{});
    }

    document.addEventListener('click', function(e){
        const btn = e.target.closest('.tab-btn');
        if(!btn) return;
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
