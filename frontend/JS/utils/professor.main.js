/**
 * frontend/JS/professor.main.js
 */
import { AuthService } from "../services/auth.service.js";
import { ApiService } from "../services/api.service.js";
import { ProfessorCourseView } from "../ui/views/professor-course.view.js";
import { ProfessorCourseController } from "../controllers/professor-course.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  try {
    // 1. Initialize Services
    const authService = new AuthService();
    const apiService = new ApiService("http://localhost:8000");

    // 2. Auth Check
    if (!authService.isAuthenticated()) {
      authService.enforceAuth();
      return;
    }

    // 3. Role Check
    const role = authService.getRole();
    if (role !== "professor") {
      window.location.href = "../Login/index.html";
      return;
    }

    // 4. Bind logout button (after auth and role checks pass)
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
      const handleLogout = (e) => {
        if (e) {
          e.stopPropagation();
        }
        console.log("Logout button clicked");
        try {
          authService.logout();
        } catch (error) {
          console.error("Error during logout:", error);
          // Force redirect even if logout fails
          sessionStorage.clear();
          window.location.href = "../Login/index.html";
        }
        return false;
      };
      
      // Add multiple event listeners to ensure it works
      logoutBtn.addEventListener("click", handleLogout);
      logoutBtn.addEventListener("mousedown", handleLogout);
      logoutBtn.onclick = handleLogout;
      
      console.log("Logout button event listener added successfully");
    } else {
      console.error("Logout button not found! ID: logout-btn");
    }

    // 5. Initialize View & Controller
    const view = new ProfessorCourseView();
    const controller = new ProfessorCourseController(
      apiService,
      authService,
      view
    );

    // 6. Start
    console.log("Professor Panel Initialized.");
    controller.init();
  } catch (error) {
    console.error("Error initializing professor panel:", error);
  }
});
