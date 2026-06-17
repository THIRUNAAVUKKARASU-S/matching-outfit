document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile Menu Toggle
    const mobileToggle = document.getElementById("mobile-toggle-btn");
    const navMenu = document.getElementById("nav-menu");
    const navLinks = document.querySelectorAll(".nav-link");

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener("click", () => {
            navMenu.classList.toggle("active");
            const icon = mobileToggle.querySelector("i");
            if (navMenu.classList.contains("active")) {
                icon.classList.replace("fa-bars", "fa-xmark");
            } else {
                icon.classList.replace("fa-xmark", "fa-bars");
            }
        });
    }

    // Close mobile menu when a link is clicked
    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            if (navMenu && navMenu.classList.contains("active")) {
                navMenu.classList.remove("active");
                const icon = mobileToggle.querySelector("i");
                icon.classList.replace("fa-xmark", "fa-bars");
            }
        });
    });

    // 2. Sticky Navbar & Active Link on Scroll
    const header = document.getElementById("navbar");
    const sections = document.querySelectorAll("section");

    window.addEventListener("scroll", () => {
        // Sticky class
        if (window.scrollY > 50) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }

        // Active section tracking
        let currentSectionId = "";
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop - 150) {
                currentSectionId = section.getAttribute("id");
            }
        });

        navLinks.forEach(link => {
            link.classList.remove("active");
            if (link.getAttribute("href") === `#${currentSectionId}`) {
                link.classList.add("active");
            }
        });
    });

    // 3. Typing Effect
    const typingSpan = document.getElementById("typing-text");
    const phrases = [
        "B.Tech Information Technology Student",
        "Machine Learning Enthusiast",
        "Software Developer"
    ];
    let phraseIndex = 0;
    let characterIndex = 0;
    let isDeleting = false;
    let typingSpeed = 100;

    function typeEffect() {
        if (!typingSpan) return;
        
        const currentPhrase = phrases[phraseIndex];
        
        if (isDeleting) {
            // Remove characters
            typingSpan.textContent = currentPhrase.substring(0, characterIndex - 1);
            characterIndex--;
            typingSpeed = 50; // Deleting is faster
        } else {
            // Add characters
            typingSpan.textContent = currentPhrase.substring(0, characterIndex + 1);
            characterIndex++;
            typingSpeed = 100;
        }

        // State changes
        if (!isDeleting && characterIndex === currentPhrase.length) {
            // End of phrase, wait before deleting
            isDeleting = true;
            typingSpeed = 1500; // Pause at full string
        } else if (isDeleting && characterIndex === 0) {
            isDeleting = false;
            phraseIndex = (phraseIndex + 1) % phrases.length;
            typingSpeed = 500; // Pause before typing next phrase
        }

        setTimeout(typeEffect, typingSpeed);
    }

    // Initialize typing
    if (typingSpan) {
        setTimeout(typeEffect, 1000);
    }

    // 4. Projects Category Filter
    const filterButtons = document.querySelectorAll(".filter-btn");
    const projectCards = document.querySelectorAll(".project-card");

    filterButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            // Active button highlight
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const filterValue = btn.getAttribute("data-filter");

            projectCards.forEach(card => {
                const category = card.getAttribute("data-category");
                
                if (filterValue === "all" || category === filterValue) {
                    card.style.display = "flex";
                    // Add subtle fade-in entrance
                    card.style.opacity = "0";
                    setTimeout(() => {
                        card.style.opacity = "1";
                        card.style.transition = "opacity 0.4s ease";
                    }, 50);
                } else {
                    card.style.display = "none";
                }
            });
        });
    });

    // 5. Contact Form Mock Handler
    const contactForm = document.getElementById("contact-form");
    const successMessage = document.getElementById("form-success-msg");

    if (contactForm && successMessage) {
        contactForm.addEventListener("submit", (e) => {
            e.preventDefault();
            
            // Collect message info (can be used for further integration, e.g. EmailJS)
            const name = document.getElementById("form-name").value;
            const email = document.getElementById("form-email").value;
            const message = document.getElementById("form-message").value;

            console.log("Mock Form Submission:", { name, email, message });

            // Display success alert
            successMessage.style.display = "flex";
            contactForm.reset();

            // Hide success message after 5 seconds
            setTimeout(() => {
                successMessage.style.display = "none";
            }, 5000);
        });
    }
});
