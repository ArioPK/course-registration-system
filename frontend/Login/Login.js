/*==================================================================
 * login SCRIPT - Backend Ready & Fully Functional
 *------------------------------------------------------------------
 * This file handles all the front-end logic for the login page.
 * Its responsibilities include:
 *
 * 1.  Authentication (Login & Auth Guard):
 * - Handles the login form on index.html.
 * - Protects the panel from unauthorized access using SessionStorage.
 *
 * 2.  Data Management:
 * - Simulates a backend API for data operations.
 * - In a real application, the `api` object would make `fetch` calls.
 *
 * 3.  State Persistence:
 * - Saves the user's last active section/tab to LocalStorage.
 * - Restores the state upon page refresh for better UX.
 *
 * 4.  UI Rendering:
 * - Dynamically builds and displays the gallery and news tables from data.
 *
 * 5.  Event Handling & CRUD Operations:
 * - Manages clicks on all interactive elements (edit, delete, add).
 * - Handles form submissions for Create, Read, Update, Delete (CRUD).
 *
 * 6.  Modal Control:
 * - Opens and closes modals for editing, adding, and confirmation.
 * - Manages image uploads and previews using FileReader.
 *
 ==================================================================*/

 document.addEventListener("DOMContentLoaded", () => {
    //==================================================================
    // SECTION 1: AUTHENTICATION
    //=================================================================
   
    // This part only runs on the login page (index.html).
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
       //==================================================================
       // API CONFIGURATION
       // Configure your login API endpoint here
       // Set USE_MOCK to false and provide your LOGIN_ENDPOINT to use real API
       //==================================================================
       const API_CONFIG = {
          // Set to true to use mock authentication (for development)
          // Set to false to use real API endpoint
          USE_MOCK: true,
          // Your actual login API endpoint URL
          LOGIN_ENDPOINT: "https://api.example.com/auth/login",
          // Request timeout in milliseconds
          TIMEOUT: 10000
       };
 
       //==================================================================
       // FORM ELEMENTS
       // Get references to all form elements for validation and state management
       //==================================================================
       const usernameInput = document.getElementById("username");
       const passwordInput = document.getElementById("password");
       const loginButton = loginForm.querySelector(".login-btn");
       const errorElement = document.getElementById("login-error");
 
       //==================================================================
       // FRONT-END VALIDATION
       // Client-side validation before API call
       // Validates username and password fields with real-time feedback
       //==================================================================
       
       /**
        * Validates username field
        * Checks for empty, length, and character restrictions
        * @param {string} username - The username to validate
        * @returns {Object} - { isValid: boolean, message: string }
        */
       function validateUsername(username) {
          const trimmed = username.trim();
          if (!trimmed) {
             return { isValid: false, message: "نام کاربری الزامی است." };
          }
          if (trimmed.length < 3) {
             return { isValid: false, message: "نام کاربری باید حداقل ۳ کاراکتر باشد." };
          }
          if (trimmed.length > 50) {
             return { isValid: false, message: "نام کاربری نمی‌تواند بیشتر از ۵۰ کاراکتر باشد." };
          }
          // Allow alphanumeric, underscore, and Persian characters
          const usernameRegex = /^[a-zA-Z0-9_\u0600-\u06FF]+$/;
          if (!usernameRegex.test(trimmed)) {
             return { isValid: false, message: "نام کاربری فقط می‌تواند شامل حروف، اعداد و خط زیر باشد." };
          }
          return { isValid: true, message: "" };
       }
 
       /**
        * Validates password field
        * Checks for empty and length restrictions
        * @param {string} password - The password to validate
        * @returns {Object} - { isValid: boolean, message: string }
        */
       function validatePassword(password) {
          if (!password) {
             return { isValid: false, message: "رمز عبور الزامی است." };
          }
          if (password.length < 4) {
             return { isValid: false, message: "رمز عبور باید حداقل ۴ کاراکتر باشد." };
          }
          if (password.length > 100) {
             return { isValid: false, message: "رمز عبور نمی‌تواند بیشتر از ۱۰۰ کاراکتر باشد." };
          }
          return { isValid: true, message: "" };
       }
 
       /**
        * Validates entire form
        * Runs validation on all fields and returns consolidated result
        * @returns {Object} - { isValid: boolean, errors: Object }
        */
       function validateForm() {
          const username = usernameInput.value;
          const password = passwordInput.value;
          
          const usernameValidation = validateUsername(username);
          const passwordValidation = validatePassword(password);
          
          const errors = {};
          if (!usernameValidation.isValid) {
             errors.username = usernameValidation.message;
          }
          if (!passwordValidation.isValid) {
             errors.password = passwordValidation.message;
          }
          
          return {
             isValid: usernameValidation.isValid && passwordValidation.isValid,
             errors: errors
          };
       }
 
       /**
        * Updates field validation state (visual feedback)
        * Adds/removes error/success classes and displays error messages
        * @param {HTMLElement} input - The input element
        * @param {boolean} isValid - Whether the field is valid
        * @param {string} message - Error message if invalid
        */
       function updateFieldValidation(input, isValid, message) {
          const formGroup = input.closest(".form-group");
          const errorSpan = formGroup.querySelector(".field-error");
          
          // Remove previous validation classes
          input.classList.remove("input-error", "input-success");
          if (errorSpan) {
             errorSpan.remove();
          }
          
          if (isValid === false) {
             input.classList.add("input-error");
             const errorElement = document.createElement("span");
             errorElement.className = "field-error";
             errorElement.textContent = message;
             formGroup.appendChild(errorElement);
          } else if (isValid === true && input.value.trim()) {
             input.classList.add("input-success");
          }
       }
 
       // Real-time validation on input blur (when user leaves the field)
       usernameInput.addEventListener("blur", () => {
          const validation = validateUsername(usernameInput.value);
          updateFieldValidation(usernameInput, validation.isValid, validation.message);
       });
 
       passwordInput.addEventListener("blur", () => {
          const validation = validatePassword(passwordInput.value);
          updateFieldValidation(passwordInput, validation.isValid, validation.message);
       });
 
       // Clear validation errors on input (real-time feedback)
       usernameInput.addEventListener("input", () => {
          if (usernameInput.classList.contains("input-error")) {
             updateFieldValidation(usernameInput, true, "");
          }
       });
 
       passwordInput.addEventListener("input", () => {
          if (passwordInput.classList.contains("input-error")) {
             updateFieldValidation(passwordInput, true, "");
          }
       });
 
       //==================================================================
       // LOGIN API INTEGRATION
       // Handles API calls to login endpoint with proper error handling
       // Supports both mock (development) and real API endpoints
       //==================================================================
       
       /**
        * Mock login function for development/testing
        * Simulates API delay and returns mock authentication response
        * @param {string} username - Username
        * @param {string} password - Password
        * @returns {Promise<Object>} - Login response with success status and data/error
        */
       async function mockLogin(username, password) {
          // Simulate API delay (1 second)
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Mock authentication logic
          if (username === "admin" && password === "1234") {
             return {
                success: true,
                data: {
                   token: "mock-jwt-token-" + Date.now(),
                   user: {
                      id: 1,
                      username: "admin",
                      role: "admin"
                   }
                }
             };
          } else {
             return {
                success: false,
                error: {
                   code: "INVALID_CREDENTIALS",
                   message: "نام کاربری یا رمز عبور اشتباه است."
                }
             };
          }
       }
 
       /**
        * Real API login function
        * Makes actual HTTP request to login endpoint
        * Handles network errors, timeouts, and server errors
        * @param {string} username - Username
        * @param {string} password - Password
        * @returns {Promise<Object>} - Login response with success status and data/error
        */
       async function apiLogin(username, password) {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
          
          try {
             const response = await fetch(API_CONFIG.LOGIN_ENDPOINT, {
                method: "POST",
                headers: {
                   "Content-Type": "application/json",
                },
                body: JSON.stringify({
                   username: username,
                   password: password
                }),
                signal: controller.signal
             });
             
             clearTimeout(timeoutId);
             
             const data = await response.json();
             
             if (!response.ok) {
                return {
                   success: false,
                   error: {
                      code: data.code || "LOGIN_FAILED",
                      message: data.message || "خطا در ورود به سیستم"
                   }
                };
             }
             
             return {
                success: true,
                data: data
             };
          } catch (error) {
             clearTimeout(timeoutId);
             
             if (error.name === "AbortError") {
                return {
                   success: false,
                   error: {
                      code: "TIMEOUT",
                      message: "زمان درخواست به پایان رسید. لطفاً دوباره تلاش کنید."
                   }
                };
             }
             
             return {
                success: false,
                error: {
                   code: "NETWORK_ERROR",
                   message: "خطا در اتصال به سرور. لطفاً اتصال اینترنت خود را بررسی کنید."
                }
             };
          }
       }
 
       //==================================================================
       // LOADING STATE MANAGEMENT
       // Handles UI states during API calls
       // Shows loading spinner and disables form during request
       //==================================================================
       
       /**
        * Sets loading state on login button
        * Disables button and shows loading spinner during API call
        * @param {boolean} isLoading - Whether to show loading state
        */
       function setLoadingState(isLoading) {
          if (isLoading) {
             loginButton.disabled = true;
             loginButton.classList.add("loading");
             loginButton.innerHTML = '<span class="spinner"></span> در حال ورود...';
          } else {
             loginButton.disabled = false;
             loginButton.classList.remove("loading");
             loginButton.textContent = "ورود";
          }
       }
 
       //==================================================================
       // SUCCESS STATE MANAGEMENT
       // Handles successful login flow
       // Stores authentication data and redirects to panel
       //==================================================================
       
       /**
        * Handles successful login
        * Stores token and user data in sessionStorage
        * Shows success message and redirects to panel
        * @param {Object} responseData - Response data from API
        */
       function handleLoginSuccess(responseData) {
          // Store authentication token/session
          if (responseData.token) {
             sessionStorage.setItem("authToken", responseData.token);
          }
          sessionStorage.setItem("isAdminLoggedIn", "true");
          
          // Store user data if available
          if (responseData.user) {
             sessionStorage.setItem("userData", JSON.stringify(responseData.user));
          }
          
          // Show success message briefly
          errorElement.textContent = "";
          errorElement.className = "success-message";
          errorElement.textContent = "ورود موفقیت‌آمیز بود. در حال انتقال...";
          
          // Redirect to panel after short delay
          setTimeout(() => {
             window.location.href = "../panel/index.html";
          }, 1000);
       }
 
       //==================================================================
       // ERROR STATE MANAGEMENT
       // Handles failed login scenarios
       // Displays appropriate error messages based on error type
       //==================================================================
       
       /**
        * Handles login errors
        * Displays error message and provides visual feedback
        * Focuses on appropriate field if needed
        * @param {Object} error - Error object from API
        */
       function handleLoginError(error) {
          setLoadingState(false);
          
          // Show error message
          errorElement.className = "error-message";
          errorElement.textContent = error.message || "خطا در ورود به سیستم";
          
          // Add shake animation to form
          loginForm.style.animation = "shake 0.5s";
          setTimeout(() => {
             loginForm.style.animation = "";
          }, 500);
          
          // Focus on first invalid field or username
          if (error.field) {
             const field = document.getElementById(error.field);
             if (field) {
                field.focus();
                field.select();
             }
          } else {
             usernameInput.focus();
          }
       }
 
       //==================================================================
       // FORM SUBMISSION HANDLER
       // Main login form submission logic
       // Validates form, calls API, and handles response
       //==================================================================
       
       loginForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          
          // Clear previous error messages
          errorElement.textContent = "";
          errorElement.className = "error-message";
          
          // Clear field validation states
          usernameInput.classList.remove("input-error", "input-success");
          passwordInput.classList.remove("input-error", "input-success");
          document.querySelectorAll(".field-error").forEach(el => el.remove());
          
          // Front-end validation
          const validation = validateForm();
          if (!validation.isValid) {
             // Show validation errors
             if (validation.errors.username) {
                updateFieldValidation(usernameInput, false, validation.errors.username);
             }
             if (validation.errors.password) {
                updateFieldValidation(passwordInput, false, validation.errors.password);
             }
             
             // Show general error message
             errorElement.textContent = "لطفاً فیلدهای فرم را به درستی پر کنید.";
             loginForm.style.animation = "shake 0.5s";
             setTimeout(() => {
                loginForm.style.animation = "";
             }, 500);
             return;
          }
          
          // Get form values
          const username = usernameInput.value.trim();
          const password = passwordInput.value;
          
          // Set loading state
          setLoadingState(true);
          
          try {
             // Call appropriate login function (mock or real API)
             const response = API_CONFIG.USE_MOCK 
                ? await mockLogin(username, password)
                : await apiLogin(username, password);
             
             if (response.success) {
                handleLoginSuccess(response.data);
             } else {
                handleLoginError(response.error);
             }
          } catch (error) {
             // Handle unexpected errors
             handleLoginError({
                code: "UNEXPECTED_ERROR",
                message: "خطای غیرمنتظره رخ داد. لطفاً دوباره تلاش کنید."
             });
             console.error("Login error:", error);
          }
       });
       
       return; // Stop script execution if on the login page
    }
 });
 