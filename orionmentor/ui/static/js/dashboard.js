(async function(){
  const $ = (id)=>document.getElementById(id);

  // Chart helpers
  const ctxRouting = $('chartRouting').getContext('2d');
  const ctxLatency = $('chartLatency').getContext('2d');
  const ctxFail    = $('chartFail').getContext('2d');
  const ctxTokens  = $('chartTokens').getContext('2d');

  const routingChart = new Chart(ctxRouting, {
    type: 'doughnut',
    data: { labels: ['Small','Big'], datasets: [{ data:[0,0] }] },
    options: { responsive:true, plugins:{ legend:{position:'bottom'} } }
  });

  const latencyChart = new Chart(ctxLatency, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Small', data: [], fill:false },
      { label: 'Big', data: [], fill:false }
    ]},
    options: { parsing:false, scales:{ x:{ type:'timeseries' } } }
  });

  const failChart = new Chart(ctxFail, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Count', data: [] }] },
    options: { indexAxis:'y' }
  });

  const tokensChart = new Chart(ctxTokens, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Small', data: [], fill:true },
      { label: 'Big', data: [], fill:true }
    ]},
    options: { parsing:false, scales:{ x:{ type:'timeseries' } } }
  });

  async function refresh(){
    const s = await (await fetch('/api/metrics/summary')).json();
    const t = await (await fetch('/api/metrics/timeseries')).json();
    const f = await (await fetch('/api/metrics/fail_reasons')).json();

    // KPIs
    $('kpi-rs').textContent = s.routed.small;
    $('kpi-rb').textContent = s.routed.big;
    $('kpi-ss').textContent = s.served.small;
    $('kpi-sb').textContent = s.served.big;
    $('kpi-ok').textContent = s.validation.ok;
    $('kpi-fail').textContent = s.validation.fail;
    $('kpi-ev').textContent = s.events;

    // Routing doughnut
    routingChart.data.datasets[0].data = [s.routed.small, s.routed.big];
    routingChart.update();

    // Latency timeseries
    const fmt = (arr)=>arr.map(p=>({x:new Date(p.t*1000), y:p.ms}));
    latencyChart.data.datasets[0].data = fmt(t.latency.small);
    latencyChart.data.datasets[1].data = fmt(t.latency.big);
    latencyChart.update();

    // Tokens timeseries
    const fmtTok = (arr)=>arr.map(p=>({x:new Date(p.t*1000), y:p.tok}));
    tokensChart.data.datasets[0].data = fmtTok(t.tokens.small);
    tokensChart.data.datasets[1].data = fmtTok(t.tokens.big);
    tokensChart.update();

    // Fail reasons
    const labels = Object.keys(f);
    const values = labels.map(k=>f[k]);
    failChart.data.labels = labels;
    failChart.data.datasets[0].data = values;
    failChart.update();
  }

  await refresh();
  setInterval(refresh, 3000);
})();
