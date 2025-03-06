
// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme based on localStorage or default to dark
    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
    
    const themeIcon = document.querySelector('.theme-icon');
    
    // Update the icon based on the current theme
    function updateIcon() {
        if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
            themeIcon.setAttribute('data-feather', 'sun');
        } else {
            themeIcon.setAttribute('data-feather', 'moon');
        }
        feather.replace(); // Update the icons
    }
    
    // Toggle theme when the button is clicked
    document.getElementById('theme-toggle').addEventListener('click', function() {
        if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        }
        updateIcon();
    });
    
    // Initialize the icon
    updateIcon();
});
