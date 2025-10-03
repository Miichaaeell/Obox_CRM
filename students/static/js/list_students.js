function studentFilters() {
  const contextdata = document.getElementById('contextData')
  return {
    baseUrl: contextdata.dataset.listUrl,
    filter: contextdata.dataset.filter,
    searchTerm: contextdata.dataset.search,
    applyFilter(value) {
      this.filter = value;
      this.navigate();
    },
    submitSearch() {
      this.navigate();
    },
    clearFilters() {
      this.filter = 'all';
      this.searchTerm = '';
      this.navigate();
    },
    navigate() {
      const params = new URLSearchParams();
      if (this.filter && this.filter !== 'all') {
        params.set('filter', this.filter);
      }
      if (this.searchTerm) {
        params.set('search', this.searchTerm);
      }
      const query = params.toString();
      window.location.href = query ? `${this.baseUrl}?${query}` : this.baseUrl;
    }
  }
}