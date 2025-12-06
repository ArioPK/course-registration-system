import { ApiService } from "./services/api.service.js";
import { AuthService } from "./services/auth.service.js";
import { LoginValidator } from "./utils/login.validator.js";
import { LoginView } from "./ui/login.view.js";
import { LoginController } from "./controllers/login.controller.js";

document.addEventListener("DOMContentLoaded", () => {
  const API_BASE_URL = "http://localhost:8000";
  const apiService = new ApiService(API_BASE_URL);
  const authService = new AuthService();
  const validator = new LoginValidator();
  const view = new LoginView();

  const controller = new LoginController(
    apiService,
    authService,
    validator,
    view
  );

 
  console.log("Login Page Initialized via MVC pattern.");
  controller.init();
});