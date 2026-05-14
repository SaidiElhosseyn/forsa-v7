/* ==========================================================
   FORSA — فرصة | Professional JS v5.0
   ========================================================== */
'use strict';

/* ── Loader ── */
window.addEventListener('load', () => {
  const loader = document.getElementById('pageLoader');
  if (loader) {
    loader.classList.add('hide');
    setTimeout(() => loader.remove(), 500);
  }
});

document.addEventListener('DOMContentLoaded', () => {

  // ── Theme ──────────────────────────────────────────────
  const applyTheme = t => {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('forsa-theme', t);
  };
  const savedTheme = localStorage.getItem('forsa-theme') || 'light';
  applyTheme(savedTheme);
  document.querySelectorAll('.theme-switch, .theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
  });

  // ── Announcement bar close ─────────────────────────────
  const announceClose = document.getElementById('announceClose');
  const announceBar   = document.getElementById('announceBar');
  if (announceClose && announceBar) {
    announceClose.addEventListener('click', () => {
      announceBar.style.height = announceBar.offsetHeight + 'px';
      requestAnimationFrame(() => {
        announceBar.style.transition = 'height .3s ease, opacity .3s ease';
        announceBar.style.height = '0';
        announceBar.style.opacity = '0';
        announceBar.style.overflow = 'hidden';
      });
      setTimeout(() => announceBar.remove(), 300);
    });
  }

  // ── Navbar scroll effect ───────────────────────────────
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const updateNavbar = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', updateNavbar, { passive: true });
    updateNavbar();
  }

  // ── Mobile nav ────────────────────────────────────────
  const hamburger  = document.getElementById('hamburger');
  const mobileNav  = document.getElementById('mobileNav');
  const mobileClose= document.getElementById('mobileNavClose');
  const mobileOverlay = document.getElementById('mobileNavOverlay');

  const openMobileNav  = () => { mobileNav?.classList.add('open'); hamburger?.classList.add('open'); document.body.style.overflow = 'hidden'; };
  const closeMobileNav = () => { mobileNav?.classList.remove('open'); hamburger?.classList.remove('open'); document.body.style.overflow = ''; };

  hamburger?.addEventListener('click', () => mobileNav?.classList.contains('open') ? closeMobileNav() : openMobileNav());
  mobileClose?.addEventListener('click', closeMobileNav);
  mobileOverlay?.addEventListener('click', closeMobileNav);

  // ── Sidebar (dashboard) ───────────────────────────────
  const sidebarToggle  = document.getElementById('sidebarToggle');
  const sidebar        = document.getElementById('mainSidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  const openSidebar  = () => { sidebar?.classList.add('open'); sidebarOverlay && (sidebarOverlay.style.display = 'block'); };
  const closeSidebar = () => { sidebar?.classList.remove('open'); sidebarOverlay && (sidebarOverlay.style.display = 'none'); };

  sidebarToggle?.addEventListener('click', () => sidebar?.classList.contains('open') ? closeSidebar() : openSidebar());
  sidebarOverlay?.addEventListener('click', closeSidebar);

  // ── Toasts ────────────────────────────────────────────
  const toastContainer = document.getElementById('toastContainer');

  window.showToast = (message, type = 'success', duration = 4500) => {
    if (!toastContainer) return;
    const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' };
    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;
    toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = 'all .3s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  };

  // Auto dismiss Django messages
  document.querySelectorAll('.toast-item').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'all .3s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateX(20px)';
      setTimeout(() => el.remove(), 300);
    }, 4500);
  });

  // ── Scroll reveal ─────────────────────────────────────
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  }

  // ── Countdown timers ──────────────────────────────────
  document.querySelectorAll('[data-expiry]').forEach(el => {
    const target = new Date(el.dataset.expiry + 'T23:59:59').getTime();
    const render = () => {
      const diff = target - Date.now();
      if (diff <= 0) {
        el.innerHTML = '<span style="color:var(--danger);font-weight:700;font-size:.8rem;"><i class="fa-solid fa-triangle-exclamation me-1"></i>Expiré</span>';
        return;
      }
      const d = Math.floor(diff/86400000);
      const h = Math.floor((diff%86400000)/3600000);
      const m = Math.floor((diff%3600000)/60000);
      const s = Math.floor((diff%60000)/1000);
      el.innerHTML = `<div class="countdown">
        <div class="cd-unit"><span class="cd-num">${String(d).padStart(2,'0')}</span><span class="cd-lbl">j</span></div>
        <div class="cd-unit"><span class="cd-num">${String(h).padStart(2,'0')}</span><span class="cd-lbl">h</span></div>
        <div class="cd-unit"><span class="cd-num">${String(m).padStart(2,'0')}</span><span class="cd-lbl">m</span></div>
        <div class="cd-unit"><span class="cd-num">${String(s).padStart(2,'0')}</span><span class="cd-lbl">s</span></div>
      </div>`;
    };
    render();
    setInterval(render, 1000);
  });

  // ── Add to cart AJAX ──────────────────────────────────
  window.addToCart = async (slug, btn) => {
    btn = btn || event?.currentTarget;
    if (!btn) return;
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check"></i> Ajouté !';
    btn.disabled = true;
    btn.style.background = 'var(--success)';
    btn.style.border = 'none';

    try {
      const csrf = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
      const res  = await fetch(`/orders/cart/add/${slug}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'quantity=1'
      });
      const data = await res.json();
      if (data.cart_count !== undefined) {
        document.querySelectorAll('.cart-count').forEach(el => el.textContent = data.cart_count);
      }
      showToast(data.message || 'Produit ajouté au panier !', 'success');
    } catch(e) {
      showToast('Erreur lors de l\'ajout au panier.', 'error');
    }

    setTimeout(() => {
      btn.innerHTML = orig;
      btn.disabled  = false;
      btn.style.background = '';
      btn.style.border = '';
    }, 2500);
  };

  // ── Cart quantity AJAX ────────────────────────────────
  window.updateCartQty = async (itemId, qty) => {
    const csrf = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
    try {
      const res  = await fetch(`/orders/cart/update/${itemId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `quantity=${qty}`
      });
      const data = await res.json();
      if (data.success) {
        if (qty < 1) {
          document.getElementById(`cart-row-${itemId}`)?.remove();
        } else {
          const subtotalEl = document.getElementById(`subtotal-${itemId}`);
          if (subtotalEl) subtotalEl.textContent = Math.round(data.subtotal).toLocaleString() + ' DA';
          const qtyEl = document.getElementById(`qty-${itemId}`);
          if (qtyEl) qtyEl.textContent = qty;
        }
        const totalEl = document.getElementById('cart-total');
        if (totalEl) totalEl.textContent = Math.round(data.cart_total).toLocaleString() + ' DA';
        document.querySelectorAll('.cart-count').forEach(el => el.textContent = data.cart_count);
      } else {
        showToast(data.error || 'Erreur', 'error');
      }
    } catch(e) {}
  };

  // ── Delivery price calculator ─────────────────────────
  const ZONES = {
    '09':'A','16':'A','35':'A','42':'A',
    '31':'B','25':'B','05':'B','06':'B','15':'B','23':'B','19':'B','22':'B','27':'B','29':'B','13':'B','21':'B','41':'B','24':'B',
    '14':'C','26':'C','28':'C','17':'C','38':'C','20':'C','18':'C','34':'C','36':'C','40':'C','44':'C','45':'C','46':'C','10':'C','02':'C','04':'C',
    '01':'D','03':'D','07':'D','08':'D','11':'D','30':'D','32':'D','33':'D','37':'D','39':'D','47':'D','49':'D','50':'D','51':'D','52':'D','53':'D','54':'D','55':'D','56':'D','57':'D','58':'D','12':'D',
  };
  const PRICES = {
    A: { std:350,exp:600,std_d:'1-2j',exp_d:'24h' },
    B: { std:450,exp:750,std_d:'2-3j',exp_d:'48h' },
    C: { std:550,exp:900,std_d:'3-5j',exp_d:'72h' },
    D: { std:700,exp:1200,std_d:'5-7j',exp_d:'4-5j' },
  };

  window.getDeliveryPrice = (wilaya, method) => {
    const z = ZONES[wilaya] || 'C';
    const p = PRICES[z];
    if (method === 'pickup')   return { price: 0, days: 'Immédiat' };
    if (method === 'express')  return { price: p.exp, days: p.exp_d };
    return { price: p.std, days: p.std_d };
  };

  window.updateCheckoutTotal = () => {
    const w = document.getElementById('delivery-wilaya')?.value || '';
    const m = document.querySelector('input[name="delivery_method"]:checked')?.value || 'standard';
    const subtotal = parseFloat(document.getElementById('checkout-subtotal')?.dataset.value || 0);
    const { price, days } = getDeliveryPrice(w, m);
    const elPrice = document.getElementById('delivery-price');
    const elDays  = document.getElementById('delivery-days');
    const elTotal = document.getElementById('checkout-total');
    if (elPrice) elPrice.textContent = price === 0 ? 'Gratuit' : price.toLocaleString() + ' DA';
    if (elDays)  elDays.textContent  = days;
    if (elTotal) elTotal.textContent = (subtotal + price).toLocaleString() + ' DA';
    // Update standard/express prices by wilaya
    if (w) {
      const z = ZONES[w] || 'C'; const p = PRICES[z];
      const stdLbl = document.getElementById('std-price-lbl');
      const expLbl = document.getElementById('exp-price-lbl');
      if (stdLbl) stdLbl.textContent = p.std.toLocaleString() + ' DA · ' + p.std_d;
      if (expLbl) expLbl.textContent = p.exp.toLocaleString() + ' DA · ' + p.exp_d;
    }
  };

  // ── Delivery option select ────────────────────────────
  window.selectDelivery = (method) => {
    document.querySelectorAll('.delivery-option').forEach(el => {
      el.classList.toggle('selected', el.dataset.method === method);
    });
    const radio = document.querySelector(`input[name="delivery_method"][value="${method}"]`);
    if (radio) radio.checked = true;
    updateCheckoutTotal();
  };

  // ── Payment option select ─────────────────────────────
  window.selectPayment = (method) => {
    document.querySelectorAll('.payment-option').forEach(el => {
      el.classList.toggle('selected', el.dataset.method === method);
    });
    const radio = document.querySelector(`input[name="payment_method"][value="${method}"]`);
    if (radio) radio.checked = true;
  };

  // ── Image preview (product form) ─────────────────────
  const imgInput = document.getElementById('imageInput');
  const imgPreview = document.getElementById('imagePreview');
  if (imgInput && imgPreview) {
    imgInput.addEventListener('change', function () {
      imgPreview.innerHTML = '';
      [...this.files].forEach((f, i) => {
        const r = new FileReader();
        r.onload = e => {
          imgPreview.innerHTML += `
            <div style="position:relative;width:80px;height:80px;">
              <img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:var(--r-10);border:2px solid ${i===0?'var(--green)':'var(--border-md)'}">
              ${i===0?'<span style="position:absolute;bottom:0;left:0;right:0;background:var(--green);color:#fff;font-size:.55rem;text-align:center;border-radius:0 0 8px 8px;padding:2px;">Principale</span>':''}
            </div>`;
        };
        r.readAsDataURL(f);
      });
    });
  }

  // ── Lightbox ──────────────────────────────────────────
  window.openLightbox = (src) => {
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay animate-fade-in';
    overlay.innerHTML = `
      <button class="lightbox-close" onclick="this.closest('.lightbox-overlay').remove()">
        <i class="fa-solid fa-xmark"></i>
      </button>
      <img src="${src}" class="lightbox-img" alt="">`;
    overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
    document.body.appendChild(overlay);
  };

  // ── Wishlist toggle ───────────────────────────────────
  window.toggleWishlist = async (btn, productId) => {
    const csrf = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
    btn.disabled = true;
    try {
      const res = await fetch(`/accounts/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (res.status === 302 || res.redirected) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        return;
      }
      const data = await res.json();
      btn.classList.toggle('active', data.added);
      const icon = btn.querySelector('i');
      if (icon) icon.className = data.added ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
      showToast(data.message || (data.added ? 'Ajouté aux favoris !' : 'Retiré des favoris.'), data.added ? 'success' : 'info');
    } catch(e) {
      showToast('Erreur lors de la mise à jour des favoris.', 'error');
    }
    btn.disabled = false;
  };

  // ── Confirm delete ────────────────────────────────────
  window.confirmDelete = (formId) => {
    if (confirm('Êtes-vous sûr ? Cette action est irréversible.')) {
      document.getElementById(formId)?.submit();
    }
  };

  // ── Category nav active link ──────────────────────────
  const catLinks = document.querySelectorAll('.cat-nav-item');
  const currentCat = new URLSearchParams(window.location.search).get('category');
  catLinks.forEach(link => {
    const href = link.getAttribute('href') || '';
    if (currentCat && href.includes(currentCat)) link.classList.add('active');
  });

  // ── Smooth scroll ─────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  // ── Back to top ───────────────────────────────────────
  const btt = document.getElementById('backToTop');
  if (btt) {
    window.addEventListener('scroll', () => {
      btt.style.opacity = window.scrollY > 400 ? '1' : '0';
      btt.style.pointerEvents = window.scrollY > 400 ? 'all' : 'none';
    }, { passive: true });
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ── Form validation ───────────────────────────────────
  document.querySelectorAll('form.validate').forEach(form => {
    form.addEventListener('submit', e => {
      let valid = true;
      form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
          field.classList.add('is-invalid');
          valid = false;
        } else {
          field.classList.remove('is-invalid');
        }
      });
      if (!valid) {
        e.preventDefault();
        showToast('Veuillez remplir tous les champs obligatoires.', 'error');
      }
    });
  });

  // ── Count-up animation ────────────────────────────────
  if ('IntersectionObserver' in window) {
    const countIO = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const el  = e.target;
        const end = parseInt(el.dataset.countTo, 10);
        if (isNaN(end) || end === 0) return;
        const duration = 1200;
        const start    = performance.now();
        const startVal = 0;
        const step = ts => {
          const progress = Math.min((ts - start) / duration, 1);
          const eased    = 1 - Math.pow(1 - progress, 3);
          el.textContent = Math.round(startVal + (end - startVal) * eased).toLocaleString('fr-DZ');
          if (progress < 1) requestAnimationFrame(step);
          else el.textContent = end.toLocaleString('fr-DZ');
        };
        requestAnimationFrame(step);
        countIO.unobserve(el);
      });
    }, { threshold: 0.3 });
    document.querySelectorAll('[data-count-to]').forEach(el => countIO.observe(el));
  }

  // ── Search autocomplete ───────────────────────────────
  const searchInput = document.getElementById('navSearchInput');
  const searchDropdown = document.getElementById('searchAutocomplete');

  if (searchInput && searchDropdown) {
    let acTimer = null;
    let acAbort = null;

    const closeAC = () => { searchDropdown.style.display = 'none'; };
    const openAC  = () => { searchDropdown.style.display = 'block'; };

    searchInput.addEventListener('input', () => {
      clearTimeout(acTimer);
      const q = searchInput.value.trim();
      if (q.length < 2) { closeAC(); return; }
      acTimer = setTimeout(async () => {
        if (acAbort) acAbort.abort();
        acAbort = new AbortController();
        try {
          const res = await fetch(`/products/search/?q=${encodeURIComponent(q)}`, {
            signal: acAbort.signal,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          });
          if (!res.ok) return;
          const data = await res.json();
          renderAC(data.results, q);
        } catch(e) { if (e.name !== 'AbortError') closeAC(); }
      }, 280);
    });

    function renderAC(results, q) {
      if (!results.length) {
        searchDropdown.innerHTML = `<div class="search-ac-empty"><i class="fa-solid fa-face-sad-tear me-2"></i>Aucun résultat pour « ${escHtmlAC(q)} »</div>`;
        openAC(); return;
      }
      const items = results.map(r => `
        <a href="/products/${r.slug}/" class="search-ac-item">
          <div class="search-ac-thumb">
            ${r.image ? `<img src="${r.image}" alt="${escHtmlAC(r.name)}">` : `<span>${r.icon}</span>`}
          </div>
          <div style="flex:1;min-width:0;">
            <div class="search-ac-name">${highlight(r.name, q)}</div>
            <div class="search-ac-meta">${escHtmlAC(r.store)} · ${escHtmlAC(r.category)}</div>
          </div>
          <div class="search-ac-price">
            ${Math.round(r.price).toLocaleString()} DA
            ${r.discount > 0 ? `<span class="search-ac-discount">-${Math.round(r.discount)}%</span>` : ''}
          </div>
        </a>`).join('');
      const footer = `<div class="search-ac-footer" onclick="document.getElementById('navSearchForm').submit()">
        <i class="fa-solid fa-magnifying-glass me-2"></i>Voir tous les résultats pour « ${escHtmlAC(q)} »
      </div>`;
      searchDropdown.innerHTML = items + footer;
      openAC();
    }

    function escHtmlAC(s) {
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
    function highlight(text, q) {
      const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      return escHtmlAC(text).replace(re, '<mark style="background:var(--green-xl);color:var(--green);border-radius:2px;padding:0 2px;">$1</mark>');
    }

    document.addEventListener('click', e => {
      if (!searchDropdown.contains(e.target) && e.target !== searchInput) closeAC();
    });
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeAC();
    });
  }

  // ── Real-time Notifications ───────────────────────────
  const notifBadge       = document.getElementById('notifBadge');
  const notifList        = document.getElementById('notifList');
  const notifUnreadLabel = document.getElementById('notifUnreadLabel');
  const notifBellIcon    = document.getElementById('notifBellIcon');

  const NOTIF_ICONS = {
    order_placed:         { icon: 'fa-bag-shopping',       color: '#1A6B2F' },
    order_confirmed:      { icon: 'fa-circle-check',       color: '#16A34A' },
    order_cancelled:      { icon: 'fa-circle-xmark',       color: '#DC2626' },
    order_shipped:        { icon: 'fa-truck',               color: '#0369A1' },
    order_delivered:      { icon: 'fa-house-circle-check', color: '#16A34A' },
    expiry_alert:         { icon: 'fa-hourglass-half',     color: '#D97706' },
    stock_warning:        { icon: 'fa-triangle-exclamation', color: '#E65000' },
    negotiation_offer:    { icon: 'fa-handshake',          color: '#7c3aed' },
    negotiation_accepted: { icon: 'fa-handshake-simple',   color: '#16A34A' },
    negotiation_rejected: { icon: 'fa-handshake-slash',    color: '#DC2626' },
    negotiation_counter:  { icon: 'fa-rotate',             color: '#0369A1' },
    new_registration:     { icon: 'fa-user-plus',          color: '#0369A1' },
    new_offer:            { icon: 'fa-tag',                color: '#1A6B2F' },
    system:               { icon: 'fa-circle-info',        color: '#6B8A6B' },
  };

  function renderNotifItem(n) {
    const meta  = NOTIF_ICONS[n.notif_type] || NOTIF_ICONS.system;
    const unreadStyle = n.is_read ? '' : 'background:var(--green-xl);border-left:3px solid var(--green);';
    const link  = n.link || '/notifications/';
    return `
      <a href="${link}" onclick="markReadNav(${n.id},event)" style="display:flex;align-items:flex-start;gap:11px;padding:11px 16px;border-bottom:1px solid var(--border);text-decoration:none;color:var(--text);transition:background .15s;${unreadStyle}" onmouseover="this.style.background='var(--surface-2)'" onmouseout="this.style.background='${n.is_read ? '' : 'var(--green-xl)'}'">
        <div style="width:34px;height:34px;border-radius:10px;background:${meta.color}18;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;">
          <i class="fa-solid ${meta.icon}" style="color:${meta.color};font-size:.85rem;"></i>
        </div>
        <div style="flex:1;min-width:0;">
          <div style="font-weight:${n.is_read ? '500' : '700'};font-size:.83rem;line-height:1.3;margin-bottom:2px;">${n.title}</div>
          ${n.body ? `<div style="font-size:.77rem;color:var(--text-lt);line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${n.body}</div>` : ''}
          <div style="font-size:.72rem;color:var(--text-xl);margin-top:3px;"><i class="fa-regular fa-clock me-1"></i>${n.created_at}</div>
        </div>
        ${!n.is_read ? '<div style="width:7px;height:7px;border-radius:50%;background:var(--danger);flex-shrink:0;margin-top:6px;"></div>' : ''}
      </a>`;
  }

  function updateNotifUI(data) {
    if (!notifBadge) return;
    const count = data.unread_count;

    // Badge
    if (count > 0) {
      notifBadge.textContent = count > 99 ? '99+' : count;
      notifBadge.style.display = 'flex';
      notifBellIcon && notifBellIcon.classList.add('fa-shake');
    } else {
      notifBadge.style.display = 'none';
      notifBellIcon && notifBellIcon.classList.remove('fa-shake');
    }

    // Unread label in dropdown header
    if (notifUnreadLabel) {
      if (count > 0) {
        notifUnreadLabel.textContent = count + ' non lue' + (count > 1 ? 's' : '');
        notifUnreadLabel.style.display = 'inline';
      } else {
        notifUnreadLabel.style.display = 'none';
      }
    }

    // Notification list
    if (notifList) {
      if (data.notifications.length === 0) {
        notifList.innerHTML = `<div style="padding:32px 16px;text-align:center;color:var(--text-lt);font-size:.84rem;"><i class="fa-regular fa-bell" style="font-size:1.8rem;display:block;margin-bottom:8px;opacity:.4;"></i>Aucune notification</div>`;
      } else {
        notifList.innerHTML = data.notifications.map(renderNotifItem).join('');
      }
    }
  }

  async function pollNotifications() {
    try {
      const res = await fetch('/notifications/api/');
      if (!res.ok) return;
      const data = await res.json();
      updateNotifUI(data);
    } catch (_) {}
  }

  window.markReadNav = async (pk, e) => {
    // Don't prevent default — let the link navigate, just mark as read in background
    try {
      const csrf = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
      await fetch(`/notifications/${pk}/read/`, { method: 'POST', headers: { 'X-CSRFToken': csrf } });
      pollNotifications();
    } catch (_) {}
  };

  window.markAllReadNav = async () => {
    try {
      const csrf = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
      await fetch('/notifications/read-all/', { method: 'POST', headers: { 'X-CSRFToken': csrf } });
      pollNotifications();
    } catch (_) {}
  };

  if (notifBadge) {
    pollNotifications();
    setInterval(pollNotifications, 20000); // poll every 20s
  }

  // ── Skeleton helpers (public API) ─────────────────────
  window.showSkeleton = (containerId, count = 4) => {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = Array(count).fill(`
      <div class="col-6 col-xl-4 col-xxl-3">
        <div class="skeleton-card">
          <div class="skeleton skeleton-img"></div>
          <div class="skeleton-body">
            <div class="skeleton skeleton-line w-80"></div>
            <div class="skeleton skeleton-line w-60"></div>
            <div class="skeleton skeleton-line h-20 w-40"></div>
          </div>
        </div>
      </div>`).join('');
  };


});

// ── Charts (Chart.js) — defined at module level so pages can call it immediately ──
window.initChart = (id, type, labels, datasets, options = {}) => {
  const canvas = document.getElementById(id);
  if (!canvas || typeof Chart === 'undefined') return;
  return new Chart(canvas, {
    type,
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: { legend: { display: false }, ...options.plugins },
      scales: type !== 'doughnut' && type !== 'pie' ? {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,.05)' }, ...(options.scales?.y || {}) },
        x: { grid: { display: false }, ...(options.scales?.x || {}) }
      } : undefined,
      ...options
    }
  });
};
