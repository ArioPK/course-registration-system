/**
 * frontend/JS/professor.main.js
 */
import { AuthService } from "./services/auth.service.js";
import { ApiService } from "./services/api.service.js";
import { ProfessorCourseView } from "./ui/professor-course.view.js";
import { ProfessorCourseController } from "./controllers/professor-course.controller.js";

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Services
    const authService = new AuthService();
    
    const apiService = new ApiService("http://localhost:8000"); 

    // 2. Auth Check
    if (!authService.isAuthenticated()) {
        authService.enforceAuth(); 
        return;
    }

    const role = authService.getRole();
    if (role !== "professor") {
       
        window.location.href = "../Login/index.html"; 
        return;
    }

    
    const logoutBtn = document.getElementById("logout-btn");
    if(logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            authService.logout();
        });
    }

    // 3. Initialize View & Controller
    const view = new ProfessorCourseView();
    const controller = new ProfessorCourseController(apiService, authService, view);

    // 4. Start
    console.log("Professor Panel Initialized.");
    controller.init();
});