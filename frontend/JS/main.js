/**
 * js/main.js
 * Responsibility: Composition Root.
 * Wires up all repositories, services, views, and controllers, then starts the application.
 */

// 1. Services & Repositories
import { AuthService } from "./services/auth.service.js";
import { CourseRepository } from "./services/repositories/course.repository.js";
import { PrerequisiteRepository } from "./services/repositories/prerequisite.repository.js";
import { SettingsRepository } from "./services/repositories/settings.repository.js";


import { NotificationService } from "./ui/notification.js";
import { LayoutView } from "./ui/views/LayoutView.js";
import { CourseManagerView } from "./ui/views/CourseManagerView.js";
import { PrerequisiteView } from "./ui/views/PrerequisiteView.js";
import { SettingsView } from "./ui/views/SettingsView.js";


import { CourseValidator } from "./utils/course.validator.js";
import { SettingsValidator } from "./utils/settings.validator.js";

// 4. Controllers
import { AdminCourseController } from "./controllers/admin-course.controller.js";
import { PrerequisiteController } from "./controllers/prerequisite.controller.js";
import { SettingsController } from "./controllers/settings.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  // 0. Check if we are on the admin panel page
  const adminContainer = document.querySelector(".admin-container");
  if (!adminContainer) return;

  // ---------------------------------------------------------
  // 1. Authentication Guard (Blocking)
  // ---------------------------------------------------------
  const authService = new AuthService();

  if (!authService.isAuthenticated()) {
    authService.enforceAuth(); // Redirects to login
    return;
  }

  const userRole = authService.getRole();
  if (userRole !== "admin") {
    console.warn(`Access denied for role: ${userRole}. Redirecting.`);
    window.location.href = authService.getRedirectUrl();
    return;
  }

  // ---------------------------------------------------------
  // 2. Infrastructure Setup
  // ---------------------------------------------------------
  const API_BASE_URL = "http://localhost:8000";

  // Shared Notification Service (Passed to all views)
  const notificationService = new NotificationService();

  // ---------------------------------------------------------
  // 3. Dependency Injection & Wiring
  // ---------------------------------------------------------

  // --- Module: Layout & Navigation ---
  const layoutView = new LayoutView(notificationService);

  // --- Module: Courses ---
  const courseRepository = new CourseRepository(API_BASE_URL);
  const courseValidator = new CourseValidator();
  const courseView = new CourseManagerView(notificationService);

  const courseController = new AdminCourseController(
    courseRepository,
    authService,
    courseValidator,
    courseView
  );

  // --- Module: Prerequisites ---
  const prereqRepository = new PrerequisiteRepository(API_BASE_URL);
  const prereqView = new PrerequisiteView(notificationService);

  const prereqController = new PrerequisiteController(
    prereqRepository,
    courseRepository,
    prereqView
  );

  // --- Module: Settings ---
  const settingsRepository = new SettingsRepository(API_BASE_URL);
  const settingsValidator = new SettingsValidator();
  const settingsView = new SettingsView(notificationService);

  const settingsController = new SettingsController(
    settingsRepository,
    settingsValidator,
    settingsView
  );

  // ---------------------------------------------------------
  // 4. Global Event Binding (Layout Logic)
  // ---------------------------------------------------------

  // Handle Sidebar Navigation
  layoutView.bindNavLinks((targetId) => {
    localStorage.setItem("activeAdminSection", targetId);
    layoutView.setActiveSection(targetId);
  });

  // Handle Logout
  layoutView.bindLogout(() => {
    authService.logout();
  });

  // Restore Active Tab on Reload
  const activeSection =
    localStorage.getItem("activeAdminSection") || "course-management";
  layoutView.setActiveSection(activeSection);

  // ---------------------------------------------------------
  // 5. Start Application Modules
  // ---------------------------------------------------------
  console.log("Admin Panel Initialized (Modular Architecture).");

  courseController.init();
  prereqController.init();
  settingsController.init();
});