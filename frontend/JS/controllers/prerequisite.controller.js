/**
 * js/controllers/prerequisite.controller.js
 
 */
export class PrerequisiteController {
    
    constructor(prereqRepo, courseRepo, view) {
      this.prereqRepo = prereqRepo;
      this.courseRepo = courseRepo;
      this.view = view;
  
      this.state = {
        prerequisites: [],
        coursesMap: {},
        coursesList: [],
      };
    }
  
    async init() {
      this._bindEvents();
      await this.loadData();
    }
  
    async loadData() {
      try {
        // تغییر: استفاده از متدهای هر ریپازیتوری به صورت جداگانه
        const [courses, prerequisites] = await Promise.all([
          this.courseRepo.getCourses(),        // دریافت دروس از CourseRepository
          this.prereqRepo.getPrerequisites(),  // دریافت پیش‌نیازها از PrerequisiteRepository
        ]);
  
        this.state.coursesList = courses || [];
        this.state.prerequisites = prerequisites || [];
  
        this.state.coursesMap = this.state.coursesList.reduce((acc, course) => {
          acc[course.id] = course;
          return acc;
        }, {});
  
        this.view.populateDropdowns(this.state.coursesList);
        this._refreshPrerequisitesList();
      } catch (error) {
        console.error(error);
        this.view.notifier.showError("خطا در بارگیری اطلاعات پیش‌نیازها.");
      }
    }
  
    _refreshPrerequisitesList() {
      this.view.renderPrerequisites(
        this.state.prerequisites,
        this.state.coursesMap
      );
    }
  
    _bindEvents() {
      this.view.bindOpenModal(() => this.view.openModal());
  
      this.view.bindSubmit((formData) =>
        this._handlePrerequisiteFormSubmit(formData)
      );
  
      this.view.bindDelete((id) => this._handleDeletePrerequisiteClick(id));
    }
  
    async _handlePrerequisiteFormSubmit(formData) {
      if (formData.target_course_id === formData.prerequisite_course_id) {
        this.view.notifier.showError(
          "درس هدف و درس پیش‌نیاز نمی‌توانند یکسان باشند."
        );
        return;
      }
  
      const isDuplicate = this.state.prerequisites.some(
        (p) =>
          p.target_course_id === formData.target_course_id &&
          p.prerequisite_course_id === formData.prerequisite_course_id
      );
  
      if (isDuplicate) {
        this.view.notifier.showError("این پیش‌نیاز قبلاً تعریف شده است.");
        return;
      }
  
      this.view.setSubmitting(true);
  
      try {
        // تغییر: استفاده از this.prereqRepo
        await this.prereqRepo.addPrerequisite(formData);
        this.view.closeModal();
        await this.loadData();
        this.view.notifier.showSuccess("پیش‌نیاز با موفقیت تعریف شد.");
      } catch (error) {
        console.error(error);
        this.view.notifier.showError(`خطا در تعریف پیش‌نیاز: ${error.message}`);
      } finally {
        this.view.setSubmitting(false);
      }
    }
  
    _handleDeletePrerequisiteClick(id) {
      const prereq = this.state.prerequisites.find((p) => p.id === id);
      if (!prereq) return;
  
      const targetName =
        this.state.coursesMap[prereq.target_course_id]?.name ||
        `ID ${prereq.target_course_id}`;
      const prereqName =
        this.state.coursesMap[prereq.prerequisite_course_id]?.name ||
        `ID ${prereq.prerequisite_course_id}`;
  
      this.view.notifier.showConfirmation(
        `آیا از حذف پیش‌نیاز "${prereqName}" برای درس "${targetName}" مطمئن هستید؟`,
        async () => {
          try {
            // تغییر: استفاده از this.prereqRepo
            await this.prereqRepo.deletePrerequisite(id);
            this.view.notifier.showSuccess("پیش‌نیاز با موفقیت حذف شد.");
            await this.loadData();
          } catch (error) {
            this.view.notifier.showError(error.message);
          }
        }
      );
    }
  }