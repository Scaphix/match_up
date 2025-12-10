// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    //  HOME PAGE BUTTONS 
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
                window.location.href = 'profile/about/';
            } else {
                // Redirect to signup if not logged in
                window.location.href = '/account/signup/';
            }
        });
    }
    
    // Browse Profiles Button - redirects to profile list
    const browseProfilesBtn = document.querySelector('secondary');
    if (browseProfilesBtn) {
        browseProfilesBtn.addEventListener('click', function(e){
            e.preventDefault();
            const isAuthenticated = this.dataset.authenticated === 'true' || 
                                    document.body.classList.contains('user-authenticated');
            if (isAuthenticated) {
                  // Redirect to profile list if logged in
                  window.location.href = '/profiles/';
            } else {
                // Redirect to login if not logged in
                alert('Please login to browse profiles');
                window.location.href = '/account/login/';
            }
        });
    }
 });

 