/**
 * MarketNest Main JavaScript
 * Handles AJAX Favorites, Gallery Previews, Form Upload Previews, and Interactive UI
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Get CSRF Token Helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // 2. AJAX Favorite Button Toggle
    const favButtons = document.querySelectorAll('.product-favorite-btn');
    favButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const productId = this.getAttribute('data-product-id');
            const targetUrl = this.getAttribute('data-url') || `/product/${productId}/favorite/`;
            const icon = this.querySelector('i');

            fetch(targetUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (response.status === 403 || response.redirected || response.status === 401) {
                    // Not logged in
                    window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return;

                if (data.is_favorited) {
                    this.classList.add('active');
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill', 'text-danger');
                    icon.classList.add('heart-animated');
                } else {
                    this.classList.remove('active');
                    icon.classList.remove('bi-heart-fill', 'text-danger');
                    icon.classList.add('bi-heart');
                    icon.classList.remove('heart-animated');
                }

                // Update navbar favorites badge if present
                const navBadge = document.getElementById('navFavBadge');
                if (navBadge) {
                    if (data.total_favorites > 0) {
                        navBadge.textContent = data.total_favorites;
                        navBadge.style.display = 'inline-block';
                    } else {
                        navBadge.style.display = 'none';
                    }
                }
            })
            .catch(err => {
                console.error("Favorite toggle error:", err);
            });
        });
    });

    // 3. Product Details Gallery Thumbnail Switcher
    const mainGalleryImg = document.getElementById('mainGalleryImage');
    const thumbnails = document.querySelectorAll('.gallery-thumb');

    if (mainGalleryImg && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function () {
                const newSrc = this.getAttribute('data-full-img');
                if (newSrc && mainGalleryImg.src !== newSrc) {
                    mainGalleryImg.style.opacity = '0.3';
                    setTimeout(() => {
                        mainGalleryImg.src = newSrc;
                        mainGalleryImg.style.opacity = '1';
                    }, 150);

                    thumbnails.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });
    }

    // 4. Image File Upload Preview (Create / Edit Listing)
    const primaryImgInput = document.getElementById('id_image') || document.querySelector('input[name="image"]');
    const previewContainer = document.getElementById('primaryImagePreviewContainer');
    const previewImage = document.getElementById('primaryImagePreview');

    if (primaryImgInput && previewContainer && previewImage) {
        primaryImgInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    previewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 5. Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 6. Initialize all Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
