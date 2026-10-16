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

  /* --- Mot d'accueil en relief ------------------------------------------ */
  var scene = document.querySelector("[data-scene]");
  var relief = document.querySelector("[data-relief]");
  var sobre = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (scene && relief && !sobre.matches) {
    var AMPLITUDE = 11; // degrés max : assez pour se voir, pas pour gêner la lecture

    function incliner(e) {
      var r = scene.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5;
      var y = (e.clientY - r.top) / r.height - 0.5;
      relief.style.transform =
        "rotateX(" + (-y * AMPLITUDE) + "deg) rotateY(" + (x * AMPLITUDE) + "deg)";
    }

    function relacher() {
      scene.dataset.actif = "false";
      relief.style.transform = "";
    }

    scene.addEventListener("pointerenter", function () { scene.dataset.actif = "true"; });
    scene.addEventListener("pointermove", incliner);
    scene.addEventListener("pointerleave", relacher);
    scene.addEventListener("pointercancel", relacher);

    // Au doigt : on suit le glissement, puis on revient au repos.
    scene.addEventListener("pointerdown", function (e) {
      scene.dataset.actif = "true";
      incliner(e);
    });
    scene.addEventListener("pointerup", relacher);
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
