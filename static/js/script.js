// Helper function to open a link

function openLink(link) {
    window.location.href = link;
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

function handleNewMatch() {
    // Check if we are on the matches page
    const matchesPage = document.getElementById('matches-page');

    if (!matchesPage) {
        return;
    }
    
    // Check if we have a new match
    const newMatch = new URLSearchParams(window.location.search).get('new_match');
    if (newMatch === 'true') {
        let alert = document.getElementById('new-match-alert');
        
        if (alert) {
            // Create alert if it doesn't exist
                
                alert.classList.add('show');
             
        }
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
                    if (result.is_match) {
                        window.location.href = `/connections/matches/?new_match=true`;
                    }
                    else {
                        myProfileCard.classList.add('fade-out');
                        setTimeout(() => {
                            window.location.reload();
                        }, 400);
                    }
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
    handleNewMatch();
});