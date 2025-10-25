(function(){
  const root = document.documentElement;
  const saved = localStorage.getItem('xyberiq-theme');
  if (saved) root.setAttribute('data-theme', saved);

  function apply(next){
    if (next) { root.setAttribute('data-theme', next); localStorage.setItem('xyberiq-theme', next); }
  }

  window.xyberTheme = {
    toggle(){
      const current = root.getAttribute('data-theme');
      apply(current === 'light' ? 'dark' : 'light');
    },
    set: apply
  };
})();
