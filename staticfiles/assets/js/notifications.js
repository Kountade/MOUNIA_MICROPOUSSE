// static/assets/js/notifications.js
class NotificationManager {
    constructor() {
        this.updateInterval = 30000; // 30 secondes
        this.init();
    }

    init() {
        this.loadNotifications();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    loadNotifications() {
        fetch('/notifications/ajax/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur réseau');
                }
                return response.json();
            })
            .then(data => {
                this.updateNotificationCount(data.total_non_lues);
                this.updateNotificationsList(data.notifications);
                this.updateDailyStats(data.statistiques);
            })
            .catch(error => {
                console.error('Erreur chargement notifications:', error);
                this.showErrorState();
            });
    }

    updateNotificationCount(count) {
        const countElement = document.getElementById('notification-count');
        if (countElement) {
            countElement.textContent = count;
            if (count > 0) {
                countElement.style.display = 'block';
                // Animation pour les nouvelles notifications
                countElement.classList.add('pulse-animation');
                setTimeout(() => {
                    countElement.classList.remove('pulse-animation');
                }, 1000);
            } else {
                countElement.style.display = 'none';
            }
        }
    }

    updateNotificationsList(notifications) {
        const container = document.getElementById('notifications-list');
        if (!container) return;
        
        if (notifications.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-bell-slash text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2 mb-0">Aucune notification</p>
                </div>
            `;
            return;
        }

        container.innerHTML = notifications.map(notif => `
            <li class="notification-item ${notif.lue ? '' : 'unread'}" data-notification-id="${notif.id}">
                <div class="d-flex align-items-start w-100">
                    <i class="bi ${this.getNotificationIcon(notif.type)} ${this.getNotificationColor(notif.type)} me-3 mt-1"></i>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${notif.titre}</h6>
                        <p class="small text-muted mb-1">${notif.message}</p>
                        <small class="text-muted">${notif.date_creation}</small>
                    </div>
                    ${!notif.lue ? '<span class="badge bg-danger badge-dot ms-2 mt-1"></span>' : ''}
                </div>
            </li>
        `).join('');

        // Ajouter les écouteurs d'événements pour marquer comme lu
        container.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('a')) {
                    this.markAsRead(item.dataset.notificationId);
                }
            });
        });
    }

    updateDailyStats(stats) {
        const section = document.getElementById('daily-stats-section');
        const title = document.getElementById('stats-title');
        const content = document.getElementById('stats-content');
        
        if (!section || !title || !content) return;
        
        if (stats.total_commandes > 0) {
            section.style.display = 'block';
            const aujourdHui = new Date().toLocaleDateString('fr-FR');
            title.innerHTML = `<i class="bi bi-calendar-check me-1"></i> Commandes du ${aujourdHui}`;
            content.innerHTML = `
                <div class="d-flex justify-content-between small">
                    <span class="text-success">✅ ${stats.commandes_livrees}</span>
                    <span class="text-warning">⏳ ${stats.commandes_en_cours}</span>
                    <span class="text-primary">📋 ${stats.commandes_confirmees}</span>
                    <span class="text-danger">❌ ${stats.commandes_annulees}</span>
                </div>
                <div class="mt-1 text-center">
                    <small class="text-muted">Total: <strong>${stats.total_commandes}</strong> commande(s)</small>
                </div>
            `;
        } else {
            section.style.display = 'none';
        }
    }

    getNotificationIcon(type) {
        const icons = {
            'commande_jour': 'bi-cart-check',
            'statut': 'bi-arrow-repeat',
            'rapport': 'bi-graph-up',
            'alerte': 'bi-exclamation-triangle'
        };
        return icons[type] || 'bi-bell';
    }

    getNotificationColor(type) {
        const colors = {
            'commande_jour': 'text-primary',
            'statut': 'text-warning',
            'rapport': 'text-info',
            'alerte': 'text-danger'
        };
        return colors[type] || 'text-secondary';
    }

    markAsRead(notificationId) {
        fetch('/notifications/marquer-lue/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ notification_id: notificationId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.loadNotifications();
            }
        })
        .catch(error => {
            console.error('Erreur marquage comme lu:', error);
        });
    }

    markAllAsRead() {
        fetch('/notifications/marquer-toutes-lues/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.loadNotifications();
                this.showToast('Toutes les notifications ont été marquées comme lues', 'success');
            }
        })
        .catch(error => {
            console.error('Erreur marquage tout comme lu:', error);
            this.showToast('Erreur lors du marquage des notifications', 'error');
        });
    }

    setupEventListeners() {
        // Marquer tout comme lu
        const markAllBtn = document.getElementById('mark-all-read');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }

        // Recharger quand le dropdown s'ouvre
        const dropdown = document.querySelector('.dropdown-notifications');
        if (dropdown) {
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');
            dropdown.addEventListener('show.bs.dropdown', () => {
                this.loadNotifications();
            });
            
            // Empêcher la fermeture quand on clique sur une notification
            dropdownMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Rafraîchissement manuel
        const refreshBtn = document.getElementById('refresh-notifications');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadNotifications();
                this.showToast('Notifications rafraîchies', 'info');
            });
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            // Ne rafraîchir que si l'utilisateur est sur la page
            if (!document.hidden) {
                this.loadNotifications();
            }
        }, this.updateInterval);
    }

    showErrorState() {
        const container = document.getElementById('notifications-list');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-wifi-off text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2 mb-0">Erreur de connexion</p>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="notificationManager.loadNotifications()">
                        Réessayer
                    </button>
                </div>
            `;
        }
    }

    showToast(message, type = 'info') {
        // Créer un toast Bootstrap simple
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Nettoyer après fermeture
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
}

// Initialisation globale
let notificationManager;

document.addEventListener('DOMContentLoaded', function() {
    notificationManager = new NotificationManager();
    
    // Exposer globalement pour le débogage
    window.notificationManager = notificationManager;
});