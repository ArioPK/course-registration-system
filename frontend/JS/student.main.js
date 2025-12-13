/**
 * js/student.main.js
 * Responsibility: Composition Root for Student Panel.
 */
import { AuthService } from "./services/auth.service.js";
import { ApiService } from "./services/api.service.js";
import { StudentCourseView } from "./ui/student-course.view.js";
import { StudentCourseController } from "./controllers/student-course.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize Services
  const authService = new AuthService();
  const apiService = new ApiService("http://localhost:8000"); // Base URL

  
  if (!authService.isAuthenticated()) {
    authService.enforceAuth();
    return;
  }

  const role = authService.getRole();
  if (role !== "student") {
      
      window.location.href = authService.getRedirectUrl();
      return;
  }

  // 3. Initialize View & Controller
  const view = new StudentCourseView();
  const controller = new StudentCourseController(apiService, authService, view);

  // 4. Start
  console.log("Student Panel Initialized.");
  controller.init();
});