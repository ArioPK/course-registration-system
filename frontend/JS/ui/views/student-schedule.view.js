/**
 * frontend/JS/ui/student-schedule.view.js
 */
export class StudentScheduleView {
  constructor() {
    this.scheduleSection = document.getElementById("schedule-section");
    this.scheduleContainer = document.getElementById("schedule-container");
    this.coursesGrid = document.getElementById("courses-grid");
    this.searchToolbar = document.querySelector(".student-search-toolbar");
    this.emptyState = document.getElementById("no-schedule-msg");

    this.dayMap = {
      SAT: "شنبه",
      SUN: "یکشنبه",
      MON: "دوشنبه",
      TUE: "سه‌شنبه",
      WED: "چهارشنبه",
      THU: "پنج‌شنبه",
      FRI: "جمعه",
    };
  }

  renderSchedule(scheduleData) {
    this.scheduleContainer.innerHTML = "";

    if (!scheduleData || !scheduleData.days || scheduleData.days.length === 0) {
      this.emptyState.classList.remove("hidden");
      return;
    }

    const hasClasses = scheduleData.days.some(
      (d) => d.blocks && d.blocks.length > 0
    );
    if (!hasClasses) {
      this.emptyState.classList.remove("hidden");
      return;
    }

    this.emptyState.classList.add("hidden");

    scheduleData.days.forEach((day) => {
      if (!day.blocks || day.blocks.length === 0) return;

      const dayCard = document.createElement("div");
      dayCard.className = "schedule-day-card";

      const persianDay = this.dayMap[day.day_of_week] || day.day_of_week;

      let blocksHTML = "";

      const sortedBlocks = day.blocks.sort((a, b) =>
        a.start_time.localeCompare(b.start_time)
      );

      sortedBlocks.forEach((block) => {
        const start = block.start_time.substring(0, 5);
        const end = block.end_time.substring(0, 5);

        blocksHTML += `
                    <div class="schedule-block">
                        <div class="block-time">
                            <i class="ri-time-line"></i> ${start} - ${end}
                        </div>
                        <div class="block-course">${block.name}</div>
                        <div class="block-details">
                            <span><i class="ri-barcode-line"></i> کد: ${block.code}</span>
                            <span><i class="ri-user-voice-line"></i> استاد: ${block.professor_name}</span>
                            <span><i class="ri-map-pin-line"></i> مکان: ${block.location}</span>
                        </div>
                    </div>
                `;
      });

      dayCard.innerHTML = `
                <div class="day-header">
                    <i class="ri-calendar-fill"></i> ${persianDay}
                </div>
                <div class="day-blocks">
                    ${blocksHTML}
                </div>
            `;

      this.scheduleContainer.appendChild(dayCard);
    });
  }

  toggleView(showSchedule) {
    const enrollmentsSection = document.getElementById("enrollments-section");
    
    if (showSchedule) {
      this.scheduleSection.classList.remove("hidden");
      this.coursesGrid.classList.add("hidden");
      if (this.searchToolbar) this.searchToolbar.classList.add("hidden"); // مخفی کردن سرچ در حالت برنامه
      if (enrollmentsSection) enrollmentsSection.classList.add("hidden"); // مخفی کردن بخش دروس من
    } else {
      this.scheduleSection.classList.add("hidden");
      this.coursesGrid.classList.remove("hidden");
      if (this.searchToolbar) this.searchToolbar.classList.remove("hidden");
      if (enrollmentsSection) enrollmentsSection.classList.add("hidden"); // اطمینان از مخفی بودن بخش دروس من
    }
  }
}
