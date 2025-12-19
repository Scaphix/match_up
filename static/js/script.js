// Helper function to open a link

function openLink(link) {
    window.location.href = link;
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

function handleProfileDetailOrigin() {
    // Check if the origin is set
    const origin = new URLSearchParams(window.location.search).get('origin');
    if (!origin) {
        return;
    }

    // Check if the return to discover button exists
    const returnToDiscoverButton = document.querySelector('.return-to-discover');
    if (!returnToDiscoverButton) {
        return;
    }

    // Set the href of the return to discover button based on the origin
    if (origin === 'liked_profiles') {
        returnToDiscoverButton.href = '/connections/liked/';
    } else if (origin === 'matches') {
        returnToDiscoverButton.href = '/connections/matches/';
    }
}

function handleLikeButtons() {
    document.querySelectorAll('.like-btn, .pass-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const csrfToken = getCSRFToken();
            const myProfileCard = this.closest('.profile-card');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(async response => {
                if (!response.ok) {
                    throw new Error("Request failed");
                }

                let result = await response.json();
                if (result.success) {
                    myProfileCard.classList.add('fade-out');
                    setTimeout(() => {
                        window.location.reload();
                    }, 400);
                    
                } else {
                    throw new Error(result.error);
                }
                console.log(result);
            })
            .catch(error => {
                console.error(error);
            });    
        });
    });  
}

// Handle like/pass buttons with AJAX
document.addEventListener('DOMContentLoaded', function() {
    handleLikeButtons();
    handleProfileDetailOrigin();
});