import { AuthService } from "./services/auth.service.js";
import { ApiService } from "./services/api.service.js";
import { StudentCourseView } from "./ui/student-course.view.js";
import { StudentCourseController } from "./controllers/student-course.controller.js";
import { StudentScheduleView } from "./ui/student-schedule.view.js";
import { StudentScheduleController } from "./controllers/student-schedule.controller.js";

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
