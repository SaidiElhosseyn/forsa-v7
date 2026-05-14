/* FORSA — فرصة · main.js v5.0 */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  /* ── Page Loader ─────────────────────────────────────────────── */
  const loader = document.getElementById('forsa-loader');
  if (loader) {
    window.addEventListener('load', () => {
      loader.classList.add('hidden');
      setTimeout(() => loader.remove(), 500);
    });
    setTimeout(() => loader.classList.add('hidden'), 3000);
  }

  /* ── Theme ───────────────────────────────────────────────────── */
  const applyTheme = t => {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('forsa-theme', t);
  };
  applyTheme(localStorage.getItem('forsa-theme') || 'light');
  document.querySelectorAll('.theme-toggle,.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cur = document.documentElement.getAttribute('data-theme');
      applyTheme(cur === 'dark' ? 'light' : 'dark');
    });
  });

  /* ── Toast Auto-dismiss ──────────────────────────────────────── */
  document.querySelectorAll('.alert-auto').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0'; el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 400);
    }, 4500);
    el.style.transition = 'all .4s ease';
  });

  /* ── Mobile Sidebar ──────────────────────────────────────────── */
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('mainSidebar');
  const overlay = document.getElementById('sbOverlay');
  if (sidebarToggle && sidebar) {
    const openSb  = () => { sidebar.classList.add('open'); if (overlay) { overlay.style.display = 'block'; } };
    const closeSb = () => { sidebar.classList.remove('open'); if (overlay) { overlay.style.display = 'none'; } };
    sidebarToggle.addEventListener('click', () => sidebar.classList.contains('open') ? closeSb() : openSb());
    overlay?.addEventListener('click', closeSb);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSb(); });
  }

  /* ── Navbar Shadow on Scroll ─────────────────────────────────── */
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Scroll Reveal ───────────────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
  }

  /* ── Countdown Timers ────────────────────────────────────────── */
  document.querySelectorAll('[data-expiry]').forEach(el => {
    const target = new Date(el.dataset.expiry + 'T23:59:59').getTime();
    const tick = () => {
      const diff = target - Date.now();
      if (diff <= 0) {
        el.innerHTML = '<span style="color:var(--danger);font-weight:700;font-size:.82rem;">Expiré</span>';
        return;
      }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      const pad = n => String(n).padStart(2, '0');
      el.innerHTML = `<div class="countdown">
        <div class="cd-block"><span class="cd-num">${pad(d)}</span><span class="cd-lbl">Jrs</span></div>
        <div class="cd-block"><span class="cd-num">${pad(h)}</span><span class="cd-lbl">Hrs</span></div>
        <div class="cd-block"><span class="cd-num">${pad(m)}</span><span class="cd-lbl">Min</span></div>
        <div class="cd-block"><span class="cd-num">${pad(s)}</span><span class="cd-lbl">Sec</span></div>
      </div>`;
    };
    tick();
    setInterval(tick, 1000);
  });

  /* ── Lightbox ────────────────────────────────────────────────── */
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  if (lb && lbImg) {
    document.querySelectorAll('[data-lightbox]').forEach(el => {
      el.addEventListener('click', () => {
        lbImg.src = el.dataset.lightbox;
        lb.classList.add('open');
      });
      el.style.cursor = 'zoom-in';
    });
    lb.querySelector('.lightbox-close')?.addEventListener('click', () => lb.classList.remove('open'));
    lb.addEventListener('click', e => { if (e.target === lb) lb.classList.remove('open'); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') lb.classList.remove('open'); });
  }

  /* ── Add to Cart (AJAX) ──────────────────────────────────────── */
  window.addToCart = async (slug, btn) => {
    if (!btn) btn = event?.currentTarget;
    if (!btn) return;
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check"></i> Ajouté !';
    btn.disabled = true;
    btn.style.background = 'var(--success)';
    try {
      const csrf = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
      const res = await fetch(`/orders/cart/add/${slug}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'quantity=1',
      });
      const data = await res.json();
      if (data.cart_count !== undefined) {
        document.querySelectorAll('.cart-count, .cart-badge').forEach(el => el.textContent = data.cart_count);
      }
      if (data.error) console.warn(data.error);
    } catch (e) { console.error('Cart error:', e); }
    setTimeout(() => {
      btn.innerHTML = orig;
      btn.disabled = false;
      btn.style.background = '';
    }, 2200);
  };

  /* ── Cart Item Quantity ──────────────────────────────────────── */
  const csrf = () => document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
  window.updateCartItem = async (itemId, qty) => {
    try {
      const res = await fetch(`/orders/cart/update/${itemId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf(), 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `quantity=${qty}`,
      });
      const data = await res.json();
      if (data.success) {
        if (qty < 1) document.getElementById(`cart-item-${itemId}`)?.remove();
        else {
          const qEl = document.getElementById(`qty-${itemId}`);
          const sEl = document.getElementById(`sub-${itemId}`);
          if (qEl) qEl.textContent = qty;
          if (sEl && data.subtotal) sEl.textContent = Math.round(data.subtotal).toLocaleString() + ' DA';
        }
        document.querySelectorAll('.cart-total-display').forEach(el => el.textContent = Math.round(data.cart_total).toLocaleString() + ' DA');
        document.querySelectorAll('.cart-count,.cart-badge').forEach(el => el.textContent = data.cart_count);
      } else if (data.error) showToast(data.error, 'error');
    } catch (e) { console.error(e); }
  };

  /* ── Toast Utility ───────────────────────────────────────────── */
  window.showToast = (msg, type = 'info') => {
    const stack = document.getElementById('toastStack') || (() => {
      const el = document.createElement('div');
      el.id = 'toastStack'; el.className = 'toast-stack';
      document.body.appendChild(el); return el;
    })();
    const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' };
    const el = document.createElement('div');
    el.className = `alert alert-${type}`;
    el.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${msg}</span>`;
    stack.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateY(-6px)'; el.style.transition = 'all .4s'; setTimeout(() => el.remove(), 400); }, 4000);
  };

  /* ── Delivery Price Calculator ───────────────────────────────── */
  const ZONES = {'09':'A','16':'A','35':'A','42':'A','31':'B','25':'B','05':'B','06':'B','15':'B','23':'B','19':'B','21':'B','41':'B','13':'B','22':'B','27':'B','29':'B','14':'C','26':'C','28':'C','17':'C','38':'C','20':'C','18':'C','34':'C','36':'C','40':'C','44':'C','45':'C','46':'C','03':'D','07':'D','08':'D','11':'D','30':'D','33':'D','37':'D','39':'D','47':'D','49':'D','50':'D','51':'D','52':'D','53':'D','54':'D','55':'D','56':'D','57':'D','58':'D'};
  const DPRICES = {A:{std:350,exp:600,sd:'1-2j',ed:'24h'},B:{std:450,exp:750,sd:'2-3j',ed:'48h'},C:{std:550,exp:900,sd:'3-5j',ed:'72h'},D:{std:700,exp:1200,sd:'5-7j',ed:'4-5j'}};
  window.getDeliveryPrice = (wilaya, method) => {
    if (method === 'pickup') return { price: 0, days: 'Immédiat' };
    const z = ZONES[wilaya] || 'C';
    const p = DPRICES[z];
    return method === 'express' ? { price: p.exp, days: p.ed } : { price: p.std, days: p.sd };
  };

  const wilayaSel = document.getElementById('delivery-wilaya');
  if (wilayaSel) {
    wilayaSel.addEventListener('change', updateDeliveryUI);
    document.querySelectorAll('[name="delivery_method"]').forEach(r => r.addEventListener('change', updateDeliveryUI));
  }

  function updateDeliveryUI() {
    const w = document.getElementById('delivery-wilaya')?.value || '';
    const m = document.querySelector('[name="delivery_method"]:checked')?.value || 'standard';
    const subtotal = parseFloat(document.getElementById('checkout-subtotal')?.dataset.value || 0);
    if (!w) return;
    const { price, days } = getDeliveryPrice(w, m);
    const priceEl = document.getElementById('delivery-price-label');
    const daysEl  = document.getElementById('delivery-days-label');
    const totalEl = document.getElementById('checkout-total-label');
    if (priceEl) priceEl.textContent = price === 0 ? 'Gratuit' : price.toLocaleString() + ' DA';
    if (daysEl)  daysEl.textContent  = days;
    if (totalEl) totalEl.textContent = (subtotal + price).toLocaleString() + ' DA';
    if (w && ZONES[w]) {
      const z = ZONES[w]; const p2 = DPRICES[z];
      document.querySelectorAll('.std-price-lbl').forEach(el => el.textContent = p2.std.toLocaleString() + ' DA · ' + p2.sd);
      document.querySelectorAll('.exp-price-lbl').forEach(el => el.textContent = p2.exp.toLocaleString() + ' DA · ' + p2.ed);
    }
  }

  /* ── Star Rating ─────────────────────────────────────────────── */
  const starContainer = document.querySelector('.star-rating');
  if (starContainer) {
    const stars = starContainer.querySelectorAll('label');
    stars.forEach((star, i) => {
      star.addEventListener('mouseover', () => stars.forEach((s, j) => s.style.color = j <= i ? '#F59E0B' : 'var(--gray-300)'));
      star.addEventListener('click',     () => { stars.forEach((s, j) => { s.style.color = j <= i ? '#F59E0B' : 'var(--gray-300)'; const inp = s.querySelector('input'); if (inp) inp.checked = (j === i); }); });
    });
    starContainer.addEventListener('mouseleave', () => {
      const val = parseInt(starContainer.querySelector('input:checked')?.value || 0) - 1;
      stars.forEach((s, i) => s.style.color = i <= val ? '#F59E0B' : 'var(--gray-300)');
    });
  }

  /* ── Image Preview ───────────────────────────────────────────── */
  document.getElementById('imageInput')?.addEventListener('change', function () {
    const prev = document.getElementById('imagePreview');
    if (!prev) return;
    prev.innerHTML = '';
    [...this.files].forEach((f, i) => {
      const r = new FileReader();
      r.onload = e => {
        prev.innerHTML += `<div style="position:relative;width:78px;height:78px;flex-shrink:0;">
          <img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;border:2px solid ${i===0?'var(--green)':'var(--border)'}">
          ${i===0 ? '<span style="position:absolute;bottom:-1px;left:0;right:0;text-align:center;font-size:.58rem;background:var(--green);color:#fff;border-radius:0 0 6px 6px;padding:1px;">Principale</span>' : ''}
        </div>`;
      };
      r.readAsDataURL(f);
    });
  });

  /* ── Checkout submit loading ─────────────────────────────────── */
  document.getElementById('checkoutForm')?.addEventListener('submit', () => {
    const btn = document.getElementById('checkoutSubmitBtn');
    if (btn) { btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Traitement...'; btn.disabled = true; }
  });

  /* ── Smooth scroll for anchor links ─────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

});
