// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    //  HOME PAGE BUTTONS 
    console.log('DOMContentLoaded');
    // Get Started Button - redirects to signup or profile creation
    const getStartedBtn = document.getElementById('cta');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Check if user is authenticated 
            const isAuthenticated = this.dataset.authenticated === 'true' || 
                                   document.body.classList.contains('user-authenticated');
            if (isAuthenticated) {
                // Redirect to profile creation if logged in
                window.location.href = '/profile/create/';
            } else {
                // Redirect to signup if not logged in
                window.location.href = '/account/signup/';
            }
        });
    }
    
    // Browse Profiles Button - redirects to profile list
    const browseProfilesBtn = document.querySelector('.secondary');
    if (browseProfilesBtn) {
        browseProfilesBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/profiles/';
        });
    }
});