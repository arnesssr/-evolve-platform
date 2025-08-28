(function(){
  const apiBase = '/platform/admin/api/v1';

  function applyGeneralSettings(s){
    try {
      const lang = s.default_language || 'en';
      const currency = s.default_currency || 'USD';
      const symbolMap = { USD:'$', EUR:'€', GBP:'£', KES:'KSh' };
      const symbol = symbolMap[currency] || '$';
      window.PlatformSettings = Object.assign({}, window.PlatformSettings || {}, {
        default_language: lang,
        default_currency: currency,
        currency_symbol: symbol,
        platform_name: s.platform_name || window.PlatformSettings?.platform_name || 'Evolve Platform',
        platform_url: s.platform_url || window.PlatformSettings?.platform_url || '',
        support_email: s.support_email || window.PlatformSettings?.support_email || '',
        timezone: s.timezone || window.PlatformSettings?.timezone || 'UTC'
      });
      document.documentElement.setAttribute('lang', lang);
      document.dispatchEvent(new CustomEvent('platform:settings:updated', { detail: window.PlatformSettings }));
    } catch(e) { console.warn('Failed to apply settings', e); }
  }

  async function fetchGeneral(){
    try{
      const res = await fetch(`${apiBase}/settings/general/`, { credentials: 'same-origin' });
      if(!res.ok) return;
      const data = await res.json();
      applyGeneralSettings(data || {});
    }catch(e){ console.warn('Failed to fetch general settings', e); }
  }

  async function saveGeneral(payload){
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const res = await fetch(`${apiBase}/settings/general/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf || '' },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    });
    if(!res.ok){
      const txt = await res.text();
      throw new Error(txt);
    }
    return res.json();
  }

  function collectGeneralForm(){
    const get = (sel) => document.querySelector(sel);
    const val = (sel) => get(sel)?.value?.trim() || undefined;
    const payload = {
      platform_name: val('[name="platform_name"]'),
      platform_url: val('[name="platform_url"]'),
      support_email: val('[name="support_email"]'),
      timezone: val('[name="timezone"]'),
      default_currency: val('[name="default_currency"]'),
      default_language: val('[name="default_language"]')
    };
    Object.keys(payload).forEach(k=> payload[k] === undefined && delete payload[k]);
    return payload;
  }

  function initAutoBind(){
    // Bind form submit for a form with id or data attribute
    const form = document.querySelector('#generalSettingsForm, form[data-settings-section="general"]') || null;
    if(form){
      form.addEventListener('submit', async (e)=>{
        e.preventDefault();
        try{
          const payload = collectGeneralForm();
          const updated = await saveGeneral(payload);
          applyGeneralSettings(updated);
          window.showToast?.('Settings saved', 'success');
        }catch(err){
          console.error(err);
          window.showToast?.('Failed to save settings', 'error');
        }
      });
    }

    // Immediate apply when selecting language/currency
    const langSel = document.querySelector('[name="default_language"]');
    if (langSel) {
      langSel.addEventListener('change', async ()=>{
        const payload = { default_language: langSel.value };
        try { const updated = await saveGeneral(payload); applyGeneralSettings(updated); } catch(e){ console.warn(e); }
      });
    }
    const curSel = document.querySelector('[name="default_currency"]');
    if (curSel) {
      curSel.addEventListener('change', async ()=>{
        const payload = { default_currency: curSel.value };
        try { const updated = await saveGeneral(payload); applyGeneralSettings(updated);} catch(e){ console.warn(e);} 
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    fetchGeneral();
    initAutoBind();
    // Also, reflect currency symbol in simple places: [data-currency-label]
    document.addEventListener('platform:settings:updated', (evt)=>{
      const s = evt.detail || window.PlatformSettings || {};
      document.querySelectorAll('[data-currency-label]').forEach(el=>{
        el.textContent = s.currency_symbol || '$';
      });
    });
  });
})();

