(function (window) {
  function toISODate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function parseISODate(isoString) {
    if (!isoString) {
      return new Date();
    }
    const [year, month, day] = isoString.split('-').map(Number);
    const date = new Date(year, (month || 1) - 1, day || 1);
    if (Number.isNaN(date.getTime())) {
      return new Date();
    }
    return date;
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  window.frequencyPage = function frequencyPage(initialData = {}) {
    return {
      apiUrl: initialData.apiUrl || '',
      currentDate: initialData.currentDate || toISODate(new Date()),
      students: initialData.students || [],
      presentStudentIds: initialData.presentStudents || [],
      search: '',
      loading: false,
      flashMessage: '',

      init() {
        this.presentStudentIds = [...new Set((this.presentStudentIds || []).map((id) => Number(id)))];
        this.scheduleIconRefresh();
      },

      get filteredStudents() {
        const term = this.search.trim().toLowerCase();
        if (!term) {
          return this.students;
        }
        return this.students.filter((student) =>
          student.name.toLowerCase().includes(term)
        );
      },

      get formattedFullDate() {
        const date = parseISODate(this.currentDate);
        return date.toLocaleDateString('pt-BR', {
          weekday: 'long',
          day: '2-digit',
          month: 'long',
          year: 'numeric',
        });
      },

      isPresent(studentId) {
        const normalizedId = Number(studentId);
        return this.presentStudentIds.includes(normalizedId);
      },

      setPresent(studentId, present) {
        const normalizedId = Number(studentId);
        if (present) {
          if (!this.isPresent(normalizedId)) {
            this.presentStudentIds = [...this.presentStudentIds, normalizedId];
          }
        } else {
          this.presentStudentIds = this.presentStudentIds.filter((id) => id !== normalizedId);
        }
        this.scheduleIconRefresh();
      },

      async changeDay(delta) {
        const date = parseISODate(this.currentDate);
        date.setDate(date.getDate() + delta);
        const iso = toISODate(date);
        this.currentDate = iso;
        await this.fetchAttendance();
      },

     async fetchAttendance() {
        if (!this.apiUrl) {
          console.error('URL da API de frequência não configurada.');
          return;
        }
        this.loading = true;
        this.flashMessage = '';
        try {
          const response = await fetch(`${this.apiUrl}?date=${this.currentDate}`);
          if (!response.ok) {
            throw new Error('Não foi possível carregar a frequência.');
          }
          const data = await response.json();
          this.presentStudentIds = (data.present_students || []).map((id) => Number(id));
          this.scheduleIconRefresh();
        } catch (error) {
          console.error(error);
          this.flashMessage = error.message || 'Erro ao carregar frequência.';
          if (window.notificationModal) {
            window.notificationModal.show({
              title: 'Erro ao carregar',
              message: error.message || 'Não foi possível carregar a frequência.',
            });
          }
        } finally {
          this.loading = false;
        }
      },

     async toggleAttendance(student) {
        if (!this.apiUrl || !student?.id) {
          return;
        }

        const isPresent = this.isPresent(student.id);
        const payload = {
          student_id: student.id,
          date: this.currentDate,
        };

        this.loading = true;
        const options = {
          method: isPresent ? 'DELETE' : 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify(payload),
        };

        try {
          const response = await fetch(this.apiUrl, options);
          if (!response.ok && response.status !== 204) {
            const data = await response.json().catch(() => ({}));
            const message = data.message || 'Não foi possível atualizar a frequência.';
            throw new Error(message);
          }

          this.setPresent(student.id, !isPresent);
          this.flashMessage = '';
          this.scheduleIconRefresh();
        } catch (error) {
          console.error(error);
          this.flashMessage = error.message || 'Não foi possível atualizar a frequência.';
          if (window.notificationModal) {
            window.notificationModal.show({
              title: 'Não foi possível atualizar',
              message: error.message || 'Não conseguimos atualizar a frequência.',
            });
          }
        } finally {
          this.loading = false;
        }
      },
      scheduleIconRefresh() {
        if (typeof this.$nextTick === 'function') {
          this.$nextTick(() => {
            if (window.lucide && typeof window.lucide.createIcons === 'function') {
              window.lucide.createIcons();
            }
          });
        }
      },
    };
  };
}(window));
