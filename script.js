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

  /* --- Filtres de la galerie -------------------------------------------- */
  var barre = document.querySelector("[data-filtres]");
  var grille = document.querySelector("[data-grille]");

  if (barre && grille) {
    var compte = document.querySelector("[data-compte]");
    var toutes = Array.prototype.slice.call(grille.querySelectorAll("[data-piece]"));

    barre.addEventListener("click", function (e) {
      var puce = e.target.closest("[data-filtre]");
      if (!puce) return;

      var choix = puce.dataset.filtre;
      barre.querySelectorAll("[data-filtre]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b === puce));
      });

      var visibles = 0;
      toutes.forEach(function (piece) {
        var garder = choix === "tout" || piece.dataset.cat === choix;
        piece.hidden = !garder;
        if (garder) visibles++;
      });

      if (compte) {
        compte.textContent =
          visibles + (visibles > 1 ? " poses affichées" : " pose affichée");
      }
    });
  }

  /* --- Visionneuse de galerie ------------------------------------------- */
  // Seules les vignettes visibles entrent dans la navigation de la visionneuse.
  var vues = Array.prototype.slice.call(document.querySelectorAll("[data-piece]"));
  var boite = document.querySelector("[data-visionneuse]");

  if (!vues.length || !boite || typeof boite.showModal !== "function") return;

  var affichee = boite.querySelector("img");
  var position = 0;
  var parcours = vues; // recalculé à chaque ouverture selon le filtre actif

  function montrer(i) {
    position = (i + parcours.length) % parcours.length;
    var source = parcours[position].querySelector("img");
    affichee.src = source.currentSrc || source.src;
    affichee.alt = source.alt;
    boite.querySelector("[data-rang]").textContent =
      position + 1 + " sur " + parcours.length;
  }

  vues.forEach(function (vue) {
    vue.addEventListener("click", function () {
      // On ne parcourt que ce qui est effectivement affiché.
      parcours = vues.filter(function (v) { return !v.hidden; });
      montrer(parcours.indexOf(vue));
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
