const image = document.getElementById("media");

const modal = document.getElementById("imageModal");

const modalImage = document.getElementById("modalImage");

const closeBtn = document.querySelector(".close");

image.onclick = function(){

    modal.style.display = "flex";

    modalImage.src = image.src;

}

closeBtn.onclick = function(){

    modal.style.display = "none";

}