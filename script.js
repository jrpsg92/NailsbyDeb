/* Nails by Deb — comportements partagés.
   Tout est optionnel : sans JS, la navigation et la galerie restent utilisables. */
(function () {
  "use strict";

  /* --- Menu mobile ------------------------------------------------------ */
  var bascule = document.querySelector("[data-bascule]");
  var nav = document.querySelector("[data-nav]");

  if (bascule && nav) {
    bascule.hidden = false;
    nav.dataset.ouvert = "false";
    bascule.setAttribute("aria-expanded", "false");

    bascule.addEventListener("click", function () {
      var ouvert = bascule.getAttribute("aria-expanded") === "true";
      bascule.setAttribute("aria-expanded", String(!ouvert));
      nav.dataset.ouvert = String(!ouvert);
    });

    // Échap referme, et le focus revient sur le bouton
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && bascule.getAttribute("aria-expanded") === "true") {
        bascule.setAttribute("aria-expanded", "false");
        nav.dataset.ouvert = "false";
        bascule.focus();
      }
    });
  }

  /* --- Visionneuse de galerie ------------------------------------------- */
  var vues = Array.prototype.slice.call(document.querySelectorAll("[data-piece]"));
  var boite = document.querySelector("[data-visionneuse]");

  if (!vues.length || !boite || typeof boite.showModal !== "function") return;

  var affichee = boite.querySelector("img");
  var position = 0;

  function montrer(i) {
    position = (i + vues.length) % vues.length;
    var source = vues[position].querySelector("img");
    affichee.src = source.currentSrc || source.src;
    affichee.alt = source.alt;
    boite.querySelector("[data-rang]").textContent =
      position + 1 + " sur " + vues.length;
  }

  vues.forEach(function (vue, i) {
    vue.addEventListener("click", function () {
      montrer(i);
      boite.showModal();
    });
  });

  boite.querySelector("[data-prec]").addEventListener("click", function () {
    montrer(position - 1);
  });
  boite.querySelector("[data-suiv]").addEventListener("click", function () {
    montrer(position + 1);
  });
  boite.querySelector("[data-fermer]").addEventListener("click", function () {
    boite.close();
  });

  boite.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") { e.preventDefault(); montrer(position - 1); }
    if (e.key === "ArrowRight") { e.preventDefault(); montrer(position + 1); }
  });

  // Clic sur le fond : on ferme
  boite.addEventListener("click", function (e) {
    if (e.target === boite) boite.close();
  });
})();
