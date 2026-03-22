document.querySelector("#claude").addEventListener("click", (e) => {
  const query = document.querySelector("#query").value;
  if (query) {
    window.location.replace(`https://claude.ai/new?q=${query}`);
  }
});
