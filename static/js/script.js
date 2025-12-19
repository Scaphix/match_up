
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

function openLink(link) {
    window.location.href = link;
}
