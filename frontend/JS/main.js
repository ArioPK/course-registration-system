/**
 * js/main.js
 * Responsibility: Composition Root.
 * Wires up all services, views, and controllers, then starts the application.
 */

import { AuthService } from "./services/auth.service.js";
import { ApiService } from "./services/api.service.js";
import { CourseValidator } from "./utils/validator.js";
import { CourseView } from "./ui/view.js";
import { CourseController } from "./controllers/course.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  // 0. Check if we are on the admin panel page
  // This prevents errors if the script is included globally but the element is missing.
  const adminContainer = document.querySelector(".admin-container");
  if (!adminContainer) return;

  // 1. Initialize Authentication Service
  const authService = new AuthService();

  // 2. Auth Guard: Redirect if not logged in
  // We check this BEFORE initializing other heavy services.
  if (!authService.isAuthenticated()) {
    authService.enforceAuth(); // Redirects to login
    return; // Stop execution
  }

  // 3. Configuration
  // You can switch this to production URL later
  const API_BASE_URL = "http://localhost:8000"; 

  // 4. Instantiate Dependencies (Services & UI)
  const apiService = new ApiService(API_BASE_URL);
  const validator = new CourseValidator();
  const view = new CourseView();

  // 5. Inject Dependencies into the Controller
  // The controller doesn't create dependencies; it receives them.
  const controller = new CourseController(
    apiService,
    authService,
    validator,
    view
  );

  // 6. Start the Application
  console.log("Admin Panel Initialized.");
  controller.init();
});