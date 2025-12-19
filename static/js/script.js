// Helper function to open a link

function openLink(link) {
    window.location.href = link;
}


// Handle like/pass buttons with AJAX
document.addEventListener('DOMContentLoaded', function() {
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
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
});

// Handle return to discover button

document.addEventListener('DOMContentLoaded', function() {
    const origin = new URLSearchParams(window.location.search).get('origin');
    if (origin === 'liked_profiles') {
        const returnToDiscoverButton = document.querySelector('.return-to-discover');
        returnToDiscoverButton.href = '/connections/liked/';
    }
});