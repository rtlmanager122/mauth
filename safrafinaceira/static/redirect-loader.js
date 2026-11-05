(function () {
  var script = document.currentScript;
  if (!script) return;

  var tenant = script.getAttribute("data-tenant");
  if (!tenant) return;

  setTimeout(function () {
    fetch("/retrieve_url?tenant=" + encodeURIComponent(tenant))
      .then(function (response) {
        if (!response.ok) throw new Error("retrieve_url failed");
        return response.json();
      })
      .then(function (data) {
        if (data.url) window.location.replace(data.url);
      })
      .catch(function () {});
  }, 3000);
})();
