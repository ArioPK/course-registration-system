import { AuthService } from "./services/auth.service.js";
import { ApiService } from "./services/api.service.js";
import { StudentCourseView } from "./ui/student-course.view.js";
import { StudentCourseController } from "./controllers/student-course.controller.js";
import { StudentScheduleView } from "./ui/views/student-schedule.view.js";
import { StudentScheduleController } from "./controllers/student-schedule.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize Services
  const authService = new AuthService();
  const apiService = new ApiService("http://localhost:8000");

  // 2. Auth Check - Must be done first
  if (!authService.isAuthenticated()) {
    authService.enforceAuth();
    return;
  }

  const role = authService.getRole();
  if (role !== "student") {
    window.location.href = "../Login/index.html";
    return;
  }

  // 3. Bind logout button (after auth check passes)
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      authService.logout();
    });
  }

  // 4. Initialize Course Catalog
  const courseView = new StudentCourseView();
  const courseController = new StudentCourseController(
    apiService,
    authService,
    courseView
  );
  courseController.init();

  // 5. Initialize Schedule (this will bind view-schedule-btn and back-to-catalog-btn)
  const scheduleView = new StudentScheduleView();
  const scheduleController = new StudentScheduleController(
    apiService,
    scheduleView
  );

  console.log("Student Panel & Schedule Initialized.");
});
