document.addEventListener("DOMContentLoaded", function () {
  const images = document.querySelectorAll("img.lazy-logo");
  images.forEach((img) => {
    img.src = img.dataset.src;
  });
});
