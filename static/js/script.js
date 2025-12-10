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
        browseProfilesBtn.addEventListener('click', function(e){
            e.preventDefault();
            const isAuthenticated = this.dataset.authenticated === 'true' || 
                                    document.body.classList.contains('user-authenticated');
            if (isAuthenticated) {
                  // Redirect to profile list if logged in
            window.location.href = '/profiles/';
            } else {
                // Redirect to login if not logged in
            window.location.href = '/account/login/';
            }
        });
    }

    

     // PROFILE FORM - SAVE BUTTON 
    
     const profileForm = document.querySelector('form[enctype="multipart/form-data"]');
     const saveProfileBtn = profileForm ? profileForm.querySelector('button[type="submit"]') : null;
     
     if (profileForm && saveProfileBtn) {
         // Add form validation before submission
         profileForm.addEventListener('submit', function(e) {
           
             // Show loading state
             saveProfileBtn.disabled = true;
             saveProfileBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Saving...';
             
             // Form will submit normally if validation passes
         });
         
       
     }
 });