import { AuthService } from "./services/auth.service.js";
import { ApiService } from "./services/api.service.js";
import { StudentCourseView } from "./ui/views/student-course.view.js";
import { StudentCourseController } from "./controllers/student-course.controller.js";
import { StudentScheduleView } from "./ui/views/student-schedule.view.js";
import { StudentScheduleController } from "./controllers/student-schedule.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize Services
  const authService = new AuthService();
  const apiService = new ApiService("http://localhost:8000");
 
document.getElementById("logout-btn").addEventListener("click", () => authService.logout());

document.getElementById("view-schedule-btn").addEventListener("click", () => {
    document.getElementById("courses-grid").classList.add("hidden");
    document.getElementById("schedule-section").classList.remove("hidden");
});

  // 2. Auth Check
  if (!authService.isAuthenticated()) {
    authService.enforceAuth();
    return;
  }

  const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        authService.logout();
    });
}

  const role = authService.getRole();
  if (role !== "student") {
    window.location.href = "../Login/index.html";
    return;
  }

  // 3. Initialize Course Catalog
  const courseView = new StudentCourseView();
  const courseController = new StudentCourseController(
    apiService,
    authService,
    courseView
  );
  courseController.init();

  // 4. Initialize Schedule
  const scheduleView = new StudentScheduleView();
  const scheduleController = new StudentScheduleController(
    apiService,
    scheduleView
  );

  console.log("Student Panel & Schedule Initialized.");
});
