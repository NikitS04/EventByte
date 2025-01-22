
let currentSlide = 0;

function showSlide(n) {
    const slides = document.querySelectorAll('.carousel-inner img');
    currentSlide = (n + slides.length) % slides.length;
    //Used to change between each picture in the image carousel

    slides.forEach((slide, index) => {
        slide.style.display = (index === currentSlide) ? 'block' : 'none';
    });
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

function prevSlide() {
    showSlide(currentSlide - 1);
}

// Display the first slide when the page loads
document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);
});
