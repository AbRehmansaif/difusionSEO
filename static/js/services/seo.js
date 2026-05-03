/* SEO Specific Logic */

document.addEventListener('DOMContentLoaded', () => {
    console.log('SEO Strategy Page Initialized');
    
    // Add any specific interactive logic for SEO page here
    // Example: Parallax orbs following mouse
    const seoOrbs = document.querySelectorAll('.seo-pulse');
    
    document.addEventListener('mousemove', (e) => {
        const x = (window.innerWidth / 2 - e.pageX) * 0.01;
        const y = (window.innerHeight / 2 - e.pageY) * 0.01;
        
        seoOrbs.forEach(orb => {
            orb.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
});
