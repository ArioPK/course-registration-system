/**
 * js/ui/views/layout.view.js
 */
export class LayoutView {
    constructor(notificationService) {
      this.notifier = notificationService;
      this.elements = {
        logoutBtn: document.getElementById("logout-btn"),
        navLinks: document.querySelectorAll(".nav-link"),
        sections: document.querySelectorAll(".management-section"),
        modalCloseBtns: document.querySelectorAll(".modal-close-btn"),
        siteLink: document.querySelector(".site-link"),
      };
      
      this._initGlobalModalClosing();
    }
  
    _initGlobalModalClosing() {
      this.elements.modalCloseBtns.forEach((btn) => {
        btn.addEventListener("click", (e) => {
          const modal = e.target.closest(".modal-backdrop");
          if (modal) this.notifier.closeModal(modal);
        });
      });
    }
  
    bindNavLinks(handler) {
      this.elements.navLinks.forEach((link) => {
        link.addEventListener("click", (e) => {
          e.preventDefault();
          if (link.dataset.target) {
            const targetId = link.dataset.target;
            handler(targetId);
          }
        });
      });
    }
  
    setActiveSection(targetId) {
      this.elements.navLinks.forEach((link) => {
        link.classList.toggle("active", link.dataset.target === targetId);
      });
  
      this.elements.sections.forEach((section) => {
        section.classList.toggle("active", section.id === targetId);
      });
    }
  
    bindLogout(handler) {
      if (this.elements.logoutBtn) {
        this.elements.logoutBtn.addEventListener("click", (e) => {
          e.preventDefault();
          handler();
        });
      }
    }
  }