document.addEventListener("DOMContentLoaded", function () {
    const image = document.getElementById("media");
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    const closeBtn = document.querySelector(".close");

    // Stop quietly if the modal markup isn't on this page
    if (!modal || !modalImage) {
        return;
    }

    function openModal(src, alt) {
        modalImage.src = src;
        modalImage.alt = alt || "Enlarged view";
        modal.style.display = "flex";
    }

    function closeModal() {
        modal.style.display = "none";
        modalImage.src = "";
    }

    // Only the home page (image days) has #media
    if (image) {
        image.addEventListener("click", function () {
            openModal(image.src, image.alt);
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    // Click the dark background to close
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Press Escape to close
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeModal();
        }
    });
});