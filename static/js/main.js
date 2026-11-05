/**
 * EcoSell - Core Client-Side Logic
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
  const dashboardSidebar = document.querySelector('.dashboard-sidebar');
  if (sidebarToggleBtn && dashboardSidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      dashboardSidebar.classList.toggle('show');
    });
  }

  // 2. Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 3. Auto-dismiss flash alerts after 6 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 6000);

  // 4. Live Image Preview for Ticket Creation
  const imageInput = document.getElementById('garbageImageInput');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');
  if (imageInput && imagePreviewContainer && imagePreview) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          imagePreview.src = e.target.result;
          imagePreviewContainer.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
      } else {
        imagePreviewContainer.classList.add('d-none');
      }
    });
  }

  // 5. Dynamic Estimated Total Calculation for Bidding Form
  const offerPriceInput = document.getElementById('offerPriceInput');
  const estQuantityElem = document.getElementById('estQuantityValue');
  const estTotalDisplay = document.getElementById('estTotalDisplay');

  if (offerPriceInput && estQuantityElem && estTotalDisplay) {
    const estQty = parseFloat(estQuantityElem.getAttribute('data-qty') || 0);
    offerPriceInput.addEventListener('input', function () {
      const price = parseFloat(this.value) || 0;
      const total = price * estQty;
      estTotalDisplay.textContent = '₹' + total.toFixed(2);
    });
  }

  // 6. Dynamic Actual Collection Weight & Final Amount Calculation
  const actualWeightInput = document.getElementById('actualWeightInput');
  const acceptedRateElem = document.getElementById('acceptedRateValue');
  const finalPayoutDisplay = document.getElementById('finalPayoutDisplay');

  if (actualWeightInput && acceptedRateElem && finalPayoutDisplay) {
    const rate = parseFloat(acceptedRateElem.getAttribute('data-rate') || 0);
    actualWeightInput.addEventListener('input', function () {
      const weight = parseFloat(this.value) || 0;
      const finalAmount = weight * rate;
      finalPayoutDisplay.textContent = '₹' + finalAmount.toFixed(2);
    });
  }

  // 7. Notification Mark Read AJAX
  const markReadButtons = document.querySelectorAll('.btn-mark-read');
  markReadButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const notifId = this.getAttribute('data-id');
      fetch(`/notifications/read/${notifId}`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const item = document.getElementById(`notif-item-${notifId}`);
          if (item) item.remove();
          updateUnreadBadgeCount();
        }
      });
    });
  });

  const markAllReadBtn = document.getElementById('btnMarkAllRead');
  if (markAllReadBtn) {
    markAllReadBtn.addEventListener('click', function(e) {
      e.preventDefault();
      fetch('/notifications/read-all', {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const list = document.getElementById('notificationList');
          if (list) {
            list.innerHTML = '<li class="p-3 text-center text-muted small">No new notifications</li>';
          }
          const badge = document.getElementById('notificationBadge');
          if (badge) badge.classList.add('d-none');
        }
      });
    });
  }

  function updateUnreadBadgeCount() {
    fetch('/notifications/unread-count')
      .then(res => res.json())
      .then(data => {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
          if (data.count > 0) {
            badge.textContent = data.count;
            badge.classList.remove('d-none');
          } else {
            badge.classList.add('d-none');
          }
        }
      });
  }
});

