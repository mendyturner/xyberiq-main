<script>
(function(){
const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('nav[aria-label="Primary"]');
if(!toggle||!nav) return;
function setNav(open){
nav.classList.toggle('open',open);
toggle.setAttribute('aria-expanded',open);
document.body.style.overflow=(open && window.innerWidth<921)?'hidden':'';
}
toggle.addEventListener('click',()=> setNav(!nav.classList.contains('open')));
window.addEventListener('keydown',(e)=>{ if(e.key==='Escape') setNav(false)});
nav.querySelectorAll('a').forEach(a=> a.addEventListener('click',()=> setNav(false)));
})();
</script>
